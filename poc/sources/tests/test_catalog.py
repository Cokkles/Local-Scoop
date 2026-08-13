import pytest
from poc.sources.catalog import SourceCatalog, SourceDefinition, SourceOrigin, TrustState

def built():
    return SourceDefinition('official','Official','https://example.com/events','rss',1,True,SourceOrigin.BUILTIN,TrustState.CURATED,{})

def test_server_overlay_can_disable_without_code_change():
    catalog=SourceCatalog([built()]); old=catalog.revision(); catalog.apply_server_overlay([{'source_id':'official','enabled':False}]); assert not catalog.get('official').enabled and catalog.revision()!=old

def test_user_feed_starts_disabled_and_tier_four():
    source=SourceCatalog().propose_user_source(name='Neighborhood',url='https://events.example.org/feed.ics',adapter_family='ical'); assert not source.enabled and source.authority_tier==4

def test_user_html_is_not_self_service():
    with pytest.raises(ValueError): SourceCatalog().propose_user_source(name='Site',url='https://events.example.org',adapter_family='custom_html')

@pytest.mark.parametrize('url',['http://example.com/feed.xml','https://localhost/feed.xml','https://127.0.0.1/feed.xml','https://10.0.0.2/feed.xml'])
def test_user_source_rejects_unsafe_urls(url):
    with pytest.raises(ValueError): SourceCatalog().propose_user_source(name='Bad',url=url,adapter_family='rss')

def test_inline_secrets_rejected():
    with pytest.raises(ValueError): SourceCatalog().propose_user_source(name='Bad',url='https://example.com/feed.xml',adapter_family='rss',config={'api_key':'secret'})
