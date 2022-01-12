import logging
import os

try:
    import dotenv
except ModuleNotFoundError:
    print("Not loading .env")
else:
    dotenv.load_dotenv()


class Config:
    token = os.environ.get("BOT_TOKEN")
    prefix = os.environ.get("PREFIX", ".")
    cogs_folder = os.environ.get("COGS_FOLDER", "cogs")
    auto_reload = os.environ.get("AUTO_RELOAD", "false") == "true"
    sync_permissions = os.environ.get("SYNC_PERMISSIONS", "true") == "true"
    sync_commands_debug = os.environ.get("SYNC_COMMANDS_DEBUG", "true") == "true"
    test_guilds = (
        [int(x.strip()) for x in test_guilds.split(",")]
        if (test_guilds := os.environ.get("TEST_GUILDS", None))
        else None
    )
    debug = os.environ.get("DEBUG", "false") == "true"
    debug_loggers = os.environ.get("DEBUG_LOGGERS")
    log_to_file = bool(os.environ.get("LOG_TO_FILE", "false").lower() == "true")
