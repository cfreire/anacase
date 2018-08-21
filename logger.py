__version__ = '1.0.0'

import logging
import platform


def setup(log_file, mode='a'):
    """start logging to file, write version and platform"""
    logging.basicConfig(filename=log_file,
                        format='%(asctime)s %(name)s\t%(levelname)s\t %(message)s',
                        filemode=mode,  # w = write / a = append
                        level=logging.INFO)
    logging.info("starting logger on platform {}".format(platform.machine()))


def level(log_type):
    logging.getLogger().setLevel(logging.INFO)
    logging.info('changing log level to {}'.format(log_type))
    logging.getLogger().setLevel(log_type)


if __name__ == '__main__':
    setup('logger.log')
    level(logging.DEBUG)
    logging.info('*tester'*8)
