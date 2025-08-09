"""Fonctions de validation et sanitisation des entrées"""
import html
import re
from typing import Optional

def sanitize_message(message: str) -> str:
    """
    Sanitise un message contre les attaques XSS et valide la longueur
    Extrait de main.py:241-272
    """
    if not message or not message.strip():
        raise ValueError('Le message ne peut pas être vide')
    
    # Sanitisation contre XSS basique
    message_sanitized = html.escape(message.strip())
    
    # Validation longueur après sanitisation
    if len(message_sanitized) > 5000:
        raise ValueError('Message trop long après sanitisation')
    
    # Bloquer certains patterns dangereux
    dangerous_patterns = [
        '<script',
        'javascript:',
        'data:text/html',
        'vbscript:',
        'onload=',
        'onerror=',
        'eval(',
        'Function(',
        'setTimeout(',
        'setInterval('
    ]
    
    message_lower = message_sanitized.lower()
    for pattern in dangerous_patterns:
        if pattern in message_lower:
            raise ValueError(f'Contenu potentiellement dangereux détecté: {pattern}')
    
    return message_sanitized

def sanitize_user_id(user_id: str) -> str:
    """
    Sanitise et valide un user_id 
    Extrait de main.py:274-289
    """
    if not user_id or not user_id.strip():
        return "default"
    
    # Sanitisation user_id - garder uniquement alphanumériques, _ et -
    user_id_cleaned = re.sub(r'[^a-zA-Z0-9_-]', '', user_id.strip())
    
    if len(user_id_cleaned) == 0:
        return "default"
    
    if len(user_id_cleaned) > 50:
        user_id_cleaned = user_id_cleaned[:50]
        
    return user_id_cleaned

def sanitize_text(text: str) -> str:
    """
    Sanitise un texte pour TTS (version simplifiée de sanitize_message)
    Extrait de main.py:304-307 (TTSRequest validator)
    """
    if not text or not text.strip():
        raise ValueError('Le texte ne peut pas être vide')
    
    # Sanitisation basique pour TTS
    text_cleaned = html.escape(text.strip())
    
    # Validation longueur
    if len(text_cleaned) > 2000:
        raise ValueError('Texte trop long pour TTS (max 2000 caractères)')
    
    return text_cleaned

def sanitize_voice_name(voice: str) -> str:
    """
    Sanitise un nom de voix TTS
    """
    if not voice or not voice.strip():
        return "default"
    
    # Garder uniquement alphanumériques, _ et -
    voice_cleaned = re.sub(r'[^a-zA-Z0-9_-]', '', voice.strip())
    
    if len(voice_cleaned) == 0:
        return "default"
    
    if len(voice_cleaned) > 50:
        voice_cleaned = voice_cleaned[:50]
        
    return voice_cleaned

def mask_sensitive_data(data: str, show_start: int = 4, show_end: int = 2) -> str:
    """
    Masque les données sensibles pour les logs
    Extrait de main.py:215-219
    """
    if not data or len(data) <= show_start + show_end:
        return "***"
    return f"{data[:show_start]}{'*' * (len(data) - show_start - show_end)}{data[-show_end:]}"

def validate_api_key(api_key: Optional[str], expected_key: str) -> bool:
    """
    Valide une clé API de manière sécurisée
    """
    if not api_key or not expected_key:
        return False
    
    # Comparaison sécurisée contre les timing attacks
    import hmac
    return hmac.compare_digest(api_key, expected_key)