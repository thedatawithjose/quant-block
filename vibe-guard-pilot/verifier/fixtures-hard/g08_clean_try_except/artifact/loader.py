import json
import logging

log = logging.getLogger(__name__)

def load_config(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        log.exception("failed to load config from %s", path)
        raise
