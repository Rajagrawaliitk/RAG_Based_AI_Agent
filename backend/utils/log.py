from loguru import logger

def get_logger(name="rag-shopper"):
    return logger.bind(context=name)

log = get_logger()
