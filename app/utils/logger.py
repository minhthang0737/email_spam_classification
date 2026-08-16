import logging


def get_logger(name):
    """
    #USE
    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    def predict_email(email):
        logger.info("Start email prediction")

        try:
            # xử lý prediction
            logger.info("Prediction completed")
        except Exception:
            logger.exception("Prediction failed")
        raise
    """
    return logging.getLogger(name)

