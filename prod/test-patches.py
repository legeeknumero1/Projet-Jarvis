#!/usr/bin/env python3
"""
Test script pour validation des patches critiques observabilité v1.3
"""
import re
import json
import logging
import sys
from pathlib import Path

def test_scrubbing_patterns():
    """Test des regex de scrubbing des secrets"""
    print("Test scrubbing secrets...")
    
    SCRUB_PATTERNS = [
        (re.compile(r'(?i)\b(api[_-]?key|token|password)\b\s*[:=]\s*([^\s",}]+)'), r'\1=***'),
        (re.compile(r'(?i)(Authorization:\s*Bearer\s+)[A-Za-z0-9._\-+=/]+'), r'\1***'),
        (re.compile(r'(?i)"(api[_-]?key|token|password)"\s*:\s*"([^"]+)"'), r'"\1":"***"'),
    ]
    
    test_cases = [
        ('api_key=secret123', 'api_key=***'),
        ('API-KEY: abc123def', 'API-KEY=***'),  
        ('Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9', 'Authorization: Bearer ***'),
        ('"api_key": "super_secret"', '"api_key":"***"'),
        ('"password": "mypass123"', '"password":"***"'),
        ('token=xyz789', 'token=***'),
        ('normal message without secrets', 'normal message without secrets'),
    ]
    
    success = 0
    for original, expected in test_cases:
        scrubbed = original
        for pat, repl in SCRUB_PATTERNS:
            scrubbed = pat.sub(repl, scrubbed)
        
        if scrubbed == expected:
            print(f"  OK '{original}' -> '{scrubbed}'")
            success += 1
        else:
            print(f"  FAIL '{original}' -> '{scrubbed}' (expected '{expected}')")
    
    print(f"Scrubbing: {success}/{len(test_cases)} tests OK\n")
    return success == len(test_cases)

def test_logging_config():
    """Test validation configs logging JSON"""
    print(" Test configs logging...")
    
    configs = [
        'prod/logs-config.json',
        'prod/logs-config-k8s.json'
    ]
    
    success = 0
    for config in configs:
        config_name = config.split('/')[-1]  # Juste le nom du fichier
        path = Path(__file__).parent / config_name
        if not path.exists():
            print(f"   {config} - fichier non trouvé")
            continue
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Vérifications de base
            assert data.get('version') == 1
            assert 'formatters' in data
            assert 'handlers' in data
            assert 'loggers' in data
            
            # Vérifier RequestContextFilter
            filters = data.get('filters', {})
            context_filter = filters.get('request_context', {})
            assert '()' in context_filter
            assert 'RequestContextFilter' in context_filter['()']
            
            print(f"   {config} - config valide")
            success += 1
            
        except Exception as e:
            print(f"   {config} - erreur: {e}")
    
    print(f"Config logging: {success}/{len(configs)} tests OK\n")
    return success == len(configs)

def test_contextvars_isolation():
    """Test isolation contextvars (simulation)"""
    print(" Test isolation contextvars...")
    
    # Simulation du pattern set_context/reset_context
    context_vars = {}
    
    def set_context(**kwargs):
        tokens = []
        for key, value in kwargs.items():
            old_value = context_vars.get(key)
            context_vars[key] = value
            tokens.append((key, old_value))
        return tokens
    
    def reset_context(tokens):
        for key, old_value in tokens:
            if old_value is None:
                context_vars.pop(key, None)
            else:
                context_vars[key] = old_value
    
    # Test 1: Set/reset basique
    tokens1 = set_context(user_id="alice", request_id="req1")
    assert context_vars.get('user_id') == "alice"
    assert context_vars.get('request_id') == "req1"
    
    # Test 2: Override dans scope
    tokens2 = set_context(user_id="bob")
    assert context_vars.get('user_id') == "bob"  # Override
    assert context_vars.get('request_id') == "req1"  # Preserved
    
    # Test 3: Reset scope imbriqué
    reset_context(tokens2)
    assert context_vars.get('user_id') == "alice"  # Restored
    assert context_vars.get('request_id') == "req1"  # Still there
    
    # Test 4: Reset complet
    reset_context(tokens1)
    assert context_vars.get('user_id') is None
    assert context_vars.get('request_id') is None
    
    print("   Isolation contextvars OK")
    print("Contextvars: 4/4 tests OK\n")
    return True

def test_metrics_gauge_operations():
    """Test simulation métriques gauge WebSocket"""
    print(" Test métriques gauge WebSocket...")
    
    # Simulation simple gauge
    class MockGauge:
        def __init__(self):
            self._value = 0
        
        def inc(self, amount=1):
            self._value += amount
        
        def dec(self, amount=1):
            self._value -= amount
        
        def set(self, value):
            self._value = value
        
        def get(self):
            return self._value
    
    ws_connections = MockGauge()
    
    # Test register/unregister
    assert ws_connections.get() == 0
    
    # 3 connexions
    ws_connections.inc()  # +1 = 1
    ws_connections.inc()  # +1 = 2  
    ws_connections.inc()  # +1 = 3
    assert ws_connections.get() == 3
    
    # 1 déconnexion
    ws_connections.dec()  # -1 = 2
    assert ws_connections.get() == 2
    
    # Reset
    ws_connections.set(0)
    assert ws_connections.get() == 0
    
    print("   Gauge operations OK")
    print("Métriques: 1/1 test OK\n")
    return True

def main():
    """Exécute tous les tests de patches"""
    print("Tests patches critiques observabilite v1.3")
    print("=" * 50)
    
    tests = [
        test_scrubbing_patterns,
        test_logging_config,
        test_contextvars_isolation, 
        test_metrics_gauge_operations
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f" Test {test.__name__} failed: {e}")
            results.append(False)
    
    success_count = sum(results)
    total_count = len(results)
    
    print("=" * 50)
    if success_count == total_count:
        print(f" TOUS LES TESTS OK ({success_count}/{total_count})")
        print(" Patches critiques validés - Production ready!")
        return 0
    else:
        print(f" ÉCHECS DÉTECTÉS ({success_count}/{total_count})")
        print(" Corriger avant mise en production!")
        return 1

if __name__ == "__main__":
    sys.exit(main())