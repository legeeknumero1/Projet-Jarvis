"""Service LLM avec Ollama - timeouts et retries"""
import asyncio
import logging
import httpx
import time
from typing import Optional, Dict, List, Any
from datetime import datetime
import random

# Import métriques Prometheus
try:
    from ..observability.metrics import llm_latency, update_service_health, service_response_time
except ImportError:
    # Fallback si prometheus_client pas installé
    def llm_latency_observe(*args, **kwargs):
        pass
    llm_latency = type('MockHistogram', (), {'observe': llm_latency_observe})()
    def update_service_health(*args, **kwargs):
        pass
    service_response_time = type('MockHistogram', (), {'labels': lambda **kw: type('', (), {'observe': lambda x: None})()})()

logger = logging.getLogger(__name__)

class LLMService:
    """Service centralisé pour interactions avec Ollama LLM"""
    
    def __init__(self, settings):
        self.settings = settings
        self.ollama_client = None
        self.model_name = "llama3.2:1b"
        # Client HTTP avec timeouts robustes
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
        )
        
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
        """Ferme proprement les clients"""
        if self.ollama_client:
            try:
                if hasattr(self.ollama_client, 'client') and self.ollama_client.client:
                    await self.ollama_client.client.aclose()
                    logger.info("✅ [LLM] Client Ollama fermé")
                else:
                    logger.info("ℹ️ [LLM] Client déjà fermé ou non initialisé")
            except Exception as e:
                logger.error(f"❌ [LLM] Erreur fermeture: {e}")
        
        # Fermer client HTTP
        await self.http_client.aclose()
        
    async def _retry_with_backoff(self, func, max_retries=3, base_delay=1.0):
        """Retry avec backoff exponentiel"""
        for attempt in range(max_retries):
            try:
                return await func()
            except (httpx.TimeoutException, httpx.ConnectError, asyncio.TimeoutError) as e:
                if attempt == max_retries - 1:
                    raise e
                
                delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"⚠️ [LLM] Tentative {attempt + 1}/{max_retries} échouée, retry dans {delay:.1f}s: {e}")
                await asyncio.sleep(delay)
    
    def is_available(self) -> bool:
        """Vérifie si le service LLM est disponible"""
        return self.ollama_client is not None
    
    async def ping(self) -> bool:
        """Health check pour readiness probe avec métriques"""
        start_time = time.perf_counter()
        is_healthy = False
        
        try:
            async def _ping():
                url = f"{self.settings.ollama_base_url}/api/version"
                resp = await self.http_client.get(url)
                return resp.status_code == 200
            
            is_healthy = await self._retry_with_backoff(_ping, max_retries=2, base_delay=0.5)
            return is_healthy
        except Exception:
            return False
        finally:
            # Enregistrer métriques
            duration = time.perf_counter() - start_time
            service_response_time.labels(service="ollama").observe(duration)
            update_service_health("ollama", is_healthy)
    
    async def generate_response(
        self,
        message: str,
        context: Dict[str, Any],
        user_id: str = "default"
    ) -> str:
        """
        Génère une réponse IA avec contexte et métriques
        Extrait de la fonction process_message() de main.py:530-696
        """
        start_time = time.perf_counter()
        
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
        finally:
            # Enregistrer latence LLM dans métriques
            duration = time.perf_counter() - start_time
            llm_latency.observe(duration)
    
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