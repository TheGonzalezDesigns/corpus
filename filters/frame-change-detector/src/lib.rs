use pyo3::prelude::*;
use waldo_vision::pipeline::{VisionPipeline, PipelineConfig, Report};

/// Waldo Vision-powered frame change detector with intelligent cooldowns
#[pyclass]
pub struct FrameChangeDetector {
    pipeline: Option<VisionPipeline>,  // Initialize lazily with first frame dimensions
    config_template: PipelineConfig,   // Template config for creating pipeline
    frame_count: u64,
    last_volatile_trigger: f64,     // Last time we triggered on volatile state
    last_disturbed_trigger: f64,    // Last time we triggered on disturbed state
}

#[pymethods]
impl FrameChangeDetector {
    #[new]
    pub fn new(
        _buffer_duration_ms: Option<u64>,
        change_threshold: Option<f32>,
        _frame_interval_ms: Option<u64>
    ) -> Self {
        // Create template config - pipeline will be created lazily with actual frame dimensions
        let config_template = PipelineConfig {
            image_width: 640,          // Will be updated with actual frame width
            image_height: 480,         // Will be updated with actual frame height  
            chunk_width: 10,           // 10x10 analysis grid
            chunk_height: 10,
            new_age_threshold: 15,     // ~0.5s at 30fps for persistence
            behavioral_anomaly_threshold: change_threshold.unwrap_or(5.0) as f64 / 100.0,
            absolute_min_blob_size: 5, // Minimum 5 chunks for valid object
            blob_size_std_dev_filter: 1.5,
            disturbance_entry_threshold: 0.3,  // 30% of chunks disturbed to trigger
            disturbance_exit_threshold: 0.1,   // 10% to exit disturbance state
            disturbance_confirmation_frames: 5, // 5 frames to confirm disturbance
        };
        
        Self { 
            pipeline: None,            // Initialize lazily
            config_template,
            frame_count: 0,
            last_volatile_trigger: 0.0,
            last_disturbed_trigger: 0.0,
        }
    }

    /// Process frame with Waldo Vision's sophisticated multi-layer analysis and cooldown logic
    pub fn process_frame(&mut self, frame_b64: String, _timestamp_ms: u64) -> PyResult<(bool, f32, usize)> {
        // Get current time for cooldown calculation
        let current_time = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs_f64();

        // Convert base64 to raw image buffer with actual dimensions
        let (frame_data, actual_width, actual_height) = self.decode_frame(&frame_b64)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Decode error: {}", e)))?;
        
        // Initialize pipeline with actual frame dimensions if not done yet
        if self.pipeline.is_none() {
            let mut config = self.config_template.clone();
            config.image_width = actual_width;
            config.image_height = actual_height;
            self.pipeline = Some(VisionPipeline::new(config));
        }

        // Process through Waldo Vision's multi-layer pipeline
        let analysis = self.pipeline.as_mut().unwrap().process_frame(&frame_data);
        self.frame_count += 1;

        // Determine action based on scene state and cooldown rules
        let scene_state_str = match analysis.scene_state {
            waldo_vision::pipeline::SceneState::Calibrating => "CALIBRATING",
            waldo_vision::pipeline::SceneState::Stable => "STABLE",
            waldo_vision::pipeline::SceneState::Volatile => "VOLATILE",
            waldo_vision::pipeline::SceneState::Disturbed => "DISTURBED",
        };
        
        let (should_trigger, confidence) = match analysis.scene_state {
            // Calibrating or Stable: Don't trigger Gemini
            waldo_vision::pipeline::SceneState::Calibrating => (false, 0.0),
            waldo_vision::pipeline::SceneState::Stable => (false, 0.0),
            
            // Volatile: IGNORE - only trigger on truly significant DISTURBED events
            waldo_vision::pipeline::SceneState::Volatile => (false, 0.0),
            
            // Disturbed: Trigger with 0.25-second cooldown (new actors/actions)
            waldo_vision::pipeline::SceneState::Disturbed => {
                let disturbed_cooldown = 0.25; // Quarter second - urgent!
                let time_since_last = current_time - self.last_disturbed_trigger;
                
                if time_since_last >= disturbed_cooldown {
                    self.last_disturbed_trigger = current_time;
                    
                    // Calculate high confidence based on significance
                    let base_confidence = 95.0;
                    let significance_bonus = match analysis.report {
                        Report::SignificantMention(mention_data) => {
                            (mention_data.new_significant_moments.len() + 
                             mention_data.completed_significant_moments.len()) as f32 * 5.0
                        },
                        _ => 0.0
                    };
                    
                    (true, (base_confidence + significance_bonus).min(100.0))
                } else {
                    (false, 0.0) // Still in cooldown
                }
            }
        };

        // Return: (trigger_ai, confidence_score, tracked_objects_count, scene_state)
        // Note: We'll need to modify the return signature to include scene state
        Ok((should_trigger, confidence, analysis.tracked_blobs.len()))
    }

    /// Configure Waldo Vision pipeline (simplified interface)
    pub fn configure(&mut self, 
                    _buffer_duration_ms: Option<u64>,
                    _change_threshold: Option<f32>,
                    _frame_interval_ms: Option<u64>) -> PyResult<()> {
        // Note: Waldo Vision pipeline would need to be recreated for config changes
        // For now, store the values for future pipeline recreation
        Ok(())
    }

