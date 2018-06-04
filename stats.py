import datetime
import logging
import random

log = logging.getLogger(__name__)


class Stats:

    def __init__(self, random_param):
        self.parameters = random_param
        self.case_random = []
        self.counter = 0
        self.timer = datetime.datetime.now()

    def reset(self):
        self.counter = 0
        self.random_samples()

    def case_random(self):
        if self.counter in self.case_random():
            self.timer = datetime.datetime.now()
            self.random_samples().remove(self.counter)

    def __str__(self):
        return 'counter:{} time:{}'.format(self.counter, datetime.datetime.now().strftime("%H:%M:%S"))

    def random_samples(self):
        """ generate random case samples """
        percentage_sample = int(self.parameters['percentage_sample'])
        loop_sample = int(self.parameters['loop_sample'])
        logging.info('starting generate random {}% of {}...'.format(percentage_sample, loop_sample))
        try:
            self.case_random.append(1)  # for debug
            for c in range(loop_sample // percentage_sample):
                luck = random.randrange(loop_sample) + 1
                self.case_random.append(luck)
                self.case_random.sort()
            logging.debug('random numbers {}'.format(self.case_random))
            return self.case_random
        except TypeError:
            logging.error('error generating random numbers {} of {}'.format(percentage_sample, loop_sample))
            self.case_random.append(1)  # generate only one random
            logging.info('only one sample created [1]')
            return self.case_random


if __name__ == '__main__':
    # simple explore test
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    random_data = {'percentage_sample': '10', 'loop_sample': '1000'}
    s = Stats(random_data)
    s.random_samples()
    print(s)
