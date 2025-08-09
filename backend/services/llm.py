"""Service LLM avec Ollama - extrait de main.py"""
import asyncio
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMService:
    """Service centralisé pour interactions avec Ollama LLM"""
    
    def __init__(self, settings):
        self.settings = settings
        self.ollama_client = None
        self.model_name = "llama3.2:1b"
        
    async def initialize(self):
        """Initialise le client Ollama"""
        try:
            # Import dynamique pour éviter dépendance au démarrage
            from integration.ollama_client import OllamaClient
            
            self.ollama_client = OllamaClient(base_url=self.settings.ollama_base_url)
            
            logger.info("🤖 [LLM] Vérification disponibilité Ollama...")
            if await self.ollama_client.is_available():
                logger.info("🤖 [LLM] Service Ollama disponible")
                
                if hasattr(self.ollama_client, 'ensure_model_available'):
                    if await self.ollama_client.ensure_model_available(self.model_name):
                        logger.info(f"✅ [LLM] Modèle {self.model_name} prêt")
                    else:
                        logger.warning(f"⚠️ [LLM] Modèle {self.model_name} non disponible")
                else:
                    logger.warning("⚠️ [LLM] Fonction ensure_model_available non disponible")
            else:
                logger.warning("⚠️ [LLM] Service Ollama non disponible")
                
        except Exception as e:
            logger.error(f"❌ [LLM] Erreur initialisation: {e}")
    
    async def close(self):
        """Ferme proprement le client Ollama"""
        if self.ollama_client:
            try:
                if hasattr(self.ollama_client, 'client') and self.ollama_client.client:
                    await self.ollama_client.client.aclose()
                    logger.info("✅ [LLM] Client Ollama fermé")
                else:
                    logger.info("ℹ️ [LLM] Client déjà fermé ou non initialisé")
            except Exception as e:
                logger.error(f"❌ [LLM] Erreur fermeture: {e}")
    
    def is_available(self) -> bool:
        """Vérifie si le service LLM est disponible"""
        return self.ollama_client is not None
    
    async def generate_response(
        self,
        message: str,
        context: Dict[str, Any],
        user_id: str = "default"
    ) -> str:
        """
        Génère une réponse IA avec contexte
        Extrait de la fonction process_message() de main.py:530-696
        """
        try:
            if not self.is_available():
                logger.error("❌ [LLM] Client Ollama non initialisé")
                return "Service IA temporairement indisponible, veuillez réessayer."
            
            # Construction du prompt système (extrait de main.py:611-648)
            system_prompt = self._build_system_prompt(context, user_id)
            
            logger.debug(f"🤖 [LLM] Génération réponse avec Ollama...")
            
            try:
                response = await self.ollama_client.chat(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    temperature=0.7,
                    max_tokens=512
                )
                
                if response:
                    logger.info(f"✅ [LLM] Réponse générée: {response[:50]}...")
                    return response.strip()
                else:
                    logger.warning("⚠️ [LLM] Ollama a retourné une réponse vide")
                    return "Désolé, je n'ai pas pu traiter votre demande."
                    
            except asyncio.TimeoutError:
                logger.error("❌ [LLM] Timeout Ollama - Service trop lent")
                return "Le service IA met trop de temps à répondre, veuillez réessayer."
            except ConnectionError as e:
                logger.error(f"❌ [LLM] Erreur connexion Ollama: {e}")
                return "Service IA temporairement indisponible, veuillez réessayer."
                
        except Exception as e:
            logger.error(f"❌ [LLM] Erreur génération: {e}")
            return "Une erreur s'est produite lors de la génération de la réponse."
    
    def _build_system_prompt(
        self, 
        context: Dict[str, Any], 
        user_id: str
    ) -> str:
        """
        Construit le prompt système avec contexte
        Extrait de main.py:611-648 
        """
        current_time = datetime.now()
        
        # Noms français des jours et mois (extrait main.py:587-591)
        french_days = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
        french_months = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 
                        'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
        
        french_date = f"{french_days[current_time.weekday()]} {current_time.day} {french_months[current_time.month-1]} {current_time.year} à {current_time.strftime('%H:%M:%S')}"
        
        # Contexte météo s'il existe
        weather_info = context.get('weather_info', '')
        
        # Contexte mémoire utilisateur s'il existe  
        user_context_str = context.get('user_context_str', '')
        
        return f"""Tu es Jarvis, l'assistant IA personnel d'Enzo.

PROFIL UTILISATEUR :
- Nom : Enzo
- Âge : 21 ans 
- Localisation : Perpignan, Pyrénées-Orientales (66), France
- Profil : Futur ingénieur réseau/cybersécurité, passionné technologie

🧠 SYSTÈME MÉMOIRE NEUROMORPHIQUE ACTIF :
- Architecture inspirée du cerveau humain (limbique/préfrontal/hippocampe)
- Analyse émotionnelle des interactions pour pondérer les souvenirs
- Consolidation automatique des mémoires importantes
- Recherche vectorielle sémantique avec Qdrant

INFORMATIONS TEMPS RÉEL :
- Date et heure actuelles : {french_date}
- Localisation : Perpignan, Pyrénées-Orientales, France

{weather_info}{user_context_str}

RÈGLES ABSOLUES :
- TOUJOURS répondre en français parfait et naturel
- Tu es JARVIS, l'assistant IA. Enzo est ton utilisateur (21 ans, Perpignan)
- NE JAMAIS dire que TU as un âge - tu es une IA
- Utiliser OBLIGATOIREMENT les informations temps réel et météo ci-dessus
- Utiliser les mémoires contextuelles neuromorphiques pour personnaliser les réponses
- Si des données météo sont fournies, les citer EXACTEMENT dans ta réponse
- Ne JAMAIS dire que tu n'as pas accès aux informations si elles sont fournies
- Être concis, précis et amical avec Enzo
- Utiliser les données de la mémoire neuromorphique, jamais d'invention

CAPACITÉS AVANCÉES :
- Mémoire neuromorphique avec contexte émotionnel
- Informations date/heure en temps réel
- Informations météo locales (Perpignan, Rivesaltes)
- Contrôle domotique
- Jeux (pendu, etc.)
- Aide générale avec contexte personnalisé"""