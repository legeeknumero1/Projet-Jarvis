"""
Endpoints API pour le monitoring des performances de base de données
Interface REST pour accéder aux métriques de performance en temps réel
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
from auth.dependencies import get_current_user, get_optional_current_user
from auth.models import User
from monitoring.query_monitor import db_monitor
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import logging

router = APIRouter(prefix="/monitoring", tags=["monitoring"])
logger = logging.getLogger(__name__)

@router.get("/health")
async def health_check():
    """Health check pour le système de monitoring"""
    try:
        # Vérifier que le monitor est opérationnel
        stats = db_monitor.get_query_statistics()
        db_metrics = await db_monitor.get_database_metrics()
        
        return {
            "status": "healthy",
            "monitoring": {
                "active": True,
                "slow_query_threshold": db_monitor.slow_query_threshold,
                "total_queries_monitored": stats["summary"]["total_queries"]
            },
            "database": {
                "active_connections": db_metrics.get("active_connections", 0),
                "cache_hit_ratio": db_metrics.get("cache_hit_ratio", 0)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Monitoring system unhealthy")

@router.get("/metrics")
async def get_prometheus_metrics():
    """Endpoint pour métriques Prometheus"""
    try:
        return PlainTextResponse(
            generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    except Exception as e:
        logger.error(f"Failed to generate Prometheus metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate metrics")

@router.get("/query-stats")
async def get_query_statistics(
    current_user: User = Depends(get_current_user)
):
    """Obtenir les statistiques détaillées des requêtes"""
    try:
        stats = db_monitor.get_query_statistics()
        db_metrics = await db_monitor.get_database_metrics()
        
        return {
            "query_performance": stats,
            "database_metrics": db_metrics,
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get query statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve statistics")

@router.get("/slow-queries")
async def get_slow_queries(
    limit: int = Query(default=50, ge=1, le=200),
    min_duration: float = Query(default=1.0, ge=0.1),
    table_filter: Optional[str] = Query(default=None),
    operation_filter: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user)
):
    """Obtenir la liste des requêtes lentes récentes"""
    try:
        stats = db_monitor.get_query_statistics()
        slow_queries = stats.get("recent_slow_queries", [])
        
        # Filtrer selon les critères
        filtered_queries = []
        for query in slow_queries:
            if query["duration"] < min_duration:
                continue
            if table_filter and table_filter.lower() not in query["table"].lower():
                continue
            if operation_filter and operation_filter.upper() != query["operation"].upper():
                continue
            filtered_queries.append(query)
        
        # Limiter le nombre de résultats
        filtered_queries = filtered_queries[-limit:]
        
        return {
            "slow_queries": filtered_queries,
            "filters": {
                "min_duration": min_duration,
                "table_filter": table_filter,
                "operation_filter": operation_filter,
                "limit": limit
            },
            "total_matching": len(filtered_queries),
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get slow queries: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve slow queries")

@router.get("/performance-summary")
async def get_performance_summary(
    current_user: User = Depends(get_current_user)
):
    """Résumé des performances pour tableau de bord"""
    try:
        stats = db_monitor.get_query_statistics()
        db_metrics = await db_monitor.get_database_metrics()
        
        summary = stats["summary"]
        
        # Identifier les requêtes les plus problématiques
        problematic_queries = []
        for query_key, query_stats in stats["query_stats"].items():
            if query_stats["slow_rate"] > 10:  # Plus de 10% de requêtes lentes
                problematic_queries.append({
                    "query_type": query_key,
                    "slow_rate": query_stats["slow_rate"],
                    "avg_duration": query_stats["avg_duration"],
                    "p95_duration": query_stats["p95_duration"],
                    "total_count": query_stats["total_count"]
                })
        
        # Trier par taux de requêtes lentes
        problematic_queries.sort(key=lambda x: x["slow_rate"], reverse=True)
        
        # Calculer les tendances (si on avait des données historiques)
        performance_grade = "A"  # A, B, C, D, F
        if summary["slow_query_rate"] > 20:
            performance_grade = "F"
        elif summary["slow_query_rate"] > 15:
            performance_grade = "D"
        elif summary["slow_query_rate"] > 10:
            performance_grade = "C"
        elif summary["slow_query_rate"] > 5:
            performance_grade = "B"
        
        return {
            "performance_grade": performance_grade,
            "summary": {
                "total_queries": summary["total_queries"],
                "slow_query_rate": round(summary["slow_query_rate"], 2),
                "monitored_types": summary["monitored_query_types"]
            },
            "database": {
                "active_connections": db_metrics.get("active_connections", 0),
                "cache_hit_ratio": round(db_metrics.get("cache_hit_ratio", 0), 2),
                "database_size": db_metrics.get("database_size", "Unknown")
            },
            "problematic_queries": problematic_queries[:5],  # Top 5
            "recommendations": _generate_recommendations(stats, db_metrics),
            "last_updated": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to generate performance summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate summary")

@router.get("/query-analysis/{operation}/{table}")
async def analyze_specific_query(
    operation: str,
    table: str,
    current_user: User = Depends(get_current_user)
):
    """Analyser en détail un type de requête spécifique"""
    try:
        stats = db_monitor.get_query_statistics()
        query_key = f"{operation.upper()}:{table.lower()}"
        
        if query_key not in stats["query_stats"]:
            raise HTTPException(
                status_code=404, 
                detail=f"No data found for {operation} on {table}"
            )
        
        query_stats = stats["query_stats"][query_key]
        
        # Analyser les requêtes récentes de ce type
        recent_queries = [
            q for q in stats["recent_slow_queries"]
            if q["operation"].upper() == operation.upper() 
            and q["table"].lower() == table.lower()
        ]
        
        # Recommandations spécifiques
        recommendations = []
        
        if query_stats["slow_rate"] > 20:
            recommendations.append("Consider adding indexes to improve query performance")
        
        if query_stats["p95_duration"] > 5.0:
            recommendations.append("Investigate query execution plan for optimization opportunities")
        
        if operation.upper() == "SELECT" and query_stats["avg_duration"] > 1.0:
            recommendations.append("Consider adding LIMIT clauses or pagination")
        
        return {
            "query_type": {
                "operation": operation.upper(),
                "table": table.lower()
            },
            "statistics": query_stats,
            "recent_slow_queries": recent_queries[-10:],  # 10 plus récentes
            "recommendations": recommendations,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze query {operation}:{table}: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@router.post("/reset-stats")
async def reset_monitoring_stats(
    current_user: User = Depends(get_current_user)
):
    """Réinitialiser les statistiques de monitoring (admin seulement)"""
    # Note: Dans une vraie application, on vérifierait les permissions admin
    try:
        # Réinitialiser les statistiques
        db_monitor.query_stats.clear()
        db_monitor.recent_slow_queries.clear()
        
        logger.info(f"Monitoring stats reset by user {current_user.username}")
        
        return {
            "message": "Monitoring statistics have been reset",
            "reset_by": current_user.username,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to reset stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to reset statistics")

@router.get("/database-insights")
async def get_database_insights(
    current_user: User = Depends(get_current_user)
):
    """Obtenir des insights avancés sur l'utilisation de la base de données"""
    try:
        db_metrics = await db_monitor.get_database_metrics()
        stats = db_monitor.get_query_statistics()
        
        # Analyser l'activité par table
        table_activity = db_metrics.get("table_activity", [])
        most_active_tables = sorted(
            table_activity, 
            key=lambda x: x.get("total_activity", 0), 
            reverse=True
        )[:5]
        
        # Identifier les tables sans index utilisés
        tables_needing_indexes = [
            table for table in table_activity
            if table.get("seq_scan", 0) > table.get("idx_scan", 0)
            and table.get("seq_tup_read", 0) > 1000
        ]
        
        # Calculer l'efficacité du cache
        cache_efficiency = "Good"
        cache_ratio = db_metrics.get("cache_hit_ratio", 0)
        if cache_ratio < 90:
            cache_efficiency = "Poor"
        elif cache_ratio < 95:
            cache_efficiency = "Fair"
        elif cache_ratio < 98:
            cache_efficiency = "Good"
        else:
            cache_efficiency = "Excellent"
        
        return {
            "database_health": {
                "size": db_metrics.get("database_size", "Unknown"),
                "active_connections": db_metrics.get("active_connections", 0),
                "cache_hit_ratio": cache_ratio,
                "cache_efficiency": cache_efficiency
            },
            "table_insights": {
                "most_active": most_active_tables,
                "needing_indexes": tables_needing_indexes[:5]
            },
            "query_patterns": {
                "total_monitored": stats["summary"]["total_queries"],
                "slow_query_rate": stats["summary"]["slow_query_rate"],
                "unique_query_types": stats["summary"]["monitored_query_types"]
            },
            "recommendations": _generate_database_recommendations(
                db_metrics, stats, cache_ratio
            ),
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to generate database insights: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate insights")

def _generate_recommendations(stats: Dict, db_metrics: Dict) -> List[str]:
    """Générer des recommandations basées sur les métriques"""
    recommendations = []
    summary = stats["summary"]
    
    # Recommandations basées sur le taux de requêtes lentes
    if summary["slow_query_rate"] > 15:
        recommendations.append(
            "High slow query rate detected. Consider query optimization and indexing."
        )
    
    if summary["slow_query_rate"] > 25:
        recommendations.append(
            "Critical: Very high slow query rate. Immediate investigation required."
        )
    
    # Recommandations basées sur les connexions
    active_connections = db_metrics.get("active_connections", 0)
    if active_connections > 80:
        recommendations.append(
            "High number of active connections. Consider connection pooling optimization."
        )
    
    # Recommandations basées sur le cache
    cache_ratio = db_metrics.get("cache_hit_ratio", 100)
    if cache_ratio < 90:
        recommendations.append(
            "Low cache hit ratio. Consider increasing shared_buffers or investigating query patterns."
        )
    
    # Recommandations générales
    if summary["total_queries"] > 10000:
        recommendations.append(
            "High query volume detected. Consider implementing query result caching."
        )
    
    return recommendations

def _generate_database_recommendations(
    db_metrics: Dict, 
    stats: Dict, 
    cache_ratio: float
) -> List[str]:
    """Générer des recommandations spécifiques à la base de données"""
    recommendations = []
    
    if cache_ratio < 95:
        recommendations.append(
            f"Cache hit ratio is {cache_ratio:.1f}%. Consider increasing PostgreSQL shared_buffers."
        )
    
    table_activity = db_metrics.get("table_activity", [])
    for table in table_activity:
        seq_scans = table.get("seq_scan", 0)
        idx_scans = table.get("idx_scan", 0)
        
        if seq_scans > idx_scans and seq_scans > 100:
            recommendations.append(
                f"Table '{table['tablename']}' has {seq_scans} sequential scans. Consider adding indexes."
            )
    
    if stats["summary"]["slow_query_rate"] > 10:
        recommendations.append(
            "Enable pg_stat_statements extension for detailed query analysis."
        )
    
    return recommendations[:5]  # Limiter à 5 recommandations