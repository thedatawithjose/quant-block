from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol
import argparse
import json
import os
import shlex
import subprocess
import sys
import tempfile

import external_flow


class TaskState(Enum):
    DEFINED = "DEFINED"
    EXECUTING = "EXECUTING"
    VALIDATING = "VALIDATING"
    REVIEW = "REVIEW"
    DONE = "DONE"


class GovernanceDecision(Enum):
    APPROVE = "APPROVE"
    CHALLENGE = "CHALLENGE"
    BACKLOG = "BACKLOG"
    REJECT = "REJECT"


class AgentStatus(Enum):
    SUCCESS = "SUCCESS"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


@dataclass
class Evidence:
    criterion: str
    kind: str
    value: str


@dataclass
class Task:
    title: str
    objective: str
    done_when: list[str]
    completed_criteria: list[str] = field(default_factory=list)
    state: TaskState = TaskState.DEFINED
    backlog: list[str] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)

    def transition_to(self, new_state: TaskState):
        allowed_transitions = {
            TaskState.DEFINED: {
                TaskState.EXECUTING,
                TaskState.REVIEW,
            },
            TaskState.EXECUTING: {
                TaskState.VALIDATING,
                TaskState.REVIEW,
            },
            TaskState.VALIDATING: {
                TaskState.DONE,
                TaskState.EXECUTING,
                TaskState.REVIEW,
            },
            TaskState.REVIEW: {
                TaskState.EXECUTING,
                TaskState.VALIDATING,
            },
            TaskState.DONE: set(),
        }

        if new_state not in allowed_transitions[self.state]:
            raise ValueError(
                f"Invalid transition: "
                f"{self.state.value} -> {new_state.value}"
            )

        self.state = new_state

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "objective": self.objective,
            "done_when": self.done_when,
            "completed_criteria": self.completed_criteria,
            "state": self.state.value,
            "backlog": self.backlog,
            "evidence": [
                {
                    "criterion": e.criterion,
                    "kind": e.kind,
                    "value": e.value,
                }
                for e in self.evidence
            ],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            title=data["title"],
            objective=data["objective"],
            done_when=list(data.get("done_when", [])),
            completed_criteria=list(data.get("completed_criteria", [])),
            state=TaskState(data.get("state", TaskState.DEFINED.value)),
            backlog=list(data.get("backlog", [])),
            evidence=[
                Evidence(
                    criterion=str(item["criterion"]),
                    kind=str(item["kind"]),
                    value=str(item["value"]),
                )
                for item in data.get("evidence", [])
                if isinstance(item, dict)
            ],
        )


TASK_FILE = "task.json"


def load_task(filepath: str = TASK_FILE) -> Task:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No task found at '{filepath}'. Run 'init' first.")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Task.from_dict(data)


def save_task(task: Task, filepath: str = TASK_FILE) -> None:
    abs_path = os.path.abspath(filepath)
    dirname = os.path.dirname(abs_path)
    prefix = f".{os.path.basename(abs_path)}."

    temp_file = tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=dirname,
        prefix=prefix,
        suffix=".tmp",
        delete=False,
    )
    temp_path = temp_file.name
    try:
        json.dump(task.to_dict(), temp_file, indent=2)
        temp_file.flush()
        os.fsync(temp_file.fileno())
        temp_file.close()
        os.replace(temp_path, abs_path)
    except BaseException:
        temp_file.close()
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


@dataclass
class Proposal:
    description: str
    problem: str
    necessary_for_objective: bool
    simpler_alternative_exists: bool
    justification: str


@dataclass
class AgentResponse:
    status: AgentStatus
    summary: str
    completed_criteria: list[str]
    evidence: list[Evidence] = field(default_factory=list)
    backlog: list[str] = field(default_factory=list)


# Backward compatibility alias
AgentResult = AgentResponse


class Agent(Protocol):
    def execute(self, task: Task) -> AgentResponse:
        ...


