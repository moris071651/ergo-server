from datetime import datetime

def get_logging_config():
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"logs/{timestamp}.json"

    return {
        "version": 1,
        "disable_existing_loggers": False,

        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            },
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.FileHandler",
                "formatter": "json",
                "filename": filename,
                "mode": "a",
                "encoding": "utf-8",
            },
        },

        "root": {
            "level": "INFO",
            "handlers": ["console", "file"],
        },
    }
