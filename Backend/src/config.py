
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class YelpConfig:
    """Configuration for Yelp API"""
    
    api_key: str
    base_url: str = "https://api.yelp.com/v3"
    default_limit: int = 10
    default_location: str = "San Francisco, CA"
    
    @classmethod
    def from_env(cls) -> 'YelpConfig':
        """Load configuration from environment variables"""
        api_key = os.getenv("YELP_API_KEY")
        if not api_key:
            raise ValueError("YELP_API_KEY environment variable is required")
        
        return cls(
            api_key=api_key,
            default_location=os.getenv("DEFAULT_LOCATION", "San Francisco, CA"),
            default_limit=int(os.getenv("DEFAULT_SEARCH_LIMIT", "10"))
        )


@dataclass
class ServerConfig:
    """Configuration for MCP Server"""
    
    host: str = "localhost"
    port: int = 8000
    log_level: str = "INFO"
    
    @classmethod
    def from_env(cls) -> 'ServerConfig':
        """Load server configuration from environment variables"""
        return cls(
            host=os.getenv("SERVER_HOST", "localhost"),
            port=int(os.getenv("SERVER_PORT", "8000")),
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )


# Category mappings for different search types
BEAUTY_CATEGORIES = {
    "salons": "beautysvc,hair,spas,skincare,eyelashservice,hairremoval",
    "products": "cosmetics,perfume,skincare",
    "spas": "spas,massage,tanning,sauna",
    "nails": "nailtechnicians,nailsalons",
    "hair": "hair,hairsalons,blowoutservices",
}