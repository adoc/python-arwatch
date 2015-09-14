"""
"""

import time

from arwatch.eye import Watcher


class ResolverWatcher(Watcher):
    def __init__(self, resolver, watch_timeout=300, first_run=True,
                 time_provider=time.time, last_poll=None):
        super(ResolverWatcher, self).__init__(self.__trigger,
                                              watch_timeout=watch_timeout,
                                              autostart=False)
        self.__resolver = resolver
        self.__time_provider = time_provider
        if last_poll is None:
            self.__last_poll = time_provider()
        else:
            try:
                float(last_poll)
            except ValueError:
                raise ValueError("'last_poll' parameter must be a number")
            else:
                self.__last_poll = last_poll

        if first_run is True:
            self.__trigger()

        self.start()

    def __trigger(self):
        try:
            return self.__resolver.query(*[domain
                    for domain, updated in self.__resolver.host_updated.items()
                    if self.__last_poll < updated])
        finally:
            self.__last_poll = self.__time_provider()
            print(self.__resolver.host_ip_map)
