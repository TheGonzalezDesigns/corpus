from flask import Flask, request
from flask_restx import Api, Resource, fields
import asyncio
import logging
import yaml
from orchestrator import CorpusOrchestrator

app = Flask(__name__)
api = Api(app,
    version='1.0',
    title='Corpus Orchestrator API', 
    description='Main coordination API for Corpus AI companion system',
    doc='/swagger'
)

logging.basicConfig(level=logging.INFO)

# Initialize orchestrator
orchestrator = CorpusOrchestrator()

# Define API models
speak_model = api.model('SpeakRequest', {
    'text': fields.String(required=True, description='Text to speak via speech capability', 
                         example='Hello! I am your AI companion.')
})

command_model = api.model('CommandRequest', {
    'command': fields.String(required=True, description='Command to process', 
                           example='say Hello world')
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

capability_status = api.model('CapabilityStatus', {
    'status': fields.String(description='Capability status'),
    'url': fields.String(description='Capability URL'), 
    'last_error': fields.String(description='Last error message', allow_null=True)
})

system_status_response = api.model('SystemStatusResponse', {
    'capabilities': fields.Nested(capability_status, description='Status of all capabilities')
})

check_response = api.model('CheckCapabilitiesResponse', {
    'message': fields.String(description='Check result message'),
    'status': fields.Nested(system_status_response, description='Updated system status')
})

@api.route('/status')
class Status(Resource):
    @api.response(200, 'Success', system_status_response)
    def get(self):
        """Get overall system status and all capability statuses"""
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

@api.route('/command')
class Command(Resource):
    @api.expect(command_model)
    @api.response(200, 'Success', command_response)
    @api.response(400, 'Bad Request', error_response)
    def post(self):
        """Process a high-level command through the orchestrator"""
        data = request.get_json()
        if not data or 'command' not in data:
            return {"error": "Missing 'command' field"}, 400
        
        # Note: This endpoint has async issues in the original code
        # For now, we'll make it synchronous
        # TODO: Fix async handling
        try:
            # Basic synchronous command processing
            command = data['command']
            if command.startswith("say "):
                text = command[4:]
                success = orchestrator.speak(text)
                result = "Spoken successfully" if success else "Failed to speak"
            else:
                result = "Unknown command"
            
            return {"result": result}
        except Exception as e:
            return {"error": f"Command processing failed: {str(e)}"}, 500

@api.route('/capabilities/check')
class CheckCapabilities(Resource):
    @api.response(200, 'Success', check_response)
    def post(self):
        """Check status of all capabilities and update their availability"""
        try:
            # Note: This endpoint has async issues in the original code
            # For now, we'll make it synchronous
            # TODO: Fix async handling properly
            
            # Basic capability check without async
            message = "Capability check initiated (async features pending)"
            status = orchestrator.get_system_status()
            
            return {
                "message": message, 
                "status": status
            }
        except Exception as e:
            return {"error": f"Capability check failed: {str(e)}"}, 500

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
            'orchestrator_endpoints': ['/status', '/speak', '/command', '/capabilities/check']
        }

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
        debug=False  # Changed from True to False for production
    )