from pprint import pprint

import requests
import urllib.parse
import re
import dateutil.parser


class DomainRecord(object):
    """A class for each JSON domain more friendly """

    tld_re = re.compile(r'^[A-Za-z0-9\-\.]+\.(\w+)$')
        
    def __init__(self, json_object):
        self.json_object = json_object

    @property
    def domain(self):
        return self.json_object['domain']

    @property
    def country(self):
        return self.json_object['country']

    @property
    def is_dead(self):
        """ String 'True' or 'False' into python boolean """
        return self.json_object['isDead'] == 'True'

    @property
    def create_date(self):
        """ Make the data type more friendly - datetime object """
        if self.json_object['create_date'] is None:
            return None
        else:
            return dateutil.parser.parse(
                self.json_object['create_date']
            )

    @property
    def update_date(self):
        """ Make the data type more friendly - datetime object """
        if self.json_object['update_date'] is None:
            return None
        else:
            return dateutil.parser.parse(
                self.json_object['update_date']
            )


    @property
    def zone(self):
        matches = self.tld_re.match(self.domain)
        if matches:
            return matches.group(1)
        else:
            return None
    

class DomainsdbResponse(object):

    def __init__(self, json_object):
        self.json_object = json_object
    
    @property
    def match_count(self):
        """Find how many match counts """
        return self.json_object.get('total', 0)
    
    @property
    def domains(self):
        """get domains as domain records objects. Convert to DomainRecord from a raw JSON  """
        return list(
               map(DomainRecord, self.json_object.get('domains', [])
            )
        )

    @property
    def is_truncated(self):
        """Return true if there are fewer returned domains than total matches """
        return self.match_count != len(self.domains)


def get_domains(search_domain, zone=None, country=None, is_dead=False):
    """ get domain data from API, query country first and then zone (Is Truncated) """

    # Begin with base URL
    base_url = 'https://api.domainsdb.info/v1/domains/search'
    base_url_parts = urllib.parse.urlsplit(base_url)
    
    # Assemble a query string
    query_string_parts = {
        'domain': search_domain,
        'zone': zone,
        'country': country,
        'isDead': is_dead
    }

    query_string_parts = {
        k:v 
        for k,v in query_string_parts.items()
        if v is not None
    }
    query_string = urllib.parse.urlencode(query_string_parts)
    
    #Compose request URL
    url_parts = urllib.parse.SplitResult(
        base_url_parts.scheme, 
        base_url_parts.hostname, 
        base_url_parts.path, 
        query_string, 
        ''
    )
    url = urllib.parse.urlunsplit(url_parts)

    # Make request
    r = requests.get(url)
    return DomainsdbResponse(r.json())


if __name__ == '__main__':
    
    from collections import Counter
    response = get_domains('lava', zone='com')
    print("Match count:", response.match_count)
    print("Is Truncated:", response.is_truncated)
    # for domain in response.domains:
    #     print(domain.domain, domain.tld)

    pprint(Counter(domain.zone for domain in response.domains ))
    pprint(Counter(domain.country for domain in response.domains ))

    for domain in response.domains:
        print("Domain:", domain.domain, 'update_date:', domain.json_object['update_date'])
        
    pprint(response.domains[0].json_object)
