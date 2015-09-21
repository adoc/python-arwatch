"""Authoritative DNS Record (Currently only A) watcher API.
"""


import logging
log = logging.getLogger(__name__)


import time

from arwatch.eye import Watcher
from arwatch.ns import Resolver


def read_stream(stream, data=b'', length=1024):
    buffer = stream(length).strip()
    if buffer:
        data += buffer
        return read_stream(stream, data)
    else:
        return data


class ResolverWatcher(Watcher):
    def __init__(self, resolver, watch_timeout=300, first_run=True,
                 time_provider=time.time, last_poll=None, update_callback=None):
        super(ResolverWatcher, self).__init__(self.__ev_resolve,
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

        assert callable(update_callback)
        self.__update_callback = update_callback

        if first_run is True:
            self.__ev_resolve()

        self.start()

    def __ev_resolve(self):
        try:
            response = self.__resolver.query(*[domain
                    for domain, updated in self.__resolver.host_updated.items()
                    if self.__last_poll < updated])
            if self.__update_callback:
                self.__update_callback(response)
            else:
                return response
        finally:
            self.__last_poll = self.__time_provider()


if __name__ == "__main__":
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)


    resolver = Resolver('privateinternetaccess.com')

    # Fire initial query.
    resolver.pre_query(
            'nl.privateinternetaccess.com',
            'france.privateinternetaccess.com',
            'ca-toronto.privateinternetaccess.com',
            'russia.privateinternetaccess.com',
            'sweden.privateinternetaccess.com',
            'ro.privateinternetaccess.com',
            'ca.privateinternetaccess.com',
            'hk.privateinternetaccess.com',
            'israel.privateinternetaccess.com',
            'swiss.privateinternetaccess.com',
            'germany.privateinternetaccess.com')

    ResolverWatcher(resolver, watch_timeout=5, first_run=True)
