from newsapi import NewsApiClient
import requests

newsapi = NewsApiClient(api_key='Your API Key')

def get_sources_and_domains():
    all_sources = newsapi.get_sources()['sources']
    # Filter sources containing the keyword "weather" in their name or description
    weather_sources = [source for source in all_sources if
                       'weather' in source['name'].lower() or 'weather' in source['description'].lower()]
    sources = []
    domains = []
    for e in weather_sources:
        id = e['id']
    # It extracts the domain from the URL in the 'url' field of the current element(e).This is done by removing any occurrences of
    #  "http://", "https://", and "www." from the URL string.
        domain = e['url'].replace("http://", "")
        domain = domain.replace("https://", "")
        domain = domain.replace("www.", "")
    # It finds the position of the first '/' character in the domain.If found, it truncates the domain string up to that position, effectively removing any paths or query parameters from the URL.
        slash = domain.find('/')
        if slash != -1:
            domain = domain[:slash]
        # print(domain)
        sources.append(id)
        domains.append(domain)
    sources = ", ".join(sources)
    domains = ", ".join(domains)
    # print(all_sources)
    # print(sources)
    # print(domains)
    return sources, domains


