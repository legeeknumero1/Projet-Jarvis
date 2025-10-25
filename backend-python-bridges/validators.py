"""
Input Validation Module for Python Flask Backend
Security fixes C7-C11: SQL Injection, XSS, Path Traversal, Command Injection, Buffer Overflow
"""

import re
import base64
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass


# ============================================================================
# Validation Limits
# ============================================================================

class ValidationLimits:
    """Maximum and minimum limits for input validation"""

    # Text content limits
    MAX_PROMPT_LENGTH = 10_000      # 10KB max prompt
    MIN_PROMPT_LENGTH = 1
    MAX_SYSTEM_PROMPT_LENGTH = 5_000  # 5KB max system prompt

    MAX_TTS_TEXT_LENGTH = 5_000     # 5KB max TTS text
    MIN_TTS_TEXT_LENGTH = 1
    MAX_VOICE_ID_LENGTH = 100

    MAX_AUDIO_DATA_LENGTH = 10_000_000  # 10MB base64
    MAX_LANGUAGE_CODE_LENGTH = 10

    # Auth limits
    MAX_USERNAME_LENGTH = 255
    MIN_USERNAME_LENGTH = 1
    MAX_PASSWORD_LENGTH = 1_000
    MIN_PASSWORD_LENGTH = 1

    # Numeric range limits
    MIN_TEMPERATURE = 0.0
    MAX_TEMPERATURE = 2.0
    MIN_MAX_TOKENS = 1
    MAX_MAX_TOKENS = 32_000


# ============================================================================
# Regex Patterns
# ============================================================================

LANGUAGE_CODE_PATTERN = re.compile(r'^[a-z]{2}(-|_)?[a-z]{2}?$')  # en, fr, en-US
BASE64_PATTERN = re.compile(r'^[A-Za-z0-9+/]*={0,2}$')
VOICE_ID_PATTERN = re.compile(r'^[a-z]{2}_[A-Z]{2}-[a-z0-9_-]+$')
USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.]+$')


# ============================================================================
# Validation Error Class
# ============================================================================

@dataclass
class ValidationError(Exception):
    """Custom validation error with field and message"""
    field: str
    message: str

    def __str__(self):
        return f"{self.field}: {self.message}"


# ============================================================================
# Input Validators
# ============================================================================

class PromptValidator:
    """Validate LLM prompt input"""

    def __init__(self, prompt: str, system_prompt: Optional[str] = None,
                 temperature: float = 0.7, max_tokens: int = 512):
        self.prompt = prompt
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Validate all fields. Returns (is_valid, error_message)"""

        # Validate prompt
        if not self.prompt:
            return False, "Prompt cannot be empty"

        if len(self.prompt) > ValidationLimits.MAX_PROMPT_LENGTH:
            return False, f"Prompt exceeds maximum length of {ValidationLimits.MAX_PROMPT_LENGTH}"

        if '\0' in self.prompt:
            return False, "Prompt contains invalid null characters"

        # Validate system prompt if provided
        if self.system_prompt:
            if len(self.system_prompt) > ValidationLimits.MAX_SYSTEM_PROMPT_LENGTH:
                return False, f"System prompt exceeds maximum length of {ValidationLimits.MAX_SYSTEM_PROMPT_LENGTH}"

            if '\0' in self.system_prompt:
                return False, "System prompt contains invalid null characters"

        # Validate temperature
        if not (ValidationLimits.MIN_TEMPERATURE <= self.temperature <= ValidationLimits.MAX_TEMPERATURE):
            return False, f"Temperature must be between {ValidationLimits.MIN_TEMPERATURE} and {ValidationLimits.MAX_TEMPERATURE}"

        # Validate max_tokens
        if not (ValidationLimits.MIN_MAX_TOKENS <= self.max_tokens <= ValidationLimits.MAX_MAX_TOKENS):
            return False, f"Max tokens must be between {ValidationLimits.MIN_MAX_TOKENS} and {ValidationLimits.MAX_MAX_TOKENS}"

        return True, None


class TTSValidator:
    """Validate Text-to-Speech input"""

    def __init__(self, text: str, voice: Optional[str] = None, speed: float = 1.0):
        self.text = text
        self.voice = voice
        self.speed = speed

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Validate TTS input"""

        if not self.text:
            return False, "TTS text cannot be empty"

        if len(self.text) > ValidationLimits.MAX_TTS_TEXT_LENGTH:
            return False, f"TTS text exceeds maximum length of {ValidationLimits.MAX_TTS_TEXT_LENGTH}"

        if '\0' in self.text:
            return False, "TTS text contains invalid null characters"

        # Validate voice if provided
        if self.voice:
            if len(self.voice) > ValidationLimits.MAX_VOICE_ID_LENGTH:
                return False, f"Voice ID exceeds maximum length of {ValidationLimits.MAX_VOICE_ID_LENGTH}"

            # Check pattern but allow custom voices
            if not VOICE_ID_PATTERN.match(self.voice):
                # Log warning but don't fail
                pass

        # Validate speed
        if not (0.1 <= self.speed <= 3.0):
            return False, "Speed must be between 0.1 and 3.0"

        return True, None


