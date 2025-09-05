"""
Routes d'authentification pour Jarvis
"""
from datetime import datetime, timedelta
from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .models import User, UserCreate, UserRead, UserUpdate, Token
from .security import security_manager
from .dependencies import get_current_user, get_current_superuser
from database import get_db

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserRead:
    """Inscription d'un nouvel utilisateur"""
    
    # Valider la force du mot de passe
    if not security_manager.validate_password_strength(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters with uppercase, lowercase, digit, and special character"
        )
    
    try:
        # Vérifier si l'utilisateur existe déjà
        result = await db.execute(
            select(User).where(
                (User.email == user_data.email) | (User.username == user_data.username)
            )
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            if existing_user.email == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Hasher le mot de passe
        hashed_password = security_manager.get_password_hash(user_data.password)
        
        # Créer le nouvel utilisateur
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False,  # Nécessite vérification email
            is_superuser=False
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return UserRead.model_validate(db_user)
        
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )

@router.post("/login", response_model=Token)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
) -> Token:
    """Connexion utilisateur"""
    
    try:
        # Récupérer l'utilisateur (username ou email)
        result = await db.execute(
            select(User).where(
                (User.username == form_data.username) | (User.email == form_data.username)
            )
        )
        user = result.scalar_one_or_none()
        
        # Vérifier l'utilisateur et le mot de passe
        if not user or not security_manager.verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Vérifier si l'utilisateur est actif
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Mettre à jour la dernière connexion
        user.last_login = datetime.utcnow()
        await db.commit()
        
        # Créer les tokens
        access_token_expires = timedelta(minutes=security_manager.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security_manager.create_access_token(
            data={"user_id": user.id, "sub": user.username},
            expires_delta=access_token_expires
        )
        
        refresh_token = security_manager.create_refresh_token(
            data={"user_id": user.id, "sub": user.username}
        )
        
        # Configurer le cookie sécurisé pour le refresh token
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,  # HTTPS only
            samesite="strict",
            max_age=7 * 24 * 60 * 60  # 7 jours
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=int(access_token_expires.total_seconds()),
            user=UserRead.model_validate(user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login error"
        )

@router.post("/refresh", response_model=Dict[str, Any])
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Renouvelle le token d'accès"""
    
    try:
        # Valider le refresh token
        payload = security_manager.verify_token(refresh_token, "refresh")
        user_id = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Récupérer l'utilisateur
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Créer un nouveau token d'accès
        access_token_expires = timedelta(minutes=security_manager.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = security_manager.create_access_token(
            data={"user_id": user.id, "sub": user.username},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(response: Response) -> Dict[str, str]:
    """Déconnexion utilisateur"""
    # Supprimer le cookie refresh token
    response.delete_cookie(key="refresh_token")
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserRead)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> UserRead:
    """Récupère les informations de l'utilisateur connecté"""
    return UserRead.model_validate(current_user)

@router.patch("/me", response_model=UserRead)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> UserRead:
    """Met à jour les informations de l'utilisateur connecté"""
    
    try:
        # Mettre à jour les champs fournis
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Validation spéciale pour le mot de passe
        if "password" in update_data:
            if not security_manager.validate_password_strength(update_data["password"]):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password must be at least 8 characters with uppercase, lowercase, digit, and special character"
                )
            update_data["hashed_password"] = security_manager.get_password_hash(update_data.pop("password"))
        
        # Vérifier l'unicité email/username si modifiés
        if "email" in update_data or "username" in update_data:
            conditions = []
            if "email" in update_data:
                conditions.append(User.email == update_data["email"])
            if "username" in update_data:
                conditions.append(User.username == update_data["username"])
                
            result = await db.execute(
                select(User).where(User.id != current_user.id).where(*conditions)
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email or username already taken"
                )
        
        # Appliquer les modifications
        for field, value in update_data.items():
            setattr(current_user, field, value)
        
        current_user.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(current_user)
        
        return UserRead.model_validate(current_user)
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user"
        )

@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> None:
    """Supprime l'utilisateur connecté"""
    
    try:
        await db.delete(current_user)
        await db.commit()
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting user"
        )

# Routes administrateur
@router.get("/users", response_model=list[UserRead])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_db)
) -> list[UserRead]:
    """Liste tous les utilisateurs (admin only)"""
    
    try:
        result = await db.execute(
            select(User).offset(skip).limit(limit)
        )
        users = result.scalars().all()
        return [UserRead.model_validate(user) for user in users]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )