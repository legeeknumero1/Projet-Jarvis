"""
Service de Recherche Web pour LLM Jarvis
Intégration internet sécurisée avec multiple providers (2025)
"""
import logging
import asyncio
import httpx
import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class WebSearchService:
    """
    Service de recherche web multi-provider pour LLM
    Providers supportés: DuckDuckGo, SearXNG, Brave, Google CSE
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.http_client = None
        self.brave_api_keys = [
            token for token in (
                getattr(settings, 'brave_api_key', None),
                getattr(settings, 'brave_api_key_backup', None)
            ) if token
        ]
        self.google_credentials_available = bool(
            getattr(settings, 'google_cse_key', None) and getattr(settings, 'google_cse_id', None)
        )
        
        # Configuration providers
        self.providers = {
            'duckduckgo': {
                'name': 'DuckDuckGo',
                'url': 'https://api.duckduckgo.com/',
                'enabled': True,
                'rate_limit': 10  # requests per minute
            },
            'searxng': {
                'name': 'SearXNG',
                'url': getattr(settings, 'searxng_url', 'https://search.privacytools.io'),
                'enabled': getattr(settings, 'searxng_enabled', False),
                'rate_limit': 30
            },
            'brave': {
                'name': 'Brave Search',
                'url': 'https://api.search.brave.com/res/v1/web/search',
                'enabled': bool(self.brave_api_keys),
                'rate_limit': 20
            },
            'google_cse': {
                'name': 'Google Custom Search',
                'url': 'https://customsearch.googleapis.com/customsearch/v1',
                'enabled': self.google_credentials_available,
                'rate_limit': 100
            }
        }
        
        # Cache résultats
        self.search_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
    async def initialize(self):
        """Initialise le service de recherche web"""
        try:
            self.http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(15.0, connect=5.0),
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
                headers={
                    'User-Agent': 'Jarvis-AI/1.0 (Educational Research Bot)',
                    'Accept': 'application/json, text/html, application/xml, text/plain',
                    'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8'
                }
            )
            
            logger.info("🌐 [WEB] Service recherche web initialisé")
            
            # Test connectivité providers
            await self._test_providers()
            
        except Exception as e:
            logger.error(f"❌ [WEB] Erreur initialisation: {e}")
            raise
    
    async def close(self):
        """Ferme les connexions HTTP"""
        if self.http_client:
            await self.http_client.aclose()
    
    async def _test_providers(self):
        """Test de connectivité des providers activés"""
        for provider_id, config in self.providers.items():
            if config['enabled']:
                try:
                    test_result = await self._test_provider(provider_id)
                    if test_result:
                        logger.info(f"✅ [WEB] Provider {config['name']} disponible")
                    else:
                        logger.warning(f"⚠️ [WEB] Provider {config['name']} indisponible")
                        config['enabled'] = False
                except Exception as e:
                    logger.warning(f"⚠️ [WEB] Provider {config['name']} erreur: {e}")
                    config['enabled'] = False
    
    async def _test_provider(self, provider_id: str) -> bool:
        """Test spécifique d'un provider"""
        try:
            if provider_id == 'duckduckgo':
                response = await self.http_client.get(
                    'https://api.duckduckgo.com/?q=test&format=json&no_html=1&skip_disambig=1'
                )
                return response.status_code == 200
            
            elif provider_id == 'searxng':
                searxng_url = self.providers['searxng']['url']
                response = await self.http_client.get(f"{searxng_url}/search?q=test&format=json")
                return response.status_code == 200
            
            elif provider_id == 'brave':
                for token in self.brave_api_keys:
                    headers = {'X-Subscription-Token': token}
                    response = await self.http_client.get(
                        'https://api.search.brave.com/res/v1/web/search?q=test',
                        headers=headers
                    )
                    if response.status_code == 200:
                        return True
                return False
            
            elif provider_id == 'google_cse':
                if self.google_credentials_available:
                    params = {
                        'key': self.settings.google_cse_key,
                        'cx': self.settings.google_cse_id,
                        'q': 'test'
                    }
                    response = await self.http_client.get(
                        'https://customsearch.googleapis.com/customsearch/v1',
                        params=params
                    )
                    return response.status_code == 200
                return False
            
            return False
            
        except Exception as e:
            logger.debug(f"Test provider {provider_id} failed: {e}")
            return False
    
    async def search(
        self, 
        query: str, 
        max_results: int = 5,
        provider: Optional[str] = None,
        include_content: bool = True
    ) -> Dict[str, Any]:
        """
        Recherche web intelligente avec fallback multi-provider
        """
        try:
            # Validation query
            if not query.strip() or len(query) > 500:
                raise ValueError("Query invalide ou trop longue")
            
            # Nettoyage query
            clean_query = self._clean_search_query(query)
            
            # Cache check
            cache_key = f"{clean_query}_{max_results}_{provider}"
            if cache_key in self.search_cache:
                cache_entry = self.search_cache[cache_key]
                if (datetime.now() - cache_entry['timestamp']).seconds < self.cache_ttl:
                    logger.debug(f"🔄 [WEB] Résultat depuis cache: {clean_query}")
                    return cache_entry['results']
            
            logger.info(f"🔍 [WEB] Recherche: '{clean_query}'")
            
            # Sélection provider
            selected_provider = await self._select_best_provider(provider)
            if not selected_provider:
                raise RuntimeError("Aucun provider de recherche disponible")
            
            # Recherche
            search_results = await self._execute_search(
                selected_provider, clean_query, max_results
            )
            
            # Enrichissement contenu si demandé
            if include_content and search_results.get('results'):
                await self._enrich_with_content(search_results['results'])
            
            # Mise en cache
            self.search_cache[cache_key] = {
                'results': search_results,
                'timestamp': datetime.now()
            }
            
            logger.info(f"✅ [WEB] Recherche terminée: {len(search_results.get('results', []))} résultats")
            return search_results
            
        except Exception as e:
            logger.error(f"❌ [WEB] Erreur recherche '{query}': {e}")
            return {
                'query': query,
                'results': [],
                'provider': 'none',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _clean_search_query(self, query: str) -> str:
        """Nettoyage et optimisation de la requête"""
        # Suppression caractères spéciaux problématiques
        cleaned = re.sub(r'[<>"\']', '', query.strip())
        
        # Limitation longueur
        cleaned = cleaned[:200]
        
        # Optimisations spécifiques français
        cleaned = cleaned.replace('é', 'e').replace('è', 'e').replace('à', 'a')
        
        return cleaned
    
    async def _select_best_provider(self, preferred: Optional[str] = None) -> Optional[str]:
        """Sélection du meilleur provider disponible"""
        # Provider préféré s'il est disponible
        if preferred and preferred in self.providers and self.providers[preferred]['enabled']:
            return preferred
        
        # Ordre de priorité par défaut
        priority_order = ['duckduckgo', 'searxng', 'brave', 'google_cse']
        
        for provider_id in priority_order:
            if self.providers[provider_id]['enabled']:
                return provider_id
        
        return None
    
    async def _execute_search(
        self, 
        provider_id: str, 
        query: str, 
        max_results: int
    ) -> Dict[str, Any]:
        """Exécution de la recherche selon le provider"""
        try:
            if provider_id == 'duckduckgo':
                return await self._search_duckduckgo(query, max_results)
            elif provider_id == 'searxng':
                return await self._search_searxng(query, max_results)
            elif provider_id == 'brave':
                return await self._search_brave(query, max_results)
            elif provider_id == 'google_cse':
                return await self._search_google_cse(query, max_results)
            else:
                raise ValueError(f"Provider inconnu: {provider_id}")
                
        except Exception as e:
            logger.error(f"❌ [WEB] Erreur provider {provider_id}: {e}")
            raise
    
    async def _search_duckduckgo(self, query: str, max_results: int) -> Dict[str, Any]:
        """Recherche DuckDuckGo avec API et scraping"""
        try:
            # Tentative API officielle (limitée)
            try:
                api_url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1&skip_disambig=1"
                response = await self.http_client.get(api_url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    results = []
                    
                    # Abstract principal
                    if data.get('Abstract'):
                        results.append({
                            'title': data.get('Heading', query),
                            'url': data.get('AbstractURL', ''),
                            'snippet': data.get('Abstract', ''),
                            'source': 'duckduckgo_abstract'
                        })
                    
                    # Topics reliés
                    for topic in data.get('RelatedTopics', [])[:max_results-1]:
                        if isinstance(topic, dict) and topic.get('Text'):
                            results.append({
                                'title': topic.get('FirstURL', {}).get('text', 'Information'),
                                'url': topic.get('FirstURL', {}).get('url', ''),
                                'snippet': topic.get('Text', ''),
                                'source': 'duckduckgo_related'
                            })
                    
                    if results:
                        return {
                            'query': query,
                            'provider': 'duckduckgo',
                            'results': results[:max_results],
                            'total_results': len(results),
                            'timestamp': datetime.now().isoformat()
                        }
            
            except Exception as api_error:
                logger.debug(f"API DuckDuckGo indisponible: {api_error}")
            
            # Fallback: scraping HTML (méthode alternative)
            return await self._search_duckduckgo_html(query, max_results)
            
        except Exception as e:
            logger.error(f"❌ [WEB] Erreur DuckDuckGo: {e}")
            raise
    
    async def _search_duckduckgo_html(self, query: str, max_results: int) -> Dict[str, Any]:
        """Recherche DuckDuckGo par scraping HTML (fallback)"""
        try:
            # URL de recherche HTML
            search_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
            
            response = await self.http_client.get(search_url)
            if response.status_code != 200:
                raise httpx.HTTPStatusError(f"Status {response.status_code}", request=response.request, response=response)
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Extraction résultats
            for result_div in soup.find_all('div', class_='result')[:max_results]:
                try:
                    # Titre et lien
                    title_link = result_div.find('a', class_='result__a')
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    url = title_link.get('href', '')
                    
                    # Snippet
                    snippet_div = result_div.find('div', class_='result__snippet')
                    snippet = snippet_div.get_text(strip=True) if snippet_div else ''
                    
                    if title and url:
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet,
                            'source': 'duckduckgo_html'
                        })
                
                except Exception as parse_error:
                    logger.debug(f"Erreur parsing résultat DuckDuckGo: {parse_error}")
                    continue
            
            return {
                'query': query,
                'provider': 'duckduckgo',
                'results': results,
                'total_results': len(results),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ [WEB] Erreur DuckDuckGo HTML: {e}")
            raise
    
    async def _search_searxng(self, query: str, max_results: int) -> Dict[str, Any]:
        """Recherche SearXNG"""
        try:
            searxng_url = self.providers['searxng']['url']
            search_url = f"{searxng_url}/search"
            
            params = {
                'q': query,
                'format': 'json',
                'engines': 'google,bing,duckduckgo',
                'categories': 'general'
            }
            
            response = await self.http_client.get(search_url, params=params)
            
            if response.status_code != 200:
                raise httpx.HTTPStatusError(f"SearXNG status {response.status_code}", request=response.request, response=response)
            
            data = response.json()
            results = []
            
            for item in data.get('results', [])[:max_results]:
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'snippet': item.get('content', ''),
                    'source': f"searxng_{item.get('engine', 'unknown')}"
                })
            
            return {
                'query': query,
                'provider': 'searxng',
                'results': results,
                'total_results': len(results),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ [WEB] Erreur SearXNG: {e}")
            raise
    
    async def _search_brave(self, query: str, max_results: int) -> Dict[str, Any]:
        """Recherche Brave Search API"""
        try:
            if not self.brave_api_keys:
                raise ValueError("Brave API key non configurée")
            
            last_error: Optional[Exception] = None
            for token in self.brave_api_keys:
                headers = {'X-Subscription-Token': token}
                params = {
                    'q': query,
                    'count': min(max_results, 20),
                    'search_lang': 'fr',
                    'country': 'FR',
                    'safesearch': 'moderate'
                }
                
                response = await self.http_client.get(
                    'https://api.search.brave.com/res/v1/web/search',
                    headers=headers,
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = []
                    
                    for item in data.get('web', {}).get('results', []):
                        results.append({
                            'title': item.get('title', ''),
                            'url': item.get('url', ''),
                            'snippet': item.get('description', ''),
                            'source': 'brave_search'
                        })
                    
                    return {
                        'query': query,
                        'provider': 'brave',
                        'results': results,
                        'total_results': len(results),
                        'timestamp': datetime.now().isoformat()
                    }
                
                last_error = httpx.HTTPStatusError(
                    f"Brave API status {response.status_code}",
                    request=response.request,
                    response=response
                )
            
            if last_error:
                raise last_error
            raise RuntimeError("Brave API inaccessible avec les clés fournies")
            
        except Exception as e:
            logger.error(f"❌ [WEB] Erreur Brave Search: {e}")
            raise
    
    async def _search_google_cse(self, query: str, max_results: int) -> Dict[str, Any]:
        """Recherche Google Custom Search Engine"""
        try:
            if not self.google_credentials_available:
                raise ValueError("Google CSE credentials non configurées")
            
            params = {
                'key': self.settings.google_cse_key,
                'cx': self.settings.google_cse_id,
                'q': query,
                'num': min(max_results, 10),
                'lr': 'lang_fr',
                'safe': 'medium'
            }
            
            response = await self.http_client.get(
                'https://customsearch.googleapis.com/customsearch/v1',
                params=params
            )
            
            if response.status_code != 200:
                raise httpx.HTTPStatusError(f"Google CSE status {response.status_code}", request=response.request, response=response)
            
            data = response.json()
            results = []
            
            for item in data.get('items', []):
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'source': 'google_cse'
                })
            
            return {
                'query': query,
                'provider': 'google_cse',
                'results': results,
                'total_results': data.get('searchInformation', {}).get('totalResults', len(results)),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ [WEB] Erreur Google CSE: {e}")
            raise
    
    async def _enrich_with_content(self, results: List[Dict[str, Any]]):
        """Enrichissement des résultats avec contenu des pages"""
        try:
            # Enrichissement en parallèle (max 3 simultanées pour éviter surcharge)
            semaphore = asyncio.Semaphore(3)
            
            async def enrich_single_result(result):
                async with semaphore:
                    try:
                        # Extraction contenu principal
                        content = await self._extract_page_content(result['url'])
                        if content:
                            result['content'] = content[:1000]  # Limite pour performance
                            result['content_available'] = True
                        else:
                            result['content_available'] = False
                    except Exception as e:
                        logger.debug(f"Échec enrichissement {result['url']}: {e}")
                        result['content_available'] = False
            
            # Traitement parallèle
            tasks = [enrich_single_result(result) for result in results[:3]]  # Max 3 pour éviter spam
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"❌ [WEB] Erreur enrichissement contenu: {e}")
    
    async def _extract_page_content(self, url: str, max_length: int = 2000) -> Optional[str]:
        """Extraction contenu textuel d'une page web"""
        try:
            # Vérification URL basique
            if not url.startswith(('http://', 'https://')):
                return None
            
            # Timeout court pour éviter blocages
            response = await self.http_client.get(
                url,
                timeout=httpx.Timeout(8.0, connect=3.0),
                follow_redirects=True
            )
            
            if response.status_code != 200:
                return None
            
            # Parse HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Suppression scripts et styles
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extraction texte principal
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            
            if main_content:
                text = main_content.get_text(separator=' ', strip=True)
            else:
                text = soup.get_text(separator=' ', strip=True)
            
            # Nettoyage et limitation
            cleaned_text = re.sub(r'\s+', ' ', text)
            return cleaned_text[:max_length] if cleaned_text else None
            
        except Exception as e:
            logger.debug(f"Échec extraction contenu {url}: {e}")
            return None
    
    def is_available(self) -> bool:
        """Vérifie si au moins un provider est disponible"""
        return any(config['enabled'] for config in self.providers.values())
    
    def get_available_providers(self) -> List[str]:
        """Retourne la liste des providers disponibles"""
        return [pid for pid, config in self.providers.items() if config['enabled']]
    
    def format_search_results_for_llm(self, search_results: Dict[str, Any]) -> str:
        """Formate les résultats pour intégration dans le contexte LLM"""
        if not search_results.get('results'):
            return f"Aucun résultat trouvé pour '{search_results.get('query', 'requête inconnue')}'"
        
        formatted = f"🔍 RÉSULTATS WEB pour '{search_results['query']}' ({search_results['provider']}):\\n"
        
        for i, result in enumerate(search_results['results'][:5], 1):
            title = result.get('title', 'Sans titre')[:80]
            snippet = result.get('snippet', 'Pas de description')[:150]
            url = result.get('url', '')
            
            formatted += f"{i}. **{title}**\\n"
            formatted += f"   {snippet}\\n"
            if result.get('content'):
                content_preview = result['content'][:200]
                formatted += f"   Extrait: {content_preview}...\\n"
            formatted += f"   Source: {url}\\n\\n"
        
        return formatted
