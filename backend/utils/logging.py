"""Configuration logging structuré avec emojis et contextvars"""
import logging
import sys
import json
import time
from pathlib import Path
from typing import Optional
from contextvars import ContextVar

# Contexte corrélations
request_id_var = ContextVar("request_id", default="-")
user_id_var    = ContextVar("user_id",    default="-")
path_var       = ContextVar("path",       default="-")
method_var     = ContextVar("method",     default="-")
status_var     = ContextVar("status_code",default=0)
latency_var    = ContextVar("latency_ms", default=0.0)
ip_var         = ContextVar("client_ip",  default="-")
component_var  = ContextVar("component",  default="backend")

def set_context(*, request_id=None, user_id=None, path=None, method=None, status_code=None, latency_ms=None, client_ip=None, component=None):
    """Définit les variables de contexte et retourne les tokens pour reset"""
    tokens = []
    if request_id is not None: tokens.append((request_id_var, request_id_var.set(request_id)))
    if user_id is not None:    tokens.append((user_id_var,    user_id_var.set(user_id)))
    if path is not None:       tokens.append((path_var,       path_var.set(path)))
    if method is not None:     tokens.append((method_var,     method_var.set(method)))
    if status_code is not None:tokens.append((status_var,     status_var.set(status_code)))
    if latency_ms is not None: tokens.append((latency_var,    latency_var.set(latency_ms)))
    if client_ip is not None:  tokens.append((ip_var,         ip_var.set(client_ip)))
    if component is not None:  tokens.append((component_var,  component_var.set(component)))
    return tokens

def reset_context(tokens):
    """Reset les variables de contexte avec les tokens"""
    for var, tok in tokens:
        var.reset(tok)

class RequestContextFilter(logging.Filter):
    """Injecte les contextvars dans le LogRecord (utilisé par dictConfig.filters)."""
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        record.user_id    = user_id_var.get()
        record.path       = path_var.get()
        record.method     = method_var.get()
        record.status_code= status_var.get()
        record.latency_ms = latency_var.get()
        record.client_ip  = ip_var.get()
        record.component  = component_var.get()
        return True

class JsonFormatter(logging.Formatter):
    """Sortie JSONL compacte (horodatage ISO, champs extras)."""
    def __init__(self, extras=None):
        super().__init__()
        self.extras = extras or []

    def format(self, record: logging.LogRecord) -> str:
        base = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()) + "Z",
            "lvl": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        
        # Ajouter champs extras de correlation
        for k in self.extras:
            v = getattr(record, k, None)
            if v is not None and v != "-" and v != 0:
                base[k] = v
        
        # Exception si présente
        if record.exc_info:
            base["exc"] = self.formatException(record.exc_info)
        
        # Scrubbing des secrets avec regex robustes
        import re
        
        SCRUB_PATTERNS = [
            (re.compile(r'(?i)\b(api[_-]?key|token|password)\b\s*[:=]\s*([^\s",}]+)'), r'\1=***'),
            (re.compile(r'(?i)(Authorization:\s*Bearer\s+)[A-Za-z0-9._\-+=/]+'), r'\1***'),
            (re.compile(r'(?i)"(api[_-]?key|token|password)"\s*:\s*"([^"]+)"'), r'"\1":"***"'),
        ]
        
        msg = base.get("msg", "")
        scrubbed = msg
        for pat, repl in SCRUB_PATTERNS:
            scrubbed = pat.sub(repl, scrubbed)
        base["msg"] = scrubbed
        
        return json.dumps(base, ensure_ascii=False)

def configure_logging(settings) -> None:
    """Configure le système de logging"""
    
    # Format avec emojis (comme dans l'actuel) pour console
    console_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Format JSON pour fichiers (production)
    json_formatter = JsonFormatter()
    
    # Handler console (format emoji pour développement)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    
    # Handler fichier JSON (si spécifié)
    handlers = [console_handler]
    if settings.log_file:
        try:
            log_path = Path(settings.log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_path)
            file_handler.setFormatter(json_formatter)  # JSON pour fichiers
            handlers.append(file_handler)
        except Exception as e:
            logging.warning(f"⚠️ [LOG] Cannot create log file {settings.log_file}: {e}")
    
    # Configuration root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        handlers=handlers,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    
    # Réduire verbosité des libs externes
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING) 
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    logging.info("🔧 [LOG] Logging configuré")

def get_logger(name: str) -> logging.Logger:
    """Helper pour créer des loggers nommés"""
    return logging.getLogger(name)

class RequestContextLogger:
    """Logger enrichi avec contexte de requête"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.request_id = None
    
    def set_request_id(self, request_id: str):
        """Définit le request_id pour les prochains logs"""
        self.request_id = request_id
    
    def _log_with_context(self, level: int, msg: str, *args, **kwargs):
        """Log avec enrichissement du contexte"""
        extra = kwargs.get('extra', {})
        if self.request_id:
            extra['request_id'] = self.request_id
        kwargs['extra'] = extra
        self.logger.log(level, msg, *args, **kwargs)
    
    def debug(self, msg, *args, **kwargs):
        self._log_with_context(logging.DEBUG, msg, *args, **kwargs)
    
    def info(self, msg, *args, **kwargs):
        self._log_with_context(logging.INFO, msg, *args, **kwargs)
    
    def warning(self, msg, *args, **kwargs):
        self._log_with_context(logging.WARNING, msg, *args, **kwargs)
    
    def error(self, msg, *args, **kwargs):
        self._log_with_context(logging.ERROR, msg, *args, **kwargs)
    
    def critical(self, msg, *args, **kwargs):
        self._log_with_context(logging.CRITICAL, msg, *args, **kwargs)