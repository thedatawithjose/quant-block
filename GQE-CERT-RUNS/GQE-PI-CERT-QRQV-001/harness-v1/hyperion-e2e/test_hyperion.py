import contextlib
import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch
from hyperion import (
    Agent,
    AgentResponse,
    AgentResult,
    AgentStatus,
    CLIAgent,
    Evidence,
    Governance,
    GovernanceDecision,
    Orchestrator,
    Proposal,
    Task,
    TaskState,
    Validator,
    cli_init,
    cli_propose,
    cli_status,
    cli_submit,
    load_task,
    parse_agent_response,
    parse_args,
    save_task,
)


class MockAgent:
    def __init__(
        self,
        status: AgentStatus = AgentStatus.SUCCESS,
        summary: str = "ok",
        completed_criteria: list[str] | None = None,
        evidence: list[Evidence] | None = None,
        backlog: list[str] | None = None,
    ):
        self.status = status
        self.summary = summary
        self.completed_criteria = completed_criteria if completed_criteria is not None else []
        self.evidence = evidence if evidence is not None else []
        self.backlog = backlog if backlog is not None else []
        self.executed_with: Task | None = None

    def execute(self, task: Task) -> AgentResponse:
        self.executed_with = task
        return AgentResponse(
            status=self.status,
            summary=self.summary,
            completed_criteria=self.completed_criteria,
            evidence=self.evidence,
            backlog=self.backlog,
        )


class TestTaskStateTransitions(unittest.TestCase):
    def setUp(self):
        self.task = Task(
            title="Test Task",
            objective="Validate state machine",
            done_when=["Criterion 1"],
        )

    def test_initial_state(self):
        self.assertEqual(self.task.state, TaskState.DEFINED)

    def test_valid_transitions(self):
        # DEFINED -> EXECUTING
        self.task.transition_to(TaskState.EXECUTING)
        self.assertEqual(self.task.state, TaskState.EXECUTING)

        # EXECUTING -> VALIDATING
        self.task.transition_to(TaskState.VALIDATING)
        self.assertEqual(self.task.state, TaskState.VALIDATING)

        # VALIDATING -> DONE
        self.task.transition_to(TaskState.DONE)
        self.assertEqual(self.task.state, TaskState.DONE)

    def test_valid_review_transitions(self):
        self.task.transition_to(TaskState.REVIEW)
        self.assertEqual(self.task.state, TaskState.REVIEW)

        self.task.transition_to(TaskState.EXECUTING)
        self.assertEqual(self.task.state, TaskState.EXECUTING)

        self.task.transition_to(TaskState.REVIEW)
        self.assertEqual(self.task.state, TaskState.REVIEW)

        self.task.transition_to(TaskState.VALIDATING)
        self.assertEqual(self.task.state, TaskState.VALIDATING)

        # VALIDATING -> EXECUTING (validation retry)
        self.task.transition_to(TaskState.EXECUTING)
        self.assertEqual(self.task.state, TaskState.EXECUTING)

    def test_invalid_transitions_raise_value_error(self):
        with self.assertRaises(ValueError):
            self.task.transition_to(TaskState.DONE)

        with self.assertRaises(ValueError):
            self.task.transition_to(TaskState.VALIDATING)

        self.task.transition_to(TaskState.EXECUTING)
        self.task.transition_to(TaskState.VALIDATING)
        self.task.transition_to(TaskState.DONE)

        for state in [TaskState.DEFINED, TaskState.EXECUTING, TaskState.VALIDATING, TaskState.REVIEW]:
            with self.subTest(state=state):
                with self.assertRaises(ValueError):
                    self.task.transition_to(state)


