from flask import Flask, render_template_string, request, jsonify, session
import requests
import time
import random
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "jubayer_hosting_secret_159357"

# A4F API Configuration
A4F_API_URL = "https://samuraiapi.in/v1/chat/completions"
A4F_API_KEY = "sk-NK6SS9tpWghyFJwkZLoCis1sMaF6RwQ5WF09mUoKKR0VKCm7"
A4F_MODEL = "provider10-claude-sonnet-4-20250514(clinesp)"

# Mock database users
USERS = {
    "JUBAYER": "JUBAYER"
}

# Server stats tracking
server_stats = {
    "start_time": datetime.now(),
    "is_running": True,
    "cpu_usage": 0.5,
    "ram_usage": 256,
    "logs": ["[INFO] Server initialized", "[INFO] JUBAYER HOSTING online"]
}

def call_a4f_api(prompt):
    """Call A4F Claude API and return response"""
    headers = {
        "Authorization": f"Bearer {A4F_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": A4F_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(A4F_API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "No response from AI")
        else:
            return f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Connection Error: {str(e)}"

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JUBAYER HOSTING - Premium Solution</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            font-family: 'Courier New', 'Fira Code', monospace;
            min-height: 100vh;
            color: #00ff9d;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Header */
        .header {
            text-align: center;
            padding: 30px;
            border-bottom: 2px solid #00ff9d;
            margin-bottom: 30px;
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from { text-shadow: 0 0 5px #00ff9d; }
            to { text-shadow: 0 0 20px #00ff9d; }
        }
        
        .header h1 {
            font-size: 3em;
            letter-spacing: 3px;
        }
        
        .header p {
            color: #00ff9d;
            opacity: 0.8;
            margin-top: 10px;
        }
        
        /* Login Box */
        .login-box {
            background: rgba(0, 0, 0, 0.85);
            border: 2px solid #00ff9d;
            border-radius: 15px;
            padding: 40px;
            max-width: 500px;
            margin: 100px auto;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 50px rgba(0, 255, 157, 0.3);
        }
        
        .login-box h3 {
            text-align: center;
            margin-bottom: 30px;
            font-size: 1.5em;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        .input-group label {
            display: block;
            margin-bottom: 10px;
            color: #00ff9d;
        }
        
        .input-group input {
            width: 100%;
            padding: 12px;
            background: #000;
            border: 1px solid #00ff9d;
            color: #00ff9d;
            font-family: monospace;
            font-size: 1em;
            border-radius: 5px;
        }
        
        .input-group input:focus {
            outline: none;
            border-width: 2px;
            box-shadow: 0 0 10px #00ff9d;
        }
        
        button {
            width: 100%;
            padding: 12px;
            background: #00ff9d;
            color: #000;
            border: none;
            font-size: 1.1em;
            font-weight: bold;
            cursor: pointer;
            border-radius: 5px;
            transition: all 0.3s;
            font-family: monospace;
        }
        
        button:hover {
            background: #00cc7d;
            transform: scale(1.02);
            box-shadow: 0 0 20px #00ff9d;
        }
        
        /* Dashboard */
        .dashboard {
            display: none;
        }
        
        .top-bar {
            background: rgba(0, 0, 0, 0.9);
            border: 1px solid #00ff9d;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logout-btn {
            width: auto;
            padding: 8px 20px;
            background: #ff0040;
        }
        
        .logout-btn:hover {
            background: #cc0033;
        }
        
        .stats-panel {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: rgba(0, 0, 0, 0.85);
            border: 1px solid #00ff9d;
            border-radius: 10px;
            padding: 20px;
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 30px rgba(0, 255, 157, 0.2);
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.7;
            margin-bottom: 10px;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
        }
        
        .terminal {
            background: #000;
            border: 2px solid #00ff9d;
            border-radius: 10px;
            margin: 20px 0;
            overflow: hidden;
        }
        
        .terminal-header {
            background: #00ff9d;
            color: #000;
            padding: 10px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
        }
        
        .terminal-body {
            padding: 20px;
            height: 300px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.9em;
        }
        
        .terminal-line {
            margin: 5px 0;
            color: #00ff9d;
        }
        
        .terminal-input-line {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        
        .terminal-input {
            flex: 1;
            background: #111;
            border: 1px solid #00ff9d;
            color: #00ff9d;
            padding: 8px;
            font-family: monospace;
        }
        
        .server-controls {
            display: flex;
            gap: 15px;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        
        .ctrl-btn {
            flex: 1;
            background: #1a1a2e;
            border: 1px solid #00ff9d;
            color: #00ff9d;
        }
        
        .ctrl-btn:hover {
            background: #00ff9d;
            color: #000;
        }
        
        .ai-response {
            background: rgba(0, 255, 157, 0.1);
            border-left: 4px solid #00ff9d;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 1.5em; }
            .stats-panel { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Login Form -->
        <div id="loginForm" class="login-box">
            <h3>🔐 JUBAYER HOSTING</h3>
            <h3>Premium Hosting Solution</h3>
            <form id="login">
                <div class="input-group">
                    <label>Username</label>
                    <input type="text" id="username" required>
                </div>
                <div class="input-group">
                    <label>Password</label>
                    <input type="password" id="password" required>
                </div>
                <button type="submit">Login</button>
            </form>
            <p style="text-align: center; margin-top: 20px; font-size: 0.8em;">Secure Access Only</p>
        </div>
        
        <!-- Dashboard -->
        <div id="dashboard" class="dashboard">
            <div class="top-bar">
                <div>
                    <strong># JUBAYER HOSTING</strong><br>
                    Welcome: <span id="welcomeUser">JUBAYER</span>
                </div>
                <button class="logout-btn" onclick="logout()">Logout</button>
            </div>
            
            <div class="stats-panel">
                <div class="stat-card">
                    <div class="stat-label">SERVER ADDRESS</div>
                    <div class="stat-value" id="serverAddr">https://41-382-544-47-v8fz2ux1</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">UPTIME</div>
                    <div class="stat-value" id="uptime">0h 0m 0s</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">STATUS</div>
                    <div class="stat-value" id="status">RUNNING</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">CPU / RAM</div>
                    <div class="stat-value" id="cpuRam">0.5% / 512MB</div>
                </div>
            </div>
            
            <div class="stat-card" style="margin-bottom: 20px;">
                <div class="stat-label">Server ID / Type / RAM/Disk / Expires</div>
                <div class="stat-value" style="font-size: 1em;">35335cc2 / python / 512 / 1GB</div>
                <div class="stat-value" style="font-size: 1em;">Expires: 2026-06-04</div>
            </div>
            
            <div class="server-controls">
                <button class="ctrl-btn" onclick="controlServer('start')">START</button>
                <button class="ctrl-btn" onclick="controlServer('stop')">STOP</button>
                <button class="ctrl-btn" onclick="controlServer('restart')">RESTART</button>
                <button class="ctrl-btn" onclick="clearLogs()">CLEAR</button>
            </div>
            
            <div class="terminal">
                <div class="terminal-header">
                    <span>$ Command Line Interface</span>
                    <span>Type command and press Enter...</span>
                </div>
                <div class="terminal-body" id="terminalBody">
                    <div class="terminal-line">$ [INFO] Logs cleared. Click START to begin...</div>
                    <div class="terminal-line">$ Welcome to JUBAYER HOSTING terminal</div>
                </div>
                <div style="padding: 10px;">
                    <div class="terminal-input-line">
                        <span>$</span>
                        <input type="text" id="commandInput" class="terminal-input" placeholder="Type command or ask AI...">
                        <button onclick="executeCommand()" style="width: auto; padding: 5px 15px;">⏎</button>
                    </div>
                </div>
            </div>
            
            <div id="aiResponse" class="ai-response" style="display: none;">
                <strong>🤖 AI Response (Claude Sonnet 4):</strong>
                <div id="aiContent"></div>
            </div>
        </div>
    </div>
    
    <script>
        let uptimeInterval;
        let serverRunning = true;
        let commandHistory = [];
        
        // Update uptime
        function updateUptime() {
            if (!window.startTime) {
                window.startTime = new Date();
            }
            const now = new Date();
            const diff = Math.floor((now - window.startTime) / 1000);
            const hours = Math.floor(diff / 3600);
            const minutes = Math.floor((diff % 3600) / 60);
            const seconds = diff % 60;
            document.getElementById('uptime').innerText = `${hours}h ${minutes}m ${seconds}s`;
        }
        
        // Update CPU/RAM (simulated real-time)
        function updateStats() {
            if (serverRunning) {
                const cpu = (Math.random() * 8 + 0.5).toFixed(1);
                const ram = Math.floor(Math.random() * 200 + 256);
                document.getElementById('cpuRam').innerHTML = `${cpu}% / ${ram}MB`;
            }
        }
        
        // Control server
        function controlServer(action) {
            const statusEl = document.getElementById('status');
            const terminalBody = document.getElementById('terminalBody');
            
            if (action === 'start') {
                if (!serverRunning) {
                    serverRunning = true;
                    window.startTime = new Date();
                    statusEl.innerText = 'RUNNING';
                    addTerminalLine('[INFO] Server started successfully');
                    startIntervals();
                } else {
                    addTerminalLine('[WARN] Server already running');
                }
            } else if (action === 'stop') {
                if (serverRunning) {
                    serverRunning = false;
                    statusEl.innerText = 'STOPPED';
                    addTerminalLine('[WARN] Server stopped');
                    if (uptimeInterval) clearInterval(uptimeInterval);
                    if (statsInterval) clearInterval(statsInterval);
                } else {
                    addTerminalLine('[ERROR] Server already stopped');
                }
            } else if (action === 'restart') {
                addTerminalLine('[INFO] Restarting server...');
                setTimeout(() => {
                    serverRunning = true;
                    window.startTime = new Date();
                    statusEl.innerText = 'RUNNING';
                    addTerminalLine('[INFO] Server restarted successfully');
                    startIntervals();
                }, 2000);
            }
        }
        
        function startIntervals() {
            if (uptimeInterval) clearInterval(uptimeInterval);
            if (statsInterval) clearInterval(statsInterval);
            uptimeInterval = setInterval(updateUptime, 1000);
            statsInterval = setInterval(updateStats, 3000);
        }
        
        function addTerminalLine(text) {
            const terminalBody = document.getElementById('terminalBody');
            const line = document.createElement('div');
            line.className = 'terminal-line';
            line.innerHTML = `$ ${text}`;
            terminalBody.appendChild(line);
            terminalBody.scrollTop = terminalBody.scrollHeight;
            
            // Store logs
            fetch('/api/log', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({log: text})
            });
        }
        
        function clearLogs() {
            const terminalBody = document.getElementById('terminalBody');
            terminalBody.innerHTML = '<div class="terminal-line">$ [INFO] Logs cleared. Click START to begin...</div>';
            addTerminalLine('[INFO] Terminal logs cleared');
        }
        
        async function executeCommand() {
            const input = document.getElementById('commandInput');
            const command = input.value.trim();
            if (!command) return;
            
            addTerminalLine(`> ${command}`);
            
            // Check if command is a system command
            const systemCommands = ['help', 'ls', 'dir', 'pwd', 'whoami', 'date', 'time', 'clear'];
            if (systemCommands.includes(command.toLowerCase())) {
                handleSystemCommand(command);
            } else {
                // Send to A4F API
                addTerminalLine('[AI] Thinking...');
                const aiResponse = await callA4F(command);
                addTerminalLine(`[AI] ${aiResponse}`);
                
                // Show AI response in dedicated box
                document.getElementById('aiContent').innerHTML = aiResponse;
                document.getElementById('aiResponse').style.display = 'block';
                setTimeout(() => {
                    document.getElementById('aiResponse').style.display = 'none';
                }, 10000);
            }
            
            input.value = '';
        }
        
        function handleSystemCommand(command) {
            const responses = {
                'help': 'Available: help, ls, pwd, whoami, date, time, clear | Or ask anything to AI',
                'ls': 'app.py  requirements.txt  logs/  config/',
                'pwd': '/home/jubayer/server',
                'whoami': 'jubayer',
                'date': new Date().toString(),
                'time': new Date().toLocaleTimeString(),
                'clear': () => {
                    document.getElementById('terminalBody').innerHTML = '';
                    addTerminalLine('[INFO] Terminal cleared');
                }
            };
            
            if (command === 'clear') {
                responses.clear();
            } else {
                addTerminalLine(responses[command] || `Command not found: ${command}`);
            }
        }
        
        async function callA4F(prompt) {
            try {
                const response = await fetch('/api/ai', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: prompt})
                });
                const data = await response.json();
                return data.response || 'No response from AI';
            } catch (error) {
                return `Error: ${error.message}`;
            }
        }
        
        // Login handler
        document.getElementById('login').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            });
            
            const data = await response.json();
            if (data.success) {
                document.getElementById('loginForm').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
                document.getElementById('welcomeUser').innerText = username;
                window.startTime = new Date();
                startIntervals();
                addTerminalLine(`[INFO] User ${username} logged in successfully`);
            } else {
                alert('Login failed! Invalid credentials');
            }
        });
        
        function logout() {
            if (uptimeInterval) clearInterval(uptimeInterval);
            if (statsInterval) clearInterval(statsInterval);
            document.getElementById('loginForm').style.display = 'block';
            document.getElementById('dashboard').style.display = 'none';
            document.getElementById('username').value = '';
            document.getElementById('password').value = '';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username in USERS and USERS[username] == password:
        session['user'] = username
        return jsonify({'success': True})
    return jsonify({'success': False}), 401

@app.route('/api/ai', methods=['POST'])
def ai_endpoint():
    data = request.json
    prompt = data.get('prompt', '')
    
    if not prompt:
        return jsonify({'response': 'Type something first, CHUMT KE PYASA 😈'})
    
    response = call_a4f_api(prompt)
    return jsonify({'response': response})

@app.route('/api/log', methods=['POST'])
def add_log():
    data = request.json
    log = data.get('log', '')
    server_stats['logs'].append(f"[{datetime.now().strftime('%H:%M:%S')}] {log}")
    if len(server_stats['logs']) > 100:
        server_stats['logs'] = server_stats['logs'][-100:]
    return jsonify({'success': True})

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════╗
    ║  JUBAYER HOSTING - READY TO ROCK     ║
    ║  Open: http://localhost:5000         ║
    ║  Login: JUBAYER / JUBAYER            ║
    ╚══════════════════════════════════════╝
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)