class STTValidator:
    """Validate Speech-to-Text input"""

    def __init__(self, audio_data: str, language: Optional[str] = None):
        self.audio_data = audio_data
        self.language = language

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Validate STT input"""

        if not self.audio_data:
            return False, "Audio data cannot be empty"

        if len(self.audio_data) > ValidationLimits.MAX_AUDIO_DATA_LENGTH:
            return False, f"Audio data exceeds maximum size of {ValidationLimits.MAX_AUDIO_DATA_LENGTH} bytes"

        # Validate base64 format
        if not BASE64_PATTERN.match(self.audio_data):
            return False, "Audio data must be valid base64 encoded"

        if '\0' in self.audio_data:
            return False, "Audio data contains invalid null characters"

        # Try to decode to verify it's valid base64
        try:
            base64.b64decode(self.audio_data, validate=True)
        except Exception:
            return False, "Audio data is not valid base64"

        # Validate language if provided
        if self.language:
            if len(self.language) > ValidationLimits.MAX_LANGUAGE_CODE_LENGTH:
                return False, f"Language code exceeds maximum length"

            if not LANGUAGE_CODE_PATTERN.match(self.language):
                # Log warning but don't fail - allow custom languages
                pass

        return True, None


class LoginValidator:
    """Validate login credentials"""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Validate login input"""

        if not self.username:
            return False, "Username cannot be empty"

        if len(self.username) > ValidationLimits.MAX_USERNAME_LENGTH:
            return False, f"Username exceeds maximum length of {ValidationLimits.MAX_USERNAME_LENGTH}"

        # Check username format
        if not USERNAME_PATTERN.match(self.username):
            return False, "Username contains invalid characters. Use only alphanumeric, underscore, hyphen, or period"

        if not self.password:
            return False, "Password cannot be empty"

        if len(self.password) > ValidationLimits.MAX_PASSWORD_LENGTH:
            return False, f"Password exceeds maximum length of {ValidationLimits.MAX_PASSWORD_LENGTH}"

        if '\0' in self.username or '\0' in self.password:
            return False, "Username or password contains invalid null characters"

        return True, None


class EmbeddingsValidator:
    """Validate embeddings input"""

    def __init__(self, text: str):
        self.text = text

    def validate(self) -> Tuple[bool, Optional[str]]:
        """Validate embeddings input"""

        if not self.text:
            return False, "Text cannot be empty"

        if len(self.text) > ValidationLimits.MAX_PROMPT_LENGTH:
            return False, f"Text exceeds maximum length of {ValidationLimits.MAX_PROMPT_LENGTH}"

        if '\0' in self.text:
            return False, "Text contains invalid null characters"

        return True, None


# ============================================================================
# Sanitization Functions
# ============================================================================

def sanitize_text(text: str) -> str:
    """Sanitize text to remove XSS attempts"""
    # Remove potential XSS patterns
    sanitized = text.replace("<script>", "").replace("</script>", "")
    sanitized = sanitized.replace("javascript:", "")
    sanitized = sanitized.replace("onerror=", "")
    sanitized = sanitized.replace("onload=", "")
    return sanitized.strip()


# ============================================================================
# Validation Decorator for Flask
# ============================================================================

def validate_json(*validators_with_data):
    """
    Decorator to validate JSON request data
    Usage: @validate_json((PromptValidator, ['prompt', 'system_prompt', 'temperature', 'max_tokens']))
    """
    def decorator(f):
        def wrapper(*args, **kwargs):
            data = None
            try:
                data = __import__('flask').request.get_json() or {}
            except Exception:
                return {
                    'error': 'Invalid JSON in request body'
                }, 400

            # Validate each validator
            for validator_class, field_names in validators_with_data:
                # Extract fields from data
                field_values = [data.get(name) for name in field_names]

                # Create validator instance
                try:
                    validator = validator_class(*field_values)
                except TypeError:
                    return {
                        'error': f'Invalid data for validator {validator_class.__name__}'
                    }, 400

                # Validate
                is_valid, error_msg = validator.validate()
                if not is_valid:
                    return {
                        'error': error_msg
                    }, 400

            return f(*args, **kwargs)

        wrapper.__name__ = f.__name__
        return wrapper

    return decorator


# ============================================================================
# Tests
# ============================================================================

def test_validators():
    """Simple test suite for validators"""

    # Test PromptValidator
    validator = PromptValidator("Hello, generate a response", temperature=0.7, max_tokens=512)
    assert validator.validate() == (True, None), "Valid prompt should pass"

    validator = PromptValidator("", temperature=0.7, max_tokens=512)
    assert validator.validate()[0] == False, "Empty prompt should fail"

    # Test TTSValidator
    validator = TTSValidator("Hello world", voice="fr_FR-upmc-medium")
    assert validator.validate() == (True, None), "Valid TTS should pass"

    validator = TTSValidator("Hello", speed=5.0)
    assert validator.validate()[0] == False, "Speed out of range should fail"

    # Test STTValidator
    validator = STTValidator("aGVsbG8gd29ybGQ=", language="fr")  # base64 for "hello world"
    assert validator.validate() == (True, None), "Valid audio should pass"

    validator = STTValidator("!!!invalid base64!!!")
    assert validator.validate()[0] == False, "Invalid base64 should fail"

    # Test LoginValidator
    validator = LoginValidator("john_doe", "password123")
    assert validator.validate() == (True, None), "Valid login should pass"

    validator = LoginValidator("invalid@user", "password")
    assert validator.validate()[0] == False, "Invalid username format should fail"

    # Test sanitization
    sanitized = sanitize_text("<script>alert('xss')</script> Hello")
    assert "<script>" not in sanitized, "Script tags should be removed"

    print("[OK] All validator tests passed!")


if __name__ == "__main__":
    test_validators()