class TestGovernance(unittest.TestCase):
    def setUp(self):
        self.governance = Governance()

    def test_empty_problem_returns_reject(self):
        proposal = Proposal(
            description="Do something",
            problem="   ",
            necessary_for_objective=True,
            simpler_alternative_exists=False,
            justification="Necessary",
        )
        decision = self.governance.evaluate(proposal)
        self.assertEqual(decision, GovernanceDecision.REJECT)

    def test_not_necessary_for_objective_returns_backlog(self):
        proposal = Proposal(
            description="Add caching",
            problem="Potential future slowness",
            necessary_for_objective=False,
            simpler_alternative_exists=False,
            justification="Performance optimization",
        )
        decision = self.governance.evaluate(proposal)
        self.assertEqual(decision, GovernanceDecision.BACKLOG)

    def test_simpler_alternative_without_justification_returns_challenge(self):
        proposal = Proposal(
            description="Add microservice",
            problem="Handle requests",
            necessary_for_objective=True,
            simpler_alternative_exists=True,
            justification="  ",
        )
        decision = self.governance.evaluate(proposal)
        self.assertEqual(decision, GovernanceDecision.CHALLENGE)

    def test_simpler_alternative_with_justification_returns_approve(self):
        proposal = Proposal(
            description="Add dedicated index",
            problem="Query times exceed SLA",
            necessary_for_objective=True,
            simpler_alternative_exists=True,
            justification="Simpler scan is order of magnitude too slow for required throughput",
        )
        decision = self.governance.evaluate(proposal)
        self.assertEqual(decision, GovernanceDecision.APPROVE)

    def test_valid_standard_proposal_returns_approve(self):
        proposal = Proposal(
            description="Implement minimal validator",
            problem="Need to confirm completion criteria",
            necessary_for_objective=True,
            simpler_alternative_exists=False,
            justification="Direct requirement",
        )
        decision = self.governance.evaluate(proposal)
        self.assertEqual(decision, GovernanceDecision.APPROVE)


class TestValidator(unittest.TestCase):
    def setUp(self):
        self.validator = Validator()

    def test_validation_passes_when_all_criteria_met_with_evidence(self):
        task = Task(
            title="Task",
            objective="Objective",
            done_when=["Criterion A", "Criterion B"],
            completed_criteria=["Criterion A", "Criterion B"],
            evidence=[
                Evidence(criterion="Criterion A", kind="tests", value="test_a passed"),
                Evidence(criterion="Criterion B", kind="files", value="created file_b"),
            ],
        )
        self.assertTrue(self.validator.validate(task))

    def test_validation_fails_when_criteria_missing(self):
        task = Task(
            title="Task",
            objective="Objective",
            done_when=["Criterion A", "Criterion B"],
            completed_criteria=["Criterion A"],
            evidence=[
                Evidence(criterion="Criterion A", kind="tests", value="test_a passed"),
            ],
        )
        self.assertFalse(self.validator.validate(task))

    def test_validation_fails_when_criterion_lacks_evidence(self):
        task = Task(
            title="Task",
            objective="Objective",
            done_when=["Criterion A"],
            completed_criteria=["Criterion A"],
            evidence=[],  # No evidence provided
        )
        self.assertFalse(self.validator.validate(task))

    def test_validation_fails_when_evidence_has_empty_kind_or_value(self):
        task = Task(
            title="Task",
            objective="Objective",
            done_when=["Criterion A"],
            completed_criteria=["Criterion A"],
            evidence=[
                Evidence(criterion="Criterion A", kind="", value="  "),
            ],
        )
        self.assertFalse(self.validator.validate(task))


class TestCLIAgent(unittest.TestCase):
    def test_empty_command_raises_value_error(self):
        with self.assertRaises(ValueError):
            CLIAgent("   ")

    def test_prompt_building(self):
        agent = CLIAgent("echo test")
        task = Task(
            title="Unit Test Task",
            objective="Test CLI prompt formatting",
            done_when=["Criterion 1", "Criterion 2"],
        )
        prompt = agent._build_prompt(task)
        self.assertIn("TASK:\nUnit Test Task", prompt)
        self.assertIn("OBJECTIVE:\nTest CLI prompt formatting", prompt)
        self.assertIn("- Criterion 1\n- Criterion 2", prompt)
        self.assertIn("RESPONSE FORMAT:", prompt)
        self.assertIn('"status": "SUCCESS" | "PARTIAL" | "BLOCKED" | "FAILED"', prompt)

    def test_successful_execution_parses_json(self):
        payload = {
            "status": "SUCCESS",
            "summary": "Executed task cleanly",
            "completed_criteria": ["CLI works"],
            "evidence": [
                {"criterion": "CLI works", "kind": "output", "value": "echo output verified"}
            ],
            "backlog": ["add flags"],
        }
        json_str = json.dumps(payload).replace("'", "'\\''")
        agent = CLIAgent(f"echo '{json_str}'")
        task = Task(
            title="CLI Task",
            objective="Run CLI echo",
            done_when=["CLI works"],
        )
        result = agent.execute(task)
        self.assertEqual(result.status, AgentStatus.SUCCESS)
        self.assertEqual(result.summary, "Executed task cleanly")
        self.assertEqual(result.completed_criteria, ["CLI works"])
        self.assertEqual(len(result.evidence), 1)
        self.assertEqual(result.evidence[0].criterion, "CLI works")
        self.assertEqual(result.evidence[0].kind, "output")
        self.assertEqual(result.evidence[0].value, "echo output verified")
        self.assertEqual(result.backlog, ["add flags"])

    def test_successful_execution_with_markdown_fences(self):
        payload = {
            "status": "PARTIAL",
            "summary": "In progress",
            "completed_criteria": [],
            "evidence": [],
            "backlog": [],
        }
        json_text = f"```json\n{json.dumps(payload)}\n```"
        json_escaped = json_text.replace("'", "'\\''")
        agent = CLIAgent(f"printf '%s' '{json_escaped}'")
        task = Task(
            title="Fence Task",
            objective="Test fence parsing",
            done_when=["Parse fences"],
        )
        result = agent.execute(task)
        self.assertEqual(result.status, AgentStatus.PARTIAL)
        self.assertEqual(result.summary, "In progress")

    def test_malformed_json_returns_failed_status(self):
        agent = CLIAgent("echo 'not valid json at all'")
        task = Task(
            title="Malformed Task",
            objective="Test malformed output",
            done_when=["Handle malformed"],
        )
        result = agent.execute(task)
        self.assertEqual(result.status, AgentStatus.FAILED)
        self.assertIn("Malformed agent response", result.summary)

    def test_invalid_status_returns_failed_status(self):
        payload = json.dumps({"status": "NONEXISTENT", "summary": "Bad status"}).replace("'", "'\\''")
        agent = CLIAgent(f"echo '{payload}'")
        task = Task(
            title="Bad Status Task",
            objective="Test bad status string",
            done_when=["Validate status"],
        )
        result = agent.execute(task)
        self.assertEqual(result.status, AgentStatus.FAILED)
        self.assertIn("Invalid agent status", result.summary)

    def test_failed_execution_raises_runtime_error(self):
        agent = CLIAgent("sh -c 'echo \"simulated error\" >&2; exit 1'")
        task = Task(
            title="Failing Task",
            objective="Test failure handling",
            done_when=["Handle failure"],
        )
        with self.assertRaises(RuntimeError) as ctx:
            agent.execute(task)
        self.assertIn("simulated error", str(ctx.exception))


class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        self.governance = Governance()
        self.validator = Validator()

    def test_full_successful_flow(self):
        agent = MockAgent(
            status=AgentStatus.SUCCESS,
            summary="Completed everything",
            completed_criteria=["Criterion 1"],
            evidence=[
                Evidence(criterion="Criterion 1", kind="tests", value="19 tests passed")
            ],
            backlog=["Next task idea"],
        )
        orchestrator = Orchestrator(
            governance=self.governance,
            validator=self.validator,
            agent=agent,
        )
        task = Task(
            title="Flow Task",
            objective="Test full flow",
            done_when=["Criterion 1"],
        )
        proposal = Proposal(
            description="Execute core task",
            problem="Required step",
            necessary_for_objective=True,
            simpler_alternative_exists=False,
            justification="Direct requirement",
        )

        orchestrator.run(task, proposal)

        self.assertEqual(task.state, TaskState.DONE)
        self.assertEqual(task.completed_criteria, ["Criterion 1"])
        self.assertEqual(len(task.evidence), 1)
        self.assertEqual(task.evidence[0].criterion, "Criterion 1")
        self.assertIn("Next task idea", task.backlog)
        self.assertEqual(agent.executed_with, task)

    def test_success_status_with_missing_evidence_fails_validation(self):
        agent = MockAgent(
            status=AgentStatus.SUCCESS,
            summary="Claimed success without evidence",
            completed_criteria=["Criterion 1"],
            evidence=[],  # No evidence
        )
        orchestrator = Orchestrator(
            governance=self.governance,
            validator=self.validator,
            agent=agent,
        )
        task = Task(
            title="Missing Evidence Task",
            objective="Test evidence requirement",
            done_when=["Criterion 1"],
        )
        proposal = Proposal(
            description="Execute without evidence",
            problem="Required step",
            necessary_for_objective=True,
            simpler_alternative_exists=False,
            justification="Direct requirement",
        )

        orchestrator.run(task, proposal)

        # Validation fails due to missing evidence; transitions back to EXECUTING
        self.assertEqual(task.state, TaskState.EXECUTING)

    def test_partial_status_routes_to_executing(self):
        agent = MockAgent(
            status=AgentStatus.PARTIAL,
            summary="Did partial work",
            completed_criteria=["Criterion 1"],
            evidence=[
                Evidence(criterion="Criterion 1", kind="output", value="partial output")
            ],
        )
        orchestrator = Orchestrator(
            governance=self.governance,
            validator=self.validator,
            agent=agent,
        )
        task = Task(
            title="Partial Task",
            objective="Test partial routing",
            done_when=["Criterion 1", "Criterion 2"],
        )
        proposal = Proposal(
            description="Execute partial task",
            problem="Required step",
            necessary_for_objective=True,
            simpler_alternative_exists=False,
            justification="Direct requirement",
        )

        orchestrator.run(task, proposal)

        self.assertEqual(task.state, TaskState.EXECUTING)
        self.assertEqual(task.completed_criteria, ["Criterion 1"])
        self.assertEqual(len(task.evidence), 1)

    def test_blocked_status_routes_to_review(self):
        agent = MockAgent(
            status=AgentStatus.BLOCKED,
            summary="Blocked on missing credentials",
        )
        orchestrator = Orchestrator(
            governance=self.governance,
            validator=self.validator,
            agent=agent,
        )
        task = Task(
            title="Blocked Task",
            objective="Test blocked routing",
            done_when=["Criterion 1"],
        )
        proposal = Proposal(
            description="Execute blocked task",
            problem="Required step",
            necessary_for_objective=True,
            simpler_alternative_exists=False,
            justification="Direct requirement",
        )

        orchestrator.run(task, proposal)

        self.assertEqual(task.state, TaskState.REVIEW)

    def test_failed_status_routes_to_review(self):
        agent = MockAgent(
            status=AgentStatus.FAILED,
            summary="Execution crashed",
        )
        orchestrator = Orchestrator(
            governance=self.governance,
            validator=self.validator,
            agent=agent,
        )
        task = Task(
            title="Failed Task",
            objective="Test failed routing",
            done_when=["Criterion 1"],
        )
        proposal = Proposal(
            description="Execute failing task",
            problem="Required step",
            necessary_for_objective=True,
            simpler_alternative_exists=False,
            justification="Direct requirement",
        )

        orchestrator.run(task, proposal)

        self.assertEqual(task.state, TaskState.REVIEW)

    def test_backlog_decision_appends_to_backlog_and_stops(self):
        agent = MockAgent()
        orchestrator = Orchestrator(
            governance=self.governance,
            validator=self.validator,
            agent=agent,
        )
        task = Task(
            title="Backlog Task",
            objective="Test backlog routing",
            done_when=["Criterion 1"],
        )
        proposal = Proposal(
            description="Add nice-to-have feature",
            problem="Could be useful",
            necessary_for_objective=False,
            simpler_alternative_exists=False,
            justification="Optimization",
        )

        orchestrator.run(task, proposal)

        self.assertEqual(task.state, TaskState.DEFINED)
        self.assertIn("Add nice-to-have feature", task.backlog)
        self.assertIsNone(agent.executed_with)

    def test_challenge_or_reject_decision_transitions_to_review(self):
        agent = MockAgent()
        orchestrator = Orchestrator(
            governance=self.governance,
            validator=self.validator,
            agent=agent,
        )
        task = Task(
            title="Review Task",
            objective="Test review transition",
            done_when=["Criterion 1"],
        )
        proposal = Proposal(
            description="Complex approach without justification",
            problem="Some problem",
            necessary_for_objective=True,
            simpler_alternative_exists=True,
            justification="",
        )

        orchestrator.run(task, proposal)

        self.assertEqual(task.state, TaskState.REVIEW)
        self.assertIsNone(agent.executed_with)


