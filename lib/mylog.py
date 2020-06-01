import logging


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s (%(filename)s:L%(lineno)d)',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='/tmp/my_alerts.log',
                    filemode='a')

logger = logging.getLogger(__name__)