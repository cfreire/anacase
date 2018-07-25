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
__version__ = '1.2.0'

import sys
import argparse as ap
import random
import logging

import config
import camera
import logger
import hardware


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


def get_random_samples(random_param):
    """ generate random case samples """
    case_random = []
    percentage_sample = int(random_param['percentage_sample'])
    loop_sample = int(random_param['loop_sample'])
    logging.info('starting generate random {}% of {}...'.format(percentage_sample, loop_sample))
    try:
        case_random.append(1)
        for c in range(loop_sample // percentage_sample):
            luck = random.randrange(loop_sample) + 1
            case_random.append(luck)
        case_random.sort()
        logging.debug('random numbers {}'.format(case_random))
        return case_random
    except TypeError:
        logging.error('error generating random numbers {} of {}'.format(percentage_sample, loop_sample))
        case_random.append(1)  # generate only one random
        logging.info('only one sample created [1]')
        return case_random


def keyboard_events():
    pass


def mouse_events():
    pass


def main():
    """ MAIN APP """
    master_config = get_start_arguments()
    logger.setup(master_config['log_file'], __version__)
    cfg = config.Config(master_config['config_file'])
    cfg.section('GLOBAL')
    logger.level(cfg.key('log_level'))
    hw = hardware.Manager(keyboard=keyboard_events,
                          mouse=mouse_events,
                          leds=cfg.section('LED')
                          )
    
    cam = camera.Camera(camera_data=cfg.section('CAMERA'),
                        led_data=cfg.section('LED'),
                        random_data=get_random_samples(cfg.section('STATS')),
                        buzzer_data=cfg.section('BUZZER'),
                        version=__version__)
    while cam.run():
        pass
    cam.close()


if __name__ == "__main__":
    main()
