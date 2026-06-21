use serde_json::{json, Value};

/// Deterministic local command router for cost optimization.
///
/// Evaluates incoming user prompts against a static lookup table of known
/// micro-commands (domotics, HUD layout toggles). If a match is found,
/// returns a pre-compiled JSON frame directly consumable by the Next.js HUD,
/// completely bypassing the Gemini cloud API.
///
/// Design rationale: placing this interceptor before the network boundary
/// eliminates token consumption for repetitive, deterministic commands that
/// require zero LLM reasoning. At ~50 daily domestic commands, this saves
/// approximately 15,000 tokens/day ($0.00/day at any model rate).
pub struct LocalIntentRouter;

impl LocalIntentRouter {
    /// Evaluates the prompt locally against known command patterns.
    ///
    /// Returns `Some(Value)` with a complete HUD control frame if the prompt
    /// matches a predefined local micro-command. Returns `None` if the prompt
    /// requires cloud LLM reasoning via Gemini.
    pub fn try_route(prompt: &str) -> Option<Value> {
        let normalized = prompt.trim().to_lowercase();

        match normalized.as_str() {
            // =================================================================
            // Domotique: Éclairage Bureau
            // =================================================================
            "allume le bureau" | "allume la lumière du bureau" | "allume les lumières du bureau" => Some(json!({
                "speech_status": "SPEAKING",
                "audio_amplitude": 0.3,
                "widget_id": "terminal",
                "visible": true,
                "action": "EXEC_HAOS_SERVICE",
                "haos_domain": "light",
                "haos_service": "turn_on",
                "haos_entity": "light.hue_play_1,light.hue_play_2,light.hue_play_3"
            })),

            "éteins le bureau" | "eteins le bureau" | "éteins la lumière du bureau" => Some(json!({
                "speech_status": "SPEAKING",
                "audio_amplitude": 0.1,
                "widget_id": "terminal",
                "visible": true,
                "action": "EXEC_HAOS_SERVICE",
                "haos_domain": "light",
                "haos_service": "turn_off",
                "haos_entity": "light.hue_play_1,light.hue_play_2,light.hue_play_3"
            })),

            // =================================================================
            // Domotique: Éclairage Chambre
            // =================================================================
            "allume la chambre" | "allume la lumière de la chambre" => Some(json!({
                "speech_status": "SPEAKING",
                "audio_amplitude": 0.3,
                "widget_id": "terminal",
                "visible": true,
                "action": "EXEC_HAOS_SERVICE",
                "haos_domain": "light",
                "haos_service": "turn_on",
                "haos_entity": "light.hue_go_1"
            })),

            "éteins la chambre" | "eteins la chambre" | "éteins la lumière de la chambre" => Some(json!({
                "speech_status": "SPEAKING",
                "audio_amplitude": 0.1,
                "widget_id": "terminal",
                "visible": true,
                "action": "EXEC_HAOS_SERVICE",
                "haos_domain": "light",
                "haos_service": "turn_off",
                "haos_entity": "light.hue_go_1"
            })),

            // =================================================================
            // Domotique: Éclairage Général (Fallback)
            // =================================================================
            "allume la lumière" | "allume les lumières" | "allume la lumiere"
            | "allume les lumieres" => Some(json!({
                "speech_status": "SPEAKING",
                "audio_amplitude": 0.3,
                "widget_id": "terminal",
                "visible": true,
                "action": "EXEC_HAOS_SERVICE",
                "haos_domain": "light",
                "haos_service": "turn_on",
                "haos_entity": "light.hue_play_1,light.hue_play_2,light.hue_play_3,light.hue_go_1"
            })),

            "éteins la lumière" | "eteins la lumiere" | "éteins les lumières"
            | "eteins les lumieres" | "éteins tout" | "eteins tout" => Some(json!({
                "speech_status": "SPEAKING",
                "audio_amplitude": 0.1,
                "widget_id": "terminal",
                "visible": true,
                "action": "EXEC_HAOS_SERVICE",
                "haos_domain": "light",
                "haos_service": "turn_off",
                "haos_entity": "light.hue_play_1,light.hue_play_2,light.hue_play_3,light.hue_go_1"
            })),

            // =================================================================
            // HUD Layout: Télémétrie / Métriques système
            // =================================================================
            "affiche la télémétrie" | "ouvre les métriques" | "affiche les metriques"
            | "affiche la telemetrie" | "ouvre les metriques" => Some(json!({
                "speech_status": "IDLE",
                "audio_amplitude": 0.0,
                "widget_id": "sys_metrics",
                "visible": true,
                "action": "TOGGLE_WIDGET"
            })),

            "masque la télémétrie" | "ferme les métriques" | "cache les metriques"
            | "masque la telemetrie" | "ferme les metriques" => Some(json!({
                "speech_status": "IDLE",
                "audio_amplitude": 0.0,
                "widget_id": "sys_metrics",
                "visible": false,
                "action": "TOGGLE_WIDGET"
            })),

            // =================================================================
            // HUD Layout: Terminal
            // =================================================================
            "ouvre le terminal" | "affiche le terminal" => Some(json!({
                "speech_status": "IDLE",
                "audio_amplitude": 0.0,
                "widget_id": "terminal",
                "visible": true,
                "action": "TOGGLE_WIDGET"
            })),

            "ferme le terminal" | "cache le terminal" | "masque le terminal" => Some(json!({
                "speech_status": "IDLE",
                "audio_amplitude": 0.0,
                "widget_id": "terminal",
                "visible": false,
                "action": "TOGGLE_WIDGET"
            })),

            // =================================================================
            // HUD Layout: Spotify / Media Player
            // =================================================================
            "ouvre spotify" | "affiche spotify" | "ouvre le lecteur" => Some(json!({
                "speech_status": "IDLE",
                "audio_amplitude": 0.0,
                "widget_id": "spotify",
                "visible": true,
                "action": "TOGGLE_WIDGET"
            })),

            "ferme spotify" | "cache spotify" | "masque spotify" => Some(json!({
                "speech_status": "IDLE",
                "audio_amplitude": 0.0,
                "widget_id": "spotify",
                "visible": false,
                "action": "TOGGLE_WIDGET"
            })),

            // =================================================================
            // Pass-through: requires Gemini cloud reasoning
            // =================================================================
            _ => None,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn light_on_matches_accented_input() {
        let result = LocalIntentRouter::try_route("Allume la lumière");
        assert!(result.is_some());
        let frame = result.unwrap();
        assert_eq!(frame["action"], "EXEC_HAOS_SERVICE");
        assert_eq!(frame["haos_service"], "turn_on");
        assert_eq!(frame["speech_status"], "SPEAKING");
    }

    #[test]
    fn light_on_matches_unaccented_input() {
        let result = LocalIntentRouter::try_route("  allume la lumiere  ");
        assert!(result.is_some());
        assert_eq!(result.unwrap()["action"], "EXEC_HAOS_SERVICE");
    }

    #[test]
    fn light_off_matches() {
        let result = LocalIntentRouter::try_route("éteins la lumière");
        assert!(result.is_some());
        let frame = result.unwrap();
        assert_eq!(frame["action"], "EXEC_HAOS_SERVICE");
        assert_eq!(frame["haos_service"], "turn_off");
    }

    #[test]
    fn telemetry_show_matches() {
        let result = LocalIntentRouter::try_route("affiche la télémétrie");
        assert!(result.is_some());
        let frame = result.unwrap();
        assert_eq!(frame["widget_id"], "sys_metrics");
        assert_eq!(frame["visible"], true);
    }

    #[test]
    fn telemetry_hide_matches() {
        let result = LocalIntentRouter::try_route("ferme les métriques");
        assert!(result.is_some());
        let frame = result.unwrap();
        assert_eq!(frame["widget_id"], "sys_metrics");
        assert_eq!(frame["visible"], false);
    }

    #[test]
    fn unknown_prompt_returns_none() {
        let result = LocalIntentRouter::try_route("Quelle est la météo demain ?");
        assert!(result.is_none());
    }

    #[test]
    fn empty_prompt_returns_none() {
        let result = LocalIntentRouter::try_route("   ");
        assert!(result.is_none());
    }
}
