-- 🧠 Initialisation TimescaleDB pour Jarvis - Mémoire Temporelle
-- Ce script crée les tables et hypertables pour la mémoire temporelle de Jarvis

-- Créer l'extension TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Table pour les métriques de mémoire en temps réel
CREATE TABLE IF NOT EXISTS memory_metrics (
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id TEXT NOT NULL,
    metric_type TEXT NOT NULL, -- 'access', 'consolidation', 'emotion', 'importance'
    metric_value DOUBLE PRECISION NOT NULL,
    metadata JSONB DEFAULT '{}',
    memory_id INTEGER,
    session_id TEXT
);

-- Convertir en hypertable (optimisé pour les séries temporelles)
SELECT create_hypertable('memory_metrics', 'time', if_not_exists => TRUE);

-- Table pour les logs d'activité Jarvis
CREATE TABLE IF NOT EXISTS jarvis_activity_logs (
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id TEXT NOT NULL,
    activity_type TEXT NOT NULL, -- 'conversation', 'action', 'consolidation', 'search'
    activity_data JSONB NOT NULL,
    duration_ms INTEGER DEFAULT 0,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    component TEXT -- 'limbic', 'prefrontal', 'hippocampus', 'backend'
);

-- Convertir en hypertable
SELECT create_hypertable('jarvis_activity_logs', 'time', if_not_exists => TRUE);

-- Table pour l'analyse émotionnelle temporelle
CREATE TABLE IF NOT EXISTS emotional_timeline (
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id TEXT NOT NULL,
    valence DOUBLE PRECISION NOT NULL, -- -1.0 à +1.0
    arousal DOUBLE PRECISION NOT NULL, -- 0.0 à 1.0
    detected_emotion TEXT NOT NULL,
    confidence DOUBLE PRECISION NOT NULL,
    trigger_content TEXT,
    memory_id INTEGER
);

-- Convertir en hypertable
SELECT create_hypertable('emotional_timeline', 'time', if_not_exists => TRUE);

-- Table pour les patterns comportementaux
CREATE TABLE IF NOT EXISTS behavior_patterns (
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id TEXT NOT NULL,
    pattern_type TEXT NOT NULL, -- 'routine', 'preference', 'habit'
    pattern_data JSONB NOT NULL,
    frequency_score DOUBLE PRECISION DEFAULT 0.0,
    confidence_score DOUBLE PRECISION DEFAULT 0.0,
    detected_by TEXT -- 'hippocampus', 'prefrontal', 'manual'
);

-- Convertir en hypertable
SELECT create_hypertable('behavior_patterns', 'time', if_not_exists => TRUE);

