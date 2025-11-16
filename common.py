import logging

def get_logger(name: str = None) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.hasHandlers():  # Prevent duplicate handlers on reload
        logger.setLevel(logging.DEBUG)

        # File handler - overwrite previous logs each run
        fh = logging.FileHandler("app.log", mode="w")  # <-- changed "a" to "w"
        fh.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
        )
        fh.setFormatter(formatter)

        logger.addHandler(fh)

        # Prevent propagation to root logger
        logger.propagate = False

    return logger
