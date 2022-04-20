import logging
import logging.config


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and
    before performing collection and entering the run test loop.
    """
    logging.config.fileConfig(fname="logging.conf", disable_existing_loggers=False)
    logger = logging.getLogger(__name__)

    logger.info("Config logging Loaded")