class TestPersistence(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.task_file = os.path.join(self.temp_dir.name, "task.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_load_task_roundtrip(self):
        task = Task(
            title="Persist Task",
            objective="Verify disk roundtrip",
            done_when=["Criterion A", "Criterion B"],
            completed_criteria=["Criterion A"],
            state=TaskState.EXECUTING,
            backlog=["Future item"],
            evidence=[
                Evidence(criterion="Criterion A", kind="files", value="task.py")
            ],
        )
        save_task(task, self.task_file)
        self.assertTrue(os.path.exists(self.task_file))

        loaded = load_task(self.task_file)
        self.assertEqual(loaded.title, "Persist Task")
        self.assertEqual(loaded.objective, "Verify disk roundtrip")
        self.assertEqual(loaded.done_when, ["Criterion A", "Criterion B"])
        self.assertEqual(loaded.completed_criteria, ["Criterion A"])
        self.assertEqual(loaded.state, TaskState.EXECUTING)
        self.assertEqual(loaded.backlog, ["Future item"])
        self.assertEqual(len(loaded.evidence), 1)
        self.assertEqual(loaded.evidence[0].criterion, "Criterion A")
        self.assertEqual(loaded.evidence[0].kind, "files")
        self.assertEqual(loaded.evidence[0].value, "task.py")

    def test_load_nonexistent_file_raises_filenotfound(self):
        with self.assertRaises(FileNotFoundError):
            load_task(os.path.join(self.temp_dir.name, "nonexistent.json"))

    def test_failed_write_preserves_existing_task_and_cleans_up_temp(self):
        original_task = Task(
            title="Original Task",
            objective="Must not be corrupted",
            done_when=["Criterion 1"],
            state=TaskState.EXECUTING,
        )
        save_task(original_task, self.task_file)
        self.assertTrue(os.path.exists(self.task_file))

        attempted_task = Task(
            title="New Attempted Task",
            objective="Will fail during save",
            done_when=["Criterion 2"],
            state=TaskState.DONE,
        )

        with patch("hyperion.json.dump", side_effect=OSError("Simulated write failure")):
            with self.assertRaises(OSError):
                save_task(attempted_task, self.task_file)

        # Existing task file must still be valid and unmodified
        loaded = load_task(self.task_file)
        self.assertEqual(loaded.title, "Original Task")
        self.assertEqual(loaded.objective, "Must not be corrupted")
        self.assertEqual(loaded.state, TaskState.EXECUTING)

        # Temporary sibling files must be cleaned up
        remaining_files = os.listdir(self.temp_dir.name)
        self.assertEqual(remaining_files, ["task.json"])

    def test_failed_write_on_new_file_cleans_up_temp(self):
        new_file = os.path.join(self.temp_dir.name, "brand_new_task.json")
        task = Task(
            title="New Task",
            objective="Will fail",
            done_when=["Criterion 1"],
        )

        with patch("hyperion.json.dump", side_effect=OSError("Simulated write failure")):
            with self.assertRaises(OSError):
                save_task(task, new_file)

        self.assertFalse(os.path.exists(new_file))
        remaining_files = os.listdir(self.temp_dir.name)
        self.assertEqual(remaining_files, [])


class TestCLIBridge(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.task_file = os.path.join(self.temp_dir.name, "task.json")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_cli_init_creates_defined_task(self):
        args = parse_args([
            "--task-file", self.task_file,
            "init",
            "--title", "CLI Task",
            "--objective", "Verify CLI init",
            "--done", "C1", "C2",
        ])
        ret = cli_init(args)
        self.assertEqual(ret, 0)

        task = load_task(self.task_file)
        self.assertEqual(task.title, "CLI Task")
        self.assertEqual(task.state, TaskState.DEFINED)
        self.assertEqual(task.done_when, ["C1", "C2"])

    def test_cli_propose_approved_transitions_to_executing(self):
        cli_init(parse_args([
            "--task-file", self.task_file,
            "init",
            "--title", "Task",
            "--objective", "Obj",
            "--done", "C1",
        ]))
        args = parse_args([
            "--task-file", self.task_file,
            "propose",
            "--description", "Execute task",
            "--problem", "Need to execute",
        ])
        ret = cli_propose(args)
        self.assertEqual(ret, 0)

        task = load_task(self.task_file)
        self.assertEqual(task.state, TaskState.EXECUTING)

    def test_cli_propose_challenged_transitions_to_review(self):
        cli_init(parse_args([
            "--task-file", self.task_file,
            "init",
            "--title", "Task",
            "--objective", "Obj",
            "--done", "C1",
        ]))
        args = parse_args([
            "--task-file", self.task_file,
            "propose",
            "--description", "Complex plan",
            "--problem", "Some problem",
            "--simpler-alternative",
        ])
        ret = cli_propose(args)
        self.assertEqual(ret, 0)

        task = load_task(self.task_file)
        self.assertEqual(task.state, TaskState.REVIEW)

    def test_cli_propose_backlog_preserves_state(self):
        cli_init(parse_args([
            "--task-file", self.task_file,
            "init",
            "--title", "Task",
            "--objective", "Obj",
            "--done", "C1",
        ]))
        args = parse_args([
            "--task-file", self.task_file,
            "propose",
            "--description", "Optional improvement",
            "--problem", "Not critical",
            "--unnecessary",
        ])
        ret = cli_propose(args)
        self.assertEqual(ret, 0)

        task = load_task(self.task_file)
        self.assertEqual(task.state, TaskState.DEFINED)
        self.assertIn("Optional improvement", task.backlog)

    def test_cli_submit_success_with_valid_evidence_completes_task(self):
        cli_init(parse_args([
            "--task-file", self.task_file,
            "init",
            "--title", "Task",
            "--objective", "Obj",
            "--done", "Criterion 1",
        ]))
        cli_propose(parse_args([
            "--task-file", self.task_file,
            "propose",
            "--description", "Execute",
            "--problem", "Do it",
        ]))

        response_file = os.path.join(self.temp_dir.name, "response.json")
        with open(response_file, "w", encoding="utf-8") as f:
            json.dump({
                "status": "SUCCESS",
                "summary": "Completed successfully",
                "completed_criteria": ["Criterion 1"],
                "evidence": [
                    {"criterion": "Criterion 1", "kind": "tests", "value": "test passed"}
                ],
                "backlog": ["Future optimization"],
            }, f)

        ret = cli_submit(parse_args([
            "--task-file", self.task_file,
            "submit",
            response_file,
        ]))
        self.assertEqual(ret, 0)

        task = load_task(self.task_file)
        self.assertEqual(task.state, TaskState.DONE)
        self.assertEqual(task.completed_criteria, ["Criterion 1"])
        self.assertIn("Future optimization", task.backlog)

    def test_cli_submit_success_without_evidence_fails_validation(self):
        cli_init(parse_args([
            "--task-file", self.task_file,
            "init",
            "--title", "Task",
            "--objective", "Obj",
            "--done", "Criterion 1",
        ]))
        cli_propose(parse_args([
            "--task-file", self.task_file,
            "propose",
            "--description", "Execute",
            "--problem", "Do it",
        ]))

        response_file = os.path.join(self.temp_dir.name, "response.json")
        with open(response_file, "w", encoding="utf-8") as f:
            json.dump({
                "status": "SUCCESS",
                "summary": "Claimed success without evidence",
                "completed_criteria": ["Criterion 1"],
                "evidence": [],
            }, f)

        ret = cli_submit(parse_args([
            "--task-file", self.task_file,
            "submit",
            response_file,
        ]))
        self.assertEqual(ret, 0)

        task = load_task(self.task_file)
        # Without evidence, validation fails and state remains EXECUTING
        self.assertEqual(task.state, TaskState.EXECUTING)

    def test_cli_submit_partial_preserves_executing_state(self):
        cli_init(parse_args([
            "--task-file", self.task_file,
            "init",
            "--title", "Task",
            "--objective", "Obj",
            "--done", "C1", "C2",
        ]))
        cli_propose(parse_args([
            "--task-file", self.task_file,
            "propose",
            "--description", "Execute",
            "--problem", "Do it",
        ]))

        response_file = os.path.join(self.temp_dir.name, "response.json")
        with open(response_file, "w", encoding="utf-8") as f:
            json.dump({
                "status": "PARTIAL",
                "summary": "Completed C1 only",
                "completed_criteria": ["C1"],
                "evidence": [
                    {"criterion": "C1", "kind": "output", "value": "done C1"}
                ],
            }, f)

        ret = cli_submit(parse_args([
            "--task-file", self.task_file,
            "submit",
            response_file,
        ]))
        self.assertEqual(ret, 0)

        task = load_task(self.task_file)
        self.assertEqual(task.state, TaskState.EXECUTING)
        self.assertEqual(task.completed_criteria, ["C1"])

    def test_cli_submit_blocked_or_failed_routes_to_review(self):
        for status in ("BLOCKED", "FAILED"):
            with self.subTest(status=status):
                cli_init(parse_args([
                    "--task-file", self.task_file,
                    "init",
                    "--title", "Task",
                    "--objective", "Obj",
                    "--done", "C1",
                ]))
                cli_propose(parse_args([
                    "--task-file", self.task_file,
                    "propose",
                    "--description", "Execute",
                    "--problem", "Do it",
                ]))

                response_file = os.path.join(self.temp_dir.name, "response.json")
                with open(response_file, "w", encoding="utf-8") as f:
                    json.dump({
                        "status": status,
                        "summary": f"Encountered {status}",
                        "completed_criteria": [],
                        "evidence": [],
                    }, f)

                cli_submit(parse_args([
                    "--task-file", self.task_file,
                    "submit",
                    response_file,
                ]))

                task = load_task(self.task_file)
                self.assertEqual(task.state, TaskState.REVIEW)

    def test_cli_submit_malformed_json_moves_to_review(self):
        cli_init(parse_args([
            "--task-file", self.task_file,
            "init",
            "--title", "Task",
            "--objective", "Obj",
            "--done", "C1",
        ]))
        cli_propose(parse_args([
            "--task-file", self.task_file,
            "propose",
            "--description", "Execute",
            "--problem", "Do it",
        ]))

        response_file = os.path.join(self.temp_dir.name, "response.json")
        with open(response_file, "w", encoding="utf-8") as f:
            f.write("not valid json at all")

        cli_submit(parse_args([
            "--task-file", self.task_file,
            "submit",
            response_file,
        ]))

        task = load_task(self.task_file)
        self.assertEqual(task.state, TaskState.REVIEW)

    def test_cli_submit_missing_file_moves_to_review(self):
        cli_init(parse_args([
            "--task-file", self.task_file,
            "init",
            "--title", "Task",
            "--objective", "Obj",
            "--done", "C1",
        ]))
        cli_propose(parse_args([
            "--task-file", self.task_file,
            "propose",
            "--description", "Execute",
            "--problem", "Do it",
        ]))

        ret = cli_submit(parse_args([
            "--task-file", self.task_file,
            "submit",
            os.path.join(self.temp_dir.name, "nonexistent.json"),
        ]))
        self.assertEqual(ret, 1)

        task = load_task(self.task_file)
        self.assertEqual(task.state, TaskState.REVIEW)

    def test_cli_status_reports_persisted_state(self):
        cli_init(parse_args([
            "--task-file", self.task_file,
            "init",
            "--title", "Status Task",
            "--objective", "Verify status output",
            "--done", "Criterion 1", "Criterion 2",
        ]))

        captured = io.StringIO()
        with contextlib.redirect_stdout(captured):
            cli_status(parse_args([
                "--task-file", self.task_file,
                "status",
            ]))
        output = captured.getvalue()
        self.assertIn("Task: Status Task", output)
        self.assertIn("State: DEFINED", output)
        self.assertIn("[ ] Criterion 1", output)
        self.assertIn("[ ] Criterion 2", output)


if __name__ == "__main__":
    unittest.main()
