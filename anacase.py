#!/usr/bin/python3
# Author: César Bento Freire <cfreire@cfreire.com.pt>
# Maintainers: Luis Antunes, José Cruz, José Charrua - ana.pt

"""
 Projecto ANACASE
 ================

 Counter and random sampler of moving objects,
 using python computer vision (opencv).


 usage: ./anacase.py

"""

import argparse as ap

import config
import logger
import manager
import netifaces

# DEFAULT FILE NAMES
_configfile_ = 'anacase.ini'
_logfile_ = 'anacase.log'


def get_start_arguments():
    """ read arguments from command line
    :return: master_config_file
    warning: no logger yet!
    """
    # default values
    defaults = {'config_file': _configfile_, 'log_file': _logfile_}
    # get args
    parser = ap.ArgumentParser(description='anacase - bag case sample python software')
    parser.add_argument('-config', metavar='config_file', help='configuration file')
    parser.add_argument('-logger', metavar='log_file', help='logger file')
    args = parser.parse_args()
    if args.config:
        defaults['config_file'] = args.config
    if args.logger:
        defaults['log_file'] = args.logger
    return defaults


def get_mac_address(port):
    try:
        mac = netifaces.ifaddresses(port)[netifaces.AF_LINK]
        # get last 4 digits of mac addr for 'port' interface
        return str.upper(mac[0]['addr'][12:14]) + str.upper(mac[0]['addr'][15:17])
    except ValueError:
        return '----'


def main():
    """ MAIN APP """
    master_config = get_start_arguments()
    logger.setup(master_config['log_file'], 'w')
    config.init(master_config['config_file'])
    config.set_section('GLOBAL')
    _version = config.key['version']
    _port = config.key['port']
    logger.level(config.key['log_level'])
    app = manager.App(camera_data=config.set_section('CAMERA'),
                      display_data=config.set_section('DISPLAY'),
                      led_data=config.set_section('LED'),
                      buzzer_data=config.set_section('BUZZER'),
                      random_data=config.set_section('STATS'),
                      version=_version,
                      port=get_mac_address(_port)
                      )
    while app.run():
        pass
    app.close()


if __name__ == "__main__":
    main()
