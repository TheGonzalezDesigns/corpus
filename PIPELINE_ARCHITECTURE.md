# 🔗 Corpus AI Companion - Pipeline Architecture

*Bash-style piping for AI components: `vision | analysis | speech | audio`*

---

## 🏗️ **Core Architecture Philosophy**

Each capability is an **isolated, upgradeable API service** that follows Unix pipe principles:
- **Standard Input/Output**: Consistent data formats between services
- **Composability**: Mix and match components freely
- **Independence**: Upgrade any component without breaking others
- **Scalability**: Run components on different machines/processes

---

## 🌊 **Data Flow Patterns**

### **Basic Pipeline: Vision → Speech**
```
Camera → Vision API → Gemini Analysis → Description → Speech API → Hume TTS → Audio Output
```

### **Debounced Event Windows (Alpha)**
```
Camera → Waldo Vision filter → [Aggregate triggers ≤ 4s or 250ms quiet]
       └─► On window close: summarize once (provider-routed) → Speech once
       └─► Persist JSONL event (ts, duration, frames_count, description)
       └─► Broadcast waldo_event over raw WebSocket (port 5010)
```


### **Enhanced Pipeline: Multi-Modal Processing**
```
Camera ─┐
        ├─→ Orchestrator ─→ Context Engine ─→ Speech API ─→ Audio
Audio ──┘                                   ↑
                                            │
                                         Emotional
                                         Intelligence
```

### **WebSocket Streaming Pipeline**
```
Continuous:  Vision Stream ──→ Analysis Stream ──→ Speech Stream ──→ Audio Stream
Control:     REST APIs     ──→ Configuration   ──→ Session Mgmt  ──→ Status
```

### Ingest Streaming & WS Digest (Current)
- Vision streams every processed frame (JPEG) to a remote EC2 WebSocket `INGEST_WS_URL`.
- A raw WebSocket hub (`ws://<host>:5010`, configurable with `LOG_WS_PORT`) broadcasts:
  - Real-time log/events (waldo_*)
  - A periodic ingest digest every ~2s with connection state and counters.

Vision Ingest Endpoints (Swagger at `http://raspberrypi:5002/swagger`):
- `GET /ingest/status` — connection state, `sent_count`, `queue_size`, `last_error`, `url`
- `POST /ingest/start` — start ingest worker and enable WS digest
- `POST /ingest/stop` — stop ingest worker and WS digest
- `POST /ingest/config` — set ingest URL at runtime (auto-restarts)

---

## 🔧 **API Contract Standards**

### **Vision API Output**
```json
{
  "timestamp": 1692304234,
  "image": {
    "format": "base64_jpeg",
    "resolution": "1920x1080",
    "data": "base64_encoded_image..."
  },
  "analysis": {
    "description": "I can see a person sitting at a desk working on a laptop...",
    "confidence": 0.95,
    "objects": ["person", "laptop", "desk"],
    "emotions": ["focused", "calm"],
    "context": "indoor_workspace"
  },
  "metadata": {
    "processing_time_ms": 245,
    "model": "gemini-1.5-flash"
  }
}
```

### **Speech API Input**
```json
{
  "text": "I can see a person sitting at a desk working on a laptop...",
  "voice_config": {
    "voice_id": "ito",
    "emotion": "calm",
    "context": "observational",
    "speed": 1.0
  },
  "output_format": "mp3",
  "metadata": {
    "source": "vision_analysis",
    "timestamp": 1692304234
  }
}
```

### **Pipeline Control Messages**
```json
{
  "command": "start_continuous_pipeline",
  "config": {
    "vision": {
      "interval_ms": 3000,
      "quality": "high"
    },
    "speech": {
      "voice_id": "ito",
      "auto_emotion": true
    }
  },
  "pipeline_id": "vision_speech_01"
}
```

---

## 🎛️ **Service Orchestration**

### **REST API Layer (Current)**
- **Control Plane**: Start/stop, configuration, status
- **Data Plane**: Single-shot processing requests
- **Synchronous**: Request → Response model

### **WebSocket Layer (Next Phase)**
- **Streaming Data**: Continuous real-time processing
- **Bi-directional**: Client ↔ Server communication  
- **Session-based**: Persistent connections with context

### **Orchestrator Role**
```python
class PipelineOrchestrator:
    def create_pipeline(self, components: List[str]) -> Pipeline:
        """Create a processing pipeline: vision | analysis | speech"""
        
    def start_continuous_mode(self, pipeline: Pipeline, config: Dict):
        """Start real-time streaming between components"""
        
    def pipe_data(self, source_api: str, dest_api: str, transform: Callable):
        """Pipe output from one API to input of another"""
```

---

## 🔄 **Pipeline Modes**

