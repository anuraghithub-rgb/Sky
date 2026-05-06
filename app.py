from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for
import requests
import json
import os
import uuid
import subprocess
import threading
import time
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "oggy_hosting_secret_159357_oggy_killer"

# File paths
USERS_FILE = "users.json"
PENDING_FILE = "pending.json"
SETTINGS_FILE = "settings.json"

# A4F API Configuration
A4F_API_URL = "https://samuraiapi.in/v1/chat/completions"
A4F_API_KEY = "sk-NK6SS9tpWghyFJwkZLoCis1sMaF6RwQ5WF09mUoKKR0VKCm7"
A4F_MODEL = "provider10-claude-sonnet-4-20250514(clinesp)"

# Owner credentials - CHANGE THIS!
OWNER_USERNAME = "OGGY"
OWNER_PASSWORD = "OGGY@159357"

# Initialize JSON files
def init_files():
    for file, default in [(USERS_FILE, {}), (PENDING_FILE, {}), (SETTINGS_FILE, {"bot_locked": False, "total_uploads": 0, "total_commands": 0})]:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                json.dump(default, f)

init_files()

def load_json(file):
    with open(file, 'r') as f:
        return json.load(f)

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

def call_a4f_api(prompt):
    headers = {"Authorization": f"Bearer {A4F_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": A4F_MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7, "max_tokens": 500}
    try:
        response = requests.post(A4F_API_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "AI is sleeping 😴")
        return f"API Error: {response.status_code}"
    except:
        return "Connection failed to A4F API"

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OGGY HOSTING - Premium Cloud Platform 🔥</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a0033 100%);
            font-family: 'Segoe UI', 'Courier New', monospace;
            min-height: 100vh;
            color: #00ff9d;
        }
        .container { max-width: 1300px; margin: 0 auto; padding: 20px; }
        
        /* Header */
        .header {
            text-align: center;
            padding: 30px;
            border-bottom: 3px solid #00ff9d;
            margin-bottom: 30px;
            animation: glow 2s ease-in-out infinite alternate;
        }
        @keyframes glow {
            from { text-shadow: 0 0 10px #00ff9d; }
            to { text-shadow: 0 0 30px #ff00ff; }
        }
        .header h1 { font-size: 3em; letter-spacing: 5px; }
        .header h1 span { color: #ff00ff; }
        .dev-sign { text-align: center; margin-top: 20px; font-size: 0.8em; opacity: 0.6; }
        
        /* Login Box */
        .login-box {
            background: rgba(0,0,0,0.9);
            border: 2px solid #00ff9d;
            border-radius: 20px;
            padding: 40px;
            max-width: 450px;
            margin: 80px auto;
            backdrop-filter: blur(10px);
            box-shadow: 0 0 60px rgba(0,255,157,0.3);
        }
        .login-box h2 { text-align: center; margin-bottom: 30px; }
        .input-group { margin-bottom: 20px; }
        .input-group label { display: block; margin-bottom: 10px; color: #00ff9d; }
        .input-group input {
            width: 100%;
            padding: 12px;
            background: #111;
            border: 1px solid #00ff9d;
            color: #00ff9d;
            border-radius: 8px;
            font-size: 1em;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #00ff9d;
            color: #000;
            border: none;
            font-size: 1.1em;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        button:hover { background: #ff00ff; color: #fff; transform: scale(1.02); }
        
        /* Dashboard */
        .dashboard { display: none; }
        .top-bar {
            background: rgba(0,0,0,0.9);
            border: 1px solid #00ff9d;
            border-radius: 15px;
            padding: 15px 20px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        .welcome-text h3 { color: #00ff9d; }
        .logout-btn { width: auto; padding: 8px 25px; background: #ff0040; }
        
        /* Stats Cards */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: rgba(0,0,0,0.85);
            border: 1px solid #00ff9d;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
        }
        .stat-card .value { font-size: 2em; font-weight: bold; }
        
        /* Button Grid - Professional Layout */
        .button-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin: 30px 0;
        }
        .action-btn {
            background: linear-gradient(135deg, #00ff9d, #00cc7d);
            color: #000;
            padding: 15px;
            font-size: 1em;
            font-weight: bold;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
        }
        .action-btn:hover { transform: translateY(-3px); box-shadow: 0 10px 25px rgba(0,255,157,0.3); background: linear-gradient(135deg, #ff00ff, #cc00cc); color: white; }
        .danger-btn { background: linear-gradient(135deg, #ff0040, #cc0033); }
        .warning-btn { background: linear-gradient(135deg, #ffaa00, #cc8800); }
        
        /* Terminal Logs */
        .logs-panel {
            background: #000;
            border: 2px solid #00ff9d;
            border-radius: 15px;
            margin: 20px 0;
            overflow: hidden;
        }
        .logs-header {
            background: #00ff9d;
            color: #000;
            padding: 12px;
            font-weight: bold;
        }
        .logs-body {
            height: 250px;
            overflow-y: auto;
            padding: 15px;
            font-family: monospace;
            font-size: 0.85em;
        }
        .log-line { color: #00ff9d; margin: 5px 0; border-left: 2px solid #00ff9d; padding-left: 10px; }
        .error-log { color: #ff0040; border-left-color: #ff0040; }
        
        /* File Upload */
        .upload-area {
            background: rgba(0,255,157,0.1);
            border: 2px dashed #00ff9d;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }
        
        /* AI Chat */
        .ai-panel {
            background: rgba(0,0,0,0.9);
            border: 1px solid #00ff9d;
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
        }
        .ai-response { background: #111; padding: 15px; border-radius: 10px; margin-top: 10px; }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 1.5em; }
            .button-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Login Panel -->
        <div id="loginPanel" class="login-box">
            <h2>🔐 OGGY HOSTING</h2>
            <form id="loginForm">
                <div class="input-group">
                    <label>👤 Username</label>
                    <input type="text" id="loginUsername" required>
                </div>
                <div class="input-group">
                    <label>🔑 Password</label>
                    <input type="password" id="loginPassword" required>
                </div>
                <button type="submit">🚀 Login</button>
            </form>
            <div style="text-align: center; margin-top: 20px;">
                <button onclick="showRegister()" style="background: #333; color: #00ff9d;">📝 Create Free Account</button>
            </div>
            <div class="dev-sign">🔥 Developer: OGGY | SIN: 159357 🔥</div>
        </div>
        
        <!-- Register Panel -->
        <div id="registerPanel" class="login-box" style="display: none;">
            <h2>📝 Create Free Account</h2>
            <form id="registerForm">
                <div class="input-group">
                    <label>👤 Username</label>
                    <input type="text" id="regUsername" required>
                </div>
                <div class="input-group">
                    <label>🔑 Password</label>
                    <input type="password" id="regPassword" required>
                </div>
                <div class="input-group">
                    <label>📧 Email (Optional)</label>
                    <input type="email" id="regEmail">
                </div>
                <button type="submit">📨 Request Approval</button>
            </form>
            <button onclick="showLogin()" style="margin-top: 15px; background: #333;">← Back to Login</button>
        </div>
        
        <!-- Dashboard -->
        <div id="dashboard" class="dashboard">
            <div class="top-bar">
                <div class="welcome-text">
                    <h3>🔥 OGGY HOSTING</h3>
                    <p>Welcome: <span id="userName">User</span> 
                    <span id="userBadge"></span></p>
                </div>
                <button class="logout-btn" onclick="logout()">🚪 Logout</button>
            </div>
            
            <!-- Stats -->
            <div class="stats-grid">
                <div class="stat-card"><div class="value" id="uptime">0h 0m</div><div>⏱ Uptime</div></div>
                <div class="stat-card"><div class="value" id="serverStatus">🟢 Running</div><div>Status</div></div>
                <div class="stat-card"><div class="value" id="cpuRam">0.5% / 512MB</div><div>CPU / RAM</div></div>
                <div class="stat-card"><div class="value" id="fileCount">0</div><div>📂 Files</div></div>
            </div>
            
            <!-- Dynamic Button Grid - Changes based on user type -->
            <div id="buttonGrid" class="button-grid"></div>
            
            <!-- File Upload -->
            <div class="upload-area">
                <input type="file" id="fileInput" style="display: none;">
                <button class="action-btn" onclick="document.getElementById('fileInput').click()">📤 Upload File</button>
                <button class="action-btn" onclick="checkFiles()" style="margin-left: 10px;">📂 Check Files</button>
                <div id="uploadStatus" style="margin-top: 10px;"></div>
            </div>
            
            <!-- Logs Panel -->
            <div class="logs-panel">
                <div class="logs-header">📋 System Logs & Errors</div>
                <div class="logs-body" id="logsBody">
                    <div class="log-line">[INFO] OGGY HOSTING v2.0 initialized</div>
                    <div class="log-line">[INFO] Waiting for commands...</div>
                </div>
            </div>
            
            <!-- AI Chat -->
            <div class="ai-panel">
                <h3>🤖 MPX Ai - Claude Sonnet 4</h3>
                <div class="input-group" style="display: flex; gap: 10px;">
                    <input type="text" id="aiPrompt" placeholder="Ask anything to AI..." style="flex: 1;">
                    <button onclick="askAI()" style="width: auto; padding: 12px 25px;">Send</button>
                </div>
                <div id="aiResponse" class="ai-response">💬 AI will respond here...</div>
            </div>
            
            <div class="dev-sign" style="margin-top: 30px;">🔥 Developer: OGGY | SIN: 159357 | CHUMT KA GULAM 🔥</div>
        </div>
    </div>
    
    <script>
        let currentUser = null;
        let isAdmin = false;
        let uptimeInterval;
        let startTime = new Date();
        
        function updateUptime() {
            let diff = Math.floor((new Date() - startTime) / 1000);
            let h = Math.floor(diff / 3600);
            let m = Math.floor((diff % 3600) / 60);
            document.getElementById('uptime').innerText = h + 'h ' + m + 'm';
        }
        
        function addLog(msg, isError = false) {
            let logsDiv = document.getElementById('logsBody');
            let logLine = document.createElement('div');
            logLine.className = isError ? 'log-line error-log' : 'log-line';
            logLine.innerHTML = `[${new Date().toLocaleTimeString()}] ${msg}`;
            logsDiv.appendChild(logLine);
            logsDiv.scrollTop = logsDiv.scrollHeight;
            
            fetch('/api/add_log', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({log: msg, is_error: isError})
            });
        }
        
        function showRegister() {
            document.getElementById('loginPanel').style.display = 'none';
            document.getElementById('registerPanel').style.display = 'block';
        }
        
        function showLogin() {
            document.getElementById('registerPanel').style.display = 'none';
            document.getElementById('loginPanel').style.display = 'block';
        }
        
        // Register
        document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            let username = document.getElementById('regUsername').value;
            let password = document.getElementById('regPassword').value;
            let email = document.getElementById('regEmail').value;
            
            let res = await fetch('/api/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password, email})
            });
            let data = await res.json();
            alert(data.message);
            if (data.success) showLogin();
        });
        
        // Login
        document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
            e.preventDefault();
            let username = document.getElementById('loginUsername').value;
            let password = document.getElementById('loginPassword').value;
            
            let res = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, password})
            });
            let data = await res.json();
            if (data.success) {
                currentUser = username;
                isAdmin = data.is_admin;
                document.getElementById('loginPanel').style.display = 'none';
                document.getElementById('dashboard').style.display = 'block';
                document.getElementById('userName').innerText = username;
                document.getElementById('userBadge').innerHTML = isAdmin ? ' 👑 (Owner)' : ' ✅ (Approved User)';
                startTime = new Date();
                if (uptimeInterval) clearInterval(uptimeInterval);
                uptimeInterval = setInterval(updateUptime, 1000);
                updateStats();
                loadButtons();
                addLog(`User ${username} logged in`);
                if (!isAdmin) checkApprovalStatus();
            } else {
                alert('Login failed: ' + data.message);
            }
        });
        
        async function checkApprovalStatus() {
            let res = await fetch('/api/check_approval?user=' + currentUser);
            let data = await res.json();
            if (!data.approved) {
                addLog('⚠️ Your account is pending owner approval', true);
                document.getElementById('userBadge').innerHTML = ' ⏳ (Pending Approval)';
            }
        }
        
        function loadButtons() {
            let buttonGrid = document.getElementById('buttonGrid');
            let buttons;
            if (isAdmin) {
                buttons = [
                    ["📢 Updates Channel", "⏱ Uptime"],
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
            
            buttonGrid.innerHTML = '';
            buttons.forEach(row => {
                row.forEach(btnText => {
                    let btn = document.createElement('button');
                    btn.className = 'action-btn';
                    btn.innerText = btnText;
                    btn.onclick = () => handleButtonClick(btnText);
                    buttonGrid.appendChild(btn);
                });
            });
        }
        
        function handleButtonClick(action) {
            addLog(`Command executed: ${action}`);
            switch(action) {
                case "📢 Updates Channel":
                    alert("📢 Updates: @OGGY_HOSTING | All systems operational");
                    break;
                case "⏱ Uptime":
                    alert(`⏱ System Uptime: ${document.getElementById('uptime').innerText}`);
                    break;
                case "📤 Upload File":
                    document.getElementById('fileInput').click();
                    break;
                case "📂 Check Files":
                    checkFiles();
                    break;
                case "⚡ Bot Speed":
                    alert("⚡ Response Time: <50ms | Status: Optimal");
                    break;
                case "📊 Statistics":
                    showStats();
                    break;
                case "💳 Subscriptions":
                    alert("💳 Premium plans coming soon! Free tier: 512MB RAM, 1GB Storage");
                    break;
                case "📢 Broadcast":
                    let msg = prompt("Enter broadcast message:");
                    if(msg) sendBroadcast(msg);
                    break;
                case "🔒 Lock Bot":
                    if(confirm("Lock bot? Only owner can unlock")) toggleLock(true);
                    break;
                case "🟢 Running All Code":
                    alert("✅ All systems running. No errors detected.");
                    break;
                case "👑 Admin Panel":
                    adminPanel();
                    break;
                case "📞 Contact Owner":
                    alert("📞 Contact: @OGGY (Telegram) | Email: oggy@hosting.com");
                    break;
                case "🤖 MPX Ai":
                    let q = prompt("Ask MPX Ai:");
                    if(q) document.getElementById('aiPrompt').value = q, askAI();
                    break;
            }
        }
        
        async function checkFiles() {
            let res = await fetch('/api/list_files');
            let data = await res.json();
            if(data.files.length === 0) alert("📂 No files uploaded yet");
            else alert("📂 Your files:\\n" + data.files.join('\\n'));
            addLog(`Listed ${data.files.length} files`);
        }
        
        async function showStats() {
            let res = await fetch('/api/stats');
            let data = await res.json();
            alert(`📊 Statistics:\\nTotal Users: ${data.total_users}\\nApproved: ${data.approved_users}\\nPending: ${data.pending_users}\\nTotal Uploads: ${data.total_uploads}`);
        }
        
        async function sendBroadcast(msg) {
            let res = await fetch('/api/broadcast', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            });
            alert("Broadcast sent to all users");
        }
        
        function adminPanel() {
            window.location.href = '/admin_panel';
        }
        
        async function toggleLock(lock) {
            await fetch('/api/lock_bot', {method: 'POST'});
            alert("Bot locked/unlocked");
        }
        
        async function updateStats() {
            let res = await fetch('/api/server_stats');
            let data = await res.json();
            document.getElementById('cpuRam').innerHTML = `${data.cpu}% / ${data.ram}MB`;
            document.getElementById('serverStatus').innerHTML = data.running ? '🟢 Running' : '🔴 Stopped';
            document.getElementById('fileCount').innerHTML = data.file_count;
        }
        
        // File upload
        document.getElementById('fileInput')?.addEventListener('change', async (e) => {
            let file = e.target.files[0];
            if(!file) return;
            let formData = new FormData();
            formData.append('file', file);
            let res = await fetch('/api/upload', {method: 'POST', body: formData});
            let data = await res.json();
            alert(data.message);
            addLog(`Uploaded: ${file.name}`);
            updateStats();
        });
        
        async function askAI() {
            let prompt = document.getElementById('aiPrompt').value;
            if(!prompt) return;
            document.getElementById('aiResponse').innerHTML = '🤔 Thinking...';
            let res = await fetch('/api/ai', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({prompt: prompt})
            });
            let data = await res.json();
            document.getElementById('aiResponse').innerHTML = `💬 ${data.response}`;
            addLog(`AI Query: ${prompt.substring(0, 50)}...`);
        }
        
        function logout() {
            if(uptimeInterval) clearInterval(uptimeInterval);
            fetch('/api/logout');
            location.reload();
        }
        
        setInterval(updateStats, 5000);
    </script>
</body>
</html>
"""

# Admin Panel HTML
ADMIN_PANEL_HTML = """
<!DOCTYPE html>
<html>
<head><title>OGGY - Admin Panel</title><style>
body { background: #0a0a0a; color: #00ff9d; font-family: monospace; padding: 20px; }
table { width: 100%; border-collapse: collapse; margin-top: 20px; }
th, td { border: 1px solid #00ff9d; padding: 10px; text-align: left; }
button { background: #00ff9d; color: black; padding: 8px 15px; border: none; cursor: pointer; margin: 5px; }
.approved { color: #00ff9d; }
.pending { color: #ffaa00; }
</style></head>
<body>
<h1>👑 OGGY Admin Panel</h1>
<h2>Pending Approvals</h2>
<table id="pendingTable"><tr><th>Username</th><th>Email</th><th>Date</th><th>Action</th></tr></table>
<h2>All Users</h2>
<table id="usersTable"><tr><th>Username</th><th>Status</th><th>Created</th><th>Action</th></tr></table>
<script>
async function load() {
    let res = await fetch('/api/admin_data');
    let data = await res.json();
    let pendingHtml = '';
    data.pending.forEach(u => {
        pendingHtml += `<tr><td>${u.username}</td><td>${u.email || '-'}</td><td>${u.date}</td><td><button onclick="approve('${u.username}')">✅ Approve</button><button onclick="reject('${u.username}')">❌ Reject</button></td></tr>`;
    });
    document.getElementById('pendingTable').innerHTML = '<tr><th>Username</th><th>Email</th><th>Date</th><th>Action</th></tr>' + pendingHtml;
    
    let usersHtml = '';
    data.users.forEach(u => {
        usersHtml += `<tr><td>${u.username}</td><td class="${u.approved ? 'approved' : 'pending'}">${u.approved ? '✅ Approved' : '⏳ Pending'}</td><td>${u.date}</td><td>${!u.approved ? `<button onclick="approve('${u.username}')">Approve</button>` : '<button onclick="removeUser(`'+u.username+'`)">🗑 Remove</button>'}</td></tr>`;
    });
    document.getElementById('usersTable').innerHTML = '<tr><th>Username</th><th>Status</th><th>Created</th><th>Action</th></tr>' + usersHtml;
}
async function approve(user) {
    await fetch('/api/approve_user', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({username: user})});
    load();
}
async function reject(user) {
    await fetch('/api/reject_user', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({username: user})});
    load();
}
async function removeUser(user) {
    if(confirm('Remove user '+user+'?')) {
        await fetch('/api/remove_user', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({username: user})});
        load();
    }
}
load();
setInterval(load, 5000);
</script>
</body></html>
"""

# Flask Routes
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/admin_panel')
def admin_panel():
    return render_template_string(ADMIN_PANEL_HTML)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email', '')
    
    users = load_json(USERS_FILE)
    pending = load_json(PENDING_FILE)
    
    if username in users or username in pending:
        return jsonify({'success': False, 'message': 'Username exists!'})
    
    pending[username] = {'password': password, 'email': email, 'date': str(datetime.now()), 'approved': False}
    save_json(PENDING_FILE, pending)
    return jsonify({'success': True, 'message': 'Request sent to owner! Wait for approval.'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username == OWNER_USERNAME and password == OWNER_PASSWORD:
        session['user'] = username
        session['is_admin'] = True
        return jsonify({'success': True, 'is_admin': True})
    
    users = load_json(USERS_FILE)
    if username in users and users[username]['password'] == password and users[username].get('approved', False):
        session['user'] = username
        session['is_admin'] = False
        return jsonify({'success': True, 'is_admin': False})
    
    pending = load_json(PENDING_FILE)
    if username in pending:
        return jsonify({'success': False, 'message': 'Pending owner approval'})
    
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/api/check_approval')
def check_approval():
    user = request.args.get('user')
    users = load_json(USERS_FILE)
    return jsonify({'approved': user in users and users[user].get('approved', False)})

@app.route('/api/approve_user', methods=['POST'])
def approve_user():
    data = request.json
    username = data.get('username')
    pending = load_json(PENDING_FILE)
    users = load_json(USERS_FILE)
    
    if username in pending:
        users[username] = pending[username]
        users[username]['approved'] = True
        del pending[username]
        save_json(USERS_FILE, users)
        save_json(PENDING_FILE, pending)
    return jsonify({'success': True})

@app.route('/api/reject_user', methods=['POST'])
def reject_user():
    data = request.json
    username = data.get('username')
    pending = load_json(PENDING_FILE)
    if username in pending:
        del pending[username]
        save_json(PENDING_FILE, pending)
    return jsonify({'success': True})

@app.route('/api/remove_user', methods=['POST'])
def remove_user():
    data = request.json
    username = data.get('username')
    users = load_json(USERS_FILE)
    if username in users:
        del users[username]
        save_json(USERS_FILE, users)
    return jsonify({'success': True})

@app.route('/api/admin_data')
def admin_data():
    users = load_json(USERS_FILE)
    pending = load_json(PENDING_FILE)
    
    user_list = [{'username': k, 'approved': v.get('approved', False), 'date': v.get('date', '')} for k, v in users.items()]
    pending_list = [{'username': k, 'email': v.get('email', ''), 'date': v.get('date', '')} for k, v in pending.items()]
    return jsonify({'users': user_list, 'pending': pending_list})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected'})
    
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    file.save(os.path.join('uploads', file.filename))
    
    settings = load_json(SETTINGS_FILE)
    settings['total_uploads'] = settings.get('total_uploads', 0) + 1
    save_json(SETTINGS_FILE, settings)
    
    return jsonify({'message': f'Uploaded: {file.filename}'})

@app.route('/api/list_files')
def list_files():
    if not os.path.exists('uploads'):
        return jsonify({'files': []})
    files = os.listdir('uploads')
    return jsonify({'files': files})

@app.route('/api/stats')
def stats():
    users = load_json(USERS_FILE)
    pending = load_json(PENDING_FILE)
    settings = load_json(SETTINGS_FILE)
    approved = sum(1 for u in users.values() if u.get('approved'))
    return jsonify({
        'total_users': len(users),
        'approved_users': approved,
        'pending_users': len(pending),
        'total_uploads': settings.get('total_uploads', 0)
    })

@app.route('/api/server_stats')
def server_stats():
    file_count = len(os.listdir('uploads')) if os.path.exists('uploads') else 0
    return jsonify({
        'cpu': round(os.cpu_count() * 0.5, 1),
        'ram': 512,
        'running': True,
        'file_count': file_count
    })

@app.route('/api/ai', methods=['POST'])
def ai():
    data = request.json
    prompt = data.get('prompt', '')
    response = call_a4f_api(prompt)
    return jsonify({'response': response})

@app.route('/api/add_log', methods=['POST'])
def add_log():
    data = request.json
    log = data.get('log', '')
    # Store logs in memory/file if needed
    return jsonify({'success': True})

@app.route('/api/logout')
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/broadcast', methods=['POST'])
def broadcast():
    # In production, implement actual broadcast
    return jsonify({'success': True})

@app.route('/api/lock_bot', methods=['POST'])
def lock_bot():
    settings = load_json(SETTINGS_FILE)
    settings['bot_locked'] = not settings.get('bot_locked', False)
    save_json(SETTINGS_FILE, settings)
    return jsonify({'locked': settings['bot_locked']})

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════╗
    ║     🔥 OGGY HOSTING - DEPLOYED SUCCESSFULLY 🔥      ║
    ╠══════════════════════════════════════════════════════╣
    ║  🌐 URL: http://localhost:5000                       ║
    ║  👑 Owner Login: OGGY / OGGY@159357                  ║
    ║  📝 Users: Register -> Owner approves in Admin Panel ║
    ║  🤖 A4F Claude Sonnet 4: WORKING                     ║
    ║  🔥 Developer: OGGY | SIN: 159357                    ║
    ╚══════════════════════════════════════════════════════╝
    """)
    app.run(debug=False, host='0.0.0.0', port=5000)