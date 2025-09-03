# 🚨 Known Issues & Limitations

**For the next developer working on Corpus AI Companion**

---

## 🔥 **Critical Issues**

### **🎥 Camera Device Management**
- **Issue**: Camera device IDs change unpredictably (0 → 1 → 3)
- **Impact**: System fails to start if camera moved to different device
- **Workaround**: Manual config.yaml updates or device scanning
- **Fix Needed**: Automatic camera detection and device enumeration

### **📝 Logging System Problems**  
- **Issue**: Timestamp format shows `%f` literally instead of microseconds
- **Impact**: Log analysis and debugging is impaired
- **Workaround**: Ignore timestamp precision, focus on sequence
- **Fix Needed**: Correct datetime formatting in waldo_vision_logger.py

### **💾 Memory Management**
- **Issue**: Long-running monitoring accumulates memory without cleanup
- **Impact**: Raspberry Pi may run out of memory over days/weeks
- **Workaround**: Periodic restarts via cron job
- **Fix Needed**: Implement garbage collection and memory monitoring

---

## ⚠️ **Operational Limitations**

### **🔌 Service Dependencies**
- **Limitation**: No graceful degradation if one service fails
- **Impact**: Entire system stops if any component crashes
- **Current State**: Manual restart required
- **Improvement Needed**: Auto-restart and fallback modes

### **🌐 Internet Dependencies**
- **Limitation**: Requires internet for voice list (101 API calls on startup)
- **Impact**: Slow startup, fails in offline scenarios
- **Current State**: No offline mode or voice caching
- **Improvement Needed**: Local voice list caching and offline fallback

### **⚙️ Configuration Persistence**
- **Limitation**: Settings don't persist between restarts
- **Impact**: Must reconfigure voice/camera settings each time
- **Current State**: Configuration via API calls only
- **Improvement Needed**: Persistent config file and live updates

---

## 🐛 **Untested Scenarios**

### **🔄 Long-term Stability**
- **Untested**: System running for days/weeks continuously
- **Potential Issues**: Memory leaks, log file gigabytes, API rate limiting
- **Risk Level**: High for production deployment

### **📱 Multiple Users**
- **Untested**: Multiple people in camera view simultaneously  
- **Potential Issues**: Rapid state changes, speech overlap, confusion
- **Risk Level**: Medium for household use

### **🌐 Network Interruptions**
- **Untested**: Internet disconnection during operation
- **Potential Issues**: API failures, service crashes, no recovery
- **Risk Level**: High for unreliable connections

### **🎚️ Audio Conflicts**
- **Untested**: Other audio applications running simultaneously
- **Potential Issues**: Pygame conflicts, audio device locks, distorted output
- **Risk Level**: Medium for multi-purpose Pi usage

---

## 🔧 **Quick Fixes Needed**

### **High Priority:**
1. **Fix timestamp logging** in waldo_vision_logger.py (line 44)
2. **Add camera device auto-detection** in corpus_vision.py
3. **Implement log rotation** for waldo_vision.log  
4. **Add memory usage monitoring** to prevent Pi crashes

### **Medium Priority:**
1. **Add service health checks** with auto-restart
2. **Implement voice list caching** for offline operation
3. **Add configuration persistence** between restarts
4. **Improve error messages** and user feedback

### **Low Priority:**
1. **Add graceful shutdown** signal handling
2. **Implement rate limiting** for Hume TTS API
3. **Add audio device selection** options
4. **Create mobile control interface**

---

## 💡 **Development Guidelines**

### **Before Making Changes:**
1. **Test with the startup script** (`./start_corpus.sh`)
2. **Monitor memory usage** during long runs
3. **Check camera device ID** after any USB changes
4. **Verify API key environment variables** are set
5. **Test camera conflicts** with other applications

### **When Adding Features:**
1. **Add proper error handling** with user-visible messages
2. **Implement graceful fallbacks** for service failures
3. **Consider memory implications** for long-running operations  
4. **Add logging** for debugging and monitoring
5. **Update documentation** with new caveats and limitations

---

## 🎯 **Current Stability Assessment**

### **✅ Production Ready For:**
- **Short-term use** (hours to days)
- **Single user scenarios** 
- **Reliable internet connection**
- **Dedicated Raspberry Pi** (not shared with other apps)

### **⚠️ Needs Work For:**
- **Long-term deployment** (weeks to months)
- **Multi-user environments**
- **Offline operation** 
- **Shared system resources**

---

**The system is functionally complete and impressive, but has the typical rough edges of a sophisticated prototype that needs production hardening.** 🛠️✨