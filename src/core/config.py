"""
Configuration for CW Agents with A2A Protocol and CrewAI.
Supports dual LLM configuration: OpenAI (primary) and Ollama (fallback).
"""
import os
from typing import Optional, Literal
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with dual LLM support."""
    
    # Server Configuration
    SERVER_HOST: str = Field(default="0.0.0.0", description="Server host")
    SERVER_PORT: int = Field(default=8001, description="A2A server port")
    DEBUG: bool = Field(default=False, description="Debug mode")
    
    # LLM Configuration - OpenAI (Primary)
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key")
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview", description="OpenAI model name")
    OPENAI_TEMPERATURE: float = Field(default=0.7, description="OpenAI temperature")
    OPENAI_MAX_TOKENS: int = Field(default=4000, description="Max tokens for OpenAI")
    OPENAI_ENABLED: bool = Field(default=True, description="Enable OpenAI")
    
    # LLM Configuration - Ollama (Fallback)
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", description="Ollama base URL")
    OLLAMA_MODEL: str = Field(default="llama3.1:latest", description="Ollama model name")
    OLLAMA_TEMPERATURE: float = Field(default=0.7, description="Ollama temperature")
    OLLAMA_ENABLED: bool = Field(default=True, description="Enable Ollama as fallback")
    
    # LLM Strategy
    LLM_STRATEGY: Literal["openai-first", "ollama-only", "openai-only"] = Field(
        default="openai-first",
        description="LLM selection strategy"
    )
    
    # MCP Server Configuration
    MCP_SERVER_URL: str = Field(default="http://localhost:8000", description="MCP server URL")
    MCP_MAX_CONNECTIONS: int = Field(default=10, description="Max MCP connections")
    MCP_TIMEOUT: int = Field(default=30, description="MCP request timeout (seconds)")
    MCP_RETRY_ATTEMPTS: int = Field(default=3, description="MCP retry attempts")
    MCP_CIRCUIT_BREAKER_THRESHOLD: int = Field(default=5, description="Circuit breaker failure threshold")
    MCP_CIRCUIT_BREAKER_TIMEOUT: int = Field(default=60, description="Circuit breaker timeout (seconds)")
    
    # Redis Configuration (for state and caching only)
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_DB: int = Field(default=0, description="Redis database")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    REDIS_ENABLED: bool = Field(default=True, description="Enable Redis for state/cache")
    
    # Agent Configuration
    TRACKING_POLL_INTERVAL: int = Field(default=300, description="Tracking poll interval (seconds)")
    BATCH_SIZE: int = Field(default=50, description="Batch processing size")
    EXCEPTION_AUTO_DETECT_HOURS: int = Field(default=24, description="Exception auto-detect threshold (hours)")
    ANALYTICS_CACHE_TTL: int = Field(default=3600, description="Analytics cache TTL (seconds)")
    
    # A2A Protocol Configuration
    AGENT_NAME: str = Field(default="CW Logistics Agent", description="Agent name")
    AGENT_DESCRIPTION: str = Field(
        default="Intelligent logistics agent for shipment tracking, routing, exception handling, and analytics",
        description="Agent description"
    )
    AGENT_VERSION: str = Field(default="2.0.0", description="Agent version")
    AGENT_CAPABILITIES: list[str] = Field(
        default=[
            "shipment-tracking",
            "route-optimization",
            "exception-handling",
            "analytics-reporting"
        ],
        description="Agent capabilities"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def openai_available(self) -> bool:
        """Check if OpenAI is available."""
        return self.OPENAI_ENABLED and bool(self.OPENAI_API_KEY)
    
    @property
    def ollama_available(self) -> bool:
        """Check if Ollama is available."""
        return self.OLLAMA_ENABLED
    
    def get_llm_config(self) -> dict:
        """Get LLM configuration based on strategy and availability."""
        config = {
            "strategy": self.LLM_STRATEGY,
            "primary": None,
            "fallback": None
        }
        
        if self.LLM_STRATEGY == "openai-only":
            if self.openai_available:
                config["primary"] = {
                    "provider": "openai",
                    "model": self.OPENAI_MODEL,
                    "temperature": self.OPENAI_TEMPERATURE,
                    "max_tokens": self.OPENAI_MAX_TOKENS,
                    "api_key": self.OPENAI_API_KEY
                }
            else:
                raise ValueError("OpenAI-only strategy selected but OpenAI not available")
        
        elif self.LLM_STRATEGY == "ollama-only":
            if self.ollama_available:
                config["primary"] = {
                    "provider": "ollama",
                    "base_url": self.OLLAMA_BASE_URL,
                    "model": self.OLLAMA_MODEL,
                    "temperature": self.OLLAMA_TEMPERATURE
                }
            else:
                raise ValueError("Ollama-only strategy selected but Ollama not available")
        
        else:  # openai-first (default)
            if self.openai_available:
                config["primary"] = {
                    "provider": "openai",
                    "model": self.OPENAI_MODEL,
                    "temperature": self.OPENAI_TEMPERATURE,
                    "max_tokens": self.OPENAI_MAX_TOKENS,
                    "api_key": self.OPENAI_API_KEY
                }
                if self.ollama_available:
                    config["fallback"] = {
                        "provider": "ollama",
                        "base_url": self.OLLAMA_BASE_URL,
                        "model": self.OLLAMA_MODEL,
                        "temperature": self.OLLAMA_TEMPERATURE
                    }
            elif self.ollama_available:
                config["primary"] = {
                    "provider": "ollama",
                    "base_url": self.OLLAMA_BASE_URL,
                    "model": self.OLLAMA_MODEL,
                    "temperature": self.OLLAMA_TEMPERATURE
                }
            else:
                raise ValueError("No LLM provider available")
        
        return config


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get global settings instance."""
    return settings
