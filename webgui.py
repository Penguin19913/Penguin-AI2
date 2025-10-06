from flask import Flask, render_template, jsonify, request
import threading
import time
import os
import signal
import asyncio
from Backend.ai import start_listening, stop_listening
import webbrowser

app = Flask(__name__)

# Global variables to track state
process_running = False
current_status = "Ready"
process_thread = None
loop = None  # Store asyncio loop

def run_main_function():
    """Function to run speech recognition loop in a separate thread"""
    global process_running, current_status, loop
    
    try:
        current_status = "Running speech recognition..."
        # Call the start_listening function directly
        # It already handles its own asyncio loop
        start_listening()
    except Exception as e:
        current_status = f"Error: {str(e)}"
    finally:
        process_running = False
        if loop and loop.is_running():
            loop.stop()

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_process():
    """Start the main function"""
    global process_running, process_thread, current_status
    
    if not process_running:
        process_running = True
        current_status = "Starting..."
        process_thread = threading.Thread(target=run_main_function)
        process_thread.start()
        return jsonify({'success': True, 'message': 'Process started'})
    else:
        return jsonify({'success': False, 'message': 'Process already running'})

@app.route('/stop', methods=['POST'])
def stop_process():
    """Stop the main function"""
    global process_running, current_status
    
    if process_running:
        process_running = False
        current_status = "Stopped by user"
        # Use the new stop_listening function
        if stop_listening():
            return jsonify({'success': True, 'message': 'Process stopped successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to stop the process'})
    else:
        return jsonify({'success': False, 'message': 'No process running'})

@app.route('/status')
def get_status():
    """Get current status"""
    return jsonify({
        'running': process_running,
        'status': current_status
    })

@app.route('/shutdown', methods=['POST'])
def shutdown_server():
    """Shutdown the Flask server"""
    global process_running, current_status
    
    # Stop any running process
    if process_running:
        process_running = False
        current_status = "Server shutting down..."
    
    # Shutdown the server
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        import os
        import signal
        os.kill(os.getpid(), signal.SIGINT)
    else:
        func()
    
    return jsonify({'success': True, 'message': 'Server shutting down...'})

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:5000/')
    app.run(debug=True, host='127.0.0.1', port=5000)