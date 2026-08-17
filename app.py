import os
import signal
import subprocess
import sys
from pathlib import Path

from flask import Flask, jsonify, request, render_template

app = Flask(__name__, static_folder='static', template_folder='templates')

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data' / 'chats'


def ensure_dirs():
    DATA_DIR.mkdir(parents=True, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/upload_chats', methods=['POST'])
def upload_chats():
    ensure_dirs()
    if 'files' not in request.files:
        return jsonify({'success': False, 'error': 'No files provided.'})

    files = request.files.getlist('files')
    saved_files = []
    for file in files:
        if file.filename:
            # Extract just the filename to flatten folder structure
            filename = os.path.basename(file.filename)
            file_path = DATA_DIR / filename
            file.save(str(file_path))
            saved_files.append(filename)

    return jsonify({'success': True, 'files': saved_files})


@app.route('/api/build', methods=['POST'])
def build_twin():
    data = request.json
    target_name = data.get('target_name', 'Villain')
    llm_provider = data.get('llm_provider', 'anthropic')
    api_key = data.get('api_key', '')
    base_url = data.get('base_url', '')
    model = data.get('model', '')

    # Set API key to environment if provided
    env = os.environ.copy()
    if llm_provider == 'anthropic' and api_key:
        env['ANTHROPIC_API_KEY'] = api_key
    elif llm_provider == 'openai' and api_key:
        env['OPENAI_API_KEY'] = api_key

    # Call build_twin.py
    cmd = [
        sys.executable,
        str(BASE_DIR / 'build_twin.py'),
        '--source-type', 'chat',
        '--dir', str(DATA_DIR),
        '--target-name', target_name,
    ]
    if llm_provider == 'demo':
        cmd.append('--dry-run')
    else:
        cmd.extend(['--llm', llm_provider])
    if base_url:
        cmd.extend(['--base-url', base_url])
    if model:
        cmd.extend(['--model', model])

    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({'success': False, 'error': result.stderr})
        return jsonify({'success': True, 'output': result.stdout})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    target_name = data.get('target_name', 'Villain')
    llm_provider = data.get('llm_provider', 'anthropic')
    api_key = data.get('api_key', '')
    base_url = data.get('base_url', '')
    model = data.get('model', '')
    scenario = data.get('message', '')

    if not scenario:
        return jsonify({'success': False, 'error': 'Message cannot be empty.'})

    # Set API key to environment if provided
    env = os.environ.copy()
    if llm_provider == 'anthropic' and api_key:
        env['ANTHROPIC_API_KEY'] = api_key
    elif llm_provider == 'openai' and api_key:
        env['OPENAI_API_KEY'] = api_key

    # Call talk_to_myself.py in scenario mode
    cmd = [
        sys.executable,
        str(BASE_DIR / 'talk_to_myself.py'),
        '--name', target_name,
        '--llm', llm_provider,
        '--scenario', scenario
    ]
    if base_url:
        cmd.extend(['--base-url', base_url])
    if model:
        cmd.extend(['--model', model])

    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            return jsonify({'success': False, 'error': result.stderr})
        
        # Parse the output to just get the agent's response
        # talk_to_myself outputs:
        # [Name (Digital Twin)]
        # <response>
        lines = result.stdout.strip().split('\n')
        response_text = ""
        capture = False
        for line in lines:
            if capture:
                response_text += line + "\n"
            if '(Digital Twin)]' in line:
                capture = True

        if not response_text.strip():
            response_text = result.stdout # fallback if format changed

        return jsonify({'success': True, 'response': response_text.strip()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    """Shutdown the Flask server"""
    # This works in Werkzeug but for general purpose on Windows we can kill our own process
    pid = os.getpid()
    # Schedule termination to allow the response to be sent first
    import threading
    import time
    def seppuku():
        time.sleep(1)
        os.kill(pid, signal.SIGTERM)
    threading.Thread(target=seppuku).start()
    
    return jsonify({"success": True, "message": "Server shutting down..."})


if __name__ == '__main__':
    # Parse port from env if provided by bat script
    port = int(os.environ.get('PORT', 3004))
    app.run(host='127.0.0.1', port=port, debug=True)
