import logging.config
import shutil
import os

logger = logging.getLogger('harbor')
logging.config.fileConfig("./logging.conf")

if __name__ == '__main__':
    logger.info('start clear')
    for path in ['./config', './resources', './services']:
        if os.path.exists(path):
            shutil.rmtree(path)
            logger.info('delete %s', path)
    logger.info('clear complete')
