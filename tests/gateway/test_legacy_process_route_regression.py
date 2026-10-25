"""Native provider pseudo-endpoints are metadata, not HTTP launch overrides."""
import json
from types import SimpleNamespace
import pytest
from gateway.session_local_migration import legacy_launch_params
from gateway.session_policy import _apply_launch_overrides


def row(endpoint):
    return {'source': 'desktop', 'model': 'native-model', 'model_config': json.dumps({
        'provider': 'native-test', 'base_url': endpoint})}


def test_registered_native_endpoint_is_not_an_http_override(monkeypatch):
    import providers
    monkeypatch.setattr(providers, 'get_provider_profile', lambda name: SimpleNamespace(
        auth_type='external_process', base_url='process://native-test') if name == 'native-test' else None)
    params, _ = legacy_launch_params(row('process://native-test'))
    assert params['provider'] == 'native-test'
    assert 'base_url' not in params
    _apply_launch_overrides(params, {'model': {}})


@pytest.mark.parametrize('endpoint', ['process://unregistered', 'process://native-test?override=1', 'https://example.com/v1'])
def test_unrecognised_or_http_endpoint_not_silently_discarded(monkeypatch, endpoint):
    import providers
    monkeypatch.setattr(providers, 'get_provider_profile', lambda name: SimpleNamespace(
        auth_type='external_process', base_url='process://native-test'))
    params, _ = legacy_launch_params(row(endpoint))
    assert params['base_url'] == endpoint
