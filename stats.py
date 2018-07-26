import logging
import random

log = logging.getLogger(__name__)


class Stats:

    def __init__(self, random_param):
        self.percentage_sample = int(random_param['percentage_sample'])
        if self.percentage_sample > 100:
            log.warning('percentage sample value error "{}"'.format(self.percentage_sample))
            raise ValueError('percentage sample value error')
        self.loop_sample = int(random_param['loop_sample'])
        self._case_random = []
        self.counter = 0
        self._total = int(self.loop_sample * self.percentage_sample / 100)
        self._get_random_sample()

    def _get_random_sample(self):
        """ generate random case samples """
        log.info('starting generating new random set {}%'.format(self.percentage_sample, self.loop_sample))
        while len(self._case_random) < self._total:
            luck = random.randrange(self.loop_sample) + 1
            if luck not in self._case_random:
                self._case_random.append(luck)
            self._case_random.sort()
        log.debug('random numbers generated {}'.format(self._case_random))

    def is_selected(self):
        if self.counter in self._case_random:
            log.info('case id={} select for review '.format(self.counter))
            self._case_random.remove(self.counter)
            return True

    def inc_counter(self):
        if self.counter < self.loop_sample:
            self.counter += 1
        else:
            self.reset()

    def reset(self):
        self.counter = 0
        self._get_random_sample()

    @property
    def percentage(self):
        try:
            return round((self.sampled / self.counter) * 100, 1)
        except ZeroDivisionError:
            return 0.0

    @property
    def sampled(self):
        return self._total - len(self._case_random)


if __name__ == '__main__':
    # simple explore test
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    random_data = {'percentage_sample': '100', 'loop_sample': '10'}
    stats = Stats(random_data)
    for n in range(20):
        print('counter: {}\tselected: {}\tpercentage: {}'.format(stats.counter, stats.sampled, stats.percentage))
        stats.inc_counter()
        stats.is_selected()
