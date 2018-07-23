__version__ = '1.0.1'

import configparser
import logging


class Config:
    """Read configuration files"""

    log = logging.getLogger(__name__)

    def __init__(self, config_file_name):
        self.config = configparser.RawConfigParser()
        self.data = dict()
        if not self.config.read(config_file_name):
            msg = 'invalid configuration file "{}"'.format(config_file_name)
            self.log.critical(msg)
            raise ValueError(msg)
        else:
            self.log.info('success reading config file "{}"'.format(config_file_name))

    def section(self, section):
        try:
            self.data = dict(self.config.items(section))
            self.log.debug('reading [{}] = {}'.format(section, self.data))
            return self.data
        except configparser.NoSectionError:
            self.log.warning('section [{}] not found'.format(section))
            return None

    def key(self, key):
        try:
            self.log.debug('reading "{}" = {}'.format(key, self.data[key]))
            return self.data[key]
        except KeyError:
            self.log.warning('key "{}" not found'.format(key))
            return None


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    cfg = Config('tests/config.ini')
    cfg.section('GLOBAL')
    assert cfg.key('log_level') == 'DEBUG'


