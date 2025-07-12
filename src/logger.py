# logger.py
import logging
from pathlib import Path

loggerName = Path(__file__).stem                 # "logger"
LOGFILE    = Path(__file__).parent / f"{loggerName}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOGFILE, mode="w"),
        logging.StreamHandler()
    ]
)

log = logging.getLogger(loggerName)
