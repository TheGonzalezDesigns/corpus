from flask import Flask, request
from flask_restx import Api, Resource, fields
import logging
import yaml
from pipeline_orchestrator import PipelineOrchestrator

app = Flask(__name__)
api = Api(app,
    version='1.0',
    title='Corpus Pipeline Orchestrator API', 
    description='Advanced pipeline coordination API for Corpus AI companion with vision→speech integration',
    doc='/swagger'
)

logging.basicConfig(level=logging.INFO)

# Initialize pipeline orchestrator
orchestrator = PipelineOrchestrator()

# Define API models
speak_model = api.model('SpeakRequest', {
    'text': fields.String(required=True, description='Text to speak via speech capability', 
                         example='Hello! I am your AI companion.')
})

command_model = api.model('CommandRequest', {
    'command': fields.String(required=True, description='Command to process', 
                           example='see and say')
})

pipeline_config_model = api.model('PipelineConfig', {
    'interval_ms': fields.Integer(description='Interval between executions in milliseconds', example=5000, default=5000),
    'voice_id': fields.String(description='Voice ID for speech synthesis', example='ito', default='ito'),
    'emotion': fields.String(description='Emotional context for descriptions', example='observant', default='observant')
})

pipeline_start_model = api.model('PipelineStartRequest', {
    'pipeline_id': fields.String(required=True, description='Unique identifier for the pipeline', example='vision_speech_01'),
    'config': fields.Nested(pipeline_config_model, description='Pipeline configuration')
})

pipeline_stop_model = api.model('PipelineStopRequest', {
    'pipeline_id': fields.String(required=True, description='Pipeline ID to stop', example='vision_speech_01')
})

success_response = api.model('SuccessResponse', {
    'status': fields.String(description='Response status'),
    'message': fields.String(description='Response message')
})

error_response = api.model('ErrorResponse', {
    'error': fields.String(description='Error message')
})

command_response = api.model('CommandResponse', {
    'result': fields.String(description='Command execution result')
})

system_status_response = api.model('SystemStatusResponse', {
    'capabilities': fields.Raw(description='Status of all capabilities'),
    'pipelines': fields.Raw(description='Status of all pipelines')
})

@api.route('/status')
class Status(Resource):
    @api.response(200, 'Success', system_status_response)
    def get(self):
        """Get overall system status including capabilities and pipelines"""
        return orchestrator.get_system_status()

@api.route('/speak')
class Speak(Resource):
    @api.expect(speak_model)
    @api.response(200, 'Success', success_response)
    @api.response(400, 'Bad Request', error_response) 
    @api.response(500, 'Internal Server Error', error_response)
    def post(self):
        """Send text to speech capability for audio output"""
        data = request.get_json()
        if not data or 'text' not in data:
            return {"error": "Missing 'text' field"}, 400
        
        success = orchestrator.speak(data['text'])
        if success:
            return {"status": "success", "message": "Text spoken"}
        else:
            return {"error": "Failed to speak text"}, 500

@api.route('/vision/describe')
class VisionDescribe(Resource):
    @api.response(200, 'Success')
    @api.response(500, 'Internal Server Error', error_response)
    def get(self):
        """Get description from vision capability"""
        description = orchestrator.get_vision_description()
        if description:
            return {"status": "success", "description": description}
        else:
            return {"error": "Failed to get vision description"}, 500

@api.route('/pipeline/execute')
class PipelineExecute(Resource):
    @api.expect(pipeline_config_model)
    @api.response(200, 'Success', success_response)
    @api.response(500, 'Internal Server Error', error_response)
    def post(self):
        """Execute a single vision→speech pipeline operation"""
        data = request.get_json() or {}
        
        success = orchestrator.pipe_vision_to_speech(data)
        if success:
            return {"status": "success", "message": "Vision→Speech pipeline executed successfully"}
        else:
            return {"error": "Pipeline execution failed"}, 500