def parse_agent_response(output: str) -> AgentResponse:
    raw = output.strip()
    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return AgentResponse(
            status=AgentStatus.FAILED,
            summary=f"Malformed agent response (invalid JSON): {exc}",
            completed_criteria=[],
            evidence=[],
            backlog=[],
        )

    if not isinstance(data, dict):
        return AgentResponse(
            status=AgentStatus.FAILED,
            summary="Malformed agent response: expected a JSON object.",
            completed_criteria=[],
            evidence=[],
            backlog=[],
        )

    try:
        status = AgentStatus(data.get("status"))
    except (ValueError, KeyError):
        return AgentResponse(
            status=AgentStatus.FAILED,
            summary=f"Invalid agent status: {data.get('status')}",
            completed_criteria=[],
            evidence=[],
            backlog=[],
        )

    summary = str(data.get("summary", ""))
    completed_criteria = list(data.get("completed_criteria", []))
    backlog = list(data.get("backlog", []))

    evidence = []
    raw_evidence = data.get("evidence", [])
    if isinstance(raw_evidence, list):
        for item in raw_evidence:
            if isinstance(item, dict):
                evidence.append(
                    Evidence(
                        criterion=str(item.get("criterion", "")),
                        kind=str(item.get("kind", "")),
                        value=str(item.get("value", "")),
                    )
                )

    return AgentResponse(
        status=status,
        summary=summary,
        completed_criteria=completed_criteria,
        evidence=evidence,
        backlog=backlog,
    )


class CLIAgent:
    def __init__(self, command: str):
        if not command.strip():
            raise ValueError("Agent command cannot be empty.")

        self.command = shlex.split(command)

    def execute(self, task: Task) -> AgentResponse:
        prompt = self._build_prompt(task)

        print("Agent command:", " ".join(self.command))
        print("Sending task to agent...")

        result = subprocess.run(
            self.command,
            input=prompt,
            text=True,
            capture_output=True,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                "Agent execution failed:\n"
                f"{result.stderr.strip()}"
            )

        output = result.stdout.strip()
        return self._parse_response(output)

    def _parse_response(self, output: str) -> AgentResponse:
        return parse_agent_response(output)

    def _build_prompt(self, task: Task) -> str:
        criteria = "\n".join(
            f"- {criterion}"
            for criterion in task.done_when
        )

        return f"""
You are an execution agent working under Hyperion governance.

TASK:
{task.title}

OBJECTIVE:
{task.objective}

DONE WHEN:
{criteria}

RULES:
- Do not expand scope unnecessarily.
- Do not claim completion without evidence.
- Prefer the simplest sufficient implementation.
- Challenge incorrect assumptions when necessary.
- Report what you actually completed.

RESPONSE FORMAT:
You must return only a valid JSON object with the following structure:
{{
  "status": "SUCCESS" | "PARTIAL" | "BLOCKED" | "FAILED",
  "summary": "Concise summary of actions taken",
  "completed_criteria": ["<criterion satisfied>"],
  "evidence": [
    {{"criterion": "<criterion satisfied>", "kind": "<files|tests|command|output|source|validation>", "value": "<evidence>"}}
  ],
  "backlog": ["<optional improvement or deferred work>"]
}}
""".strip()


class Governance:
    def evaluate(self, proposal: Proposal) -> GovernanceDecision:
        if not proposal.problem.strip():
            return GovernanceDecision.REJECT

        if not proposal.necessary_for_objective:
            return GovernanceDecision.BACKLOG

        if (
            proposal.simpler_alternative_exists
            and not proposal.justification.strip()
        ):
            return GovernanceDecision.CHALLENGE

        return GovernanceDecision.APPROVE


class Validator:
    def validate(self, task: Task) -> bool:
        missing = [
            criterion
            for criterion in task.done_when
            if criterion not in task.completed_criteria
        ]

        if missing:
            print("Validation failed.")
            print("Missing criteria:")

            for criterion in missing:
                print(f"- {criterion}")

            return False

        evidence_by_criterion: dict[str, list[Evidence]] = {}
        for ev in task.evidence:
            if ev.criterion and ev.kind.strip() and ev.value.strip():
                evidence_by_criterion.setdefault(ev.criterion, []).append(ev)

        missing_evidence = [
            criterion
            for criterion in task.completed_criteria
            if criterion not in evidence_by_criterion
        ]

        if missing_evidence:
            print("Validation failed.")
            print("Criteria lacking supporting evidence:")

            for criterion in missing_evidence:
                print(f"- {criterion}")

            return False

        print("Validation passed.")
        return True


