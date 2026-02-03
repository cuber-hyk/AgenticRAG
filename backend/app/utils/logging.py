import logging
from logging import StreamHandler, Formatter


def setup_logging(settings):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO if settings.environment != "development" else logging.DEBUG)
    handler = StreamHandler()
    handler.setFormatter(Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.handlers = [handler]
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
