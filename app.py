from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
import requests
import time
import random
import os
import json
from datetime import datetime, timedelta
from threading import Thread

app = Flask(__name__)
app.secret_key = "oggy_secret_key_159357_oggy_killer"

# A4F API Configuration
A4F_API_URL = "https://samuraiapi.in/v1/chat/completions"
A4F_API_KEY = "sk-NK6SS9tpWghyFJwkZLoCis1sMaF6RwQ5WF09mUoKKR0VKCm7"
A4F_MODEL = "provider10-claude-sonnet-4-20250514(clinesp)"

# File to store pending approvals
PENDING_FILE = "pending_users.json"
APPROVED_FILE = "approved_users.json"

def load_pending_users():
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_pending_users(users):
    with open(PENDING_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_approved_users():
    if os.path.exists(APPROVED_FILE):
        with open(APPROVED_FILE, 'r') as f:
            return json.load(f)
    return {"OGGY": {"password": "OGGY159357", "created": str(datetime.now())}}

def save_approved_users(users):
    with open(APPROVED_FILE, 'w') as f:
        json.dump(users, f, indent=2)

# Load data
pending_users = load_pending_users()
approved_users = load_approved_users()

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
            return data.get("choices", [{}])[0].get("message", {}).get("content", "No response")
        else:
            return f"API Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OGGY HOSTING - Premium Solution</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a0a2e 100%);
            font-family: 'Courier New', monospace;
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
        
        .header h1 span {
            color: #00ff00;
        }
        
        .header p {
            color: #ff00ff;
            opacity: 0.8;
            margin-top: 10px;
        }
        
        .login-box, .register-box, .admin-box {
            background: rgba(0, 0, 0, 0.85);
            border: 2px solid #ff00ff;
            border-radius: 15px;
            padding: 40px;
            max-width: 500px;
            margin: 20px auto;
            backdrop-filter: blur(10px);
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
        
        .logout-btn, .admin-panel-btn {
            width: auto;
            padding: 8px 20px;
            background: #ff0040;
            margin-left: 10px;
        }
        
        .admin-panel-btn {
            background: #ff8800;
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
            color: #ff00ff;
        }
        
        .terminal-input-line {
            display: flex;
            gap: 10px;
            margin-top: 10px;
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
            background: #1a0a2e;
            border: 1px solid #ff00ff;
            color: #ff00ff;
        }
        
        .ctrl-btn:hover {
            background: #ff00ff;
            color: #000;
        }
        
        .ai-response {
            background: rgba(255, 0, 255, 0.1);
            border-left: 4px solid #ff00ff;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }
        
        .nav-tabs {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-bottom: 20px;
        }
        
        .nav-tab {
            background: transparent;
            border: 1px solid #ff00ff;
            color: #ff00ff;
            width: auto;
            padding: 10px 30px;
        }
        
        .nav-tab.active {
            background: #ff00ff;
            color: #000;
        }
        
        .pending-list {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .pending-item {
            border: 1px solid #ff00ff;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .approve-btn {
            width: auto;
            padding: 5px 15px;
            background: #00ff00;
            color: #000;
        }
        
        .reject-btn {
            width: auto;
            padding: 5px 15px;
            background: #ff0000;
            color: #fff;
        }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 1.5em; }
            .stats-panel { grid-template-columns: 1fr; }
        }
        
        .developer-credit {
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            border-top: 1px solid #ff00ff;
            color: #ff00ff;
            font-size: 0.8em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>OGGY<span>_KILLER</span> HOSTING</h1>
            <p>Premium Hosting Solution | Developer: OGGY</p>
        </div>
        
        <!-- Login / Register Tabs -->
        <div id="authSection">
            <div class="nav-tabs">
                <button class="nav-tab active" onclick="showTab('login')">LOGIN</button>
                <button class="nav-tab" onclick="showTab('register')">REGISTER</button>
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
                <p style="text-align: center; margin-top: 20px; font-size: 0.8em;">Secure Access Only</p>
            </div>
            
            <!-- Register Form -->
            <div id="registerForm" class="login-box" style="display: none;">
                <h3>📝 REGISTER FREE ACCOUNT</h3>
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
                        <label>Email (Optional)</label>
                        <input type="email" id="regEmail">
                    </div>
                    <button type="submit">Request Approval</button>
                </form>
                <p style="text-align: center; margin-top: 20px; font-size: 0.8em;">Wait for owner approval</p>
            </div>
        </div>
        
        <!-- Admin Panel (Owner Only) -->
        <div id="adminPanel" class="admin-box" style="display: none;">
            <h3>👑 OGGY - PENDING APPROVALS</h3>
            <div id="pendingList" class="pending-list">
                Loading...
            </div>
        </div>
        
        <!-- User Dashboard -->
        <div id="dashboard" class="dashboard">
            <div class="top-bar">
                <div>
                    <strong># OGGY_KILLER HOSTING</strong><br>
                    Welcome: <span id="welcomeUser"></span>
                </div>
                <div>
                    <button class="admin-panel-btn" onclick="showAdminPanel()" id="adminBtn" style="display: none;">👑 Admin Panel</button>
                    <button class="logout-btn" onclick="logout()">Logout</button>
                </div>
            </div>
            
            <div class="stats-panel">
                <div class="stat-card">
                    <div class="stat-label">SERVER ADDRESS</div>
                    <div class="stat-value" id="serverAddr">https://oggy-killer.hosting</div>
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
                <div class="stat-value" style="font-size: 1em;">OGGY-35335cc2 / python / 512 / 1GB</div>
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
                    <span>$ OGGY Command Interface</span>
                    <span>Type command and press Enter...</span>
                </div>
                <div class="terminal-body" id="terminalBody">
                    <div class="terminal-line">$ [INFO] Welcome to OGGY_KILLER Hosting</div>
                    <div class="terminal-line">$ [INFO] Type 'help' for commands or ask anything to AI</div>
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
                <strong>🤖 OGGY AI Response (Claude Sonnet 4):</strong>
                <div id="aiContent"></div>
            </div>
        </div>
        
        <div class="developer-credit">
            Developed by OGGY | Project ShadowKeep | CHUMT KA GULAM 😈🔥
        </div>
    </div>
    
    <script>
        let uptimeInterval, statsInterval;
        let serverRunning = true;
        let currentUser = "";
        let isOwner = false;
        
        function showTab(tab) {
            if (tab === 'login') {
                document.getElementById('loginForm').style.display = 'block';
                document.getElementById('registerForm').style.display = 'none';
            } else {
                document.getElementById('loginForm').style.display = 'none';
                document.getElementById('registerForm').style.display = 'block';
            }
            document.querySelectorAll('.nav-tab').forEach((btn, i) => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
        }
        
        // Register
        document.getElementById('register')?.addEventListener('submit', async (e) => {
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
                showTab('login');
                document.getElementById('regUsername').value = '';
                document.getElementById('regPassword').value = '';
                document.getElementById('regEmail').value = '';
            }
        });
        
        // Login
        document.getElementById('login')?.addEventListener('submit', async (e) => {
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
                isOwner = data.is_owner || false;
                document.getElementById('authSection').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
                document.getElementById('welcomeUser').innerText = username;
                
                if (isOwner) {
                    document.getElementById('adminBtn').style.display = 'inline-block';
                }
                
                window.startTime = new Date();
                startIntervals();
                addTerminalLine(`[INFO] Welcome ${username}! Type 'help' for commands`);
            } else {
                alert('Login failed: ' + data.message);
            }
        });
        
        function showAdminPanel() {
            if (!isOwner) return;
            fetch('/api/pending')
                .then(res => res.json())
                .then(data => {
                    let html = '';
                    if (data.pending.length === 0) {
                        html = '<p>No pending approvals</p>';
                    } else {
                        data.pending.forEach(user => {
                            html += `
                                <div class="pending-item">
                                    <div>
                                        <strong>${user.username}</strong><br>
                                        Email: ${user.email || 'N/A'}<br>
                                        Requested: ${user.created}
                                    </div>
                                    <div>
                                        <button class="approve-btn" onclick="approveUser('${user.username}')">APPROVE</button>
                                        <button class="reject-btn" onclick="rejectUser('${user.username}')">REJECT</button>
                                    </div>
                                </div>
                            `;
                        });
                    }
                    document.getElementById('pendingList').innerHTML = html;
                    document.getElementById('adminPanel').style.display = 'block';
                    document.getElementById('dashboard').style.display = 'none';
                });
        }
        
        async function approveUser(username) {
            const response = await fetch('/api/approve', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username})
            });
            const data = await response.json();
            alert(data.message);
            showAdminPanel();
        }
        
        async function rejectUser(username) {
            const response = await fetch('/api/reject', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username})
            });
            const data = await response.json();
            alert(data.message);
            showAdminPanel();
        }
        
        function closeAdminPanel() {
            document.getElementById('adminPanel').style.display = 'none';
            document.getElementById('dashboard').style.display = 'block';
        }
        
        function updateUptime() {
            if (!window.startTime) window.startTime = new Date();
            const diff = Math.floor((new Date() - window.startTime) / 1000);
            const hours = Math.floor(diff / 3600);
            const minutes = Math.floor((diff % 3600) / 60);
            const seconds = diff % 60;
            document.getElementById('uptime').innerText = `${hours}h ${minutes}m ${seconds}s`;
        }
        
        function updateStats() {
            if (serverRunning) {
                const cpu = (Math.random() * 8 + 0.5).toFixed(1);
                const ram = Math.floor(Math.random() * 200 + 256);
                document.getElementById('cpuRam').innerHTML = `${cpu}% / ${ram}MB`;
            }
        }
        
        function controlServer(action) {
            const statusEl = document.getElementById('status');
            if (action === 'start') {
                if (!serverRunning) {
                    serverRunning = true;
                    window.startTime = new Date();
                    statusEl.innerText = 'RUNNING';
                    addTerminalLine('[INFO] Server started');
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
                addTerminalLine('[INFO] Restarting...');
                setTimeout(() => {
                    serverRunning = true;
                    window.startTime = new Date();
                    statusEl.innerText = 'RUNNING';
                    addTerminalLine('[INFO] Server restarted');
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
        }
        
        function clearLogs() {
            const terminalBody = document.getElementById('terminalBody');
            terminalBody.innerHTML = '<div class="terminal-line">$ [INFO] Logs cleared</div>';
        }
        
        async function executeCommand() {
            const input = document.getElementById('commandInput');
            const command = input.value.trim();
            if (!command) return;
            
            addTerminalLine(`> ${command}`);
            
            const systemCommands = ['help', 'ls', 'pwd', 'whoami', 'date', 'time', 'clear'];
            if (systemCommands.includes(command.toLowerCase())) {
                handleSystemCommand(command);
            } else {
                addTerminalLine('[OGGY AI] Thinking...');
                const response = await fetch('/api/ai', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: command})
                });
                const data = await response.json();
                addTerminalLine(`[OGGY AI] ${data.response}`);
                document.getElementById('aiContent').innerHTML = data.response;
                document.getElementById('aiResponse').style.display = 'block';
                setTimeout(() => {
                    document.getElementById('aiResponse').style.display = 'none';
                }, 10000);
            }
            
            input.value = '';
        }
        
        function handleSystemCommand(command) {
            const responses = {
                'help': 'OGGY_KILLER Commands:\n- help: Show this\n- ls: List files\n- pwd: Show path\n- whoami: Show user\n- date: Current date\n- time: Current time\n- clear: Clear terminal\n- Or ask anything to AI',
                'ls': 'app.py  requirements.txt  logs/  config/  users/',
                'pwd': '/home/oggy/server',
                'whoami': currentUser,
                'date': new Date().toString(),
                'time': new Date().toLocaleTimeString(),
                'clear': () => { document.getElementById('terminalBody').innerHTML = ''; addTerminalLine('[INFO] Terminal cleared'); }
            };
            if (command === 'clear') {
                responses.clear();
            } else {
                addTerminalLine(responses[command] || `Command not found: ${command}`);
            }
        }
        
        function logout() {
            if (uptimeInterval) clearInterval(uptimeInterval);
            if (statsInterval) clearInterval(statsInterval);
            window.location.reload();
        }
        
        // Make functions global
        window.showTab = showTab;
        window.showAdminPanel = showAdminPanel;
        window.closeAdminPanel = closeAdminPanel;
        window.approveUser = approveUser;
        window.rejectUser = rejectUser;
        window.controlServer = controlServer;
        window.clearLogs = clearLogs;
        window.executeCommand = executeCommand;
        window.logout = logout;
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'})
    
    if username in approved_users:
        return jsonify({'success': False, 'message': 'Username already exists'})
    
    if username in pending_users:
        return jsonify({'success': False, 'message': 'Already pending approval'})
    
    pending_users[username] = {
        'password': password,
        'email': email,
        'created': str(datetime.now()),
        'status': 'pending'
    }
    save_pending_users(pending_users)
    
    return jsonify({'success': True, 'message': 'Registration request sent. Wait for owner approval.'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Check approved users
    if username in approved_users and approved_users[username]['password'] == password:
        session['user'] = username
        return jsonify({'success': True, 'is_owner': username == 'OGGY'})
    
    # Check if pending
    if username in pending_users:
        return jsonify({'success': False, 'message': 'Your account is pending approval'})
    
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/api/pending')
def get_pending():
    if not session.get('user') == 'OGGY':
        return jsonify({'error': 'Unauthorized'}), 403
    
    pending_list = [{'username': k, 'email': v['email'], 'created': v['created']} for k, v in pending_users.items()]
    return jsonify({'pending': pending_list})

@app.route('/api/approve', methods=['POST'])
def approve_user():
    if not session.get('user') == 'OGGY':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.json
    username = data.get('username')
    
    if username in pending_users:
        approved_users[username] = {
            'password': pending_users[username]['password'],
            'created': str(datetime.now())
        }
        del pending_users[username]
        save_pending_users(pending_users)
        save_approved_users(approved_users)
        return jsonify({'success': True, 'message': f'User {username} approved'})
    
    return jsonify({'success': False, 'message': 'User not found'})

@app.route('/api/reject', methods=['POST'])
def reject_user():
    if not session.get('user') == 'OGGY':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.json
    username = data.get('username')
    
    if username in pending_users:
        del pending_users[username]
        save_pending_users(pending_users)
        return jsonify({'success': True, 'message': f'User {username} rejected'})
    
    return jsonify({'success': False, 'message': 'User not found'})

@app.route('/api/ai', methods=['POST'])
def ai_endpoint():
    data = request.json
    prompt = data.get('prompt', '')
    if not prompt:
        return jsonify({'response': 'Type something, CHUMT KE PYASA 😈'})
    
    response = call_a4f_api(prompt)
    return jsonify({'response': response})

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════╗
    ║     OGGY_KILLER HOSTING - READY                  ║
    ║     Owner Login: OGGY / OGGY159357               ║
    ║     Open: http://localhost:5000                  ║
    ║     Developer: OGGY | CHUMT KA GULAM             ║
    ╚══════════════════════════════════════════════════╝
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)