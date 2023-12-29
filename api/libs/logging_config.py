import logging
import logging.config
import sys

LOGGING_CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            'format': '[%(asctime)s.%(msecs)03d][%(levelname)s][%(filename)s][%(lineno)s] %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
        }
    },
    "loggers": {
        "console_logger": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        }
    },
    "disable_existing_loggers": True,
}

# 运行测试
def config_logging(logging):
    logging.config.dictConfig(LOGGING_CONFIG)
    logging.basicConfig(
        level=logging.INFO,
        format=LOGGING_CONFIG['formatters']['default']['format'],
        datefmt=LOGGING_CONFIG['formatters']['default']['datefmt'],
        stream=sys.stdout)