"""Read configuration files"""

import configparser
import logging

__version__ = '1.2.0'
_log = logging.getLogger(__name__)

key = dict()  # global dictionary


def init(config_file_name):
    global _config
    _config = configparser.RawConfigParser()
    if not _config.read(config_file_name):
        msg = 'invalid configuration file "{}"'.format(config_file_name)
        _log.critical(msg)
        raise ValueError(msg)
    else:
        _log.info('success reading config file "{}"'.format(config_file_name))


def set_section(section):
    try:
        global key
        key = dict(_config.items(section))
        _log.debug('reading [{}] = {}'.format(section, key))
        return key
    except configparser.NoSectionError:
        _log.warning('section [{}] not found'.format(section))
        return None


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    init('tests/config.ini')
    set_section('GLOBAL')
    assert key['log_level'] == 'DEBUG'


