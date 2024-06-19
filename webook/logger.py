import logging


def get_logger(component):
    logger = logging.getLogger()
    extra = {
        "component": component
    }
    return logging.LoggerAdapter(logger, extra)
