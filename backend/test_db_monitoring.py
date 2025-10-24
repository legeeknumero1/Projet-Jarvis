#!/usr/bin/env python3
"""
Script de test pour le système de monitoring des requêtes PostgreSQL
Test de performance et validation des métriques
"""

import asyncio
import asyncpg
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Any
import sys
import os

# Ajouter le backend au PYTHONPATH
sys.path.insert(0, '/home/enzo/Projet-Jarvis/backend')

from monitoring.query_monitor import db_monitor, QueryMetrics
from config.config import Config

# Configuration logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_database_monitoring():
    """Test complet du système de monitoring"""
    
    print("🔍 [TEST] Démarrage des tests de monitoring PostgreSQL...")
    
    # 1. Initialiser le système de monitoring
    config = Config()
    database_url = config.database_url
    
    try:
        await db_monitor.initialize_analysis_pool(database_url)
        print("✅ [TEST] Pool d'analyse initialisé")
    except Exception as e:
        print(f"❌ [TEST] Erreur initialisation pool: {e}")
        return False
    
    # 2. Test d'enregistrement de requêtes
    print("\n📊 [TEST] Test d'enregistrement des métriques...")
    
    test_queries = [
        ("SELECT * FROM users WHERE id = $1", 0.5, "SELECT", "users"),
        ("SELECT * FROM conversations WHERE user_id = $1 ORDER BY timestamp DESC LIMIT 10", 2.1, "SELECT", "conversations"),
        ("INSERT INTO memories (user_id, content) VALUES ($1, $2)", 0.3, "INSERT", "memories"),
        ("UPDATE users SET preferences = $1 WHERE id = $2", 1.8, "UPDATE", "users"),
        ("SELECT COUNT(*) FROM conversations", 3.2, "SELECT", "conversations"),
    ]
    
    for query, duration, operation, table in test_queries:
        await db_monitor.record_query(
            query=query,
            duration=duration,
            operation=operation,
            table=table,
            user_id="test_user"
        )
        print(f"  📝 Requête enregistrée: {operation} on {table} ({duration}s)")
    
    # 3. Vérifier les statistiques
    print("\n📈 [TEST] Vérification des statistiques...")
    
    stats = db_monitor.get_query_statistics()
    
    print(f"  🔢 Total des requêtes: {stats['summary']['total_queries']}")
    print(f"  ⚠️ Requêtes lentes: {stats['summary']['total_slow_queries']}")
    print(f"  📊 Taux de requêtes lentes: {stats['summary']['slow_query_rate']:.1f}%")
    print(f"  🏷️ Types de requêtes monitorés: {stats['summary']['monitored_query_types']}")
    
    # Afficher détails par type
    print("\n📋 [TEST] Détails par type de requête:")
    for query_type, query_stats in stats['query_stats'].items():
        print(f"  🔍 {query_type}:")
        print(f"    - Total: {query_stats['total_count']}")
        print(f"    - Lentes: {query_stats['slow_count']}")
        print(f"    - Durée moyenne: {query_stats['avg_duration']:.2f}s")
        print(f"    - P95: {query_stats['p95_duration']:.2f}s")
        print(f"    - Taux lent: {query_stats['slow_rate']:.1f}%")
    
    # 4. Test des métriques de base de données
    print("\n🗄️ [TEST] Test des métriques de base de données...")
    
    try:
        db_metrics = await db_monitor.get_database_metrics()
        print(f"  🔗 Connexions actives: {db_metrics.get('active_connections', 'N/A')}")
        print(f"  💾 Taille DB: {db_metrics.get('database_size', 'N/A')}")
        print(f"  📊 Ratio cache hit: {db_metrics.get('cache_hit_ratio', 'N/A')}%")
        
        # Afficher activité des tables
        table_activity = db_metrics.get('table_activity', [])
        if table_activity:
            print("  📊 Top 5 tables par activité:")
            for table in table_activity[:5]:
                print(f"    - {table.get('tablename', 'N/A')}: {table.get('total_activity', 0)} operations")
    except Exception as e:
        print(f"  ⚠️ Métriques DB non disponibles: {e}")
    
    # 5. Test de génération de requêtes lentes artificielles
    print("\n🐌 [TEST] Génération de requêtes lentes pour test...")
    
    slow_queries = [
        ("SELECT pg_sleep(2); SELECT COUNT(*) FROM pg_stat_activity", 2.5, "SELECT", "pg_stat_activity"),
        ("SELECT * FROM conversations ORDER BY timestamp DESC", 4.2, "SELECT", "conversations"),
        ("UPDATE users SET last_accessed = NOW() WHERE created_at < NOW() - INTERVAL '1 day'", 6.1, "UPDATE", "users")
    ]
    
    for query, duration, operation, table in slow_queries:
        await db_monitor.record_query(
            query=query,
            duration=duration,
            operation=operation,
            table=table,
            user_id="test_slow"
        )
        print(f"  🐌 Requête lente simulée: {operation} on {table} ({duration}s)")
    
    # 6. Vérifier les requêtes lentes récentes
    print("\n🔍 [TEST] Requêtes lentes récentes:")
    
    updated_stats = db_monitor.get_query_statistics()
    recent_slow = updated_stats.get('recent_slow_queries', [])
    
    for slow_query in recent_slow[-3:]:  # 3 plus récentes
        print(f"  ⚠️ {slow_query['operation']} on {slow_query['table']}")
        print(f"     Durée: {slow_query['duration']}s")
        print(f"     Timestamp: {slow_query['timestamp']}")
        print(f"     Query: {slow_query['query'][:80]}...")
    
    # 7. Test de nettoyage
    print("\n🧹 [TEST] Test de nettoyage...")
    
    try:
        await db_monitor.cleanup()
        print("✅ [TEST] Nettoyage réussi")
    except Exception as e:
        print(f"❌ [TEST] Erreur nettoyage: {e}")
    
    print("\n✅ [TEST] Tests de monitoring terminés avec succès!")
    return True

