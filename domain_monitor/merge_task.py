from domain_monitor.models import Zone, Country, Domain, Registration, HostedCountry, ResourceRecord, Search
from domain_monitor.domainsdb_client import get_domains
from domain_monitor import app, db
from datetime import datetime, timedelta
from pprint import pprint
import logging

logger = logging.getLogger("domain_monitor.merge_task")


class InMemoryDimension(object):
    """Dependency for zone_dim and country_dim"""
    
    def __init__(self, model, create_func, key_func):
        self.model = model
        self.create_func = create_func
        self.key_func = key_func
        self.dict = None
    
    def load(self):
        self.dict = {self.key_func(m):m for m in self.model.query.all()}
    
    def ensure_contains(self, key):
        if key not in self.dict and key is not None:
            model = self.create_func(key)
            self.dict[key] = model
            db.session.add(model)
        return self.dict.get(key)


class ChangeSet(object):
    """ dependency use for change_set in merge_all_search"""
    def __init__(self):
        self.added = []
        self.removed = []


def remove_unseen_domains(stale_threshold=timedelta(hours=12), change_set=None):
    """categorize domain to be unseen domain if they have a new create date"""

    q = (Registration.query
        .filter(Registration.last_seen_date < datetime.utcnow() - stale_threshold)
        .filter(Registration.removed_date.is_(None)))
    stale = q.all()
    for reg in stale:
        logger.info("Stale registration found: %r", reg)
        reg.removed_date = datetime.utcnow()
        if change_set is not None:
            change_set.removed.append(reg)

    db.session.commit()


def merge_all_searches():
    """Load searches from the database and execute each"""
    
    searches = Search.query.all()
    change_set = ChangeSet()

    for search in searches:

        merge_search(domain_search=search.search_string, is_dead=False, change_set=change_set)
        merge_search(domain_search=search.search_string, is_dead=True, change_set=change_set)

    remove_unseen_domains(change_set=change_set)

    if len(change_set.added) > 0:
        logger.info("Added %d domains", len(change_set.added))
    else:
        logger.info("No Domains Added")
    
    if len(change_set.removed) > 0:
        logger.info("Removed %d domains", len(change_set.removed))
    else:
        logger.info("No Domains Removed")
    

def merge_search(domain_search, is_dead, change_set=None):
    """Seach domains and load into the dabase. 

       Execute search for each known country as well as coutnry omitted. 
       For each result set, if it is truncated, also try searching with all known zones. 
       To find as many as matching domains as possible. """

    countries = {c_model.country_name for c_model in Country.query.all()}    
    
    countries.add(None)
    
    zones = {z_model.zone for z_model in Zone.query.all()}

    for country in countries:
        
        country_result = get_domains(domain_search, country=country, is_dead=is_dead)
        load_domain_results(country_result, change_set)

        if country_result.is_truncated:
            for zone in zones:
                zone_result = get_domains(domain_search, zone, country, is_dead=is_dead)
                load_domain_results(zone_result, change_set)
                if zone_result.is_truncated:
                    logger.warn(
                        "truncated data search(domain=%r, zone=%r, country=%r, isDead=%r) len = %r", 
                        domain_search, zone, country, is_dead , zone_result.match_count
                    )
    

def load_domain_results(results, change_set=None):
    """call InMemoryDimension function and build zone and country in memory"""

    # Build Zone dimension in memory
    zone_dim = InMemoryDimension(
        Zone, 
        lambda key: Zone(zone=key), 
        lambda zone: zone.zone
    )
    
    zone_dim.load()
        
    # Build Country dimension in memory
    country_dim = InMemoryDimension(
        Country,
        lambda key: Country(country_name=key),
        lambda country: country.country_name
    )
    country_dim.load()
    
    # Merge in new domains
    for domain in results.domains:
        zone = zone_dim.ensure_contains(domain.zone)
        country = country_dim.ensure_contains(domain.country)
    
        domain_model = Domain.query.filter(Domain.domain_name == domain.domain).one_or_none()
        if domain_model is None:
            domain_model = Domain(
                domain_name=domain.domain, 
                zone=zone
            )
            db.session.add(domain_model)
        
        logger.debug("%r", domain_model.registrations)

        matching_registrations = [
            reg 
            for reg in domain_model.registrations
            if  reg.create_date == domain.create_date 
                and (reg.removed_date is None or domain.is_dead)
        ]
        non_matching_registrations = [
            reg 
            for reg in domain_model.registrations
            if reg.create_date != domain.create_date
        ]

        if len(matching_registrations) > 0:
            logger.debug("Found existing registration")
            registration = matching_registrations[0]
        else:
            logger.info("New registration found: %r", domain.json_object)
            registration = Registration(
                domain=domain_model,
                create_date=domain.create_date,
                is_dead=domain.is_dead,
                added_date=datetime.utcnow()
            )
            db.session.add(registration)

            if change_set is not None:
                change_set.added.append(registration)

        registration.last_seen_date = datetime.utcnow()

        # Record as dead if domain is_dead
        if domain.is_dead:
            if registration.removed_date is None:
                logger.info("Dead registration found: %r", domain.json_object)
                registration.removed_date = datetime.utcnow()
                if change_set is not None:
                    change_set.removed.append(registration)

        
        registration.is_dead = domain.is_dead
        registration.update_date = domain.update_date
        
        
        # If non-matching registrations exist, mark them as removed

        for non_matching_registration in non_matching_registrations:
            if non_matching_registration.removed_date is None:
                logger.info("Old registration found: %r", non_matching_registration)
                non_matching_registration.removed_date = datetime.utcnow()
                if change_set is not None:
                    change_set.removed.append(non_matching_registration)

        
        if country is not None:
            matching_hcs = [
                hc
                for hc in registration.hosted_countries
                if hc.country == country
            ]
            if len(matching_hcs) > 0:
                logger.debug("Found matching hc")
            else:
                hc = HostedCountry(country=country, registration=registration)
                db.session.add(hc)


    db.session.commit()