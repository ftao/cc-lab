import logging

def setup_logging(verbose=False):
    level = "WARN"
    if verbose:
        level = "DEBUG"
    FORMAT = '[%(asctime)-15s] [%(levelname)s] %(message)s'
    logging.basicConfig(format=FORMAT, level=level)
