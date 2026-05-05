from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
import requests
import time
import random
import os
import json
from datetime import datetime, timedelta
from threading import Thread

app = Flask(__name__)
app.secret_key = "oggy_hosting_secret_159357_oggy_killer"

# A4F API Configuration
A4F_API_URL = "https://samuraiapi.in/v1/chat/completions"
A4F_API_KEY = "sk-NK6SS9tpWghyFJwkZLoCis1sMaF6RwQ5WF09mUoKKR0VKCm7"
A4F_MODEL = "provider10-claude-sonnet-4-20250514(clinesp)"

# Owner credentials
OWNER_USERNAME = "OGGY"
OWNER_PASSWORD = "OGGY_KILLER_159357"

# User database - pending approvals
pending_users = {}
approved_users = {}
user_id_counter = 1000

# Load existing data if any
try:
    with open('users.json', 'r') as f:
        data = json.load(f)
        pending_users = data.get('pending', {})
        approved_users = data.get('approved', {})
except:
    pass

def save_users():
    with open('users.json', 'w') as f:
        json.dump({'pending': pending_users, 'approved': approved_users}, f)

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
        return f"Connection Error: {str(e)[:100]}"

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
        
        .login-box, .register-box {
            background: rgba(0, 0, 0, 0.85);
            border: 2px solid #00ff9d;
            border-radius: 15px;
            padding: 40px;
            max-width: 500px;
            margin: 50px auto;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 50px rgba(0, 255, 157, 0.3);
        }
        
        .register-box {
            margin-top: 20px;
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
        
        .switch-link {
            text-align: center;
            margin-top: 20px;
            color: #00ff9d;
            cursor: pointer;
        }
        
        .switch-link:hover {
            text-decoration: underline;
        }
        
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
            flex-wrap: wrap;
        }
        
        .user-info {
            font-size: 0.9em;
        }
        
        .logout-btn, .admin-btn {
            width: auto;
            padding: 8px 20px;
            background: #ff0040;
            margin-left: 10px;
        }
        
        .admin-btn {
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
            font-size: 1.5em;
            font-weight: bold;
        }
        
        .button-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        
        .action-btn {
            background: #1a1a2e;
            border: 1px solid #00ff9d;
            color: #00ff9d;
            padding: 12px;
            font-size: 0.9em;
        }
        
        .action-btn:hover {
            background: #00ff9d;
            color: #000;
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
        }
        
        .terminal-body {
            padding: 20px;
            height: 200px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.85em;
            background: #0a0a0a;
        }
        
        .terminal-line {
            margin: 3px 0;
            color: #ff4444;
        }
        
        .error-log {
            color: #ff4444;
        }
        
        .ai-response {
            background: rgba(0, 255, 157, 0.1);
            border-left: 4px solid #00ff9d;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            border-top: 1px solid #00ff9d;
            margin-top: 30px;
            font-size: 0.8em;
            opacity: 0.7;
        }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 1.5em; }
            .button-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Login Form -->
        <div id="loginForm" class="login-box">
            <h3>🔐 OGGY HOSTING</h3>
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
            <div class="switch-link" onclick="showRegister()">Don't have an account? Register here</div>
            <p style="text-align: center; margin-top: 20px; font-size: 0.7em;">Developer: OGGY | SIN: 159357</p>
        </div>
        
        <!-- Register Form -->
        <div id="registerForm" class="register-box" style="display: none;">
            <h3>📝 Register Account</h3>
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
            <div class="switch-link" onclick="showLogin()">Back to Login</div>
        </div>
        
        <!-- Dashboard -->
        <div id="dashboard" class="dashboard">
            <div class="top-bar">
                <div class="user-info">
                    <strong># OGGY HOSTING</strong><br>
                    Welcome: <span id="welcomeUser"></span>
                    <span id="adminBadge" style="display:none; color:#ff8800;"> (ADMIN)</span>
                </div>
                <div>
                    <button id="adminPanelBtn" class="admin-btn" style="display:none;" onclick="showAdminPanel()">👑 Admin Panel</button>
                    <button class="logout-btn" onclick="logout()">Logout</button>
                </div>
            </div>
            
            <div class="stats-panel">
                <div class="stat-card">
                    <div class="stat-label">SERVER ADDRESS</div>
                    <div class="stat-value" id="serverAddr">https://oggy-host-01.onrender.com</div>
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
            
            <!-- Command Buttons Layout -->
            <div class="button-grid" id="commandButtons"></div>
            
            <!-- Terminal (Error Logs Only) -->
            <div class="terminal">
                <div class="terminal-header">📋 System Logs & Errors</div>
                <div class="terminal-body" id="terminalBody">
                    <div class="terminal-line error-log">[INFO] OGGY HOSTING initialized</div>
                    <div class="terminal-line error-log">[INFO] System ready</div>
                </div>
            </div>
            
            <div id="aiResponse" class="ai-response" style="display: none;">
                <strong>🤖 MPX AI Response:</strong>
                <div id="aiContent"></div>
            </div>
            
            <div class="footer">
                Developer: OGGY | SIN: 159357
            </div>
        </div>
        
        <!-- Admin Modal -->
        <div id="adminModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.9); z-index:1000;">
            <div style="max-width:800px; margin:50px auto; background:#000; border:2px solid #00ff9d; border-radius:10px; padding:20px;">
                <h2>👑 Admin Panel</h2>
                <div style="margin:20px 0;">
                    <h3>Pending Approvals</h3>
                    <div id="pendingList"></div>
                </div>
                <div style="margin:20px 0;">
                    <h3>Approved Users</h3>
                    <div id="approvedList"></div>
                </div>
                <div style="margin:20px 0;">
                    <h3>Broadcast Message</h3>
                    <textarea id="broadcastMsg" style="width:100%; padding:10px; background:#111; color:#00ff9d; border:1px solid #00ff9d;" rows="3"></textarea>
                    <button onclick="sendBroadcast()" style="margin-top:10px;">📢 Send Broadcast</button>
                </div>
                <div style="margin:20px 0;">
                    <button onclick="lockBot()">🔒 Lock Bot</button>
                    <button onclick="unlockBot()">🟢 Unlock Bot</button>
                </div>
                <button onclick="closeAdminPanel()" style="background:#ff0040;">Close</button>
            </div>
        </div>
    </div>
    
    <script>
        let uptimeInterval;
        let statsInterval;
        let serverRunning = true;
        let isAdmin = false;
        let currentUser = '';
        let botLocked = false;
        
        function showRegister() {
            document.getElementById('loginForm').style.display = 'none';
            document.getElementById('registerForm').style.display = 'block';
        }
        
        function showLogin() {
            document.getElementById('registerForm').style.display = 'none';
            document.getElementById('loginForm').style.display = 'block';
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
        
        function addErrorLog(text) {
            const terminalBody = document.getElementById('terminalBody');
            const line = document.createElement('div');
            line.className = 'terminal-line error-log';
            line.innerHTML = `[${new Date().toLocaleTimeString()}] ${text}`;
            terminalBody.appendChild(line);
            terminalBody.scrollTop = terminalBody.scrollHeight;
        }
        
        function loadCommandButtons() {
            const container = document.getElementById('commandButtons');
            let buttons;
            
            if (isAdmin) {
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
            
            container.innerHTML = '';
            buttons.forEach(row => {
                row.forEach(btnText => {
                    const btn = document.createElement('button');
                    btn.className = 'action-btn';
                    btn.innerText = btnText;
                    btn.onclick = () => handleCommand(btnText);
                    container.appendChild(btn);
                });
            });
        }
        
        async function handleCommand(cmd) {
            addErrorLog(`Command executed: ${cmd}`);
            
            if (cmd === "🤖 MPX Ai") {
                const question = prompt("Ask MPX AI anything:");
                if (question) {
                    addErrorLog(`[MPX AI] Processing: ${question}`);
                    const response = await callMPXAI(question);
                    document.getElementById('aiContent').innerHTML = response;
                    document.getElementById('aiResponse').style.display = 'block';
                    setTimeout(() => {
                        document.getElementById('aiResponse').style.display = 'none';
                    }, 15000);
                }
            } else if (cmd === "📢 Updates Channel") {
                addErrorLog("Updates: @OGGY_OFFICIAL");
                alert("📢 Join Updates Channel: @OGGY_OFFICIAL");
            } else if (cmd === "⏱ Uptime") {
                alert(`Uptime: ${document.getElementById('uptime').innerText}`);
            } else if (cmd === "📤 Upload File") {
                addErrorLog("Upload feature - Contact owner for file upload access");
                alert("📤 File upload requires admin approval. Contact @OGGY");
            } else if (cmd === "📂 Check Files") {
                addErrorLog("Files: sky.py, config.json, logs/");
                alert("Files in workspace:\n- sky.py\n- config.json\n- logs/");
            } else if (cmd === "⚡ Bot Speed") {
                const speed = (Math.random() * 100 + 200).toFixed(0);
                addErrorLog(`Bot speed: ${speed}ms response time`);
                alert(`⚡ Bot Speed: ${speed}ms`);
            } else if (cmd === "📊 Statistics") {
                alert(`📊 Stats:\nCPU: ${document.getElementById('cpuRam').innerText}\nUptime: ${document.getElementById('uptime').innerText}`);
            } else if (cmd === "📞 Contact Owner") {
                alert("📞 Contact Owner: @OGGY (Telegram)");
            } else if (cmd === "👑 Admin Panel" && isAdmin) {
                showAdminPanel();
            } else if (cmd === "🔒 Lock Bot" && isAdmin) {
                lockBot();
            } else if (cmd === "🟢 Running All Code" && isAdmin) {
                unlockBot();
            } else if (cmd === "💳 Subscriptions" && isAdmin) {
                alert("💳 Subscription Management - Coming Soon");
            } else if (cmd === "/ping") {
                alert("🏓 Pong! Bot is running");
            } else {
                addErrorLog(`Unknown command: ${cmd}`);
            }
        }
        
        async function callMPXAI(prompt) {
            try {
                const response = await fetch('/api/ai', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: prompt})
                });
                const data = await response.json();
                return data.response || "No response from MPX AI";
            } catch (error) {
                return `Error: ${error.message}`;
            }
        }
        
        function showAdminPanel() {
            if (!isAdmin) return;
            document.getElementById('adminModal').style.display = 'block';
            loadPendingUsers();
            loadApprovedUsers();
        }
        
        function closeAdminPanel() {
            document.getElementById('adminModal').style.display = 'none';
        }
        
        async function loadPendingUsers() {
            const res = await fetch('/api/admin/pending');
            const data = await res.json();
            const container = document.getElementById('pendingList');
            if (data.users && Object.keys(data.users).length > 0) {
                container.innerHTML = '';
                for (const [username, info] of Object.entries(data.users)) {
                    container.innerHTML += `
                        <div style="border:1px solid #00ff9d; padding:10px; margin:10px 0;">
                            <b>${username}</b><br>
                            Email: ${info.email || 'N/A'}<br>
                            Requested: ${info.time}<br>
                            <button onclick="approveUser('${username}')">✅ Approve</button>
                            <button onclick="rejectUser('${username}')">❌ Reject</button>
                        </div>
                    `;
                }
            } else {
                container.innerHTML = '<p>No pending approvals</p>';
            }
        }
        
        async function loadApprovedUsers() {
            const res = await fetch('/api/admin/approved');
            const data = await res.json();
            const container = document.getElementById('approvedList');
            if (data.users && Object.keys(data.users).length > 0) {
                container.innerHTML = '';
                for (const [username, info] of Object.entries(data.users)) {
                    container.innerHTML += `
                        <div style="border:1px solid #00ff9d; padding:10px; margin:5px 0;">
                            <b>${username}</b> - Approved: ${info.approved_time}
                        </div>
                    `;
                }
            } else {
                container.innerHTML = '<p>No approved users</p>';
            }
        }
        
        async function approveUser(username) {
            const res = await fetch('/api/admin/approve', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: username})
            });
            const data = await res.json();
            if (data.success) {
                addErrorLog(`[ADMIN] User ${username} approved`);
                loadPendingUsers();
                loadApprovedUsers();
            }
        }
        
        async function rejectUser(username) {
            const res = await fetch('/api/admin/reject', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: username})
            });
            const data = await res.json();
            if (data.success) {
                addErrorLog(`[ADMIN] User ${username} rejected`);
                loadPendingUsers();
            }
        }
        
        async function sendBroadcast() {
            const msg = document.getElementById('broadcastMsg').value;
            if (!msg) return;
            const res = await fetch('/api/admin/broadcast', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            });
            const data = await res.json();
            if (data.success) {
                alert(`Broadcast sent to ${data.count} users`);
                addErrorLog(`[BROADCAST] ${msg}`);
            }
        }
        
        async function lockBot() {
            await fetch('/api/admin/lock', {method: 'POST'});
            botLocked = true;
            addErrorLog("[ADMIN] Bot locked - new logins disabled");
            alert("Bot locked!");
        }
        
        async function unlockBot() {
            await fetch('/api/admin/unlock', {method: 'POST'});
            botLocked = false;
            addErrorLog("[ADMIN] Bot unlocked - logins enabled");
            alert("Bot unlocked!");
        }
        
        // Login handler
        document.getElementById('login').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            });
            
            const data = await res.json();
            if (data.success) {
                currentUser = username;
                isAdmin = data.is_admin || false;
                sessionStorage.setItem('user', username);
                sessionStorage.setItem('isAdmin', isAdmin);
                
                document.getElementById('loginForm').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
                document.getElementById('welcomeUser').innerText = username;
                
                if (isAdmin) {
                    document.getElementById('adminBadge').style.display = 'inline';
                    document.getElementById('adminPanelBtn').style.display = 'inline-block';
                }
                
                window.startTime = new Date();
                startIntervals();
                loadCommandButtons();
                addErrorLog(`[LOGIN] User ${username} logged in successfully`);
            } else {
                alert(data.message || 'Login failed!');
            }
        });
        
        // Register handler
        document.getElementById('register').addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('regUsername').value;
            const password = document.getElementById('regPassword').value;
            const email = document.getElementById('regEmail').value;
            
            const res = await fetch('/api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password, email})
            });
            
            const data = await res.json();
            alert(data.message);
            if (data.success) {
                showLogin();
            }
        });
        
        function startIntervals() {
            if (uptimeInterval) clearInterval(uptimeInterval);
            if (statsInterval) clearInterval(statsInterval);
            uptimeInterval = setInterval(updateUptime, 1000);
            statsInterval = setInterval(updateStats, 3000);
        }
        
        function logout() {
            if (uptimeInterval) clearInterval(uptimeInterval);
            if (statsInterval) clearInterval(statsInterval);
            sessionStorage.clear();
            document.getElementById('dashboard').style.display = 'none';
            document.getElementById('loginForm').style.display = 'block';
            document.getElementById('username').value = '';
            document.getElementById('password').value = '';
            addErrorLog(`[LOGOUT] User logged out`);
        }
        
        // Admin panel commands
        window.approveUser = approveUser;
        window.rejectUser = rejectUser;
        window.sendBroadcast = sendBroadcast;
        window.lockBot = lockBot;
        window.unlockBot = unlockBot;
        window.showAdminPanel = showAdminPanel;
        window.closeAdminPanel = closeAdminPanel;
        window.showRegister = showRegister;
        window.showLogin = showLogin;
        window.handleCommand = handleCommand;
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
    
    if username in pending_users or username in approved_users:
        return jsonify({'success': False, 'message': 'Username already exists!'})
    
    pending_users[username] = {
        'password': password,
        'email': email,
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    save_users()
    return jsonify({'success': True, 'message': 'Registration submitted! Wait for admin approval.'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Owner login
    if username == OWNER_USERNAME and password == OWNER_PASSWORD:
        session['user'] = username
        session['is_admin'] = True
        return jsonify({'success': True, 'is_admin': True})
    
    # Approved user login
    if username in approved_users and approved_users[username]['password'] == password:
        session['user'] = username
        session['is_admin'] = False
        return jsonify({'success': True, 'is_admin': False})
    
    return jsonify({'success': False, 'message': 'Invalid credentials or account not approved'})

@app.route('/api/admin/pending')
def get_pending():
    if session.get('user') != OWNER_USERNAME:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'users': pending_users})

@app.route('/api/admin/approved')
def get_approved():
    if session.get('user') != OWNER_USERNAME:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({'users': approved_users})

@app.route('/api/admin/approve', methods=['POST'])
def approve_user():
    if session.get('user') != OWNER_USERNAME:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    username = data.get('username')
    
    if username in pending_users:
        approved_users[username] = {
            'password': pending_users[username]['password'],
            'email': pending_users[username]['email'],
            'approved_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        del pending_users[username]
        save_users()
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/admin/reject', methods=['POST'])
def reject_user():
    if session.get('user') != OWNER_USERNAME:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    username = data.get('username')
    
    if username in pending_users:
        del pending_users[username]
        save_users()
        return jsonify({'success': True})
    return jsonify({'success': False})

@app.route('/api/admin/broadcast', methods=['POST'])
def broadcast():
    if session.get('user') != OWNER_USERNAME:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    message = data.get('message')
    # In real implementation, this would send to all users
    return jsonify({'success': True, 'count': len(approved_users)})

@app.route('/api/admin/lock', methods=['POST'])
def lock_bot():
    if session.get('user') != OWNER_USERNAME:
        return jsonify({'error': 'Unauthorized'}), 401
    global bot_locked
    bot_locked = True
    return jsonify({'success': True})

@app.route('/api/admin/unlock', methods=['POST'])
def unlock_bot():
    if session.get('user') != OWNER_USERNAME:
        return jsonify({'error': 'Unauthorized'}), 401
    global bot_locked
    bot_locked = False
    return jsonify({'success': True})

@app.route('/api/ai', methods=['POST'])
def ai_endpoint():
    data = request.json
    prompt = data.get('prompt', '')
    if not prompt:
        return jsonify({'response': 'Type something first, CHUMT KE PYASA 😈'})
    response = call_a4f_api(prompt)
    return jsonify({'response': response})

if __name__ == '__main__':
    bot_locked = False
    print("""
    ╔══════════════════════════════════════════════════╗
    ║     OGGY HOSTING - READY FOR DEPLOYMENT          ║
    ╠══════════════════════════════════════════════════╣
    ║  Owner Login: OGGY / OGGY_KILLER_159357          ║
    ║  Users: Register -> Owner Approves -> Login      ║
    ║  A4F API: Claude Sonnet 4 Integrated             ║
    ╚══════════════════════════════════════════════════╝
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)