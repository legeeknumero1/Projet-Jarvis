"""
Sanitizer pour logs sécurisés - masquer les informations sensibles
"""

import re
import logging
from typing import Any, Dict, List, Union
import json


class LoggingSanitizer:
    """Classe pour nettoyer les logs des informations sensibles"""
    
    def __init__(self):
        # Patterns pour identifier les données sensibles
        self.sensitive_patterns = {
            'password': [
                r'password["\s]*[:=]["\s]*([^"\s,}]+)',
                r'pwd["\s]*[:=]["\s]*([^"\s,}]+)',
                r'pass["\s]*[:=]["\s]*([^"\s,}]+)',
            ],
            'token': [
                r'token["\s]*[:=]["\s]*([^"\s,}]+)',
                r'auth["\s]*[:=]["\s]*([^"\s,}]+)',
                r'bearer["\s]*[:=]["\s]*([^"\s,}]+)',
            ],
            'key': [
                r'key["\s]*[:=]["\s]*([^"\s,}]+)',
                r'secret["\s]*[:=]["\s]*([^"\s,}]+)',
                r'api_key["\s]*[:=]["\s]*([^"\s,}]+)',
            ],
            'email': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            ],
            'phone': [
                r'\b(?:\+33|0)[1-9](?:[0-9]{8})\b',
            ],
            'credit_card': [
                r'\b(?:\d{4}[\s-]?){3}\d{4}\b',
            ],
            'ip_address': [
                r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            ]
        }
        
        # Champs sensibles dans les dictionnaires
        self.sensitive_fields = {
            'password', 'pwd', 'pass', 'passwd', 'secret', 'token', 
            'auth', 'authorization', 'bearer', 'key', 'api_key',
            'private_key', 'access_token', 'refresh_token', 'session_id',
            'csrf_token', 'x-api-key', 'x-auth-token'
        }
    
    def mask_string(self, text: str, mask_char: str = "*", show_chars: int = 3) -> str:
        """Masquer une chaîne en gardant quelques caractères visibles"""
        if not text or len(text) <= show_chars:
            return mask_char * max(len(text), 3)
        
        visible_part = text[:show_chars]
        masked_part = mask_char * (len(text) - show_chars)
        return visible_part + masked_part
    
    def sanitize_string(self, text: str) -> str:
        """Nettoyer une chaîne de caractères des données sensibles"""
        if not isinstance(text, str):
            return str(text)
        
        sanitized = text
        
        # Appliquer tous les patterns de nettoyage
        for category, patterns in self.sensitive_patterns.items():
            for pattern in patterns:
                # Trouver toutes les correspondances
                matches = re.finditer(pattern, sanitized, re.IGNORECASE)
                for match in reversed(list(matches)):  # Reverse pour préserver les indices
                    if category == 'email':
                        # Pour les emails, masquer seulement la partie avant @
                        email = match.group()
                        local_part, domain = email.split('@', 1)
                        masked_email = self.mask_string(local_part, show_chars=2) + '@' + domain
                        sanitized = sanitized[:match.start()] + masked_email + sanitized[match.end():]
                    elif category == 'ip_address':
                        # Pour les IPs, masquer les 2 derniers octets
                        ip = match.group()
                        parts = ip.split('.')
                        if len(parts) == 4:
                            masked_ip = f"{parts[0]}.{parts[1]}.xxx.xxx"
                            sanitized = sanitized[:match.start()] + masked_ip + sanitized[match.end():]
                    else:
                        # Pour les autres, masquer complètement
                        if match.groups():
                            # Pattern avec groupe de capture
                            sensitive_value = match.group(1)
                            masked_value = self.mask_string(sensitive_value)
                            sanitized = sanitized[:match.start(1)] + masked_value + sanitized[match.end(1):]
                        else:
                            # Pattern simple
                            masked_value = self.mask_string(match.group())
                            sanitized = sanitized[:match.start()] + masked_value + sanitized[match.end():]
        
        return sanitized
    
    def sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Nettoyer un dictionnaire des données sensibles"""
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        
        for key, value in data.items():
            # Vérifier si la clé est sensible
            if key.lower() in self.sensitive_fields:
                sanitized[key] = self.mask_string(str(value))
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = self.sanitize_list(value)
            elif isinstance(value, str):
                sanitized[key] = self.sanitize_string(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def sanitize_list(self, data: List[Any]) -> List[Any]:
        """Nettoyer une liste des données sensibles"""
        if not isinstance(data, list):
            return data
        
        sanitized = []
        
        for item in data:
            if isinstance(item, dict):
                sanitized.append(self.sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(self.sanitize_list(item))
            elif isinstance(item, str):
                sanitized.append(self.sanitize_string(item))
            else:
                sanitized.append(item)
        
        return sanitized
    
    def sanitize_json(self, json_str: str) -> str:
        """Nettoyer une chaîne JSON des données sensibles"""
        try:
            # Parser le JSON
            data = json.loads(json_str)
            
            # Nettoyer les données
            if isinstance(data, dict):
                sanitized_data = self.sanitize_dict(data)
            elif isinstance(data, list):
                sanitized_data = self.sanitize_list(data)
            else:
                return self.sanitize_string(json_str)
            
            # Reconvertir en JSON
            return json.dumps(sanitized_data, ensure_ascii=False, indent=2)
            
        except (json.JSONDecodeError, TypeError):
            # Si ce n'est pas du JSON valide, traiter comme string
            return self.sanitize_string(json_str)
    
    def sanitize_log_record(self, record: logging.LogRecord) -> logging.LogRecord:
        """Nettoyer un enregistrement de log"""
        # Nettoyer le message principal
        if hasattr(record, 'msg') and record.msg:
            record.msg = self.sanitize_string(str(record.msg))
        
        # Nettoyer les arguments
        if hasattr(record, 'args') and record.args:
            sanitized_args = []
            for arg in record.args:
                if isinstance(arg, dict):
                    sanitized_args.append(self.sanitize_dict(arg))
                elif isinstance(arg, list):
                    sanitized_args.append(self.sanitize_list(arg))
                elif isinstance(arg, str):
                    sanitized_args.append(self.sanitize_string(arg))
                else:
                    sanitized_args.append(arg)
            record.args = tuple(sanitized_args)
        
        return record


class SanitizedFilter(logging.Filter):
    """Filtre de logging pour nettoyer automatiquement les logs"""
    
    def __init__(self):
        super().__init__()
        self.sanitizer = LoggingSanitizer()
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filtrer et nettoyer l'enregistrement de log"""
        try:
            # Nettoyer l'enregistrement
            self.sanitizer.sanitize_log_record(record)
            return True
        except Exception as e:
            # En cas d'erreur, laisser passer le log original
            # mais ajouter une note d'erreur
            record.msg = f"[LOG_SANITIZATION_ERROR] {record.msg}"
            return True


# Instance globale du sanitizer
sanitizer = LoggingSanitizer()

def setup_secure_logging():
    """Configurer le logging sécurisé pour toute l'application"""
    # Ajouter le filtre à tous les loggers existants
    sanitized_filter = SanitizedFilter()
    
    # Logger racine
    root_logger = logging.getLogger()
    root_logger.addFilter(sanitized_filter)
    
    # Loggers spécifiques
    for logger_name in ['uvicorn', 'fastapi', 'sqlalchemy', 'httpx', 'redis']:
        logger = logging.getLogger(logger_name)
        logger.addFilter(sanitized_filter)
    
    logging.info("🛡️ Secure logging configured - sensitive data will be masked")

def sanitize_for_log(data: Any) -> Any:
    """Fonction utilitaire pour nettoyer des données avant de les logger"""
    if isinstance(data, dict):
        return sanitizer.sanitize_dict(data)
    elif isinstance(data, list):
        return sanitizer.sanitize_list(data)
    elif isinstance(data, str):
        return sanitizer.sanitize_string(data)
    else:
        return data