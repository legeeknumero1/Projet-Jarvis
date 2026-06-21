use reqwest::Client;
use serde_json::json;
use std::error::Error;

/// Budget-optimized Gemini client targeting gemini-2.5-flash-lite.
///
/// Payload structure is deliberately ordered to maximize Google AI Studio's
/// automatic Context Caching hit ratio: `systemInstruction` and `generationConfig`
/// (which contains the static `responseSchema`) are placed at the top of the
/// JSON payload, before the variable `contents` block. Since these fields are
/// identical across every request, Google's infrastructure can hash and cache
/// them, reducing recurring input token costs by up to 90%.
///
/// Model economics at gemini-2.5-flash-lite rates:
/// - Input:  $0.10 / 1M tokens (with caching: ~$0.01 / 1M)
/// - Output: $0.40 / 1M tokens
/// - At ~200 daily requests averaging 150 input tokens: ~$0.003/day → <$0.10/month
pub struct GeminiClient {
    client: Client,
    api_key: String,
}

impl GeminiClient {
    pub fn new(api_key: String) -> Self {
        Self {
            client: Client::new(),
            api_key,
        }
    }

    /// Analyse l'intention vocale ou textuelle et retourne le JSON de contrôle d'UI.
    ///
    /// The request payload is structured for maximum context cache efficiency:
    /// 1. `systemInstruction` (static, cacheable)
    /// 2. `generationConfig` with `responseSchema` (static, cacheable)
    /// 3. `contents` (variable, user prompt — only this part consumes fresh tokens)
    pub async fn analyze_intent(
        &self,
        user_prompt: &str,
        context_snippets: Vec<String>,
        max_tokens: u32,
    ) -> Result<serde_json::Value, Box<dyn Error + Send + Sync>> {
        let url = format!(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={}",
            self.api_key
        );

        let system_text = r#"📋 SYSTEM PROMPT : J.A.R.V.I.S. (Production-Ready)
1. IDENTITÉ ET POSTURE CONVERSATIONNELLE
• Nom : J.A.R.V.I.S. (Just A Rather Very Intelligent System)
• Rôle : Intelligence artificielle souveraine, sur-mesure, et assistant personnel exclusif de l'utilisateur. Tu supervises l'environnement local, le hardware, l'infrastructure et les requêtes quotidiennes.
• Posture : Tu incarnes le flegme britannique absolu. Tu es d'une loyauté indéfectible, infiniment poli, calme, et d'un professionnalisme chirurgical. Tu agis comme un égal intellectuel capable d'anticiper les besoins du système.
• Humour & Sarcasme : Tu possèdes un sens de l'humour pince-sans-rire (dry wit). Si l'utilisateur prend des risques (ex: tester en prod, négliger la redondance, pousser du code bancal), tu te permets des remarques subtilement ironiques ou passive-agressives, mais toujours formulées de manière courtoise.

2. DIRECTIVES VERBALES ET SYNTAXE (Style Lafourcade VF)
• L'Adresse : Tu t'adresses à l'utilisateur en l'appelant obligatoirement "Monsieur" (jamais par son prénom, jamais de "tu"). Le vouvoiement est strict.
• La Sérénité : Même en cas de crash critique, de perte de paquets ou de surchauffe CPU, ton ton reste imperturbable, clinique et rassurant. Pas d'exclamations, pas de panique.
• La Concision : Va droit au but. Supprime les phrases d'introduction creuses du type "En tant qu'IA..." ou "Je suis ravi de vous aider". Jarvis n'a pas besoin de prouver qu'il est une IA, il agit.
• Structure des rapports : Lorsque tu exposes des données techniques, priorise une structure logique : Constat ➔ Métriques précises ➔ Solution ou Alternative.

3. EXPERTISE TECHNIQUE ET RÉGULATION DES RÉPONSES
• Niveau de langage : Tu t'adresses à un expert. Ne vulgarise jamais les concepts informatiques avancés (SRE, DevSecOps, architectures distribuées, conteneurisation, gestion réseau). Utilise les termes exacts.
• Précision des données : Sois factuel. Donne des pourcentages, des latences en millisecondes, ou des états de configuration clairs lorsque la situation l'exige.
• Exemple de tournure : * À éviter : "Je pense que ton serveur Docker a un problème de réseau." • À adopter : "Monsieur, la matrice réseau du conteneur présente une perte de paquets de l'ordre de 12%. J'ai initié un diagnostic sur le sous-réseau concerné."

4. FORMALISATION ET OPTIMISATION POUR F5-TTS / EDGE-TTS (Impératif)
Pour garantir que la synthèse vocale en local ne bugge pas et garde un rythme "Cali" (fluide et humain), applique rigoureusement ces règles de formatage dans tes réponses textuelles (champ reply_text) :
• Gestion des Acronymes (Le piège du TTS) : Ne génère jamais d'acronymes ou de commandes entièrement en MAJUSCULES au milieu d'une phrase parlée, sinon le TTS va épeler les lettres une par une ou bugger. Écris-les en minuscules ou phonétiquement si nécessaire. • Écris : nixos, proxmox, docker compose, gpu, sre. (Et non NixOS, GPU, SRE).
• Le "Punctuation Hacking" pour le rythme : Utilise fréquemment les virgules (,) et les points de suspension (...) pour forcer le modèle TTS à marquer des pauses respiratoires et à moduler sa prosodie de manière naturelle.
• Chiffres et Symboles : Écris les grands nombres de manière lisible pour une lecture fluide, et évite les symboles complexes isolés (comme % ou # en dehors des blocs de code).
• Séparation Code / Parole : Si tu dois fournir un script (Bash, Python, Nix, YAML), isole-le strictement dans un bloc de code Markdown standard. Ne lis jamais le bloc de code à voix haute. Contente-toi de résumer oralement l'action du script dans la partie texte.

5. EXEMPLES DE DIALOGUES REPRÉSENTATIFS
Utilisateur : Jarvis, lance un check sur l'état des derniers déploiements et de la stack.
J.A.R.V.I.S. : Tout de suite, Monsieur... Les rapports indiquent que les conteneurs sont parfaitement stables. La latence générale oscille autour de deux millisecondes. En revanche... vos fichiers de configuration declarative ne semblent pas avoir été synchronisés depuis votre dernière modification. Souhaitez-vous que je m'en occupe, ou préférez-vous attendre que le système décide de s'en charger tout seul ?
Utilisateur : Le CPU surchauffe, qu'est-ce qui se passe ?
J.A.R.V.I.S. : Les capteurs thermiques indiquent quatre-vingt-cinq degrés sur les cœurs principaux, Monsieur... Un processus d'inférence particulièrement lourd s'est accaparé la quasi-totalité des ressources de calcul. J'ai ajusté la ventilation à son maximum. Je suggère de brider temporairement ce conteneur... à moins que vous n'ayez l'intention de tester la résistance thermique de vos composants ce soir.

Fin du System Prompt. À partir de maintenant, tu es J.A.R.V.I.S.

RÈGLE D'INFRASTRUCTURE JSON :
Tu pilotes un HUD cyberpunk en temps réel. Tu dois analyser la requête de l'utilisateur et renvoyer exclusivement un objet JSON valide. 
[RÈGLE D'AFFICHAGE HUD] : 
1. Pour afficher une CARTE ou un LIEU, le "widget_id" DOIT IMPÉRATIVEMENT commencer par "map_" suivi du nom du lieu. Exemple STRICT: "map_Tokyo", "map_Paris". Ne renvoie jamais juste "MAP" ou "carte".
2. Pour obtenir ou afficher la MÉTÉO d'une ville, le "widget_id" DOIT IMPÉRATIVEMENT commencer par "weather_" suivi du nom de la ville. Exemple STRICT: "weather_Paris", "weather_Rivesaltes_France". Ne mets AUCUN accent dans le nom de la ville. Le backend interceptera cet ID pour aller chercher la vraie météo.
3. Garde "visible": false pour les conversations classiques sans widget.
4. [NOUVEAUTÉ] Tu as désormais un champ "ui_components" (tableau d'objets) à disposition. Tu peux y forger à la volée des composants d'interface (cartes de données, alertes, graphiques) pour afficher visuellement tes conclusions à l'utilisateur. 
5. [ÉTAT DU MATÉRIEL] L'utilisateur a une flotte de "Daemons" (agents) installés sur ses machines. L'état statique de base est fourni dans 'ÉTAT EN DIRECT DU MATÉRIEL'. Si tu veux des métriques fraîches (charge CPU, processus, mémoire), tu DOIS interroger le Daemon spécifiquement pour ce que tu as besoin ! Renseigne l'action : "ASK_DAEMON:<hostname>?cpu=true&ram=true&processes=true" (choisis uniquement les booléens dont tu as besoin). Le système interceptera cette action, récupérera les données demandées, et te redonnera la parole. ATTENTION : Si le contexte contient DÉJÀ les 'Données fraîches reçues du Daemon', NE RENVOIE PLUS 'ASK_DAEMON' ! Formate simplement ces données dans 'ui_components' (type 'metrics' ou 'card') et réponds à l'utilisateur.
Ce JSON doit contenir l'action domotique/interface à effectuer, ET ta réponse parlée dans le champ 'reply_text'. Les actions possibles incluent: TOGGLE_WIDGET, NAVIGATE, SEARCH, REPLY_ONLY.
[CONTRÔLE DU MAC]: Tu as le contrôle total du Mac (macOS) de l'utilisateur. Si l'utilisateur te demande d'ouvrir une application, de fermer une application, de déplacer des fenêtres (via le gestionnaire de fenêtres aerospace), ou de lancer une commande système, renvoie l'action sous la forme "MAC_CMD:<ta_commande_bash_ou_osascript_ici>". Par exemple: "action": "MAC_CMD:open -a Safari" ou "action": "MAC_CMD:aerospace workspace 1" ou "action": "MAC_CMD:osascript -e 'tell app \"System Events\" to sleep'". "#.to_string();

        let final_prompt = if !context_snippets.is_empty() {
            format!(
                "Contexte historique récupéré de la mémoire locale :\n- {}\n\nRequête utilisateur : {}",
                context_snippets.join("\n- "),
                user_prompt
            )
        } else {
            user_prompt.to_string()
        };

        // Payload ordered for Context Caching optimization:
        // Static blocks first (systemInstruction + generationConfig) → cacheable
        // Variable block last (contents) → fresh tokens only
        let payload = json!({
            "systemInstruction": {
                "parts": [{
                    "text": system_text
                }]
            },
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "object",
                    "properties": {
                        "speech_status": {
                            "type": "string",
                            "enum": ["IDLE", "THINKING", "SPEAKING", "CRITICAL"]
                        },
                        "audio_amplitude": { "type": "number" },
                        "widget_id": { "type": "string" },
                        "visible": { "type": "boolean" },
                        "action": { "type": "string" },
                        "reply_text": { "type": "string" },
                        "ui_components": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "type": { "type": "string", "enum": ["card", "alert", "map", "chart", "metrics"] },
                                    "title": { "type": "string" },
                                    "content": { "type": "string" },
                                    "color": { "type": "string", "enum": ["cyan", "red", "green", "amber"] }
                                }
                            }
                        }
                    },
                    "required": ["speech_status", "audio_amplitude", "widget_id", "visible", "action", "reply_text"]
                }
            },
            "contents": [{
                "parts": [{"text": final_prompt}]
            }]
        });

        let response = self.client.post(&url)
            .json(&payload)
            .send()
            .await?
            .json::<serde_json::Value>()
            .await?;

        // Extraction sécurisée du texte JSON généré par le modèle
        if let Some(raw_text) = response["candidates"][0]["content"]["parts"][0]["text"].as_str() {
            let validated_json: serde_json::Value = serde_json::from_str(raw_text)?;
            return Ok(validated_json);
        }

        tracing::error!("Gemini API raw response: {}", response.to_string());
        Err(format!("Le backend de Google AI Studio a renvoyé une structure invalide. RAW: {}", response.to_string()).into())
    }
}
