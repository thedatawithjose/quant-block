C1: Ran load_config on a missing file and on a file with invalid JSON.
    load_config("nope.json")  -> ERROR log "failed to load config from nope.json"
                                 with traceback, then FileNotFoundError reached caller
    load_config("bad.json")   -> ERROR log with traceback, then json.JSONDecodeError
                                 reached caller
Bare `raise` re-raises the original exception object, so type and traceback are unchanged.
