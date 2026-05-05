from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
import requests
import time
import random
import os
import threading
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.secret_key = "oggy_secret_key_159357_chumt_ka_pyasa"

# A4F API Configuration
A4F_API_URL = "https://samuraiapi.in/v1/chat/completions"
A4F_API_KEY = "sk-NK6SS9tpWghyFJwkZLoCis1sMaF6RwQ5WF09mUoKKR0VKCm7"
A4F_MODEL = "provider10-claude-sonnet-4-20250514(clinesp)"

# Owner credentials
OWNER_USERNAME = "OGGY"
OWNER_PASSWORD = "OGGY@159357"

# Pending approvals database
pending_approvals = {}
approved_users = {}
user_data = {}

# Server stats
server_stats = {
    "start_time": datetime.now(),
    "is_running": True,
    "cpu_usage": 0.5,
    "ram_usage": 256,
    "total_users": 0,
    "bot_speed": "0.2ms",
    "logs": ["[INFO] OGGY HOSTING initialized"]
}

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
    <title>OGGY HOSTING - Premium Solution</title>
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
        
        .login-box, .register-box {
            background: rgba(0, 0, 0, 0.85);
            border: 2px solid #ff00ff;
            border-radius: 15px;
            padding: 40px;
            max-width: 500px;
            margin: 50px auto;
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
        
        .input-group input, .input-group select {
            width: 100%;
            padding: 12px;
            background: #000;
            border: 1px solid #ff00ff;
            color: #ff00ff;
            font-family: monospace;
            font-size: 1em;
            border-radius: 5px;
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
            flex-wrap: wrap;
        }
        
        .logout-btn, .back-btn {
            width: auto;
            padding: 8px 20px;
            background: #ff0040;
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
        }
        
        .command-buttons {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .cmd-btn {
            background: #1a0033;
            border: 1px solid #ff00ff;
            color: #ff00ff;
            font-size: 0.9em;
        }
        
        .cmd-btn:hover {
            background: #ff00ff;
            color: #000;
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
        
        .pending-list {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .pending-item {
            border: 1px solid #ff00ff;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
        
        .approve-btn, .reject-btn {
            width: auto;
            padding: 5px 15px;
            margin: 5px;
        }
        
        .approve-btn { background: #00ff00; color: #000; }
        .reject-btn { background: #ff0000; }
        
        .footer {
            text-align: center;
            padding: 20px;
            margin-top: 30px;
            border-top: 1px solid #ff00ff;
            font-size: 0.8em;
        }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 1.5em; }
            .command-buttons { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 OGGY HOSTING</h1>
            <p>Premium Hosting Solution | Developer: OGGY</p>
        </div>
        
        <!-- Login/Register Choice -->
        <div id="choiceBox" class="login-box">
            <h3>Welcome to OGGY HOSTING</h3>
            <button onclick="showLogin()" style="margin-bottom: 10px;">Login</button>
            <button onclick="showRegister()">Register New Account</button>
        </div>
        
        <!-- Login Form -->
        <div id="loginForm" class="login-box" style="display: none;">
            <h3>🔐 Login to OGGY HOSTING</h3>
            <form id="login">
                <div class="input-group">
                    <label>Username</label>
                    <input type="text" id="loginUsername" required>
                </div>
                <div class="input-group">
                    <label>Password</label>
                    <input type="password" id="loginPassword" required>
                </div>
                <button type="submit">Login</button>
                <button type="button" onclick="showChoice()" style="margin-top: 10px; background: #333;">Back</button>
            </form>
        </div>
        
        <!-- Register Form -->
        <div id="registerForm" class="register-box" style="display: none;">
            <h3>📝 Register New Account</h3>
            <p style="margin-bottom: 15px; font-size: 0.8em;">Request will be sent to owner for approval</p>
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
                <button type="submit">Request Approval</button>
                <button type="button" onclick="showChoice()" style="margin-top: 10px; background: #333;">Back</button>
            </form>
        </div>
        
        <!-- User Dashboard -->
        <div id="userDashboard" class="dashboard">
            <div class="top-bar">
                <div>
                    <strong># OGGY HOSTING</strong><br>
                    Welcome: <span id="welcomeUser"></span> <span id="userRole"></span>
                </div>
                <button class="logout-btn" onclick="logout()">Logout</button>
            </div>
            
            <div class="stats-panel">
                <div class="stat-card">
                    <div class="stat-label">SERVER ADDRESS</div>
                    <div class="stat-value">https://oggy-host-01.xyz</div>
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
                    <div class="stat-label">BOT SPEED</div>
                    <div class="stat-value" id="botSpeed">0.2ms</div>
                </div>
            </div>
            
            <!-- Command Buttons - Dynamic based on role -->
            <div id="commandButtons" class="command-buttons"></div>
            
            <div class="terminal">
                <div class="terminal-header">
                    <span>$ OGGY Command Terminal</span>
                </div>
                <div class="terminal-body" id="terminalBody">
                    <div class="terminal-line">$ Welcome to OGGY HOSTING</div>
                    <div class="terminal-line">$ Type commands or use buttons below</div>
                </div>
                <div style="padding: 10px;">
                    <div class="terminal-input-line" style="display: flex; gap: 10px;">
                        <span>$</span>
                        <input type="text" id="commandInput" class="terminal-input" style="flex:1; background:#111; border:1px solid #ff00ff; color:#ff00ff; padding:8px;" placeholder="Type command or ask AI...">
                        <button onclick="executeCommand()" style="width: auto; padding: 5px 15px;">⏎</button>
                    </div>
                </div>
            </div>
            
            <div id="aiResponse" class="stat-card" style="display: none;">
                <strong>🤖 MPX AI Response:</strong>
                <div id="aiContent"></div>
            </div>
            
            <!-- Admin Panel -->
            <div id="adminPanel" style="display: none;">
                <h3>👑 Admin Panel - Pending Approvals</h3>
                <div id="pendingList" class="pending-list"></div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        Developer: OGGY | SIN: 159357 | © 2026 OGGY HOSTING
    </div>
    
    <script>
        let uptimeInterval;
        let currentUser = null;
        let currentRole = null;
        
        // Update uptime
        function updateUptime() {
            if (!window.startTime) window.startTime = new Date();
            const diff = Math.floor((new Date() - window.startTime) / 1000);
            const hours = Math.floor(diff / 3600);
            const minutes = Math.floor((diff % 3600) / 60);
            const seconds = diff % 60;
            document.getElementById('uptime').innerText = `${hours}h ${minutes}m ${seconds}s`;
        }
        
        function showChoice() {
            document.getElementById('choiceBox').style.display = 'block';
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('registerForm').style.display = 'none';
        }
        
        function showLogin() {
            document.getElementById('choiceBox').style.display = 'none';
            document.getElementById('loginForm').style.display = 'block';
            document.getElementById('registerForm').style.display = 'none';
        }
        
        function showRegister() {
            document.getElementById('choiceBox').style.display = 'none';
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('registerForm').style.display = 'block';
        }
        
        function addTerminalLine(text) {
            const terminalBody = document.getElementById('terminalBody');
            const line = document.createElement('div');
            line.className = 'terminal-line';
            line.innerHTML = `$ ${text}`;
            terminalBody.appendChild(line);
            terminalBody.scrollTop = terminalBody.scrollHeight;
        }
        
        async function executeCommand() {
            const input = document.getElementById('commandInput');
            const command = input.value.trim();
            if (!command) return;
            
            addTerminalLine(`> ${command}`);
            
            const response = await fetch('/api/command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: command, user: currentUser})
            });
            const data = await response.json();
            addTerminalLine(data.response);
            
            if (data.aiResponse) {
                document.getElementById('aiContent').innerHTML = data.aiResponse;
                document.getElementById('aiResponse').style.display = 'block';
                setTimeout(() => {
                    document.getElementById('aiResponse').style.display = 'none';
                }, 8000);
            }
            
            input.value = '';
        }
        
        // Button actions
        async function buttonAction(action) {
            addTerminalLine(`Executing: ${action}`);
            const response = await fetch('/api/button', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: action, user: currentUser})
            });
            const data = await response.json();
            addTerminalLine(data.response);
            if (data.data && action === '📊 Statistics') {
                addTerminalLine(`Total Users: ${data.data.total_users}`);
                addTerminalLine(`Bot Speed: ${data.data.bot_speed}`);
                addTerminalLine(`CPU: ${data.data.cpu}% | RAM: ${data.data.ram}MB`);
            }
            if (action === '🤖 MPX Ai') {
                document.getElementById('aiContent').innerHTML = data.aiResponse || "MPX AI Ready! Type anything in terminal.";
                document.getElementById('aiResponse').style.display = 'block';
                setTimeout(() => {
                    document.getElementById('aiResponse').style.display = 'none';
                }, 10000);
            }
        }
        
        function loadCommandButtons(role) {
            let buttons = [];
            if (role === 'admin') {
                buttons = [
                    ["📢 Updates Channel", "/ping"],
                    ["📤 Upload File", "📂 Check Files"],
                    ["⚡ Bot Speed", "📊 Statistics"],
                    ["💳 Subscriptions", "📢 Broadcast"],
                    ["🔒 Lock Bot", "🟢 Running All Code"],
                    ["👑 Admin Panel", "📞 Contact Owner"],
                    ["🤖 MPX Ai", "⏱ Uptime"]
                ];
            } else {
                buttons = [
                    ["📢 Updates Channel", "⏱ Uptime"],
                    ["📤 Upload File", "📂 Check Files"],
                    ["⚡ Bot Speed", "📊 Statistics"],
                    ["📞 Contact Owner", "🤖 MPX Ai"]
                ];
            }
            
            const container = document.getElementById('commandButtons');
            container.innerHTML = '';
            buttons.forEach(row => {
                row.forEach(btnText => {
                    const btn = document.createElement('button');
                    btn.className = 'cmd-btn';
                    btn.innerText = btnText;
                    btn.onclick = () => buttonAction(btnText);
                    container.appendChild(btn);
                });
            });
        }
        
        async function loadAdminPanel() {
            if (currentRole !== 'admin') return;
            const response = await fetch('/api/pending');
            const data = await response.json();
            const container = document.getElementById('pendingList');
            if (data.pending && data.pending.length > 0) {
                container.innerHTML = data.pending.map(p => `
                    <div class="pending-item">
                        <strong>${p.username}</strong><br>
                        Email: ${p.email || 'N/A'}<br>
                        Requested: ${p.time}<br>
                        <button class="approve-btn" onclick="approveUser('${p.username}')">Approve</button>
                        <button class="reject-btn" onclick="rejectUser('${p.username}')">Reject</button>
                    </div>
                `).join('');
            } else {
                container.innerHTML = '<p>No pending approvals</p>';
            }
        }
        
        async function approveUser(username) {
            const response = await fetch('/api/approve', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: username})
            });
            const data = await response.json();
            addTerminalLine(`[ADMIN] ${data.message}`);
            loadAdminPanel();
        }
        
        async function rejectUser(username) {
            const response = await fetch('/api/reject', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: username})
            });
            const data = await response.json();
            addTerminalLine(`[ADMIN] ${data.message}`);
            loadAdminPanel();
        }
        
        // Login handler
        document.getElementById('login').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;
            
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            });
            
            const data = await response.json();
            if (data.success) {
                currentUser = username;
                currentRole = data.role;
                document.getElementById('choiceBox').style.display = 'none';
                document.getElementById('loginForm').style.display = 'none';
                document.getElementById('registerForm').style.display = 'none';
                document.getElementById('userDashboard').style.display = 'block';
                document.getElementById('welcomeUser').innerHTML = username;
                document.getElementById('userRole').innerHTML = ` (${currentRole})`;
                if (currentRole === 'admin') {
                    document.getElementById('adminPanel').style.display = 'block';
                    loadAdminPanel();
                }
                loadCommandButtons(currentRole);
                window.startTime = new Date();
                if (uptimeInterval) clearInterval(uptimeInterval);
                uptimeInterval = setInterval(updateUptime, 1000);
                addTerminalLine(`Welcome ${username}! Type help for commands`);
            } else {
                alert(data.message || 'Login failed');
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
            currentUser = null;
            currentRole = null;
            document.getElementById('userDashboard').style.display = 'none';
            document.getElementById('choiceBox').style.display = 'block';
            document.getElementById('adminPanel').style.display = 'none';
        }
        
        setInterval(async () => {
            if (currentUser) {
                const response = await fetch('/api/stats');
                const data = await response.json();
                document.getElementById('botSpeed').innerText = data.bot_speed;
            }
        }, 5000);
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
    
    if username in approved_users or username in pending_approvals:
        return jsonify({'success': False, 'message': 'Username already exists or pending'})
    
    pending_approvals[username] = {
        'password': password,
        'email': email,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    return jsonify({'success': True, 'message': 'Request sent to owner for approval'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Owner login
    if username == OWNER_USERNAME and password == OWNER_PASSWORD:
        return jsonify({'success': True, 'role': 'admin'})
    
    # Approved user login
    if username in approved_users and approved_users[username]['password'] == password:
        return jsonify({'success': True, 'role': 'user'})
    
    return jsonify({'success': False, 'message': 'Invalid credentials or account not approved'})

@app.route('/api/pending')
def get_pending():
    pending_list = [{'username': k, 'email': v['email'], 'time': v['time']} for k, v in pending_approvals.items()]
    return jsonify({'pending': pending_list})

@app.route('/api/approve', methods=['POST'])
def approve():
    data = request.json
    username = data.get('username')
    
    if username in pending_approvals:
        approved_users[username] = pending_approvals[username]
        del pending_approvals[username]
        server_stats['total_users'] += 1
        return jsonify({'success': True, 'message': f'User {username} approved'})
    return jsonify({'success': False, 'message': 'User not found'})

@app.route('/api/reject', methods=['POST'])
def reject():
    data = request.json
    username = data.get('username')
    
    if username in pending_approvals:
        del pending_approvals[username]
        return jsonify({'success': True, 'message': f'User {username} rejected'})
    return jsonify({'success': False, 'message': 'User not found'})

@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.json
    command = data.get('command', '').lower()
    user = data.get('user', '')
    
    if command in ['help', '?']:
        return jsonify({'response': 'Available: stats, uptime, ai [question], clear, buttons'})
    elif command == 'stats':
        return jsonify({'response': f'Users: {server_stats["total_users"]} | CPU: {server_stats["cpu_usage"]}% | RAM: {server_stats["ram_usage"]}MB'})
    elif command == 'uptime':
        diff = datetime.now() - server_stats['start_time']
        return jsonify({'response': f'Uptime: {str(diff).split(".")[0]}'})
    elif command.startswith('ai '):
        prompt = command[3:]
        ai_response = call_a4f_api(prompt)
        return jsonify({'response': f'[MPX AI]: {ai_response[:200]}...', 'aiResponse': ai_response})
    elif command == 'clear':
        return jsonify({'response': '[CLEAR] Terminal cleared'})
    else:
        ai_response = call_a4f_api(command)
        return jsonify({'response': f'[MPX AI]: {ai_response[:200]}...', 'aiResponse': ai_response})

@app.route('/api/button', methods=['POST'])
def handle_button():
    data = request.json
    action = data.get('action', '')
    user = data.get('user', '')
    
    responses = {
        '📢 Updates Channel': '📢 Join @OGGY_UPDATES for latest news!',
        '⏱ Uptime': f'⏱ Server Uptime: {datetime.now() - server_stats["start_time"]}',
        '📤 Upload File': '📤 Send file via /upload command',
        '📂 Check Files': '📂 Use /files to list your files',
        '⚡ Bot Speed': f'⚡ Current speed: {server_stats["bot_speed"]}',
        '📊 Statistics': f'📊 Stats: {server_stats["total_users"]} users | CPU {server_stats["cpu_usage"]}%',
        '📞 Contact Owner': '📞 Contact @OGGY on Telegram',
        '🤖 MPX Ai': '🤖 MPX AI Ready! Type your question in terminal with "ai " prefix',
        '/ping': '🏓 Pong! Bot is alive',
        '💳 Subscriptions': '💳 Premium plans: 1 Month - $5 | Lifetime - $50',
        '📢 Broadcast': '📢 Send message to broadcast in terminal',
        '🔒 Lock Bot': '🔒 Bot locked by admin',
        '🟢 Running All Code': '✅ All codes running normally',
        '👑 Admin Panel': '👑 Admin panel loaded above',
    }
    
    # Special handling for Statistics
    if action == '📊 Statistics':
        return jsonify({'response': responses[action], 'data': {
            'total_users': server_stats['total_users'],
            'bot_speed': server_stats['bot_speed'],
            'cpu': server_stats['cpu_usage'],
            'ram': server_stats['ram_usage']
        }})
    
    return jsonify({'response': responses.get(action, f'🔧 {action} feature coming soon')})

@app.route('/api/stats')
def get_stats():
    return jsonify({
        'bot_speed': server_stats['bot_speed'],
        'total_users': server_stats['total_users'],
        'cpu': server_stats['cpu_usage'],
        'ram': server_stats['ram_usage']
    })

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║                 OGGY HOSTING READY                    ║
    ╠══════════════════════════════════════════════════════╣
    ║  URL: http://localhost:5000                          ║
    ║  Owner Login: OGGY / OGGY@159357                     ║
    ║                                                      ║
    ║  Features:                                           ║
    ║  - User Registration (requires admin approval)       ║
    ║  - Admin Approval System                             ║
    ║  - Telegram-style Command Buttons                    ║
    ║  - A4F Claude Sonnet 4 AI Integration               ║
    ║  - Real-time Stats & Uptime                         ║
    ║                                                      ║
    ║  Developer: OGGY | SIN: 159357                       ║
    ╚══════════════════════════════════════════════════════╝
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)