__version__ = "1.0.0"

import sys
import configparser
import logging


class Config:
    """ Read configuration files"""
    _log = logging.getLogger(__name__)

    def __init__(self, config_file_name):
        self.config = configparser.RawConfigParser()
        if not self.config.read(config_file_name):
            msg = f'invalid configuration file "{config_file_name}". Aborting!'
            self._log.critical(msg)
            sys.exit(msg)
        else:
            self._log.info(f'success reading config file "{config_file_name}"')

    def get_str(self, section, key):
        try:
            Config._logger_debug('get_str', section, key)
            return self.config.get(section, key)
        except (configparser.Error, ValueError):
            Config._logger_warning(section, key)

    def get_int(self, section, key):
        try:
            Config._logger_debug('get_int', section, key)
            return self.config.getint(section, key)
        except (configparser.Error, ValueError):
            Config._logger_warning(section, key)

    def get_float(self, section, key):
        try:
            Config._logger_debug('get_float', section, key)
            return self.config.getfloat(section, key)
        except (configparser.Error, ValueError):
            Config._logger_warning(section, key)

    def get(self, section):
        try:
            data = dict(self.config.items(section))
            Config._logger_debug('get', section, '*', data)
            return data
        except (configparser.Error, ValueError):
            Config._logger_warning(section, '[*]')

    @staticmethod
    def _logger_warning(section, key):
        Config._log.warning(f'invalid key "{key}" in section [{section}]')

    @staticmethod
    def _logger_debug(func, section, key, data=''):
        Config._log.debug(f'call function {func}() key "{key}" in section [{section}] {data}')


if __name__ == "__main__":
    # simple explore test
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    cfg = Config('anacase.ini')
    cfg.get_str('GLOBAL', 'percentage_sample')