### **Mode 1: On-Demand Processing**
```bash
# REST API equivalent of: vision | speech
curl vision/describe | curl -d @- speech/speak
```

### **Mode 2: Continuous Loop**
```python
# Periodic processing with REST APIs
while running:
    description = vision_api.describe()
    speech_api.speak(description)
    sleep(interval)
```

### **Mode 3: Real-Time Streaming** *(Future WebSocket)*
```python
# Continuous streaming pipeline
vision_stream = VisionWebSocket()
speech_stream = SpeechWebSocket()
pipeline = vision_stream | analysis_filter | speech_stream
pipeline.start()
```

---

## 🎯 **Implementation Strategy**

### **Phase 1: REST Pipeline Integration** *(Current Focus)*
- ✅ Vision API returns descriptions
- ✅ Speech API accepts text input
- 🔄 Orchestrator pipes vision→speech
- 🔄 Continuous loop with configurable interval

### **Phase 2: WebSocket Foundation**
- 🚀 WebSocket endpoints for each service
- 🚀 Real-time data streaming
- 🚀 Session management and reconnection
- 🚀 Backpressure and flow control

### **Phase 3: Advanced Pipelines**
- 🌟 Multi-input fusion (vision + audio)
- 🌟 Context-aware processing chains
- 🌟 Emotional state propagation
- 🌟 Dynamic pipeline reconfiguration

---

## 📡 **Network Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vision API    │    │  Orchestrator   │    │   Speech API    │
│   Port 5002     │◄──►│   Port 5000     │◄──►│   Port 5001     │
│                 │    │                 │    │                 │
│ Camera → Gemini │    │ Pipeline Logic  │    │ Text → Hume TTS │
│ Description ────┼────┼─────────────────┼────┼─► Audio Output  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **API Endpoints for Piping**
```
# Vision API
GET  /capture          # Single image + analysis
GET  /describe          # Description with speech output
POST /start_continuous  # Begin continuous analysis
POST /stop_continuous   # End continuous analysis

# Speech API  
POST /speak             # Text → Audio
POST /speak_from_vision # Accept vision API format directly
GET  /voices            # Available voice configurations

# Orchestrator
POST /pipeline/start    # Start vision→speech pipeline
POST /pipeline/stop     # Stop pipeline
GET  /pipeline/status   # Pipeline state and metrics
POST /pipeline/config   # Update pipeline settings
```

---

## 🔀 **Data Transformation Layers**

### **Vision → Speech Adapter**
```python
def vision_to_speech_transform(vision_output: dict) -> dict:
    """Transform vision API output to speech API input"""
    return {
        "text": vision_output["analysis"]["description"],
        "voice_config": {
            "voice_id": "ito",
            "emotion": infer_emotion(vision_output["analysis"]["emotions"]),
            "context": vision_output["analysis"]["context"]
        }
    }
```

### **Emotion Context Pipeline**
```python
def add_emotional_context(description: str, visual_context: dict) -> str:
    """Enhance description with emotional awareness"""
    emotions = visual_context.get("emotions", [])
    if "peaceful" in emotions:
        return f"In this serene moment, {description}"
    elif "busy" in emotions:  
        return f"I notice the bustling activity where {description}"
    return description
```

---

## 🎮 **Control Interface**

### **Pipeline Commands**
```python
# Start continuous vision→speech with 5-second intervals
pipeline.start("vision|speech", interval=5000, voice="ito")

# Add emotion detection to the pipeline
pipeline.add_filter("emotion_enhancer", after="vision")

# Switch voice dynamically based on content
pipeline.add_conditional("voice_switcher", 
    condition=lambda data: "exciting" in data.emotions,
    action=lambda: switch_voice("aiden"))
```

### **Status Monitoring**
```json
{
  "pipeline_id": "vision_speech_01",
  "status": "running",
  "components": {
    "vision": {"status": "active", "fps": 0.33, "last_update": 1692304567},
    "speech": {"status": "active", "queue_length": 0, "last_spoken": 1692304565}
  },
  "metrics": {
    "uptime": 3600,
    "descriptions_generated": 1200,
    "audio_clips_played": 1198,
    "avg_processing_time_ms": 2847
  }
}
```

---

## 🚀 **Next Steps: Vision Integration**

1. **Create Pipeline Controller** in orchestrator
2. **Add vision→speech endpoints** for direct piping
3. **Implement continuous loop** with configurable intervals
4. **Test emotional speech** with vision context
5. **Prepare WebSocket foundation** for real-time streaming

**Goal**: `curl orchestrator/pipeline/start` → Your Pi continuously sees, understands, and speaks about its world with emotional intelligence! 🤖✨

---

*This architecture enables the dream: "Your AI companion that sees your world and speaks about it with genuine understanding and emotion."*
