import logging

def setup_logger(name: str, log_file: str, level=logging.INFO) -> logging.Logger:
    """
    Set up a logger with a specified name and log file.
    
    Args:
        name (str): The name of the logger.
        log_file (str): The file where logs will be stored.
        level: Logging level (default: logging.INFO).
        
    Returns:
        logging.Logger: Configured logger.
    """
    # Create a logger object
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Create a file handler that logs even debug messages
    fh = logging.FileHandler(log_file)
    fh.setLevel(level)
    
    # Create a console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    # Add the handlers to the logger
    if not logger.handlers:
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger

logger = setup_logger('myLogger', 'mylog.log')