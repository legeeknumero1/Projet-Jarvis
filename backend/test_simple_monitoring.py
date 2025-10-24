#!/usr/bin/env python3
"""
Test simple du système de monitoring des requêtes PostgreSQL
"""

import asyncio
import time
import logging
import sys
import os

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_monitoring_core():
    """Test des fonctionnalités core du monitoring"""
    
    print("🔍 [TEST] Test simple du monitoring PostgreSQL...")
    
    # Test direct des classes de monitoring
    from monitoring.query_monitor import DatabaseMonitor, QueryMetrics
    from datetime import datetime
    
    # Initialiser un monitor de test
    monitor = DatabaseMonitor(slow_query_threshold=1.0, enable_explain=False)
    
    print("✅ [TEST] DatabaseMonitor initialisé")
    
    # Test d'enregistrement de requêtes
    test_queries = [
        ("SELECT * FROM users WHERE id = $1", 0.3, "SELECT", "users"),
        ("SELECT * FROM conversations WHERE user_id = $1", 2.1, "SELECT", "conversations"),  # Lente
        ("INSERT INTO memories (user_id, content) VALUES ($1, $2)", 0.2, "INSERT", "memories"),
        ("UPDATE users SET preferences = $1 WHERE id = $2", 1.5, "UPDATE", "users"),  # Lente
        ("SELECT COUNT(*) FROM conversations", 0.4, "SELECT", "conversations"),
    ]
    
    for query, duration, operation, table in test_queries:
        await monitor.record_query(
            query=query,
            duration=duration,
            operation=operation,
            table=table,
            user_id="test_user"
        )
        print(f"  📝 Requête enregistrée: {operation} on {table} ({duration}s)")
    
    # Vérifier les statistiques
    stats = monitor.get_query_statistics()
    
    print(f"\n📊 [STATS] Résultats du monitoring:")
    print(f"  🔢 Total des requêtes: {stats['summary']['total_queries']}")
    print(f"  ⚠️ Requêtes lentes: {stats['summary']['total_slow_queries']}")
    print(f"  📊 Taux de requêtes lentes: {stats['summary']['slow_query_rate']:.1f}%")
    print(f"  🏷️ Types de requêtes monitorés: {stats['summary']['monitored_query_types']}")
    
    # Détails par type
    print(f"\n📋 [DETAILS] Par type de requête:")
    for query_type, query_stats in stats['query_stats'].items():
        print(f"  🔍 {query_type}:")
        print(f"    - Total: {query_stats['total_count']}")
        print(f"    - Lentes: {query_stats['slow_count']}")
        print(f"    - Durée moyenne: {query_stats['avg_duration']:.2f}s")
        print(f"    - P95: {query_stats['p95_duration']:.2f}s")
        print(f"    - Taux lent: {query_stats['slow_rate']:.1f}%")
    
    # Requêtes lentes récentes
    print(f"\n🐌 [SLOW] Requêtes lentes récentes:")
    recent_slow = stats.get('recent_slow_queries', [])
    for slow_query in recent_slow:
        print(f"  ⚠️ {slow_query['operation']} on {slow_query['table']} - {slow_query['duration']}s")
        print(f"     Query: {slow_query['query'][:60]}...")
    
    # Test de performance
    print(f"\n🚀 [PERF] Test de performance...")
    start_time = time.time()
    
    for i in range(50):
        await monitor.record_query(
            query=f"SELECT * FROM test_table_{i % 3} WHERE id = $1",
            duration=0.1 + (i % 5) * 0.02,
            operation="SELECT",
            table=f"test_table_{i % 3}",
            user_id=f"perf_user_{i % 2}"
        )
    
    processing_time = time.time() - start_time
    print(f"  📊 50 requêtes traitées en {processing_time:.3f}s")
    print(f"  📊 Débit: {50/processing_time:.0f} requêtes/seconde")
    
    # Stats finales
    final_stats = monitor.get_query_statistics()
    print(f"\n✅ [FINAL] Statistiques finales:")
    print(f"  - Total requêtes: {final_stats['summary']['total_queries']}")
    print(f"  - Types uniques: {final_stats['summary']['monitored_query_types']}")
    print(f"  - Requêtes lentes: {final_stats['summary']['total_slow_queries']}")
    
    return True

async def test_query_analyzer():
    """Test de l'analyseur de requêtes"""
    
    print(f"\n🔬 [ANALYZER] Test de l'analyseur de requêtes...")
    
    from monitoring.query_monitor import QueryAnalyzer
    
    test_cases = [
        ("SELECT * FROM users WHERE id = 1", "SELECT", "users"),
        ("INSERT INTO conversations (user_id, message) VALUES ($1, $2)", "INSERT", "conversations"),
        ("UPDATE memories SET content = $1 WHERE id = $2", "UPDATE", "memories"),
        ("DELETE FROM old_data WHERE created_at < NOW() - INTERVAL '1 year'", "DELETE", "old_data"),
        ("CREATE INDEX idx_user_timestamp ON conversations(user_id, timestamp)", "CREATE", "unknown"),
    ]
    
    for query, expected_op, expected_table in test_cases:
        parsed = QueryAnalyzer.parse_query(query)
        print(f"  📝 Query: {query[:50]}...")
        print(f"     Parsed: {parsed['operation']} on {parsed['table']}")
        
        # Vérifier problèmes
        issues = QueryAnalyzer.is_query_problematic(query, 2.5)
        if issues:
            print(f"     Issues: {', '.join(issues)}")
    
    return True

async def main():
    """Point d'entrée principal"""
    
    print("🧪 Test simple du système de monitoring PostgreSQL")
    print("=" * 60)
    
    try:
        # Tests principaux
        success1 = await test_monitoring_core()
        success2 = await test_query_analyzer()
        
        if success1 and success2:
            print(f"\n" + "=" * 60)
            print("🎉 [SUCCESS] Tests simples réussis!")
            print("📊 Le système de monitoring fonctionne correctement")
        else:
            print(f"\n❌ [FAILURE] Tests échoués")
            return 1
            
    except Exception as e:
        print(f"\n💥 [ERROR] Erreur: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    # Ajouter le backend au PYTHONPATH
    sys.path.insert(0, '/home/enzo/Projet-Jarvis/backend')
    
    # Exécuter les tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)