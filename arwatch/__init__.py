"""Route Sneak

The goal of this script is to watch a series of FDQNs and set up routes
to associated IP addresses.

"""


import logging
log = logging.getLogger(__name__)

from arwatch.ns import Resolver
from arwatch.nseye import ResolverWatcher


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