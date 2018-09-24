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
__version__ = '1.3.0'

import sys
import argparse as ap

import config
import logger
import manager


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
    parser.add_argument('-version', action="store_true", help='version information')
    parser.add_argument('-config', metavar='config_file', help='configuration file')
    parser.add_argument('-logger', metavar='log_file', help='logger file')
    args = parser.parse_args()
    if args.version:
        print(__file__ + '\nversion:' + str(__version__))
        sys.exit(0)
    if args.config:
        defaults['config_file'] = args.config
    if args.logger:
        defaults['log_file'] = args.logger
    return defaults


def main():
    """ MAIN APP """
    master_config = get_start_arguments()
    logger.setup(master_config['log_file'], 'w')
    config.init(master_config['config_file'])
    config.set_section('GLOBAL')
    logger.level(config.key['log_level'])
    app = manager.App(camera_data=config.set_section('CAMERA'),
                      display_data=config.set_section('DISPLAY'),
                      led_data=config.set_section('LED'),
                      buzzer_data=config.set_section('BUZZER'),
                      random_data=config.set_section('STATS'),
                      version=__version__)
    while app.run():
        pass
    app.close()


if __name__ == "__main__":
    main()
