"""Configuration validation utilities for Beehive application.

This module provides validators to ensure all required environment variables
are set and configured properly before the application starts.
"""

import os
import sys
from functools import wraps
from typing import List, Optional


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""
    pass


class ConfigValidator:
    """Validates application configuration and environment variables."""

    # Required environment variables for production
    REQUIRED_ENV_VARS = [
        'FLASK_SECRET_KEY',
        'JWT_SECRET',
        'MONGODB_URI',
    ]

    # Optional environment variables with defaults
    OPTIONAL_ENV_VARS = {
        'ALLOWED_ORIGINS': ['http://localhost:3000'],
        'FLASK_ENV': 'development',
        'MONGODB_DB_NAME': 'beehive',
        'JWT_EXPIRATION_HOURS': '24',
    }

    @staticmethod
    def validate_all() -> None:
        """Validate all required configuration settings.
        
        Raises:
            ConfigValidationError: If any required configuration is missing.
        """
        missing_vars = []
        
        # Check required variables
        for var in ConfigValidator.REQUIRED_ENV_VARS:
            value = os.getenv(var)
            if not value or value.strip() == '':
                missing_vars.append(var)
            # Additional validation for secrets
            elif var in ['FLASK_SECRET_KEY', 'JWT_SECRET']:
                if len(value) < 16:
                    missing_vars.append(f"{var} (must be at least 16 characters)")
        
        if missing_vars:
            error_msg = (
                f"Missing or invalid required environment variables:\n"
                f"{chr(10).join(f'  - {var}' for var in missing_vars)}\n"
                f"Please set these variables and restart the application."
            )
            raise ConfigValidationError(error_msg)
        
        # Validate MONGODB_URI
        mongo_uri = os.getenv('MONGODB_URI')
        if not mongo_uri.startswith('mongodb'):
            raise ConfigValidationError(
                "Invalid MONGODB_URI: Must start with 'mongodb' or 'mongodb+srv'"
            )
        
        # Validate CORS origins
        ConfigValidator._validate_cors_origins()

    @staticmethod
    def _validate_cors_origins() -> None:
        """Validate and set CORS allowed origins.
        
        Raises:
            ConfigValidationError: If CORS origins are not properly configured.
        """
        origins_str = os.getenv('ALLOWED_ORIGINS')
        
        if not origins_str:
            # Use default origins if not set
            origins = ConfigValidator.OPTIONAL_ENV_VARS['ALLOWED_ORIGINS']
            os.environ['ALLOWED_ORIGINS'] = ','.join(origins)
        else:
            # Validate format of provided origins
            origins = [o.strip() for o in origins_str.split(',')]
            if not origins or all(o == '' for o in origins):
                raise ConfigValidationError(
                    "ALLOWED_ORIGINS is empty. Please provide at least one origin."
                )
            # Validate each origin format
            for origin in origins:
                if not origin.startswith(('http://', 'https://')):
                    raise ConfigValidationError(
                        f"Invalid CORS origin: {origin}. "
                        f"Must start with 'http://' or 'https://'"
                    )

    @staticmethod
    def get_config_dict() -> dict:
        """Get current configuration as a dictionary.
        
        Returns:
            Dictionary containing all application configuration.
        """
        config = {}
        
        # Add all required variables
        for var in ConfigValidator.REQUIRED_ENV_VARS:
            config[var] = os.getenv(var, '[NOT SET]')
        
        # Add optional variables with defaults
        for var, default in ConfigValidator.OPTIONAL_ENV_VARS.items():
            config[var] = os.getenv(var, default)
        
        # Mask sensitive values in output
        for secret_var in ['FLASK_SECRET_KEY', 'JWT_SECRET', 'MONGODB_URI']:
            if secret_var in config and config[secret_var] != '[NOT SET]':
                value = str(config[secret_var])
                config[secret_var] = value[:3] + '*' * (len(value) - 6) + value[-3:]
        
        return config


def validate_config_on_startup():
    """Decorator to validate configuration on application startup.
    
    Usage:
        @validate_config_on_startup()
        def create_app():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                ConfigValidator.validate_all()
            except ConfigValidationError as e:
                print(f"Configuration Error: {e}", file=sys.stderr)
                sys.exit(1)
            return func(*args, **kwargs)
        return wrapper
    return decorator