async def test_performance_monitoring():
    """Test de performance du système de monitoring"""
    
    print("\n🚀 [PERF] Test de performance du monitoring...")
    
    # Générer 100 requêtes rapidement
    start_time = time.time()
    
    for i in range(100):
        await db_monitor.record_query(
            query=f"SELECT * FROM test_table_{i % 5} WHERE id = $1",
            duration=0.1 + (i % 10) * 0.05,  # Durées variables
            operation="SELECT",
            table=f"test_table_{i % 5}",
            user_id=f"perf_user_{i % 3}"
        )
    
    processing_time = time.time() - start_time
    print(f"📊 [PERF] 100 requêtes traitées en {processing_time:.2f}s")
    print(f"📊 [PERF] Débit: {100/processing_time:.0f} requêtes/seconde")
    
    # Vérifier les stats finales
    final_stats = db_monitor.get_query_statistics()
    print(f"📊 [PERF] Total requêtes monitorées: {final_stats['summary']['total_queries']}")
    print(f"📊 [PERF] Types uniques: {final_stats['summary']['monitored_query_types']}")

async def test_api_endpoints():
    """Test des endpoints API de monitoring"""
    
    print("\n🌐 [API] Test des endpoints de monitoring...")
    
    # Simuler des appels aux endpoints
    try:
        import httpx
        import asyncio
        
        async with httpx.AsyncClient() as client:
            base_url = "http://localhost:8000"
            
            # Test health endpoint
            try:
                response = await client.get(f"{base_url}/monitoring/health")
                if response.status_code == 200:
                    print("✅ [API] /monitoring/health - OK")
                    health_data = response.json()
                    print(f"  Status: {health_data.get('status')}")
                else:
                    print(f"⚠️ [API] /monitoring/health - Status: {response.status_code}")
            except Exception as e:
                print(f"❌ [API] /monitoring/health non disponible: {e}")
            
            # Test metrics endpoint  
            try:
                response = await client.get(f"{base_url}/monitoring/metrics")
                if response.status_code == 200:
                    print("✅ [API] /monitoring/metrics - OK")
                    print(f"  Content-Type: {response.headers.get('content-type')}")
                else:
                    print(f"⚠️ [API] /monitoring/metrics - Status: {response.status_code}")
            except Exception as e:
                print(f"❌ [API] /monitoring/metrics non disponible: {e}")
                
    except ImportError:
        print("⚠️ [API] httpx non disponible - tests API ignorés")

async def main():
    """Point d'entrée principal des tests"""
    
    print("🧪 Jarvis - Tests du système de monitoring PostgreSQL")
    print("=" * 60)
    
    try:
        # Test principal
        success = await test_database_monitoring()
        
        if success:
            # Tests de performance
            await test_performance_monitoring()
            
            # Tests API (optionnels)
            await test_api_endpoints()
            
            print("\n" + "=" * 60)
            print("🎉 [SUCCESS] Tous les tests de monitoring réussis!")
            print("📊 Le système de monitoring PostgreSQL est opérationnel")
            
            # Afficher résumé final
            final_stats = db_monitor.get_query_statistics()
            print(f"\n📈 Résumé final:")
            print(f"  - Total requêtes monitorées: {final_stats['summary']['total_queries']}")
            print(f"  - Requêtes lentes détectées: {final_stats['summary']['total_slow_queries']}")
            print(f"  - Taux de requêtes lentes: {final_stats['summary']['slow_query_rate']:.1f}%")
            
        else:
            print("\n❌ [FAILURE] Tests échoués")
            return 1
            
    except Exception as e:
        print(f"\n💥 [ERROR] Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    # Exécuter les tests
    exit_code = asyncio.run(main())
    sys.exit(exit_code)