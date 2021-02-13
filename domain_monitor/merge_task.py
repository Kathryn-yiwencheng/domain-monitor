from domain_monitor.models import Zone, Country, Domain, Registration, HostedCountry, ResourceRecord
from domain_monitor.domainsdb_client import get_domains
from domain_monitor import app, db

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

def load_data():
    
    results = get_domains("lava")
    
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
        
        pprint(domain_model.registrations)

        matching_registrations = [
            reg 
            for reg in domain_model.registrations
            if reg.create_date == domain.create_date
        ]
        if len(matching_registrations) > 0:
            print("Found existing registration")
            registration = matching_registrations[0]
        else:
            print("New registration")
            registration = Registration(
                domain=domain_model,
                create_date=domain.create_date,
                is_dead=domain.is_dead
            )
            db.session.add(registration)
    
        if country is not None:
            matching_hcs = [
                hc
                for hc in registration.hosted_countries
                if hc.country == country
            ]
            if len(matching_hcs) > 0:
                print("Found matching hc")
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