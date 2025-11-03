"""
LangSmith Configuration and Utilities
Provides tracing and monitoring for the multi-agent system
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# LangSmith is automatically enabled if environment variables are set
# No need to manually initialize - LangChain detects the env vars


def get_langsmith_config() -> Dict[str, Any]:
    """Get current LangSmith configuration."""
    return {
        'enabled': os.getenv('LANGCHAIN_TRACING_V2', 'false').lower() == 'true',
        'endpoint': os.getenv('LANGCHAIN_ENDPOINT', 'https://api.smith.langchain.com'),
        'project': os.getenv('LANGCHAIN_PROJECT', 'default'),
        'api_key_set': bool(os.getenv('LANGCHAIN_API_KEY'))
    }


def is_langsmith_enabled() -> bool:
    """Check if LangSmith tracing is enabled."""
    return os.getenv('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'


def log_agent_decision(agent_name: str, query: str, decision: str, metadata: Optional[Dict] = None):
    """
    Log agent routing decision to console.
    LangSmith will automatically capture LangChain/LangGraph traces.

    Args:
        agent_name: Name of the agent making the decision
        query: User query
        decision: Decision made by the agent
        metadata: Additional metadata to log
    """
    timestamp = datetime.now().isoformat()

    log_data = {
        'timestamp': timestamp,
        'agent': agent_name,
        'query': query[:100],  # Truncate long queries
        'decision': decision,
        'metadata': metadata or {}
    }

    if is_langsmith_enabled():
        logger.info(f"[LangSmith] Agent Decision: {log_data}")
    else:
        logger.debug(f"Agent Decision: {log_data}")


def log_agent_execution(agent_name: str, query: str, response: str, duration_ms: float, metadata: Optional[Dict] = None):
    """
    Log agent execution details.

    Args:
        agent_name: Name of the executing agent
        query: User query
        response: Agent response (truncated)
        duration_ms: Execution duration in milliseconds
        metadata: Additional metadata
    """
    log_data = {
        'agent': agent_name,
        'query': query[:100],
        'response': response[:200] if response else None,
        'duration_ms': duration_ms,
        'metadata': metadata or {}
    }

    if is_langsmith_enabled():
        logger.info(f"[LangSmith] Agent Execution: {log_data}")
    else:
        logger.debug(f"Agent Execution: {log_data}")


def trace_agent(agent_name: str):
    """
    Decorator to trace agent execution.
    Logs execution time and basic metrics.

    Usage:
        @trace_agent("ProductAgent")
        async def run(self, query: str):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = await func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds() * 1000

                # Extract query from args/kwargs
                query = kwargs.get('query') or (args[1] if len(args) > 1 else 'unknown')

                log_agent_execution(
                    agent_name=agent_name,
                    query=str(query),
                    response=str(result)[:200] if result else None,
                    duration_ms=duration,
                    metadata={'success': True}
                )
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds() * 1000
                log_agent_execution(
                    agent_name=agent_name,
                    query='error',
                    response=None,
                    duration_ms=duration,
                    metadata={'success': False, 'error': str(e)}
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds() * 1000

                query = kwargs.get('query') or (args[1] if len(args) > 1 else 'unknown')

                log_agent_execution(
                    agent_name=agent_name,
                    query=str(query),
                    response=str(result)[:200] if result else None,
                    duration_ms=duration,
                    metadata={'success': True}
                )
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds() * 1000
                log_agent_execution(
                    agent_name=agent_name,
                    query='error',
                    response=None,
                    duration_ms=duration,
                    metadata={'success': False, 'error': str(e)}
                )
                raise

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def print_langsmith_status():
    """Print LangSmith configuration status."""
    config = get_langsmith_config()

    print("\n" + "=" * 60)
    print("LangSmith Tracing Configuration")
    print("=" * 60)
    print(f"Enabled: {config['enabled']}")
    print(f"Project: {config['project']}")
    print(f"Endpoint: {config['endpoint']}")
    print(f"API Key Set: {config['api_key_set']}")

    if config['enabled']:
        print("\n[OK] LangSmith tracing is ACTIVE")
        print(f"  View traces at: https://smith.langchain.com/")
        print(f"  Project: {config['project']}")
    else:
        print("\n[DISABLED] LangSmith tracing is DISABLED")
        print("  To enable, set LANGCHAIN_TRACING_V2=true in .env")

    print("=" * 60 + "\n")


# Print status on import
if __name__ != "__main__":
    if is_langsmith_enabled():
        logger.info("LangSmith tracing enabled")