class Orchestrator:
    def __init__(
        self,
        governance: Governance,
        validator: Validator,
        agent: Agent,
    ):
        self.governance = governance
        self.validator = validator
        self.agent = agent

    def run(self, task: Task, proposal: Proposal):
        decision = self.governance.evaluate(proposal)

        print("Governance decision:", decision.value)

        if decision == GovernanceDecision.BACKLOG:
            task.backlog.append(proposal.description)
            return

        if decision != GovernanceDecision.APPROVE:
            task.transition_to(TaskState.REVIEW)
            return

        task.transition_to(TaskState.EXECUTING)

        result = self.agent.execute(task)

        print("\n--- AGENT RESULT ---")
        print(f"Status: {result.status.value}")
        print(result.summary)
        print("--------------------\n")

        task.backlog.extend(result.backlog)

        if result.status in (AgentStatus.BLOCKED, AgentStatus.FAILED):
            task.transition_to(TaskState.REVIEW)
            return

        if result.status == AgentStatus.PARTIAL:
            task.completed_criteria.extend(result.completed_criteria)
            task.evidence.extend(result.evidence)
            return

        if result.status == AgentStatus.SUCCESS:
            task.completed_criteria.extend(result.completed_criteria)
            task.evidence.extend(result.evidence)
            task.transition_to(TaskState.VALIDATING)

            if self.validator.validate(task):
                task.transition_to(TaskState.DONE)
            else:
                task.transition_to(TaskState.EXECUTING)


def cli_init(args) -> int:
    if external_flow.reject_legacy(args.task_file):
        return 1
    task = Task(
        title=args.title,
        objective=args.objective,
        done_when=list(args.done),
        state=TaskState.DEFINED,
    )
    save_task(task, args.task_file)
    print(f"Task initialized: {task.title}")
    print(f"State: {task.state.value}")
    print(f"Objective: {task.objective}")
    print("Done when:")
    for c in task.done_when:
        print(f"- {c}")
    return 0


def cli_propose(args) -> int:
    if external_flow.reject_legacy(args.task_file):
        return 1
    task = load_task(args.task_file)
    proposal = Proposal(
        description=args.description,
        problem=args.problem,
        necessary_for_objective=not args.unnecessary,
        simpler_alternative_exists=args.simpler_alternative,
        justification=args.justification,
    )
    governance = Governance()
    decision = governance.evaluate(proposal)
    print("Governance decision:", decision.value)

    if decision == GovernanceDecision.BACKLOG:
        task.backlog.append(proposal.description)
        print(f"Proposal moved to backlog: {proposal.description}")
    elif decision == GovernanceDecision.APPROVE:
        if task.state != TaskState.EXECUTING:
            task.transition_to(TaskState.EXECUTING)
        print(f"Proposal approved. State: {task.state.value}")
    else:  # CHALLENGE or REJECT
        if task.state != TaskState.REVIEW:
            task.transition_to(TaskState.REVIEW)
        print(f"Proposal {decision.value}. State: {task.state.value}")

    save_task(task, args.task_file)
    return 0


def cli_submit(args) -> int:
    if external_flow.reject_legacy(args.task_file):
        return 1
    task = load_task(args.task_file)

    if task.state == TaskState.DONE:
        print("Task is already DONE. No further submissions accepted.")
        return 0

    if not os.path.exists(args.response_file):
        print(f"Error: Response file not found: {args.response_file}")
        if task.state != TaskState.REVIEW:
            task.transition_to(TaskState.REVIEW)
            save_task(task, args.task_file)
        return 1

    try:
        with open(args.response_file, "r", encoding="utf-8") as f:
            raw = f.read().strip()
    except Exception as exc:
        print(f"Error reading response file: {exc}")
        if task.state != TaskState.REVIEW:
            task.transition_to(TaskState.REVIEW)
            save_task(task, args.task_file)
        return 1

    response = parse_agent_response(raw)

    print(f"Parsed response status: {response.status.value}")
    print(f"Summary: {response.summary}")

    task.backlog.extend(response.backlog)

    if response.status in (AgentStatus.BLOCKED, AgentStatus.FAILED):
        if task.state != TaskState.REVIEW:
            task.transition_to(TaskState.REVIEW)
        print(f"Submission resulted in {response.status.value}. State: {task.state.value}")
    elif response.status == AgentStatus.PARTIAL:
        task.completed_criteria.extend(response.completed_criteria)
        task.evidence.extend(response.evidence)
        if task.state == TaskState.REVIEW:
            task.transition_to(TaskState.EXECUTING)
        print(f"Submission PARTIAL. Progress recorded. State: {task.state.value}")
    elif response.status == AgentStatus.SUCCESS:
        task.completed_criteria.extend(response.completed_criteria)
        task.evidence.extend(response.evidence)
        task.transition_to(TaskState.VALIDATING)
        validator = Validator()
        if validator.validate(task):
            task.transition_to(TaskState.DONE)
            print(f"Validation passed. Task completed! State: {task.state.value}")
        else:
            task.transition_to(TaskState.EXECUTING)
            print(f"Validation failed. Task remains in {task.state.value}")

    save_task(task, args.task_file)
    return 0


