""" Watcher.
"""

import logging
log = logging.getLogger(__name__)

import threading


class Watcher:
    """ Wrap threading.Timer to provide repeating timing.

    *Mainly allows for the Watcher to be molded and used for other APIs.
    """

    def __init__(self, trigger, watch_timeout=10,
                 timer_provider=threading.Timer, autostart=False):
        self.__trigger = trigger
        self.__watch_timeout = watch_timeout
        self.__timer_provider = timer_provider
        self.__timer = None
        if autostart is True:
            self.start()

    def __watch_trigger(self):
        response = self.__trigger()
        if response:
            log.info("Watcher trigger response: %s" % response)
        self.__start()

    def __start(self):
        self.__cancel()
        self.__timer = self.__timer_provider(self.__watch_timeout,
                                             self.__watch_trigger)
        self.__timer.start()
        log.debug("Watcher timer (re)started: %s" % self.__timer)

    def __cancel(self):
        if self.__timer:
            self.__timer.cancel()
            log.debug("Watcher timer cancelled: %s" % self.__timer)
            del self.__timer
            self.__timer = None
            return True

    def start(self):
        log.info("Watcher timer started.")
        self.__start()

    def cancel(self):
        if self.__cancel() is True:
            log.info("Watcher timer cancelled.")

    def join(self):
        log.info("Watcher timer joined.")
        self.__timer.join()
