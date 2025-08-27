import requests
import yaml
import logging
import asyncio
import threading
import time
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class CapabilityStatus(Enum):
    OFFLINE = "offline"
    ONLINE = "online"
    ERROR = "error"

class PipelineStatus(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    ERROR = "error"

@dataclass
class Capability:
    name: str
    url: str
    status: CapabilityStatus = CapabilityStatus.OFFLINE
    last_error: Optional[str] = None

@dataclass  
class Pipeline:
    id: str
    components: list
    status: PipelineStatus = PipelineStatus.STOPPED
    config: Dict[str, Any] = None
    thread: threading.Thread = None
    stop_flag: bool = False
    stats: Dict[str, Any] = None

class PipelineOrchestrator:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.capabilities: Dict[str, Capability] = {}
        self.pipelines: Dict[str, Pipeline] = {}
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
        """Direct speech API call"""
        if 'speech' not in self.capabilities:
            logging.error("Speech capability not configured")
            return False
            
        capability = self.capabilities['speech']
        try:
            response = requests.post(
                f"{capability.url}/speak",
                json={'text': text},
                timeout=30
            )
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Failed to speak: {e}")
            return False
    
    def get_vision_description(self) -> Optional[str]:
        """Get description from vision API"""
        if 'vision' not in self.capabilities:
            logging.error("Vision capability not configured")
            return None
            
        capability = self.capabilities['vision']
        try:
            response = requests.post(f"{capability.url}/analyze", timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data.get('description')
            else:
                logging.error(f"Vision API returned status {response.status_code}")
                return None
        except Exception as e:
            logging.error(f"Failed to get vision description: {e}")
            return None
    
    def vision_to_speech_transform(self, description: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Transform vision description for speech API"""
        if not config:
            config = {}
            
        # Enhance description with emotional context
        enhanced_description = self._add_emotional_context(description, config)
        
        return {
            'text': enhanced_description,
            'voice_config': {
                'voice_id': config.get('voice_id', 'ito'),
                'emotion': config.get('emotion', 'conversational'),
                'context': 'visual_observation'
            }
        }
    
    def _add_emotional_context(self, description: str, config: Dict[str, Any]) -> str:
        """Add emotional context to descriptions"""
        emotion_prefixes = {
            'calm': "In this peaceful moment, ",
            'excited': "I'm excited to see that ",
            'curious': "I'm curious about what I'm seeing - ",
            'observant': "I notice that "
        }
        
        emotion = config.get('emotion', 'observant')
        prefix = emotion_prefixes.get(emotion, "I can see that ")
        
        return prefix + description.lower()
    
    def pipe_vision_to_speech(self, config: Dict[str, Any] = None) -> bool:
        """Single vision→speech pipeline execution"""
        try:
            # Get vision description
            description = self.get_vision_description()
            if not description:
                return False
            
            # Transform for speech
            speech_data = self.vision_to_speech_transform(description, config)
            
            # Send to speech API
            return self.speak(speech_data['text'])
            
        except Exception as e:
            logging.error(f"Pipeline execution failed: {e}")
            return False
    
    def start_continuous_pipeline(self, pipeline_id: str, config: Dict[str, Any]) -> bool:
        """Start continuous vision→speech pipeline"""
        if pipeline_id in self.pipelines and self.pipelines[pipeline_id].status == PipelineStatus.RUNNING:
            logging.warning(f"Pipeline {pipeline_id} is already running")
            return False
        
        # Create pipeline object
        pipeline = Pipeline(
            id=pipeline_id,
            components=['vision', 'speech'],
            config=config,
            stats={'executions': 0, 'successes': 0, 'start_time': time.time()}
        )
        
        # Start pipeline thread
        pipeline.thread = threading.Thread(
            target=self._continuous_pipeline_worker,
            args=(pipeline,),
            daemon=True
        )
        
        pipeline.status = PipelineStatus.RUNNING
        self.pipelines[pipeline_id] = pipeline
        pipeline.thread.start()
        
        logging.info(f"Started continuous pipeline: {pipeline_id}")
        return True
    
    def _continuous_pipeline_worker(self, pipeline: Pipeline):
        """Worker function for continuous pipeline execution"""
        interval = pipeline.config.get('interval_ms', 5000) / 1000.0
        
        while not pipeline.stop_flag:
            try:
                # Execute pipeline
                pipeline.stats['executions'] += 1
                success = self.pipe_vision_to_speech(pipeline.config)
                
                if success:
                    pipeline.stats['successes'] += 1
                    logging.info(f"Pipeline {pipeline.id} executed successfully")
                else:
                    logging.warning(f"Pipeline {pipeline.id} execution failed")
                
                # Wait for next execution
                time.sleep(interval)
                
            except Exception as e:
                logging.error(f"Pipeline {pipeline.id} worker error: {e}")
                pipeline.status = PipelineStatus.ERROR
                break
        
        logging.info(f"Pipeline {pipeline.id} worker stopped")
    
    def stop_pipeline(self, pipeline_id: str) -> bool:
        """Stop continuous pipeline"""
        if pipeline_id not in self.pipelines:
            logging.warning(f"Pipeline {pipeline_id} not found")
            return False
        
        pipeline = self.pipelines[pipeline_id]
        pipeline.stop_flag = True
        pipeline.status = PipelineStatus.STOPPED
        
        # Wait for thread to finish
        if pipeline.thread and pipeline.thread.is_alive():
            pipeline.thread.join(timeout=2)
        
        logging.info(f"Stopped pipeline: {pipeline_id}")
        return True
    
    def get_pipeline_status(self, pipeline_id: str = None) -> Dict[str, Any]:
        """Get status of specific pipeline or all pipelines"""
        if pipeline_id:
            if pipeline_id not in self.pipelines:
                return {"error": f"Pipeline {pipeline_id} not found"}
            
            pipeline = self.pipelines[pipeline_id]
            return {
                'id': pipeline.id,
                'status': pipeline.status.value,
                'components': pipeline.components,
                'config': pipeline.config,
                'stats': pipeline.stats
            }
        else:
            return {
                'pipelines': {
                    pid: {
                        'id': p.id,
                        'status': p.status.value,
                        'components': p.components,
                        'stats': p.stats
                    }
                    for pid, p in self.pipelines.items()
                }
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            'capabilities': {
                name: {
                    'status': cap.status.value,
                    'url': cap.url,
                    'last_error': cap.last_error
                }
                for name, cap in self.capabilities.items()
            },
            'pipelines': {
                pid: p.status.value for pid, p in self.pipelines.items()
            }
        }
    
    async def process_command(self, command: str) -> str:
        """Enhanced command processing with pipeline support"""
        if command.startswith("say "):
            text = command[4:]
            success = self.speak(text)
            return "Spoken successfully" if success else "Failed to speak"
        
        elif command.startswith("see and say"):
            success = self.pipe_vision_to_speech()
            return "Vision→Speech pipeline executed" if success else "Pipeline execution failed"
            
        elif command.startswith("start continuous vision"):
            config = {'interval_ms': 5000, 'voice_id': 'ito', 'emotion': 'observant'}
            success = self.start_continuous_pipeline('default_vision_speech', config)
            return "Continuous vision→speech started" if success else "Failed to start pipeline"
            
        elif command.startswith("stop continuous"):
            success = self.stop_pipeline('default_vision_speech')
            return "Continuous pipeline stopped" if success else "Failed to stop pipeline"
        
        return "Unknown command"
    
    def cleanup(self):
        """Clean up all running pipelines"""
        for pipeline_id in list(self.pipelines.keys()):
            self.stop_pipeline(pipeline_id)