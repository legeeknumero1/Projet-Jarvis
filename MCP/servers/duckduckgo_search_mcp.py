#!/usr/bin/env python3
"""
DuckDuckGo Search MCP Server pour Jarvis
Recherche privée sans clé API - aucun tracking
"""

import asyncio
import json
import logging
import urllib.parse
import urllib.request
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DuckDuckGoSearchMCP:
    """Serveur MCP pour DuckDuckGo Search - sans API key requise"""
    
    def __init__(self):
        """Initialisation du serveur MCP DuckDuckGo"""
        self.base_url = "https://html.duckduckgo.com/html/"
        self.instant_url = "https://api.duckduckgo.com/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        logger.info("🦆 DuckDuckGo Search MCP Server initialized")
        logger.info("🔒 Privacy-focused search - No API key required")
    
    def _clean_text(self, text: str) -> str:
        """Nettoie le texte des balises HTML et entités"""
        if not text:
            return ""
        
        # Supprimer les balises HTML
        text = re.sub(r'<[^>]+>', '', text)
        
        # Décoder les entités HTML communes
        text = text.replace('&quot;', '"')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&#x27;', "'")
        
        # Nettoyer les espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _make_request(self, url: str, params: Dict[str, str] = None) -> str:
        """Fait une requête HTTP synchrone vers DuckDuckGo"""
        try:
            if params:
                url += '?' + urllib.parse.urlencode(params)
                
            request = urllib.request.Request(url, headers=self.headers)
            
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 200:
                    content = response.read()
                    return content.decode('utf-8', errors='ignore')
                else:
                    logger.error(f"❌ HTTP {response.status} for {url}")
                    return ""
                    
        except Exception as e:
            logger.error(f"❌ Request error: {e}")
            return ""
    
    async def web_search(self, query: str, count: int = 10, region: str = "fr-fr", 
                        safesearch: str = "moderate", time_filter: str = "") -> Dict[str, Any]:
        """Recherche web avec DuckDuckGo"""
        logger.info(f"🦆 Web search: '{query}' (count={count}, region={region})")
        
        try:
            # Paramètres de recherche DuckDuckGo
            params = {
                'q': query,
                'kl': region,  # Région (fr-fr, en-us, etc.)
                'safe': 'on' if safesearch == 'strict' else ('moderate' if safesearch == 'moderate' else 'off'),
                's': '0',  # Start index
                'dc': str(min(count, 50)),  # Nombre de résultats
                'v': 'l',  # Layout
                'o': 'json',
                'api': '/d.js'
            }
            
            if time_filter:
                if time_filter == 'day':
                    params['df'] = 'd'
                elif time_filter == 'week': 
                    params['df'] = 'w'
                elif time_filter == 'month':
                    params['df'] = 'm'
                elif time_filter == 'year':
                    params['df'] = 'y'
            
            # Faire la requête
            html_content = self._make_request(self.base_url, params)
            
            if not html_content:
                return {
                    "query": query,
                    "error": "No response from DuckDuckGo",
                    "timestamp": datetime.now().isoformat(),
                    "results": []
                }
            
            # Parser les résultats HTML (simplifié)
            results = self._parse_search_results(html_content)
            
            formatted_results = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "total_results": len(results),
                "provider": "DuckDuckGo",
                "privacy": "high",
                "tracking": "none",
                "results": results[:count]
            }
            
            logger.info(f"✅ Found {len(results)} web results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"❌ Web search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "results": []
            }
    
    def _parse_search_results(self, html_content: str) -> List[Dict[str, Any]]:
        """Parse les résultats de recherche depuis le HTML DuckDuckGo"""
        results = []
        
        try:
            # Regex patterns pour extraire les résultats
            # Pattern pour les liens de résultats
            link_pattern = r'<a[^>]+class="[^"]*result__a[^"]*"[^>]+href="([^"]+)"[^>]*>([^<]+)</a>'
            snippet_pattern = r'<a[^>]+class="[^"]*result__snippet[^"]*"[^>]*>([^<]+)</a>'
            
            # Trouver tous les liens
            links = re.findall(link_pattern, html_content, re.IGNORECASE | re.DOTALL)
            
            # Parser les résultats basiques
            result_blocks = re.split(r'<div[^>]+class="[^"]*result[^"]*"', html_content)
            
            for i, block in enumerate(result_blocks[1:21]):  # Max 20 résultats
                try:
                    # Extraire le titre
                    title_match = re.search(r'<a[^>]+class="[^"]*result__a[^"]*"[^>]*>([^<]+)</a>', block)
                    title = self._clean_text(title_match.group(1)) if title_match else f"Result {i+1}"
                    
                    # Extraire l'URL
                    url_match = re.search(r'<a[^>]+href="([^"]+)"', block)
                    url = url_match.group(1) if url_match else ""
                    
                    # Extraire la description
                    desc_match = re.search(r'<a[^>]+class="[^"]*result__snippet[^"]*"[^>]*>([^<]+)</a>', block)
                    description = self._clean_text(desc_match.group(1)) if desc_match else ""
                    
                    # Nettoyer l'URL DuckDuckGo
                    if url.startswith('/l/?uddg='):
                        url = urllib.parse.unquote(url.split('uddg=')[1].split('&')[0])
                    
                    if title and url:
                        results.append({
                            "title": title,
                            "url": url,
                            "description": description,
                            "source": "DuckDuckGo",
                            "privacy": "protected",
                            "tracking": "disabled"
                        })
                        
                except Exception as e:
                    logger.debug(f"Error parsing result block {i}: {e}")
                    continue
            
            # Si parsing HTML échoue, utiliser fallback simple
            if not results:
                results = self._fallback_simple_search(html_content)
                
        except Exception as e:
            logger.error(f"❌ Error parsing results: {e}")
            
        return results
    
    def _fallback_simple_search(self, html_content: str) -> List[Dict[str, Any]]:
        """Fallback simple pour extraire au moins quelques résultats"""
        results = []
        
        try:
            # Pattern très simple pour les liens
            basic_links = re.findall(r'href="([^"]+)"[^>]*>([^<]+)</a>', html_content)
            
            for i, (url, title) in enumerate(basic_links[:10]):
                if url.startswith('http') and len(title.strip()) > 3:
                    results.append({
                        "title": self._clean_text(title),
                        "url": url,
                        "description": "Description not available",
                        "source": "DuckDuckGo (fallback)",
                        "privacy": "protected", 
                        "tracking": "disabled"
                    })
                    
        except Exception as e:
            logger.error(f"❌ Fallback search failed: {e}")
            
        return results
    
    async def instant_answer(self, query: str) -> Dict[str, Any]:
        """Recherche de réponse instantanée DuckDuckGo"""
        logger.info(f"🦆 Instant answer: '{query}'")
        
        try:
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response_text = self._make_request(self.instant_url, params)
            
            if response_text:
                data = json.loads(response_text)
                
                result = {
                    "query": query,
                    "timestamp": datetime.now().isoformat(),
                    "provider": "DuckDuckGo Instant",
                    "answer": data.get("Answer", ""),
                    "abstract": data.get("Abstract", ""),
                    "definition": data.get("Definition", ""),
                    "type": data.get("Type", ""),
                    "topic": data.get("Topic", ""),
                    "related": data.get("RelatedTopics", []),
                    "infobox": data.get("Infobox", {}),
                    "privacy": "high"
                }
                
                logger.info(f"✅ Instant answer retrieved")
                return result
            else:
                return {
                    "query": query,
                    "error": "No instant answer available",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ Instant answer failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def news_search(self, query: str, count: int = 10, region: str = "fr-fr") -> Dict[str, Any]:
        """Recherche d'actualités avec DuckDuckGo"""
        logger.info(f"🦆 News search: '{query}' (count={count})")
        
        # Ajouter news keyword à la recherche
        news_query = f"{query} news actualités"
        
        try:
            result = await self.web_search(
                news_query, 
                count=count, 
                region=region, 
                time_filter="week"
            )
            
            # Reformater pour news
            result["search_type"] = "news"
            result["provider"] = "DuckDuckGo News"
            
            return result
            
        except Exception as e:
            logger.error(f"❌ News search failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "results": []
            }

# Point d'entrée principal  
async def main():
    """Fonction principale du serveur MCP"""
    ddg_mcp = DuckDuckGoSearchMCP()
    
    try:
        # Test de base
        result = await ddg_mcp.web_search("Jarvis AI assistant", count=5)
        print("Test search result:", json.dumps(result, indent=2, ensure_ascii=False))
        
        # Test instant answer
        instant = await ddg_mcp.instant_answer("what is artificial intelligence")
        print("Test instant answer:", json.dumps(instant, indent=2, ensure_ascii=False))
        
    except Exception as e:
        logger.error(f"❌ MCP Server error: {e}")

if __name__ == "__main__":
    asyncio.run(main())