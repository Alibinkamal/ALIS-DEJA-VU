import logging
from pathlib import Path
def get_logger(name="alis_deja_vu"):
    log_dir=Path.home()/".alis_deja_vu";log_dir.mkdir(parents=True,exist_ok=True)
    logger=logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        h=logging.FileHandler(log_dir/"app.log",encoding="utf-8")
        h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(h)
    return logger