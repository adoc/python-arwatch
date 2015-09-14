"""(Hopefully) Safe DNS resolution for routes.
"""

import logging
log = logging.getLogger(__name__)

import time
import collections

import dns.name
import dns.message
import dns.rdatatype
import dns.resolver
import dns.query


REQUEST_THROTTLE_MS = 100


def throttle():
    time.sleep(REQUEST_THROTTLE_MS / 1000)


def _get_soa_addr(fqdn):
    """ Use resolver to return the IP address of the SOA of
    :param fqdn:.

    :param domainname:
    :return: ip addr
    """

    domain = dns.name.from_text(fqdn)
    assert len(domain.labels) == 3, ("Requires root domain name string. "
                                     "(i.e. google.com)")

    throttle()
    soa_query = dns.resolver.query(domain, 'SOA')
    assert len(soa_query) == 1

    a_query = dns.resolver.query(soa_query[0].mname, 'A')
    assert len(a_query) == 1

    soa_addr = a_query[0].address

    log.debug("_get_soa_addr() soa_addr: %s for fqdn: %s" % (soa_addr, fqdn))

    return soa_addr


def _get_name_query_ips(dns_addr, record):
    """ Query server at `dns_addr` for the A (Name) Records of `record`
    and a list of IP addresses.

    :param dns_addr:
    :param record:
    :return:
    """

    name = dns.name.from_text(record)
    assert len(name.labels) >= 3, ("")

    request = dns.message.make_query(name, dns.rdatatype.A)
    throttle()
    response = dns.query.udp(request, dns_addr)

    answer = response.answer
    assert len(answer) == 1

    addresses = set([record.address for record in answer[0]])

    log.debug("_get_name_query_ips() addresses: %s" % addresses)
    return addresses


def parse(root_authority, namelist):
    """

    :param root_authority: Root domain to get SOA (i.e. 'google.com')
    :param namelist: List of names to parse A/Name Records.
    :return tuple: dict of hosts: [ips] and set of all ips.
    """

    all_ips = set()
    soa_addr = _get_soa_addr(root_authority)

    def dict_namelist_ips(all_ips):
        for name in namelist:
            ips = _get_name_query_ips(soa_addr, name)
            all_ips.update(ips)
            yield name, ips

    return dict(dict_namelist_ips(all_ips)), all_ips


class Resolver:

    __serializable__ = ('root_authority', 'host_ip_map',
                        'host_updated')

    def __init__(self, root_authority, time_provider=time.time):
        self.__root_authority = None
        self.__root_authority_addr = None

        self.__host_ip_map = collections.defaultdict(set)
        self.__host_updated = collections.defaultdict(lambda: 0)
        self.__all_ips = set()

        self.__time_provider = time_provider

        self.root_authority = root_authority

    @property
    def root_authority(self):
        return self.__root_authority

    @root_authority.setter
    def root_authority(self, val):
        self.__root_authority = str(val)
        self.__root_authority_addr = _get_soa_addr(self.__root_authority)

    @property
    def root_authority_addr(self):
        return self.__root_authority_addr

    @property
    def host_ip_map(self):
        return self.__host_ip_map

    def __des_host_ip_map__(self, host_map):
        for host, ips in host_map.items():
            self.__host_ip_map[str(host)] = set(ips)
            self.__all_ips |= ips

    @property
    def host_updated(self):
        return self.__host_updated

    def __des_host_updated__(self, host_updated):
        for host, updated in host_updated.items():
            self.__host_updated[str(host)] = float(updated)

    @property
    def all_ips(self):
        return self.__all_ips

    def pre_query(self, *args):
        for name in args:
            self.__host_ip_map[name]

    def query(self, *args):
        hosts = args or self.__host_ip_map.keys()
        def dict_namelist_ips():
            for name in hosts:
                host_ips = self.__host_ip_map.get(name, set())
                ips = _get_name_query_ips(self.__root_authority_addr, name)

                if len(ips ^ host_ips) > 0: # New or changed IPs.
                    self.__all_ips -= ips - host_ips
                    self.__all_ips |= ips
                    self.__host_ip_map[name] = ips
                    self.__host_updated[name] = self.__time_provider()
                    yield name, ips

        return dict(dict_namelist_ips())






if __name__ == "__main__":
    # API Example.
    print(parse("privateinternetaccess.com",
                      ['nl.privateinternetaccess.com',
                        'france.privateinternetaccess.com']))

    r = Resolver("privateinternetaccess.com")
    r.query('nl.privateinternetaccess.com',
            'france.privateinternetaccess.com')
    print(r.all_ips)
    print(r.host_ip_map)
    print(r.host_updated)
    r.query('nl.privateinternetaccess.com',
            'france.privateinternetaccess.com')
    print(r.all_ips)
    print(r.host_ip_map)
    print(r.host_updated)