def cli_status(args) -> int:
    if external_flow.is_external(args.task_file):
        return external_flow.run(args)
    task = load_task(args.task_file)
    print(f"Task: {task.title}")
    print(f"State: {task.state.value}")
    print(f"Objective: {task.objective}")

    print("\nCriteria:")
    missing = [c for c in task.done_when if c not in task.completed_criteria]
    for c in task.done_when:
        status_mark = "[X]" if c in task.completed_criteria else "[ ]"
        print(f"  {status_mark} {c}")

    evidence_by_criterion = {
        ev.criterion: ev for ev in task.evidence
        if ev.criterion and ev.kind.strip() and ev.value.strip()
    }
    unsupported = [c for c in task.completed_criteria if c not in evidence_by_criterion]
    if unsupported:
        print("\nUnsupported Completed Criteria (Missing Evidence):")
        for c in unsupported:
            print(f"  - {c}")

    if missing:
        print("\nMissing Criteria:")
        for c in missing:
            print(f"  - {c}")

    if task.backlog:
        print("\nBacklog:")
        for item in task.backlog:
            print(f"  - {item}")

    return 0


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        prog="hyperion",
        description="Hyperion v0 Orchestration & Governance Engine",
    )
    parser.add_argument(
        "--task-file",
        default=TASK_FILE,
        help="Path to task persistence file (default: task.json)",
    )
    subparsers = parser.add_subparsers(dest="command")

    # init
    init_parser = subparsers.add_parser("init", help="Create a new task in DEFINED state")
    init_parser.add_argument("--title", required=True, help="Task title")
    init_parser.add_argument("--objective", required=True, help="Task objective")
    init_parser.add_argument("--done", nargs="+", required=True, help="Done when criteria")

    # propose
    propose_parser = subparsers.add_parser("propose", help="Evaluate a proposal under Governance")
    propose_parser.add_argument("--description", required=True, help="Proposal description")
    propose_parser.add_argument("--problem", required=True, help="Problem this solves")
    propose_parser.add_argument(
        "--unnecessary",
        action="store_true",
        help="Set if NOT necessary for current objective",
    )
    propose_parser.add_argument(
        "--simpler-alternative",
        action="store_true",
        help="Set if a simpler alternative exists",
    )
    propose_parser.add_argument(
        "--justification",
        default="",
        help="Justification if simpler alternative exists",
    )

    # submit
    submit_parser = subparsers.add_parser("submit", help="Submit an agent response JSON file")
    submit_parser.add_argument("response_file", help="Path to AgentResponse JSON file")

    # status
    subparsers.add_parser("status", help="Show current persisted task status")

    external_flow.add_parsers(subparsers)
    return parser.parse_args(args)


def main():
    if len(sys.argv) > 1:
        args = parse_args()
        if args.command in external_flow.COMMANDS:
            sys.exit(external_flow.run(args))
        if args.command == "init":
            sys.exit(cli_init(args))
        elif args.command == "propose":
            sys.exit(cli_propose(args))
        elif args.command == "submit":
            sys.exit(cli_submit(args))
        elif args.command == "status":
            sys.exit(cli_status(args))
        elif args.command is None:
            command = os.getenv("HYPERION_AGENT_CMD")
            if not command:
                parse_args(["--help"])
                return

    command = os.getenv("HYPERION_AGENT_CMD")

    if not command:
        parse_args(["--help"])
        return

    task = Task(
        title="Hyperion agent integration test",
        objective=(
            "Confirm that Hyperion can delegate a task "
            "to an external CLI agent."
        ),
        done_when=[
            "External agent receives the task",
            "External agent returns a response",
        ],
    )

    proposal = Proposal(
        description="Connect Hyperion to an external CLI agent.",
        problem=(
            "Hyperion currently depends on an internal mock agent."
        ),
        necessary_for_objective=True,
        simpler_alternative_exists=False,
        justification=(
            "Model-independent agent execution is a core requirement."
        ),
    )

    governance = Governance()
    validator = Validator()
    agent = CLIAgent(command)

    orchestrator = Orchestrator(
        governance=governance,
        validator=validator,
        agent=agent,
    )

    print("Initial state:", task.state.value)

    orchestrator.run(task, proposal)

    print("Final state:", task.state.value)


if __name__ == "__main__":
    main()