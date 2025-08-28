# 🦀 Setting Up the Rust Frame Change Filter

The intelligent frame change detection filter that saves API costs by only triggering AI analysis when significant visual changes occur.

## 🛠️ **Prerequisites**

### Install Rust (if not already installed)
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source ~/.cargo/env
```

### Install Python dependencies
```bash
cd capabilities/vision
source venv/bin/activate
pip install -r requirements.txt
```

## 🔧 **Build the Filter**

```bash
cd filters/frame-change-detector
chmod +x build.sh
./build.sh
```

This will:
1. Install maturin (Rust-Python bridge)
2. Build the Rust extension
3. Install it in your Python environment

## 🚀 **Architecture Overview**

### **Pipeline Flow:**
```
Camera (20ms) → Rust Filter → [Change?] → AI Analysis → Speech
     50fps         <1ms        Yes/No      3-5s        2-4s
```

### **Performance Benefits:**
- **Without filter**: 50 AI calls/second = 180,000 calls/hour 💸💸💸
- **With filter**: ~2-5 AI calls/second = 7,200-18,000 calls/hour 💸
- **Cost savings**: ~90-95% reduction in API calls

## 🎛️ **Filter Configuration**

```python
detector = FrameChangeDetector(
    buffer_duration_ms=100,   # Compare against last 100ms of frames
    change_threshold=5.0,     # 5% pixel change triggers AI
    frame_interval_ms=20      # Expect frames every 20ms
)
```

## 🔌 **WebSocket Interface**

### **Start Filtered Stream:**
```javascript
socket.emit('start_filtered_stream', {
    frame_interval_ms: 20,
    change_threshold: 5.0,
    filter_enabled: true
});
```

### **Events Received:**
- `filtered_frame` - Frame with change detection results
- `ai_triggered` - When AI analysis is triggered
- `performance_stats` - Real-time efficiency metrics

## 🧪 **Testing**

### **Test Client:**
Open `test_websocket_client.html` in browser:
- Real-time frame preview
- Change detection visualization  
- Performance statistics
- Configuration controls

### **Manual Testing:**
```bash
cd capabilities/vision
source venv/bin/activate
python vision_filtered_websocket.py
```

Then open: `http://raspberrypi:5002/test_websocket_client.html`

## 🎯 **What You'll Implement**

In `/filters/frame-change-detector/src/lib.rs`, replace the `process_frame` method with your algorithm:

```rust
pub fn process_frame(&mut self, frame_b64: String, timestamp_ms: u64) -> PyResult<(bool, f32, usize)> {
    // 1. Decode base64 → image pixels
    // 2. Compare with frames in buffer (last 100ms)  
    // 3. Calculate percentage of changed pixels
    // 4. Return (change > threshold, change_percentage, buffer_size)
    
    // Your algorithm here...
}
```

## ✨ **Ready State**

Everything is set up! You just need to:
1. **Build the filter**: `./build.sh`
2. **Implement your algorithm** in `process_frame` method
3. **Test the pipeline** with the WebSocket client

The architecture handles:
- ✅ 50fps frame capture
- ✅ WebSocket streaming  
- ✅ Filter integration
- ✅ Conditional AI triggering
- ✅ Performance monitoring
- ✅ Speech pipeline integration

Ready for your algorithm! 🦀⚡