-- Indexes pour optimiser les requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_memory_metrics_user_type ON memory_metrics (user_id, metric_type, time DESC);
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_activity ON jarvis_activity_logs (user_id, activity_type, time DESC);
CREATE INDEX IF NOT EXISTS idx_emotional_timeline_user ON emotional_timeline (user_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_behavior_patterns_user ON behavior_patterns (user_id, pattern_type, time DESC);

-- Politiques de rétention automatique (nettoyage des anciennes données)
-- Garder les métriques de mémoire pendant 1 an
SELECT add_retention_policy('memory_metrics', INTERVAL '1 year', if_not_exists => TRUE);

-- Garder les logs d'activité pendant 6 mois
SELECT add_retention_policy('jarvis_activity_logs', INTERVAL '6 months', if_not_exists => TRUE);

-- Garder l'analyse émotionnelle pendant 2 ans (données précieuses)
SELECT add_retention_policy('emotional_timeline', INTERVAL '2 years', if_not_exists => TRUE);

-- Garder les patterns comportementaux pendant 3 ans
SELECT add_retention_policy('behavior_patterns', INTERVAL '3 years', if_not_exists => TRUE);

-- Vues matérialisées pour analyses rapides
CREATE MATERIALIZED VIEW IF NOT EXISTS daily_emotional_summary AS
SELECT 
    time_bucket('1 day', time) AS day,
    user_id,
    AVG(valence) AS avg_valence,
    AVG(arousal) AS avg_arousal,
    MODE() WITHIN GROUP (ORDER BY detected_emotion) AS dominant_emotion,
    COUNT(*) AS total_interactions,
    AVG(confidence) AS avg_confidence
FROM emotional_timeline
GROUP BY day, user_id
ORDER BY day DESC;

-- Rafraîchir automatiquement la vue quotidiennement
SELECT add_continuous_aggregate_policy('daily_emotional_summary',
    start_offset => INTERVAL '2 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE);

-- Vue pour les patterns de consolidation
CREATE MATERIALIZED VIEW IF NOT EXISTS consolidation_patterns AS
SELECT 
    time_bucket('1 hour', time) AS hour,
    user_id,
    COUNT(*) FILTER (WHERE activity_type = 'consolidation') AS consolidations,
    AVG(duration_ms) FILTER (WHERE activity_type = 'consolidation') AS avg_consolidation_time,
    COUNT(*) FILTER (WHERE activity_type = 'search') AS searches,
    COUNT(*) FILTER (WHERE success = FALSE) AS failures
FROM jarvis_activity_logs
GROUP BY hour, user_id
ORDER BY hour DESC;

-- Fonctions utilitaires pour Jarvis

-- Fonction pour obtenir le profil émotionnel récent d'un utilisateur
CREATE OR REPLACE FUNCTION get_recent_emotional_profile(p_user_id TEXT, p_hours INTEGER DEFAULT 24)
RETURNS TABLE(
    avg_valence DOUBLE PRECISION,
    avg_arousal DOUBLE PRECISION,
    dominant_emotion TEXT,
    emotion_stability DOUBLE PRECISION,
    total_interactions BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        AVG(et.valence) as avg_valence,
        AVG(et.arousal) as avg_arousal,
        MODE() WITHIN GROUP (ORDER BY et.detected_emotion) as dominant_emotion,
        1.0 - STDDEV(et.valence) as emotion_stability, -- Plus stable = moins de variation
        COUNT(*) as total_interactions
    FROM emotional_timeline et
    WHERE et.user_id = p_user_id 
      AND et.time >= NOW() - (p_hours || ' hours')::INTERVAL;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour détecter les patterns comportementaux
CREATE OR REPLACE FUNCTION detect_behavior_pattern(
    p_user_id TEXT,
    p_activity_type TEXT,
    p_time_window_hours INTEGER DEFAULT 168 -- 1 semaine par défaut
) RETURNS TABLE(
    pattern_description TEXT,
    frequency DOUBLE PRECISION,
    confidence DOUBLE PRECISION,
    last_occurrence TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        CASE 
            WHEN COUNT(*) >= 5 AND EXTRACT(dow FROM time) IN (1,2,3,4,5) THEN 'Routine hebdomadaire'
            WHEN COUNT(*) >= 3 AND EXTRACT(hour FROM time) BETWEEN 8 AND 10 THEN 'Routine matinale'
            WHEN COUNT(*) >= 3 AND EXTRACT(hour FROM time) BETWEEN 18 AND 22 THEN 'Routine soirée'
            ELSE 'Pattern détecté'
        END as pattern_description,
        (COUNT(*)::DOUBLE PRECISION / p_time_window_hours * 24) as frequency,
        LEAST(COUNT(*)::DOUBLE PRECISION / 10.0, 1.0) as confidence,
        MAX(time) as last_occurrence
    FROM jarvis_activity_logs
    WHERE user_id = p_user_id 
      AND activity_type = p_activity_type
      AND time >= NOW() - (p_time_window_hours || ' hours')::INTERVAL
      AND success = TRUE
    GROUP BY 
        EXTRACT(dow FROM time),
        EXTRACT(hour FROM time)
    HAVING COUNT(*) >= 2;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour nettoyer les données anciennes manuellement si besoin
CREATE OR REPLACE FUNCTION cleanup_old_timeseries_data(p_retention_days INTEGER DEFAULT 365)
RETURNS TEXT AS $$
DECLARE
    deleted_count INTEGER;
    result_text TEXT;
BEGIN
    -- Nettoyer les métriques anciennes
    DELETE FROM memory_metrics WHERE time < NOW() - (p_retention_days || ' days')::INTERVAL;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    result_text := 'Deleted ' || deleted_count || ' old memory metrics. ';
    
    -- Nettoyer les logs anciens
    DELETE FROM jarvis_activity_logs WHERE time < NOW() - ((p_retention_days/2) || ' days')::INTERVAL;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    result_text := result_text || 'Deleted ' || deleted_count || ' old activity logs.';
    
    RETURN result_text;
END;
$$ LANGUAGE plpgsql;

-- Insérer des données d'exemple pour tester
INSERT INTO memory_metrics (user_id, metric_type, metric_value, metadata) VALUES
('enzo', 'access_frequency', 5.2, '{"memory_type": "episodic"}'),
('enzo', 'consolidation_score', 0.75, '{"trigger": "high_emotion"}'),
('enzo', 'emotional_weight', 0.8, '{"detected_emotion": "satisfaction"}');

INSERT INTO jarvis_activity_logs (user_id, activity_type, activity_data, duration_ms, component) VALUES
('enzo', 'conversation', '{"message": "Test initialization", "response_length": 150}', 250, 'backend'),
('enzo', 'consolidation', '{"memories_processed": 5, "consolidated": 2}', 1500, 'hippocampus'),
('enzo', 'search', '{"query": "test", "results_found": 3}', 85, 'prefrontal');

INSERT INTO emotional_timeline (user_id, valence, arousal, detected_emotion, confidence, trigger_content) VALUES
('enzo', 0.6, 0.4, 'satisfaction', 0.85, 'Test emotional analysis'),
('enzo', -0.2, 0.7, 'stress', 0.72, 'Configuration setup'),
('enzo', 0.8, 0.6, 'enthousiasme', 0.91, 'System working perfectly');

-- Log d'initialisation
INSERT INTO jarvis_activity_logs (user_id, activity_type, activity_data, component) VALUES
('system', 'initialization', '{"component": "timescaledb", "status": "success", "version": "2.0"}', 'timescale');

-- Message de succès
DO $$
BEGIN
    RAISE NOTICE '🧠 TimescaleDB pour Jarvis initialisé avec succès!';
    RAISE NOTICE '📊 Tables créées: memory_metrics, jarvis_activity_logs, emotional_timeline, behavior_patterns';
    RAISE NOTICE '⏰ Politiques de rétention configurées';
    RAISE NOTICE '🔍 Vues matérialisées et fonctions utilitaires créées';
END $$;