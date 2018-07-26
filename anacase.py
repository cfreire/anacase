#!/usr/bin/python3
# Author: César Bento Freire <cfreire@cfreire.com.pt>
# Maintainers: Luis Antunes, José Cruz, José Charrua - ana.pt

"""
 Projecto ANACASE
 ================

 Gestor de sorteio de bagagens para o aeroporto de Lisboa
 utilizando hardware e software opensource

 usage: ./anacase.py

"""
__version__ = '1.2.5'

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
    cfg = config.Config(master_config['config_file'])
    cfg.section('GLOBAL')
    logger.level(cfg.key('log_level'),)
    app = manager.App(camera_data=cfg.section('CAMERA'),
                      display_data=cfg.section('DISPLAY'),
                      led_data=cfg.section('LED'),
                      buzzer_data=cfg.section('BUZZER'),
                      random_data=cfg.section('STATS'),
                      version=__version__)
    while app.run():
        pass
    app.close()


if __name__ == "__main__":
    main()
