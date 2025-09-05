"""
Dépendances d'authentification pour FastAPI
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .security import security_manager
from .models import User, TokenData
from database import get_db

# Configuration du schéma de sécurité Bearer
security = HTTPBearer()

class AuthDependencies:
    """Classe pour gérer les dépendances d'authentification"""
    
    @staticmethod
    async def get_current_user_token(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> TokenData:
        """Extrait et valide le token JWT"""
        try:
            # Valider le token
            payload = security_manager.verify_token(credentials.credentials)
            
            user_id = payload.get("user_id")
            username = payload.get("sub")
            
            if user_id is None or username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            return TokenData(user_id=user_id, username=username)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def get_current_user(
        token_data: TokenData = Depends(get_current_user_token),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        """Récupère l'utilisateur actuel depuis la DB"""
        try:
            # Récupérer l'utilisateur depuis la base
            result = await db.execute(
                select(User).where(User.id == token_data.user_id)
            )
            user = result.scalar_one_or_none()
            
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Inactive user"
                )
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error retrieving user"
            )
    
    @staticmethod
    async def get_current_verified_user(
        current_user: User = Depends(get_current_user)
    ) -> User:
        """Récupère un utilisateur vérifié"""
        if not current_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not verified"
            )
        return current_user
    
    @staticmethod
    async def get_current_superuser(
        current_user: User = Depends(get_current_user)
    ) -> User:
        """Récupère un superutilisateur"""
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    
    @staticmethod
    async def get_optional_current_user(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
        db: AsyncSession = Depends(get_db)
    ) -> Optional[User]:
        """Récupère l'utilisateur actuel si connecté (optionnel)"""
        if not credentials:
            return None
            
        try:
            # Valider le token
            payload = security_manager.verify_token(credentials.credentials)
            user_id = payload.get("user_id")
            
            if user_id is None:
                return None
            
            # Récupérer l'utilisateur
            result = await db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user and user.is_active:
                return user
                
        except Exception:
            # En cas d'erreur, retourner None (utilisateur non connecté)
            pass
        
        return None

# Instances des dépendances pour utilisation directe
auth_deps = AuthDependencies()

# Exports pour usage direct
get_current_user_token = auth_deps.get_current_user_token
get_current_user = auth_deps.get_current_user
get_current_verified_user = auth_deps.get_current_verified_user
get_current_superuser = auth_deps.get_current_superuser
get_optional_current_user = auth_deps.get_optional_current_user