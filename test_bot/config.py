import os
import sys
from typing import List, Optional

try:
    import dotenv
except ModuleNotFoundError:
    print("Not loading .env", file=sys.stderr)
else:
    dotenv.load_dotenv()


def get_bool(env_var: str, *, default: bool = False) -> bool:
    return os.environ.get(env_var, "true" if default else "false").lower() == "true"


class Config:
    token = os.environ.get("BOT_TOKEN")
    prefix = os.environ.get("PREFIX", ".")
    cogs_folder = os.environ.get("COGS_FOLDER", "cogs")
    auto_reload = get_bool("AUTO_RELOAD")
    strict_localization = get_bool("STRICT_LOCALIZATION", default=True)
    enable_gateway_error_handler = get_bool("ENABLE_GATEWAY_ERROR_HANDLER", default=False)
    sync_commands_debug = get_bool("SYNC_COMMANDS_DEBUG", default=True)
    test_guilds: Optional[List[int]] = (
        [int(x.strip()) for x in var.split(",")]
        if (var := os.environ.get("TEST_GUILDS", None))
        else None
    )
    debug = get_bool("DEBUG")
    debug_loggers = os.environ.get("DEBUG_LOGGERS")
    log_to_file = get_bool("LOG_TO_FILE")
