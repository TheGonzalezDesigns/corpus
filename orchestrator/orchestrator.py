import requests
import yaml
import logging
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class CapabilityStatus(Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    ERROR = "error"

@dataclass
class Capability:
    name: str
    url: str
    status: CapabilityStatus = CapabilityStatus.OFFLINE
    last_error: Optional[str] = None

class CorpusOrchestrator:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.capabilities: Dict[str, Capability] = {}
        self._initialize_capabilities()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logging.warning(f"Config file {config_path} not found, using defaults")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        return {
            'capabilities': {
                'speech': {'url': 'http://localhost:5001'},
                'vision': {'url': 'http://localhost:5002'},
                'audio': {'url': 'http://localhost:5003'},
                'brain': {'url': 'http://localhost:5004'}
            }
        }
    
    def _initialize_capabilities(self):
        for name, config in self.config['capabilities'].items():
            self.capabilities[name] = Capability(
                name=name,
                url=config['url']
            )
    
    async def check_capability_status(self, capability_name: str) -> bool:
        if capability_name not in self.capabilities:
            return False
            
        capability = self.capabilities[capability_name]
        try:
            response = requests.get(f"{capability.url}/status", timeout=5)
            if response.status_code == 200:
                capability.status = CapabilityStatus.ONLINE
                capability.last_error = None
                return True
        except Exception as e:
            capability.status = CapabilityStatus.ERROR
            capability.last_error = str(e)
            logging.error(f"Capability {capability_name} check failed: {e}")
        
        return False
    
    async def check_all_capabilities(self):
        tasks = [
            self.check_capability_status(name) 
            for name in self.capabilities.keys()
        ]
        await asyncio.gather(*tasks)
    
    def speak(self, text: str) -> bool:
        if 'speech' not in self.capabilities:
            logging.error("Speech capability not configured")
            return False
            
        capability = self.capabilities['speech']
        if capability.status != CapabilityStatus.ONLINE:
            logging.error("Speech capability is offline")
            return False
        
        try:
            response = requests.post(
                f"{capability.url}/speak",
                json={'text': text},
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Failed to speak: {e}")
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        return {
            'capabilities': {
                name: {
                    'status': cap.status.value,
                    'url': cap.url,
                    'last_error': cap.last_error
                }
                for name, cap in self.capabilities.items()
            }
        }
    
    async def process_command(self, command: str) -> str:
        # Basic command processing - expand this based on your needs
        if command.startswith("say "):
            text = command[4:]
            success = self.speak(text)
            return "Spoken successfully" if success else "Failed to speak"
        
        return "Unknown command"