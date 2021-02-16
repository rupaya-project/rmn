import logging

__version__ = '1.0.0'

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
logger = logging.getLogger('rupayamn')
logger.addHandler(handler)
logger.setLevel('CRITICAL')
