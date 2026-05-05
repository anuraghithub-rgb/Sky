from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
import requests
import time
import random
import json
import os
from datetime import datetime, timedelta
from threading import Lock

app = Flask(__name__)
app.secret_key = "oggy_hosting_secret_159357"

# A4F API Configuration
A4F_API_URL = "https://samuraiapi.in/v1/chat/completions"
A4F_API_KEY = "sk-NK6SS9tpWghyFJwkZLoCis1sMaF6RwQ5WF09mUoKKR0VKCm7"
A4F_MODEL = "provider10-claude-sonnet-4-20250514(clinesp)"

# File for storing data
USERS_FILE = "users.json"
REQUESTS_FILE = "requests.json"

# Load/Save functions
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {"OGGY": {"password": "OGGY@123", "role": "owner", "approved": True, "created_at": str(datetime.now())}}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_requests():
    if os.path.exists(REQUESTS_FILE):
        with open(REQUESTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_requests(requests):
    with open(REQUESTS_FILE, 'w') as f:
        json.dump(requests, f, indent=2)

# Mock server stats for each user
user_servers = {}

def get_server_stats(username):
    if username not in user_servers:
        user_servers[username] = {
            "start_time": datetime.now(),
            "is_running": True,
            "cpu_usage": 0.5,
            "ram_usage": 256,
            "logs": ["[INFO] OGGY HOSTING online", f"[INFO] Welcome {username}"]
        }
    return user_servers[username]

def call_a4f_api(prompt):
    headers = {
        "Authorization": f"Bearer {A4F_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": A4F_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 500
    }
    try:
        response = requests.post(A4F_API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "No response from AI")
        else:
            return f"API Error: {response.status_code}"
    except Exception as e:
        return f"Connection Error: {str(e)}"

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OGGY HOSTING - Premium OGGY Solution</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a0033 100%);
            font-family: 'Courier New', 'Fira Code', monospace;
            min-height: 100vh;
            color: #ff00ff;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            padding: 30px;
            border-bottom: 2px solid #ff00ff;
            margin-bottom: 30px;
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from { text-shadow: 0 0 5px #ff00ff; }
            to { text-shadow: 0 0 20px #ff00ff; }
        }
        
        .header h1 {
            font-size: 3em;
            letter-spacing: 3px;
        }
        
        .login-box, .register-box, .approval-box {
            background: rgba(0, 0, 0, 0.95);
            border: 2px solid #ff00ff;
            border-radius: 15px;
            padding: 40px;
            max-width: 500px;
            margin: 50px auto;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 50px rgba(255, 0, 255, 0.3);
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        
        .input-group label {
            display: block;
            margin-bottom: 10px;
            color: #ff00ff;
        }
        
        .input-group input {
            width: 100%;
            padding: 12px;
            background: #000;
            border: 1px solid #ff00ff;
            color: #ff00ff;
            font-family: monospace;
            font-size: 1em;
            border-radius: 5px;
        }
        
        .input-group input:focus {
            outline: none;
            border-width: 2px;
            box-shadow: 0 0 10px #ff00ff;
        }
        
        button {
            width: 100%;
            padding: 12px;
            background: #ff00ff;
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
            background: #cc00cc;
            transform: scale(1.02);
            box-shadow: 0 0 20px #ff00ff;
        }
        
        .dashboard {
            display: none;
        }
        
        .top-bar {
            background: rgba(0, 0, 0, 0.9);
            border: 1px solid #ff00ff;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logout-btn, .owner-btn {
            width: auto;
            padding: 8px 20px;
            background: #ff0040;
        }
        
        .owner-btn {
            background: #00ff9d;
            color: #000;
        }
        
        .stats-panel {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: rgba(0, 0, 0, 0.85);
            border: 1px solid #ff00ff;
            border-radius: 10px;
            padding: 20px;
            transition: transform 0.3s;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 0 30px rgba(255, 0, 255, 0.2);
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
            border: 2px solid #ff00ff;
            border-radius: 10px;
            margin: 20px 0;
            overflow: hidden;
        }
        
        .terminal-header {
            background: #ff00ff;
            color: #000;
            padding: 10px;
            font-weight: bold;
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
            color: #ff00ff;
        }
        
        .terminal-input-line {
            display: flex;
            gap: 10px;
            margin-top: 10px;
            padding: 10px;
        }
        
        .terminal-input {
            flex: 1;
            background: #111;
            border: 1px solid #ff00ff;
            color: #ff00ff;
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
            background: #1a0033;
            border: 1px solid #ff00ff;
            color: #ff00ff;
        }
        
        .ctrl-btn:hover {
            background: #ff00ff;
            color: #000;
        }
        
        .request-card {
            background: rgba(255, 0, 255, 0.1);
            border: 1px solid #ff00ff;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
        }
        
        .approve-btn {
            width: auto;
            padding: 5px 15px;
            margin: 5px;
            background: #00ff9d;
            color: #000;
        }
        
        .reject-btn {
            background: #ff0040;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            margin-top: 40px;
            border-top: 1px solid #ff00ff;
            font-size: 0.9em;
            opacity: 0.7;
        }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 1.5em; }
            .stats-panel { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 OGGY HOSTING 🔥</h1>
            <p>Premium Hosting Solution | By OGGY</p>
        </div>
        
        <!-- Login Form -->
        <div id="loginForm" class="login-box">
            <h3>🔐 LOGIN TO OGGY HOSTING</h3>
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
            <p style="text-align: center; margin-top: 20px;">
                <a href="#" onclick="showRegister()" style="color: #ff00ff;">Create Free Account</a>
            </p>
        </div>
        
        <!-- Register Form -->
        <div id="registerForm" class="register-box" style="display: none;">
            <h3>📝 CREATE FREE ACCOUNT</h3>
            <p style="margin-bottom: 20px;">Request will be sent to OGGY for approval</p>
            <form id="register">
                <div class="input-group">
                    <label>Username</label>
                    <input type="text" id="regUsername" required>
                </div>
                <div class="input-group">
                    <label>Password</label>
                    <input type="password" id="regPassword" required>
                </div>
                <div class="input-group">
                    <label>Email (optional)</label>
                    <input type="email" id="regEmail">
                </div>
                <button type="submit">Send Request</button>
            </form>
            <p style="text-align: center; margin-top: 20px;">
                <a href="#" onclick="showLogin()" style="color: #ff00ff;">Back to Login</a>
            </p>
        </div>
        
        <!-- Owner Approval Panel -->
        <div id="approvalPanel" class="approval-box" style="display: none;">
            <h3>👑 OWNER - PENDING REQUESTS</h3>
            <div id="requestsList"></div>
            <p style="text-align: center; margin-top: 20px;">
                <a href="#" onclick="showLogin()" style="color: #ff00ff;">Back to Login</a>
            </p>
        </div>
        
        <!-- User Dashboard -->
        <div id="dashboard" class="dashboard">
            <div class="top-bar">
                <div>
                    <strong># OGGY HOSTING</strong><br>
                    Welcome: <span id="welcomeUser"></span>
                </div>
                <div>
                    <button class="owner-btn" id="ownerPanelBtn" onclick="showOwnerPanel()" style="display: none;">👑 Owner Panel</button>
                    <button class="logout-btn" onclick="logout()">Logout</button>
                </div>
            </div>
            
            <div class="stats-panel">
                <div class="stat-card">
                    <div class="stat-label">SERVER ADDRESS</div>
                    <div class="stat-value">https://oggy-host-41-382-544-47</div>
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
                <div class="stat-value" style="font-size: 1em;">oggy-35335cc2 / python / 512 / 1GB</div>
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
                    <span>$ OGGY TERMINAL - Type command or ask AI</span>
                </div>
                <div class="terminal-body" id="terminalBody">
                    <div class="terminal-line">$ [INFO] Welcome to OGGY HOSTING</div>
                    <div class="terminal-line">$ Type 'help' for commands or ask anything to AI</div>
                </div>
                <div class="terminal-input-line">
                    <span style="color: #ff00ff;">$</span>
                    <input type="text" id="commandInput" class="terminal-input" placeholder="Type command or ask AI..." onkeypress="if(event.key==='Enter') executeCommand()">
                    <button onclick="executeCommand()" style="width: auto; padding: 5px 15px;">⏎</button>
                </div>
            </div>
            
            <div id="aiResponse" class="stat-card" style="display: none; background: rgba(255,0,255,0.1);">
                <strong>🤖 AI Response (OGGY AI - Claude):</strong>
                <div id="aiContent" style="margin-top: 10px;"></div>
            </div>
        </div>
        
        <div class="footer">
            Developed by OGGY 🔥 | OGGY HOSTING v2.0
        </div>
    </div>
    
    <script>
        let uptimeInterval, statsInterval;
        let serverRunning = true;
        let currentUser = "";
        
        function showRegister() {
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('registerForm').style.display = 'block';
            document.getElementById('approvalPanel').style.display = 'none';
        }
        
        function showLogin() {
            document.getElementById('loginForm').style.display = 'block';
            document.getElementById('registerForm').style.display = 'none';
            document.getElementById('approvalPanel').style.display = 'none';
        }
        
        function updateUptime() {
            if (!window.startTime) window.startTime = new Date();
            const diff = Math.floor((new Date() - window.startTime) / 1000);
            document.getElementById('uptime').innerText = `${Math.floor(diff/3600)}h ${Math.floor((diff%3600)/60)}m ${diff%60}s`;
        }
        
        function updateStats() {
            if (serverRunning) {
                const cpu = (Math.random() * 8 + 0.5).toFixed(1);
                const ram = Math.floor(Math.random() * 200 + 256);
                document.getElementById('cpuRam').innerHTML = `${cpu}% / ${ram}MB`;
            }
        }
        
        function controlServer(action) {
            fetch('/api/control', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: action})
            }).then(res => res.json()).then(data => {
                serverRunning = data.running;
                document.getElementById('status').innerText = data.running ? 'RUNNING' : 'STOPPED';
                addTerminalLine(data.message);
                if (action === 'restart') {
                    setTimeout(() => { window.startTime = new Date(); }, 2000);
                } else if (action === 'start') {
                    window.startTime = new Date();
                }
            });
        }
        
        function addTerminalLine(text) {
            const terminalBody = document.getElementById('terminalBody');
            const line = document.createElement('div');
            line.className = 'terminal-line';
            line.innerHTML = `$ ${text}`;
            terminalBody.appendChild(line);
            terminalBody.scrollTop = terminalBody.scrollHeight;
        }
        
        function clearLogs() {
            document.getElementById('terminalBody').innerHTML = '<div class="terminal-line">$ [INFO] Logs cleared</div>';
            addTerminalLine('[INFO] Terminal cleared');
        }
        
        async function executeCommand() {
            const input = document.getElementById('commandInput');
            const command = input.value.trim();
            if (!command) return;
            addTerminalLine(`> ${command}`);
            
            const systemCommands = ['help', 'ls', 'pwd', 'whoami', 'date', 'time', 'clear'];
            if (systemCommands.includes(command.toLowerCase())) {
                const responses = {
                    'help': 'OGGY HOSTING Commands: help, ls, pwd, whoami, date, time, clear | Or ask anything to AI',
                    'ls': 'app.py  requirements.txt  logs/  config/  oggy_secrets/',
                    'pwd': '/home/oggy/server',
                    'whoami': currentUser,
                    'date': new Date().toString(),
                    'time': new Date().toLocaleTimeString(),
                    'clear': () => { document.getElementById('terminalBody').innerHTML = '<div class="terminal-line">$ [INFO] Cleared</div>'; }
                };
                if (command === 'clear') responses.clear();
                else addTerminalLine(responses[command] || `Command not found: ${command}`);
                input.value = '';
                return;
            }
            
            addTerminalLine('[AI] Processing...');
            const response = await fetch('/api/ai', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({prompt: command})
            });
            const data = await response.json();
            addTerminalLine(`[OGGY-AI] ${data.response}`);
            document.getElementById('aiContent').innerHTML = data.response;
            document.getElementById('aiResponse').style.display = 'block';
            setTimeout(() => { document.getElementById('aiResponse').style.display = 'none'; }, 15000);
            input.value = '';
        }
        
        function showOwnerPanel() {
            fetch('/api/pending-requests').then(res => res.json()).then(data => {
                let html = '';
                data.requests.forEach(req => {
                    html += `<div class="request-card">
                        <strong>User:</strong> ${req.username}<br>
                        <strong>Email:</strong> ${req.email || 'N/A'}<br>
                        <strong>Requested:</strong> ${req.created_at}<br>
                        <button class="approve-btn" onclick="approveRequest('${req.username}')">✅ Approve</button>
                        <button class="reject-btn" onclick="rejectRequest('${req.username}')">❌ Reject</button>
                    </div>`;
                });
                if (data.requests.length === 0) html = '<p>No pending requests</p>';
                document.getElementById('requestsList').innerHTML = html;
                document.getElementById('loginForm').style.display = 'none';
                document.getElementById('dashboard').style.display = 'none';
                document.getElementById('approvalPanel').style.display = 'block';
            });
        }
        
        function approveRequest(username) {
            fetch('/api/approve-request', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: username, action: 'approve'})
            }).then(() => { showOwnerPanel(); alert('User approved!'); });
        }
        
        function rejectRequest(username) {
            fetch('/api/approve-request', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: username, action: 'reject'})
            }).then(() => { showOwnerPanel(); alert('User rejected!'); });
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
                currentUser = username;
                document.getElementById('loginForm').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
                document.getElementById('welcomeUser').innerHTML = username;
                if (data.is_owner) {
                    document.getElementById('ownerPanelBtn').style.display = 'inline-block';
                }
                window.startTime = new Date();
                serverRunning = true;
                if (uptimeInterval) clearInterval(uptimeInterval);
                if (statsInterval) clearInterval(statsInterval);
                uptimeInterval = setInterval(updateUptime, 1000);
                statsInterval = setInterval(updateStats, 3000);
                addTerminalLine(`[INFO] Welcome ${username} to OGGY HOSTING`);
            } else {
                alert(data.message || 'Login failed! Account not approved or invalid credentials');
            }
        });
        
        // Register handler
        document.getElementById('register').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('regUsername').value;
            const password = document.getElementById('regPassword').value;
            const email = document.getElementById('regEmail').value;
            
            const response = await fetch('/api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password, email})
            });
            const data = await response.json();
            alert(data.message);
            if (data.success) {
                showLogin();
            }
        });
        
        function logout() {
            if (uptimeInterval) clearInterval(uptimeInterval);
            if (statsInterval) clearInterval(statsInterval);
            document.getElementById('dashboard').style.display = 'none';
            document.getElementById('loginForm').style.display = 'block';
            document.getElementById('username').value = '';
            document.getElementById('password').value = '';
            currentUser = "";
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    users = load_users()
    
    if username in users:
        user = users[username]
        if user.get('password') == password:
            if user.get('approved', False):
                session['user'] = username
                return jsonify({'success': True, 'is_owner': user.get('role') == 'owner'})
            else:
                return jsonify({'success': False, 'message': 'Account pending approval from OGGY'})
    
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email', '')
    
    users = load_users()
    
    if username in users:
        return jsonify({'success': False, 'message': 'Username already exists'})
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'})
    
    # Add to pending requests
    requests_list = load_requests()
    requests_list.append({
        'username': username,
        'password': password,
        'email': email,
        'created_at': str(datetime.now()),
        'status': 'pending'
    })
    save_requests(requests_list)
    
    return jsonify({'success': True, 'message': 'Request sent to OGGY for approval'})

@app.route('/api/pending-requests', methods=['GET'])
def api_pending_requests():
    if session.get('user') != 'OGGY':
        return jsonify({'requests': []})
    
    requests_list = load_requests()
    pending = [r for r in requests_list if r.get('status') == 'pending']
    return jsonify({'requests': pending})

@app.route('/api/approve-request', methods=['POST'])
def api_approve_request():
    if session.get('user') != 'OGGY':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    data = request.json
    username = data.get('username')
    action = data.get('action')
    
    requests_list = load_requests()
    users = load_users()
    
    for req in requests_list:
        if req['username'] == username and req.get('status') == 'pending':
            if action == 'approve':
                users[username] = {
                    'password': req['password'],
                    'role': 'user',
                    'approved': True,
                    'created_at': str(datetime.now())
                }
                save_users(users)
                req['status'] = 'approved'
            else:
                req['status'] = 'rejected'
            save_requests(requests_list)
            return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Request not found'})

@app.route('/api/ai', methods=['POST'])
def api_ai():
    data = request.json
    prompt = data.get('prompt', '')
    if not prompt:
        return jsonify({'response': 'Type something first, CHUMT KE PYASA 😈'})
    response = call_a4f_api(prompt)
    return jsonify({'response': response})

@app.route('/api/control', methods=['POST'])
def api_control():
    data = request.json
    action = data.get('action')
    username = session.get('user', 'guest')
    stats = get_server_stats(username)
    
    if action == 'start':
        stats['is_running'] = True
        stats['start_time'] = datetime.now()
        return jsonify({'running': True, 'message': '[INFO] Server started'})
    elif action == 'stop':
        stats['is_running'] = False
        return jsonify({'running': False, 'message': '[WARN] Server stopped'})
    elif action == 'restart':
        stats['is_running'] = True
        stats['start_time'] = datetime.now()
        return jsonify({'running': True, 'message': '[INFO] Server restarted'})
    return jsonify({'running': stats['is_running'], 'message': '[INFO] OK'})

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════╗
    ║     🔥 OGGY HOSTING - FULLY LOADED 🔥            ║
    ╠══════════════════════════════════════════════════╣
    ║  Owner Login:  OGGY / OGGY@123                  ║
    ║  URL:          http://localhost:5000            ║
    ║                                                  ║
    ║  Features:                                      ║
    ║  - Free account registration                    ║
    ║  - Owner approval system                        ║
    ║  - A4F Claude AI integration                    ║
    ║  - Live server stats                            ║
    ║  - Terminal with AI commands                    ║
    ╚══════════════════════════════════════════════════╝
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)