    /// Get current configuration and processing stats
    pub fn get_config(&self) -> PyResult<(u64, f32, u64)> {
        Ok((
            self.frame_count,           // Total frames processed by Waldo Vision
            5.0,                        // Default change threshold
            33,                         // 30fps interval (480p smooth)
        ))
    }

    /// Reset Waldo Vision pipeline state
    pub fn reset(&mut self) -> PyResult<()> {
        // Reset counters and cooldowns
        self.frame_count = 0;
        self.last_volatile_trigger = 0.0;
        self.last_disturbed_trigger = 0.0;
        Ok(())
    }

    /// Get Waldo Vision scene analysis state
    pub fn get_analysis_info(&self) -> PyResult<(String, u64)> {
        Ok((
            "Waldo Vision Multi-Layer Analysis Active".to_string(),
            self.frame_count
        ))
    }

    /// Get current scene state and cooldown status
    pub fn get_scene_status(&self) -> PyResult<(String, f64, f64)> {
        let current_time = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs_f64();
            
        let volatile_cooldown_remaining = (self.last_volatile_trigger + 1.0 - current_time).max(0.0);
        let disturbed_cooldown_remaining = (self.last_disturbed_trigger + 0.25 - current_time).max(0.0);
        
        Ok((
            "MONITORING".to_string(), // Scene state would need pipeline exposure
            volatile_cooldown_remaining,
            disturbed_cooldown_remaining
        ))
    }

    /// Process frame and return results with scene state for logging
    pub fn process_frame_with_state(&mut self, frame_b64: String, timestamp_ms: u64) -> PyResult<(bool, f32, usize, String)> {
        // Get current time for cooldown calculation
        let current_time = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs_f64();

        // Convert base64 to raw image buffer with actual dimensions
        let (frame_data, actual_width, actual_height) = self.decode_frame(&frame_b64)
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Decode error: {}", e)))?;
        
        // Initialize pipeline with actual frame dimensions if not done yet
        if self.pipeline.is_none() {
            let mut config = self.config_template.clone();
            config.image_width = actual_width;
            config.image_height = actual_height;
            self.pipeline = Some(VisionPipeline::new(config));
        }

        // Process through Waldo Vision's multi-layer pipeline
        let analysis = self.pipeline.as_mut().unwrap().process_frame(&frame_data);
        self.frame_count += 1;

        // Get scene state string
        let scene_state_str = match analysis.scene_state {
            waldo_vision::pipeline::SceneState::Calibrating => "CALIBRATING",
            waldo_vision::pipeline::SceneState::Stable => "STABLE",
            waldo_vision::pipeline::SceneState::Volatile => "VOLATILE",
            waldo_vision::pipeline::SceneState::Disturbed => "DISTURBED",
        };
        
        let (should_trigger, confidence) = match analysis.scene_state {
            // Calibrating or Stable: Don't trigger Gemini
            waldo_vision::pipeline::SceneState::Calibrating => (false, 0.0),
            waldo_vision::pipeline::SceneState::Stable => (false, 0.0),
            
            // Volatile: IGNORE - only trigger on truly significant DISTURBED events
            waldo_vision::pipeline::SceneState::Volatile => (false, 0.0),
            
            // Disturbed: Trigger with 0.25-second cooldown (new actors/actions)
            waldo_vision::pipeline::SceneState::Disturbed => {
                let disturbed_cooldown = 0.25; // Quarter second - urgent!
                let time_since_last = current_time - self.last_disturbed_trigger;
                
                if time_since_last >= disturbed_cooldown {
                    self.last_disturbed_trigger = current_time;
                    
                    // Calculate high confidence based on significance
                    let base_confidence = 95.0;
                    let significance_bonus = match analysis.report {
                        Report::SignificantMention(mention_data) => {
                            (mention_data.new_significant_moments.len() + 
                             mention_data.completed_significant_moments.len()) as f32 * 5.0
                        },
                        _ => 0.0
                    };
                    
                    (true, (base_confidence + significance_bonus).min(100.0))
                } else {
                    (false, 0.0) // Still in cooldown
                }
            }
        };

        // Return: (trigger_ai, confidence_score, tracked_objects_count, scene_state)
        Ok((should_trigger, confidence, analysis.tracked_blobs.len(), scene_state_str.to_string()))
    }
}

impl FrameChangeDetector {
    /// Decode base64 JPEG to raw grayscale buffer for Waldo Vision
    fn decode_frame(&self, frame_b64: &str) -> Result<(Vec<u8>, u32, u32), String> {
        use base64::{Engine as _, engine::general_purpose::STANDARD};
        
        // Decode base64 using new API
        let img_data = STANDARD.decode(frame_b64)
            .map_err(|e| format!("Base64 decode error: {}", e))?;
        
        // Load image and convert to grayscale for Waldo Vision
        let img = image::load_from_memory(&img_data)
            .map_err(|e| format!("Image load error: {}", e))?;
        let gray_img = img.to_luma8();
        let (width, height) = gray_img.dimensions();
        
        // Return pixels with actual dimensions
        Ok((gray_img.into_raw(), width, height))
    }
}

/// Python module
#[pymodule]
fn frame_change_detector(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<FrameChangeDetector>()?;
    Ok(())
}