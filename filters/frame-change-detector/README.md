# Frame Change Detector

High-performance Rust-based filter for detecting significant changes between video frames in the Corpus AI vision pipeline.

## Purpose

This filter analyzes frames captured every 20ms and determines if there's sufficient visual change to trigger expensive AI processing. This prevents unnecessary API calls when the scene is static while maintaining responsiveness to actual changes.

## Algorithm Overview

1. **Frame Buffer**: Maintains 100ms sliding window of frames
2. **Pixel Comparison**: Compares current frame against buffer frames  
3. **Change Calculation**: Calculates percentage of pixels that changed
4. **Threshold Decision**: Returns `true` if change exceeds threshold, `false` otherwise

## Configuration

- `buffer_duration_ms`: How long to keep frames for comparison (default: 100ms)
- `change_threshold`: Percentage change required to trigger (default: 5.0%)
- `frame_interval_ms`: Expected time between frames (default: 20ms)

## Performance

- **Target**: Sub-millisecond processing per frame
- **Memory**: Circular buffer prevents memory leaks
- **CPU**: Optimized for real-time video processing

## Usage

```python
from frame_change_detector import FrameChangeDetector

detector = FrameChangeDetector(
    buffer_duration_ms=100,
    change_threshold=5.0,
    frame_interval_ms=20
)

# Process frame (base64 encoded)
should_trigger, change_pct, buffer_size = detector.process_frame(frame_b64, timestamp_ms)

if should_trigger:
    # Trigger expensive AI analysis
    pass
```

## Integration

This filter integrates with the vision WebSocket pipeline:
1. Vision captures frames every 20ms
2. Rust filter processes each frame  
3. Only "changed" frames trigger Gemini analysis + speech
4. Saves API costs while maintaining responsiveness

## Building

```bash
pip install maturin
maturin develop --release
```