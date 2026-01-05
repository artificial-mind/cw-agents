"""
LLM Factory for creating language models with automatic fallback.
Supports OpenAI (primary) and Ollama (fallback).
"""
import logging
from typing import Optional, Any
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama

from .config import settings

logger = logging.getLogger(__name__)


class LLMFactory:
    """Factory for creating LLM instances with automatic fallback."""
    
    _primary_llm: Optional[Any] = None
    _fallback_llm: Optional[Any] = None
    _llm_config: Optional[dict] = None
    
    @classmethod
    def initialize(cls):
        """Initialize LLM instances based on configuration."""
        try:
            cls._llm_config = settings.get_llm_config()
            logger.info(f"LLM Strategy: {cls._llm_config['strategy']}")
            
            # Initialize primary LLM
            if cls._llm_config["primary"]:
                cls._primary_llm = cls._create_llm(cls._llm_config["primary"])
                provider = cls._llm_config["primary"]["provider"]
                model = cls._llm_config["primary"].get("model", "unknown")
                logger.info(f"Primary LLM initialized: {provider} ({model})")
            
            # Initialize fallback LLM
            if cls._llm_config["fallback"]:
                cls._fallback_llm = cls._create_llm(cls._llm_config["fallback"])
                provider = cls._llm_config["fallback"]["provider"]
                model = cls._llm_config["fallback"].get("model", "unknown")
                logger.info(f"Fallback LLM initialized: {provider} ({model})")
            
            if not cls._primary_llm:
                raise ValueError("No primary LLM available")
                
        except Exception as e:
            logger.error(f"Failed to initialize LLMs: {e}")
            raise
    
    @classmethod
    def _create_llm(cls, config: dict) -> Any:
        """Create an LLM instance from configuration."""
        provider = config["provider"]
        
        if provider == "openai":
            return ChatOpenAI(
                model=config["model"],
                temperature=config["temperature"],
                max_tokens=config.get("max_tokens", 4000),
                api_key=config["api_key"],
                streaming=True
            )
        
        elif provider == "ollama":
            return ChatOllama(
                base_url=config["base_url"],
                model=config["model"],
                temperature=config["temperature"]
            )
        
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")
    
    @classmethod
    def get_llm(cls, use_fallback: bool = False) -> Any:
        """
        Get an LLM instance.
        
        Args:
            use_fallback: If True and fallback exists, return fallback LLM
        
        Returns:
            LLM instance
        """
        if not cls._primary_llm:
            cls.initialize()
        
        if use_fallback and cls._fallback_llm:
            return cls._fallback_llm
        
        return cls._primary_llm
    
    @classmethod
    async def get_llm_with_retry(cls, max_attempts: int = 2) -> Any:
        """
        Get an LLM instance with automatic fallback on failure.
        
        Args:
            max_attempts: Maximum number of attempts (1 = primary only, 2 = primary + fallback)
        
        Returns:
            LLM instance that is currently available
        """
        if not cls._primary_llm:
            cls.initialize()
        
        # Try primary first
        try:
            # Test primary LLM with a simple prompt
            test_response = await cls._primary_llm.ainvoke("test")
            logger.debug("Primary LLM is available")
            return cls._primary_llm
        except Exception as e:
            logger.warning(f"Primary LLM failed: {e}")
            
            # Try fallback if available and attempts allow
            if max_attempts > 1 and cls._fallback_llm:
                try:
                    test_response = await cls._fallback_llm.ainvoke("test")
                    logger.info("Switched to fallback LLM")
                    return cls._fallback_llm
                except Exception as fallback_error:
                    logger.error(f"Fallback LLM also failed: {fallback_error}")
                    raise
            else:
                raise
    
    @classmethod
    def has_fallback(cls) -> bool:
        """Check if fallback LLM is available."""
        return cls._fallback_llm is not None
    
    @classmethod
    def get_config(cls) -> Optional[dict]:
        """Get current LLM configuration."""
        return cls._llm_config
    
    @classmethod
    def reset(cls):
        """Reset LLM instances (useful for testing)."""
        cls._primary_llm = None
        cls._fallback_llm = None
        cls._llm_config = None


# Convenience function for getting LLM
def get_llm(use_fallback: bool = False) -> Any:
    """Get an LLM instance."""
    return LLMFactory.get_llm(use_fallback=use_fallback)


async def get_llm_with_retry(max_attempts: int = 2) -> Any:
    """Get an LLM instance with automatic fallback on failure."""
    return await LLMFactory.get_llm_with_retry(max_attempts=max_attempts)
