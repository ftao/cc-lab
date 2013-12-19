import logging

def setup_logging(verbose=False):
    level = "WARN"
    if verbose:
        level = "DEBUG"
    FORMAT = '[%(asctime)-15s] [%(levelname)s] %(message)s'
    logging.basicConfig(format=FORMAT, level=level)

def read_last_line(fp, max_line_length=1024):
    fp.seek(-max_line_length, 2)
    return fp.readlines()[-1].decode()