@api.route('/pipeline/start')
class PipelineStart(Resource):
    @api.expect(pipeline_start_model)
    @api.response(200, 'Success', success_response)
    @api.response(400, 'Bad Request', error_response)
    @api.response(500, 'Internal Server Error', error_response)
    def post(self):
        """Start a continuous vision→speech pipeline"""
        data = request.get_json()
        if not data or 'pipeline_id' not in data:
            return {"error": "Missing 'pipeline_id' field"}, 400
        
        pipeline_id = data['pipeline_id']
        config = data.get('config', {
            'interval_ms': 5000,
            'voice_id': 'ito',
            'emotion': 'observant'
        })
        
        success = orchestrator.start_continuous_pipeline(pipeline_id, config)
        if success:
            return {
                "status": "success", 
                "message": f"Continuous pipeline '{pipeline_id}' started",
                "config": config
            }
        else:
            return {"error": f"Failed to start pipeline '{pipeline_id}'"}, 500

@api.route('/pipeline/stop')
class PipelineStop(Resource):
    @api.expect(pipeline_stop_model)
    @api.response(200, 'Success', success_response)
    @api.response(400, 'Bad Request', error_response)
    @api.response(404, 'Not Found', error_response)
    def post(self):
        """Stop a continuous pipeline"""
        data = request.get_json()
        if not data or 'pipeline_id' not in data:
            return {"error": "Missing 'pipeline_id' field"}, 400
        
        pipeline_id = data['pipeline_id']
        success = orchestrator.stop_pipeline(pipeline_id)
        
        if success:
            return {"status": "success", "message": f"Pipeline '{pipeline_id}' stopped"}
        else:
            return {"error": f"Failed to stop pipeline '{pipeline_id}'"}, 500

@api.route('/pipeline/status')
@api.route('/pipeline/status/<string:pipeline_id>')
class PipelineStatus(Resource):
    @api.response(200, 'Success')
    @api.response(404, 'Not Found', error_response)
    def get(self, pipeline_id=None):
        """Get status of specific pipeline or all pipelines"""
        status = orchestrator.get_pipeline_status(pipeline_id)
        
        if 'error' in status:
            return status, 404
        else:
            return status

@api.route('/command')
class Command(Resource):
    @api.expect(command_model)
    @api.response(200, 'Success', command_response)
    @api.response(400, 'Bad Request', error_response)
    def post(self):
        """Process a high-level command with pipeline support"""
        data = request.get_json()
        if not data or 'command' not in data:
            return {"error": "Missing 'command' field"}, 400
        
        try:
            result = orchestrator.process_command(data['command'])
            return {"result": result}
        except Exception as e:
            return {"error": f"Command processing failed: {str(e)}"}, 500

@api.route('/capabilities')
class Capabilities(Resource):
    @api.response(200, 'Success')
    def get(self):
        """List all available capabilities and their endpoints"""
        capabilities_info = {}
        for name, capability in orchestrator.capabilities.items():
            capabilities_info[name] = {
                'url': capability.url,
                'status': capability.status.value,
                'endpoints': {
                    'speech': ['/speak', '/status', '/config', '/voices'],
                    'vision': ['/capture', '/analyze', '/describe', '/start_loop', '/stop_loop', '/config'],
                    'audio': ['(not implemented)'],
                    'brain': ['(not implemented)'],
                    'wings': ['(not implemented)']
                }.get(name, ['(unknown)'])
            }
        
        return {
            'available_capabilities': capabilities_info,
            'orchestrator_endpoints': [
                '/status', '/speak', '/command', 
                '/vision/describe', '/pipeline/execute', 
                '/pipeline/start', '/pipeline/stop', '/pipeline/status'
            ],
            'pipeline_features': [
                'Single-shot vision→speech execution',
                'Continuous vision→speech streaming', 
                'Configurable intervals and voice settings',
                'Pipeline status monitoring and control',
                'Emotional context enhancement'
            ]
        }

# Clean up on shutdown
import atexit
atexit.register(orchestrator.cleanup)

if __name__ == '__main__':
    # Load config
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        orchestrator_config = config.get('orchestrator', {})
    except:
        orchestrator_config = {'host': '0.0.0.0', 'port': 5000}
    
    app.run(
        host=orchestrator_config.get('host', '0.0.0.0'),
        port=orchestrator_config.get('port', 5000),
        debug=False
    )