"""
Système d'authentification JWT ultra-sécurisé pour Jarvis (2025)
Conforme OWASP API Security Top 10 et best practices JWT
"""
import logging
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List
import jwt
import bcrypt
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncpg
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class JWTAuthManager:
    """
    Gestionnaire d'authentification JWT ultra-sécurisé
    - Tokens JWT avec expiration courte
    - Refresh tokens sécurisés 
    - Blacklist tokens révoqués
    - Rate limiting par IP
    - Audit trails complets
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.pg_pool = None
        self.redis_client = None
        
        # Configuration JWT sécurisée
        self.algorithm = "HS256"
        self.secret_key = self._get_or_generate_secret()
        self.access_token_expire = 15  # 15 minutes (court pour sécurité)
        self.refresh_token_expire = 7 * 24 * 60  # 7 jours en minutes
        
        # Rate limiting strict
        self.max_login_attempts = 5
        self.lockout_duration = 30  # minutes
        self.max_tokens_per_user = 3
        
        # Security bearer pour extraction automatique
        self.security = HTTPBearer(auto_error=False)
        
    async def initialize(self):
        """Initialise les connexions DB et Redis"""
        try:
            # Connexion PostgreSQL pour users et audit
            await self._init_postgresql()
            
            # Connexion Redis pour tokens et rate limiting
            await self._init_redis()
            
            # Création des tables de sécurité
            await self._create_security_tables()
            
            logger.info("🔐 [JWT] Système d'authentification initialisé")
            
        except Exception as e:
            logger.error(f"❌ [JWT] Erreur initialisation: {e}")
            raise
    
    async def _init_postgresql(self):
        """Initialise PostgreSQL pour users/audit"""
        try:
            # Configuration depuis settings
            dsn = f"postgresql://{self.settings.db_user}:{self.settings.db_password}@{self.settings.db_host}:{self.settings.db_port}/{self.settings.db_name}"
            
            self.pg_pool = await asyncpg.create_pool(
                dsn,
                min_size=2,
                max_size=10,
                command_timeout=30
            )
            
            logger.info("🐘 [JWT] PostgreSQL connecté pour auth")
            
        except Exception as e:
            logger.error(f"❌ [JWT] Erreur PostgreSQL: {e}")
            raise
    
    async def _init_redis(self):
        """Initialise Redis pour tokens et cache"""
        try:
            redis_url = f"redis://{getattr(self.settings, 'redis_host', 'localhost')}:{getattr(self.settings, 'redis_port', 6379)}"
            
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connexion
            await self.redis_client.ping()
            logger.info("🔗 [JWT] Redis connecté pour tokens")
            
        except Exception as e:
            logger.error(f"❌ [JWT] Erreur Redis: {e}")
            raise
    
    def _get_or_generate_secret(self) -> str:
        """Génère ou récupère la clé secrète JWT"""
        # Priorité : variable d'environnement
        if hasattr(self.settings, 'jwt_secret_key') and self.settings.jwt_secret_key:
            return self.settings.jwt_secret_key
        
        # Génération sécurisée si pas définie
        secret = secrets.token_urlsafe(64)  # 512 bits d'entropie
        logger.warning("⚠️ [JWT] Clé JWT générée automatiquement - définir JWT_SECRET_KEY en production")
        return secret
    
    async def _create_security_tables(self):
        """Crée les tables de sécurité"""
        try:
            async with self.pg_pool.acquire() as conn:
                # Table utilisateurs sécurisée
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS jwt_users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        salt TEXT NOT NULL,
                        is_active BOOLEAN DEFAULT true,
                        is_superuser BOOLEAN DEFAULT false,
                        failed_login_attempts INTEGER DEFAULT 0,
                        locked_until TIMESTAMP NULL,
                        last_login TIMESTAMP NULL,
                        password_changed_at TIMESTAMP DEFAULT NOW(),
                        mfa_enabled BOOLEAN DEFAULT false,
                        mfa_secret TEXT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        updated_at TIMESTAMP DEFAULT NOW()
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_jwt_users_username ON jwt_users(username);
                    CREATE INDEX IF NOT EXISTS idx_jwt_users_email ON jwt_users(email);
                """)
                
                # Table audit des connexions
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS jwt_audit_log (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES jwt_users(id),
                        action VARCHAR(50) NOT NULL,
                        ip_address INET,
                        user_agent TEXT,
                        success BOOLEAN NOT NULL,
                        failure_reason TEXT NULL,
                        timestamp TIMESTAMP DEFAULT NOW(),
                        session_id VARCHAR(100),
                        additional_data JSONB DEFAULT '{}'
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_jwt_audit_timestamp ON jwt_audit_log(timestamp DESC);
                    CREATE INDEX IF NOT EXISTS idx_jwt_audit_user_id ON jwt_audit_log(user_id);
                """)
                
                # Table refresh tokens
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS jwt_refresh_tokens (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES jwt_users(id) ON DELETE CASCADE,
                        token_hash TEXT NOT NULL,
                        expires_at TIMESTAMP NOT NULL,
                        created_at TIMESTAMP DEFAULT NOW(),
                        revoked_at TIMESTAMP NULL,
                        device_info JSONB DEFAULT '{}'
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_jwt_refresh_user_id ON jwt_refresh_tokens(user_id);
                    CREATE INDEX IF NOT EXISTS idx_jwt_refresh_expires ON jwt_refresh_tokens(expires_at);
                """)
                
                logger.info("📊 [JWT] Tables de sécurité créées")
                
        except Exception as e:
            logger.error(f"❌ [JWT] Erreur création tables: {e}")
            raise
    
    async def create_user(
        self, 
        username: str, 
        email: str, 
        password: str,
        is_superuser: bool = False
    ) -> Dict[str, Any]:
        """
        Création sécurisée d'un utilisateur avec hachage bcrypt + salt
        """
        try:
            # Validation input
            if len(password) < 12:
                raise ValueError("Mot de passe trop court (minimum 12 caractères)")
            
            # Génération salt et hash sécurisés
            salt = bcrypt.gensalt(rounds=14)  # 14 rounds pour 2025
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            async with self.pg_pool.acquire() as conn:
                # Vérification unicité
                existing = await conn.fetchrow(
                    "SELECT id FROM jwt_users WHERE username = $1 OR email = $2",
                    username, email
                )
                
                if existing:
                    raise ValueError("Utilisateur ou email déjà existant")
                
                # Insertion sécurisée
                user_id = await conn.fetchval("""
                    INSERT INTO jwt_users 
                    (username, email, password_hash, salt, is_superuser, password_changed_at)
                    VALUES ($1, $2, $3, $4, $5, NOW())
                    RETURNING id
                """, username, email, password_hash.decode('utf-8'), salt.decode('utf-8'), is_superuser)
                
                logger.info(f"✅ [JWT] Utilisateur créé: {username} (ID: {user_id})")
                
                return {
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'is_superuser': is_superuser,
                    'created_at': datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ [JWT] Erreur création utilisateur: {e}")
            raise
    
    async def authenticate_user(
        self, 
        username: str, 
        password: str,
        request: Request
    ) -> Optional[Dict[str, Any]]:
        """
        Authentification sécurisée avec rate limiting et audit
        """
        client_ip = request.client.host
        user_agent = request.headers.get('user-agent', 'Unknown')
        session_id = secrets.token_urlsafe(16)
        
        try:
            # 1. Vérification rate limiting
            await self._check_rate_limiting(client_ip, username)
            
            # 2. Récupération utilisateur
            async with self.pg_pool.acquire() as conn:
                user = await conn.fetchrow("""
                    SELECT id, username, email, password_hash, salt, is_active, 
                           is_superuser, failed_login_attempts, locked_until
                    FROM jwt_users 
                    WHERE username = $1
                """, username)
                
                if not user:
                    await self._log_auth_attempt(
                        None, 'login_attempt', client_ip, user_agent, 
                        False, 'User not found', session_id
                    )
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Identifiants invalides"
                    )
                
                # 3. Vérification compte actif et non verrouillé
                if not user['is_active']:
                    await self._log_auth_attempt(
                        user['id'], 'login_attempt', client_ip, user_agent,
                        False, 'Account disabled', session_id
                    )
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Compte désactivé"
                    )
                
                if user['locked_until'] and user['locked_until'] > datetime.now(timezone.utc):
                    await self._log_auth_attempt(
                        user['id'], 'login_attempt', client_ip, user_agent,
                        False, 'Account locked', session_id
                    )
                    raise HTTPException(
                        status_code=status.HTTP_423_LOCKED,
                        detail="Compte temporairement verrouillé"
                    )
                
                # 4. Vérification mot de passe
                is_valid = bcrypt.checkpw(
                    password.encode('utf-8'),
                    user['password_hash'].encode('utf-8')
                )
                
                if not is_valid:
                    # Incrémenter tentatives échouées
                    await self._handle_failed_login(user['id'], client_ip, user_agent, session_id)
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Identifiants invalides"
                    )
                
                # 5. Succès - Reset failed attempts et update last_login
                await conn.execute("""
                    UPDATE jwt_users 
                    SET failed_login_attempts = 0, locked_until = NULL, last_login = NOW()
                    WHERE id = $1
                """, user['id'])
                
                # 6. Log succès
                await self._log_auth_attempt(
                    user['id'], 'login_success', client_ip, user_agent,
                    True, None, session_id
                )
                
                logger.info(f"✅ [JWT] Authentification réussie: {username} from {client_ip}")
                
                return {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'is_superuser': user['is_superuser'],
                    'session_id': session_id
                }
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ [JWT] Erreur authentification: {e}")
            await self._log_auth_attempt(
                None, 'login_error', client_ip, user_agent,
                False, str(e), session_id
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur interne d'authentification"
            )
    
    async def _check_rate_limiting(self, ip: str, username: str):
        """Vérification rate limiting par IP et username"""
        try:
            # Rate limiting par IP
            ip_key = f"rate_limit_ip:{ip}"
            ip_attempts = await self.redis_client.get(ip_key) or "0"
            
            if int(ip_attempts) >= self.max_login_attempts:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Trop de tentatives depuis cette IP. Réessayez dans {self.lockout_duration} minutes."
                )
            
            # Rate limiting par username
            user_key = f"rate_limit_user:{username}"
            user_attempts = await self.redis_client.get(user_key) or "0"
            
            if int(user_attempts) >= self.max_login_attempts:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Trop de tentatives pour cet utilisateur. Réessayez dans {self.lockout_duration} minutes."
                )
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ [JWT] Erreur rate limiting: {e}")
    
    async def _handle_failed_login(self, user_id: int, ip: str, user_agent: str, session_id: str):
        """Gestion des tentatives de connexion échouées"""
        try:
            async with self.pg_pool.acquire() as conn:
                # Incrémenter compteur d'échecs
                result = await conn.fetchrow("""
                    UPDATE jwt_users 
                    SET failed_login_attempts = failed_login_attempts + 1
                    WHERE id = $1
                    RETURNING failed_login_attempts, username
                """, user_id)
                
                failed_attempts = result['failed_login_attempts']
                username = result['username']
                
                # Verrouillage si trop d'échecs
                if failed_attempts >= self.max_login_attempts:
                    await conn.execute("""
                        UPDATE jwt_users 
                        SET locked_until = NOW() + INTERVAL '%s minutes'
                        WHERE id = $1
                    """, self.lockout_duration, user_id)
                    
                    logger.warning(f"🔒 [JWT] Compte verrouillé: {username} après {failed_attempts} tentatives")
                
                # Rate limiting Redis
                await self._update_rate_limit_counters(ip, username)
                
                # Log tentative échouée
                await self._log_auth_attempt(
                    user_id, 'login_failed', ip, user_agent,
                    False, f"Wrong password ({failed_attempts} attempts)", session_id
                )
                
        except Exception as e:
            logger.error(f"❌ [JWT] Erreur gestion échec login: {e}")
    
    async def _update_rate_limit_counters(self, ip: str, username: str):
        """Mise à jour des compteurs de rate limiting Redis"""
        try:
            # Compteur IP
            ip_key = f"rate_limit_ip:{ip}"
            await self.redis_client.incr(ip_key)
            await self.redis_client.expire(ip_key, self.lockout_duration * 60)
            
            # Compteur username
            user_key = f"rate_limit_user:{username}"
            await self.redis_client.incr(user_key)
            await self.redis_client.expire(user_key, self.lockout_duration * 60)
            
        except Exception as e:
            logger.error(f"❌ [JWT] Erreur update rate limiting: {e}")
    
    async def _log_auth_attempt(
        self,
        user_id: Optional[int],
        action: str,
        ip: str,
        user_agent: str,
        success: bool,
        failure_reason: Optional[str],
        session_id: str,
        additional_data: Dict = None
    ):
        """Enregistrement audit trail complet"""
        try:
            async with self.pg_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO jwt_audit_log 
                    (user_id, action, ip_address, user_agent, success, 
                     failure_reason, session_id, additional_data)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, user_id, action, ip, user_agent, success, 
                failure_reason, session_id, json.dumps(additional_data or {}))
                
        except Exception as e:
            logger.error(f"❌ [JWT] Erreur audit log: {e}")
    
    async def create_tokens(self, user: Dict[str, Any], request: Request) -> Dict[str, Any]:
        """
        Génération sécurisée des tokens JWT + refresh token
        """
        try:
            now = datetime.now(timezone.utc)
            
            # Payload JWT sécurisé
            access_payload = {
                'sub': str(user['id']),
                'username': user['username'],
                'email': user['email'],
                'is_superuser': user.get('is_superuser', False),
                'iat': now,
                'exp': now + timedelta(minutes=self.access_token_expire),
                'jti': secrets.token_urlsafe(16),  # JWT ID pour révocation
                'session_id': user.get('session_id'),
                'ip': request.client.host
            }
            
            # Génération tokens
            access_token = jwt.encode(access_payload, self.secret_key, algorithm=self.algorithm)
            refresh_token = secrets.token_urlsafe(64)
            
            # Stockage refresh token sécurisé
            refresh_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            device_info = {
                'user_agent': request.headers.get('user-agent', 'Unknown'),
                'ip': request.client.host,
                'created_at': now.isoformat()
            }
            
            async with self.pg_pool.acquire() as conn:
                # Nettoyage anciens refresh tokens
                await conn.execute("""
                    DELETE FROM jwt_refresh_tokens 
                    WHERE user_id = $1 AND (
                        expires_at < NOW() OR 
                        id NOT IN (
                            SELECT id FROM jwt_refresh_tokens 
                            WHERE user_id = $1 
                            ORDER BY created_at DESC 
                            LIMIT $2
                        )
                    )
                """, user['id'], self.max_tokens_per_user - 1)
                
                # Insertion nouveau refresh token
                await conn.execute("""
                    INSERT INTO jwt_refresh_tokens 
                    (user_id, token_hash, expires_at, device_info)
                    VALUES ($1, $2, $3, $4)
                """, user['id'], refresh_hash, 
                now + timedelta(minutes=self.refresh_token_expire),
                json.dumps(device_info))
            
            # Cache access token pour révocation rapide
            token_cache_key = f"jwt_token:{access_payload['jti']}"
            await self.redis_client.setex(
                token_cache_key, 
                self.access_token_expire * 60,
                json.dumps({
                    'user_id': user['id'],
                    'username': user['username'],
                    'valid': True
                })
            )
            
            logger.info(f"🔐 [JWT] Tokens créés pour {user['username']}")
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'bearer',
                'expires_in': self.access_token_expire * 60,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'is_superuser': user.get('is_superuser', False)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ [JWT] Erreur création tokens: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur génération tokens"
            )
    
    async def verify_token(self, credentials: HTTPAuthorizationCredentials) -> Dict[str, Any]:
        """
        Vérification sécurisée du token JWT avec blacklist
        """
        try:
            if not credentials or not credentials.credentials:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token manquant"
                )
            
            token = credentials.credentials
            
            # Décodage JWT
            try:
                payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            except jwt.ExpiredSignatureError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expiré"
                )
            except jwt.InvalidTokenError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token invalide"
                )
            
            # Vérification blacklist
            jti = payload.get('jti')
            if jti:
                token_cache_key = f"jwt_token:{jti}"
                cached_token = await self.redis_client.get(token_cache_key)
                
                if not cached_token:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token révoqué"
                    )
                
                token_data = json.loads(cached_token)
                if not token_data.get('valid', False):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token révoqué"
                    )
            
            # Vérification utilisateur toujours actif
            user_id = int(payload['sub'])
            async with self.pg_pool.acquire() as conn:
                user = await conn.fetchrow("""
                    SELECT id, username, email, is_active, is_superuser
                    FROM jwt_users 
                    WHERE id = $1
                """, user_id)
                
                if not user or not user['is_active']:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Utilisateur inactif"
                    )
            
            return {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'is_superuser': user['is_superuser'],
                'jti': jti,
                'session_id': payload.get('session_id')
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ [JWT] Erreur vérification token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Erreur vérification token"
            )
    
    async def revoke_token(self, jti: str):
        """Révocation immédiate d'un token via blacklist"""
        try:
            if jti:
                token_cache_key = f"jwt_token:{jti}"
                await self.redis_client.setex(
                    token_cache_key,
                    self.access_token_expire * 60,
                    json.dumps({'valid': False, 'revoked_at': datetime.now(timezone.utc).isoformat()})
                )
                
                logger.info(f"🚫 [JWT] Token révoqué: {jti}")
                
        except Exception as e:
            logger.error(f"❌ [JWT] Erreur révocation token: {e}")
    
    async def refresh_access_token(self, refresh_token: str, request: Request) -> Dict[str, Any]:
        """Renouvellement sécurisé du token d'accès"""
        try:
            refresh_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            
            async with self.pg_pool.acquire() as conn:
                # Vérification refresh token
                token_data = await conn.fetchrow("""
                    SELECT rt.*, u.username, u.email, u.is_active, u.is_superuser
                    FROM jwt_refresh_tokens rt
                    JOIN jwt_users u ON rt.user_id = u.id
                    WHERE rt.token_hash = $1 
                      AND rt.expires_at > NOW()
                      AND rt.revoked_at IS NULL
                      AND u.is_active = true
                """, refresh_hash)
                
                if not token_data:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Refresh token invalide ou expiré"
                    )
                
                # Création nouveau token d'accès
                user = {
                    'id': token_data['user_id'],
                    'username': token_data['username'],
                    'email': token_data['email'],
                    'is_superuser': token_data['is_superuser'],
                    'session_id': secrets.token_urlsafe(16)
                }
                
                tokens = await self.create_tokens(user, request)
                
                # Log renouvellement
                await self._log_auth_attempt(
                    user['id'], 'token_refresh', request.client.host,
                    request.headers.get('user-agent', 'Unknown'),
                    True, None, user['session_id']
                )
                
                return tokens
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ [JWT] Erreur refresh token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur renouvellement token"
            )
    
    async def close(self):
        """Fermeture propre des connexions"""
        try:
            if self.pg_pool:
                await self.pg_pool.close()
            if self.redis_client:
                await self.redis_client.close()
            logger.info("✅ [JWT] Connexions fermées")
        except Exception as e:
            logger.error(f"❌ [JWT] Erreur fermeture: {e}")

# Instance globale
jwt_auth = None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))
) -> Dict[str, Any]:
    """Dependency pour récupérer l'utilisateur authentifié"""
    if not jwt_auth:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service d'authentification non initialisé"
        )
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token d'authentification requis"
        )
    
    return await jwt_auth.verify_token(credentials)

async def get_superuser(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Dependency pour vérifier les droits superuser"""
    if not current_user.get('is_superuser', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Droits administrateur requis"
        )
    return current_user