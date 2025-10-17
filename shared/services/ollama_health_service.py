"""
Ollama Health Check and Model Management Service
Handles Ollama server health checks, model availability verification, and auto-pulling missing models
"""

import requests
import subprocess
import logging
import time
from typing import Dict, List, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class OllamaHealthService:
    """Service for checking Ollama server health and managing models"""
    
    def __init__(self, ollama_base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama health service
        
        Args:
            ollama_base_url: Base URL for Ollama server (default: http://localhost:11434)
        """
        self.ollama_base_url = ollama_base_url
        self.health_endpoint = f"{ollama_base_url}/api/tags"
        self.timeout = 5  # seconds
        
    def check_server_health(self) -> Tuple[bool, str]:
        """
        Check if Ollama server is running and responding
        
        Returns:
            Tuple[bool, str]: (is_healthy, message)
        """
        try:
            response = requests.get(
                self.health_endpoint,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info("✅ Ollama server is healthy and responding")
                return True, "Ollama server is running"
            else:
                logger.error(f"❌ Ollama server returned status {response.status_code}")
                return False, f"Ollama server error: {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("❌ Ollama server timeout - not responding")
            return False, "Ollama server is not responding (timeout)"
        except requests.exceptions.ConnectionError:
            logger.error("❌ Cannot connect to Ollama server")
            return False, "Cannot connect to Ollama server. Is it running?"
        except Exception as e:
            logger.error(f"❌ Error checking Ollama health: {str(e)}")
            return False, f"Error checking Ollama: {str(e)}"
    
    def get_available_models(self) -> Tuple[bool, List[str], str]:
        """
        Get list of available models from Ollama
        
        Returns:
            Tuple[bool, List[str], str]: (success, models_list, message)
        """
        try:
            response = requests.get(
                self.health_endpoint,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                logger.info(f"✅ Found {len(models)} available models: {models}")
                return True, models, f"Found {len(models)} models"
            else:
                return False, [], f"Failed to get models: {response.status_code}"
                
        except Exception as e:
            logger.error(f"❌ Error getting available models: {str(e)}")
            return False, [], f"Error getting models: {str(e)}"
    
    def is_model_available(self, model_name: str) -> Tuple[bool, str]:
        """
        Check if a specific model is available
        
        Args:
            model_name: Name of the model to check (e.g., 'llava')
            
        Returns:
            Tuple[bool, str]: (is_available, message)
        """
        success, models, message = self.get_available_models()
        
        if not success:
            return False, f"Cannot check models: {message}"
        
        # Check for exact match or partial match
        for model in models:
            if model_name in model or model in model_name:
                logger.info(f"✅ Model '{model_name}' is available")
                return True, f"Model '{model_name}' is available"
        
        logger.warning(f"⚠️ Model '{model_name}' not found. Available: {models}")
        return False, f"Model '{model_name}' not found. Available: {', '.join(models)}"
    
    def pull_model(self, model_name: str, progress_callback=None) -> Tuple[bool, str]:
        """
        Pull a model from Ollama registry
        
        Args:
            model_name: Name of the model to pull
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        try:
            logger.info(f"🔄 Attempting to pull model: {model_name}")
            
            # Use ollama pull command
            process = subprocess.Popen(
                ['ollama', 'pull', model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Stream output for progress tracking
            for line in process.stdout:
                line = line.strip()
                if line:
                    logger.info(f"📥 {line}")
                    if progress_callback:
                        progress_callback(line)
            
            process.wait()
            
            if process.returncode == 0:
                logger.info(f"✅ Successfully pulled model: {model_name}")
                return True, f"Model '{model_name}' pulled successfully"
            else:
                error = process.stderr.read() if process.stderr else "Unknown error"
                logger.error(f"❌ Failed to pull model: {error}")
                return False, f"Failed to pull model: {error}"
                
        except FileNotFoundError:
            logger.error("❌ 'ollama' command not found. Is Ollama installed?")
            return False, "Ollama CLI not found. Is Ollama installed?"
        except Exception as e:
            logger.error(f"❌ Error pulling model: {str(e)}")
            return False, f"Error pulling model: {str(e)}"
    
    def ensure_model_available(self, model_name: str, auto_pull: bool = True) -> Tuple[bool, str]:
        """
        Ensure a model is available, optionally pulling it if missing
        
        Args:
            model_name: Name of the model
            auto_pull: Whether to automatically pull the model if missing
            
        Returns:
            Tuple[bool, str]: (success, message)
        """
        # First check server health
        is_healthy, health_msg = self.check_server_health()
        if not is_healthy:
            return False, f"Ollama server not available: {health_msg}"
        
        # Check if model is available
        is_available, availability_msg = self.is_model_available(model_name)
        if is_available:
            return True, availability_msg
        
        # If not available and auto_pull is enabled, try to pull it
        if auto_pull:
            logger.info(f"🔄 Model not available, attempting to pull: {model_name}")
            return self.pull_model(model_name)
        else:
            return False, f"Model not available: {availability_msg}"
    
    def get_health_status(self) -> Dict:
        """
        Get comprehensive health status
        
        Returns:
            Dict with server health, available models, and status
        """
        is_healthy, health_msg = self.check_server_health()
        success, models, models_msg = self.get_available_models()
        
        return {
            'server_healthy': is_healthy,
            'server_message': health_msg,
            'models_available': success,
            'models': models if success else [],
            'models_count': len(models) if success else 0,
            'timestamp': datetime.utcnow().isoformat()
        }


# Singleton instance
_ollama_health_service = None


def get_ollama_health_service(ollama_base_url: str = "http://localhost:11434") -> OllamaHealthService:
    """Get or create singleton instance of OllamaHealthService"""
    global _ollama_health_service
    if _ollama_health_service is None:
        _ollama_health_service = OllamaHealthService(ollama_base_url)
    return _ollama_health_service

