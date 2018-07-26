import logging
import random
import datetime

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
        self._time_counter = []
        self._time_selected = []

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
            self._time_selected.append(datetime.datetime.now())
            return True

    def inc_counter(self):
        if self.counter < self.loop_sample:
            self._time_counter.append(datetime.datetime.now())
            self.counter += 1
        else:
            self.reset()

    def reset(self):
        self.counter = 0
        self._get_random_sample()
        self._time_counter = []
        self._time_selected = []

    @property
    def counter_by_time(self):
        min5 = 0
        min15 = 0
        min60 = 0
        for t in self._time_counter:
            if datetime.datetime.now() - t < datetime.timedelta(minutes=5):
                min5 += 1
            if datetime.datetime.now() - t < datetime.timedelta(minutes=15):
                min15 += 1
            if datetime.datetime.now() - t < datetime.timedelta(minutes=60):
                min60 += 1
        return {'min5': min5, 'min15': min15, 'min60': min60}

    @property
    def selected_by_time(self):
        min5 = 0
        min15 = 0
        min60 = 0
        for t in self._time_selected:
            if datetime.datetime.now() - t < datetime.timedelta(minutes=5):
                min5 += 1
            if datetime.datetime.now() - t < datetime.timedelta(minutes=15):
                min15 += 1
            if datetime.datetime.now() - t < datetime.timedelta(minutes=60):
                min60 += 1
        return {'min5': min5, 'min15': min15, 'min60': min60}

    @property
    def first_counter(self):
        if self._time_counter:
            return self._time_counter[0]
        else:
            return datetime.datetime.now()

    @property
    def percentage(self):
        try:
            return round((self.sampled / self.counter) * 100, 1)
        except ZeroDivisionError:
            return 0.0

    @property
    def percentage_by_time(self):
        min60_sel = 0
        min60_cnt = 0
        for t in self._time_selected:
            if datetime.datetime.now() - t < datetime.timedelta(minutes=60):
                min60_sel += 1
        for t in self._time_counter:
            if datetime.datetime.now() - t < datetime.timedelta(minutes=60):
                min60_cnt += 1
        if min60_cnt:
            return round((min60_sel / min60_cnt) * 100, 1)
        else:
            return 0

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

    print(stats.counter_by_time)
