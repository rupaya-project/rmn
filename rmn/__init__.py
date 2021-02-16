import logging

__version__ = '0.5.12'

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
logger = logging.getLogger('rmn')
logger.addHandler(handler)
logger.setLevel('CRITICAL')
