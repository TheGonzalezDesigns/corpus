from flask import Flask, request, jsonify
import asyncio
import logging
import yaml
from orchestrator import CorpusOrchestrator

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Initialize orchestrator
orchestrator = CorpusOrchestrator()

@app.route('/status', methods=['GET'])
def status():
    return jsonify(orchestrator.get_system_status())

@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Missing 'text' field"}), 400
    
    success = orchestrator.speak(data['text'])
    if success:
        return jsonify({"status": "success", "message": "Text spoken"})
    else:
        return jsonify({"error": "Failed to speak text"}), 500

@app.route('/command', methods=['POST'])
async def command():
    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({"error": "Missing 'command' field"}), 400
    
    result = await orchestrator.process_command(data['command'])
    return jsonify({"result": result})

@app.route('/capabilities/check', methods=['POST'])
async def check_capabilities():
    await orchestrator.check_all_capabilities()
    return jsonify({"message": "Capability check complete", "status": orchestrator.get_system_status()})

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
        debug=True
    )