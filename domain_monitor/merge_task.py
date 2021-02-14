from domain_monitor.models import Zone, Country, Domain, Registration, HostedCountry, ResourceRecord, Search
from domain_monitor.domainsdb_client import get_domains
from domain_monitor import app, db
from datetime import datetime

import logging

logger = logging.getLogger("domain_monitor.merge_task")

from pprint import pprint

class InMemoryDimension(object):
    
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

def merge_all_data():
    searches = Search.query.all()
    for search in searches:

        merge_data(False, search.search_string)
        merge_data(True, search.search_string)

def merge_data(is_dead, domain_search):

    countries = {c_model.country_name for c_model in Country.query.all()}
    
    countries.add(None)

    zones = {z_model.zone for z_model in Zone.query.all()}

    for country in countries:
        
        country_result = get_domains(domain_search, country=country, is_dead=is_dead)
        load_data(country_result)

        if country_result.is_truncated:
            for zone in zones:
                zone_result = get_domains(domain_search, zone, country, is_dead=is_dead)
                load_data(zone_result)
                if zone_result.is_truncated:
                    logger.warn(
                        "truncated data search(%r, %r, %r, %r) len = %r", 
                        domain_search, zone, country, is_dead , zone_result.match_count
                    )
    

def load_data(results):
    
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
            if reg.create_date == domain.create_date
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

        registration.last_seen_date = datetime.utcnow()

        # Record as dead if domain is_dead
        if domain.is_dead:
            if registration.removed_date is None:
                logger.info("Dead registration found: %r", domain.json_object)
                registration.removed_date = datetime.utcnow()
        
        registration.is_dead = domain.is_dead
        registration.update_date = domain.update_date
        
        
        # If non-matching registrations exist, mark them as removed

        for non_matching_registration in non_matching_registrations:
            if non_matching_registration.removed_date is None:
                logger.info("Old registration found: %r", non_matching_registration)
                non_matching_registration.removed_date = datetime.utcnow()
        
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
            
    # hosted_country = {domain.hosted_country for domain in results.domains if domain.hosted_country is not None}
    # hosted_country_models = [HostedCountry(country_name=country) for country in countries]
    # for country_model in country_models:
    #     db.session.add(country_model)

    # registration = {domain.registration for domain in results.domains if domain.domain is not None}
    # registration_models = [Registration(domain_name=domain) for domain in domains]
    # for domain_model in domain_models:
    #     db.session.add(domain_model)
    

    db.session.commit()