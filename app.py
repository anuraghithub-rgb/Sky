from flask import Flask, render_template_string, request, jsonify, session, send_file
import requests
import json
import os
import uuid
from datetime import datetime
from threading import Lock
import mimetypes

app = Flask(__name__)
app.secret_key = "oggy_killer_secret_159357_oggy_hosting"

# ========== CONFIGURATION ==========
USERS_FILE = "users.json"
PENDING_FILE = "pending.json"
SETTINGS_FILE = "settings.json"
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'py', 'js', 'html', 'css', 'zip', 'rar', 'mp4', 'mp3'}

# Owner credentials
OWNER_USERNAME = "OGGY"
OWNER_PASSWORD = "OGGY@159357"

# OGGY AI API Configuration
OGGY_AI_URL = "https://api.deepai.org/hacking_is_a_serious_crime"
OGGY_API_KEY = "tryit-71209460785-0d83ccc5af9bd7a408f4328b4"

# Create folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

file_lock = Lock()

# ========== FILE HANDLING ==========
def init_files():
    for file, default in [(USERS_FILE, {}), (PENDING_FILE, {}), (SETTINGS_FILE, {
        "bot_locked": False,
        "file_upload_enabled": True,
        "total_uploads": 0,
        "total_users": 0,
        "start_time": str(datetime.now())
    })]:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                json.dump(default, f, indent=2)

init_files()

def load_json(file):
    with file_lock:
        with open(file, 'r') as f:
            return json.load(f)

def save_json(file, data):
    with file_lock:
        with open(file, 'w') as f:
            json.dump(data, f, indent=2)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def call_oggy_ai(prompt):
    """Call OGGY AI via DeepAI API"""
    headers = {
        "api-key": OGGY_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": prompt,
        "response_format": "text"
    }
    try:
        response = requests.post(OGGY_AI_URL, headers=headers, json=payload, timeout=60)
        if response.status_code == 200:
            data = response.json()
            return data.get("output", data.get("response", "🤖 OGGY AI is thinking..."))
        return f"⚠️ OGGY AI Error: {response.status_code}"
    except Exception as e:
        return f"⚠️ OGGY AI Connection Error: {str(e)[:50]}"

# ========== HTML TEMPLATE ==========
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
        
        .login-box {
            background: rgba(0,0,0,0.95);
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
            cursor: pointer;
            transition: all 0.3s;
        }
        .stat-card:hover { transform: translateY(-5px); box-shadow: 0 0 20px rgba(0,255,157,0.3); }
        .stat-card .value { font-size: 2em; font-weight: bold; }
        
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
        .disabled-btn { background: #555; cursor: not-allowed; opacity: 0.5; }
        
        .upload-area {
            background: rgba(0,255,157,0.1);
            border: 2px dashed #00ff9d;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            margin: 20px 0;
        }
        
        .file-list {
            background: rgba(0,0,0,0.8);
            border-radius: 10px;
            padding: 15px;
            margin-top: 15px;
            max-height: 200px;
            overflow-y: auto;
        }
        .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px;
            border-bottom: 1px solid #00ff9d;
        }
        .file-item button {
            width: auto;
            padding: 5px 10px;
            background: #ff0040;
            margin-left: 10px;
        }
        
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
            height: 200px;
            overflow-y: auto;
            padding: 15px;
            font-family: monospace;
            font-size: 0.85em;
        }
        .log-line { color: #00ff9d; margin: 5px 0; border-left: 2px solid #00ff9d; padding-left: 10px; }
        .error-log { color: #ff0040; border-left-color: #ff0040; }
        
        .ai-panel {
            background: rgba(0,0,0,0.9);
            border: 1px solid #00ff9d;
            border-radius: 15px;
            padding: 20px;
            margin-top: 20px;
        }
        .ai-response { background: #111; padding: 15px; border-radius: 10px; margin-top: 10px; white-space: pre-wrap; }
        
        .toggle-switch {
            position: relative;
            display: inline-block;
            width: 60px;
            height: 34px;
        }
        .toggle-switch input { opacity: 0; width: 0; height: 0; }
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #ccc;
            transition: 0.4s;
            border-radius: 34px;
        }
        .slider:before {
            position: absolute;
            content: "";
            height: 26px;
            width: 26px;
            left: 4px;
            bottom: 4px;
            background-color: white;
            transition: 0.4s;
            border-radius: 50%;
        }
        input:checked + .slider { background-color: #00ff9d; }
        input:checked + .slider:before { transform: translateX(26px); }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 1.5em; }
            .button-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
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
        
        <div id="dashboard" class="dashboard">
            <div class="top-bar">
                <div class="welcome-text">
                    <h3>🔥 OGGY HOSTING</h3>
                    <p>Welcome: <span id="userName">User</span> <span id="userBadge"></span></p>
                </div>
                <button class="logout-btn" onclick="logout()">🚪 Logout</button>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card" onclick="refreshStats()">
                    <div class="value" id="uptime">0h 0m</div>
                    <div>⏱ Uptime</div>
                </div>
                <div class="stat-card">
                    <div class="value" id="serverStatus">🟢 Running</div>
                    <div>Status</div>
                </div>
                <div class="stat-card">
                    <div class="value" id="cpuRam">0.5% / 512MB</div>
                    <div>CPU / RAM</div>
                </div>
                <div class="stat-card">
                    <div class="value" id="fileCount">0</div>
                    <div>📂 Files</div>
                </div>
            </div>
            
            <div style="display: flex; justify-content: space-between; align-items: center; margin: 20px 0; padding: 15px; background: rgba(0,0,0,0.5); border-radius: 15px;">
                <span>📁 FILE UPLOAD SYSTEM</span>
                <label class="toggle-switch">
                    <input type="checkbox" id="fileToggle" onchange="toggleFileUpload()">
                    <span class="slider"></span>
                </label>
                <span id="toggleStatus" style="font-size: 0.9em;">Loading...</span>
            </div>
            
            <div id="buttonGrid" class="button-grid"></div>
            
            <div class="upload-area" id="uploadArea">
                <input type="file" id="fileInput" style="display: none;" multiple>
                <button class="action-btn" id="uploadBtn" onclick="document.getElementById('fileInput').click()">📤 Upload File(s)</button>
                <button class="action-btn" onclick="refreshFileList()">📂 Check Files</button>
                <div id="uploadStatus" style="margin-top: 10px;"></div>
                <div id="fileListContainer" class="file-list" style="display: none;"></div>
            </div>
            
            <div class="logs-panel">
                <div class="logs-header">📋 System Logs & Errors</div>
                <div class="logs-body" id="logsBody">
                    <div class="log-line">[INFO] OGGY HOSTING v4.0 initialized</div>
                    <div class="log-line">[INFO] OGGY AI ready with DeepAI API</div>
                </div>
            </div>
            
            <div class="ai-panel">
                <h3>🤖 OGGY AI - Powered by DeepAI</h3>
                <div class="input-group" style="display: flex; gap: 10px;">
                    <input type="text" id="aiPrompt" placeholder="Ask OGGY AI anything..." style="flex: 1;">
                    <button onclick="askOGGY()" style="width: auto; padding: 12px 25px;">Send</button>
                </div>
                <div id="aiResponse" class="ai-response">💬 OGGY AI will respond here...</div>
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
            let s = diff % 60;
            document.getElementById('uptime').innerText = h + 'h ' + m + 'm ' + s + 's';
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
            }).catch(e => console.log(e));
        }
        
        function showRegister() {
            document.getElementById('loginPanel').style.display = 'none';
            document.getElementById('registerPanel').style.display = 'block';
        }
        
        function showLogin() {
            document.getElementById('registerPanel').style.display = 'none';
            document.getElementById('loginPanel').style.display = 'block';
        }
        
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
                loadFileToggleStatus();
                refreshFileList();
                addLog(`User ${username} logged in successfully`);
            } else {
                alert('Login failed: ' + data.message);
            }
        });
        
        async function loadFileToggleStatus() {
            let res = await fetch('/api/file_upload_status');
            let data = await res.json();
            let toggle = document.getElementById('fileToggle');
            toggle.checked = data.enabled;
            document.getElementById('toggleStatus').innerHTML = data.enabled ? '🟢 ENABLED' : '🔴 DISABLED';
            updateUploadUI(data.enabled);
        }
        
        async function toggleFileUpload() {
            let toggle = document.getElementById('fileToggle');
            let newState = toggle.checked;
            let res = await fetch('/api/toggle_file_upload', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({enabled: newState})
            });
            let data = await res.json();
            document.getElementById('toggleStatus').innerHTML = data.enabled ? '🟢 ENABLED' : '🔴 DISABLED';
            updateUploadUI(data.enabled);
            addLog(`File upload ${data.enabled ? 'ENABLED' : 'DISABLED'} by ${currentUser}`);
        }
        
        function updateUploadUI(enabled) {
            let uploadBtn = document.getElementById('uploadBtn');
            let fileInput = document.getElementById('fileInput');
            if (!enabled) {
                uploadBtn.classList.add('disabled-btn');
                uploadBtn.disabled = true;
                fileInput.disabled = true;
            } else {
                uploadBtn.classList.remove('disabled-btn');
                uploadBtn.disabled = false;
                fileInput.disabled = false;
            }
        }
        
        function loadButtons() {
            let buttonGrid = document.getElementById('buttonGrid');
            let buttons;
            if (isAdmin) {
                buttons = [
                    ["📢 Updates Channel", "⏱ Uptime Stats"],
                    ["📤 Upload File", "📂 Check Files"],
                    ["⚡ Bot Speed", "📊 Statistics"],
                    ["💳 Subscriptions", "📢 Broadcast"],
                    ["🔒 Lock Bot", "🔄 File Upload ON/OFF"],
                    ["👑 Admin Panel", "📞 Contact Owner"],
                    ["🤖 OGGY AI", "🗑 Clear Logs"]
                ];
            } else {
                buttons = [
                    ["📢 Updates Channel", "⏱ Uptime Stats"],
                    ["📤 Upload File", "📂 Check Files"],
                    ["⚡ Bot Speed", "📊 Statistics"],
                    ["📞 Contact Owner", "🤖 OGGY AI"]
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
            addLog(`Command: ${action}`);
            switch(action) {
                case "📢 Updates Channel":
                    alert("📢 Updates Channel: @OGGY_HOSTING\nAll systems operational ✅");
                    break;
                case "⏱ Uptime Stats":
                    alert(`⏱ System Uptime: ${document.getElementById('uptime').innerText}`);
                    break;
                case "📤 Upload File":
                    if(document.getElementById('fileToggle').checked) {
                        document.getElementById('fileInput').click();
                    } else {
                        alert("❌ File upload is currently DISABLED by owner!");
                    }
                    break;
                case "📂 Check Files":
                    refreshFileList();
                    break;
                case "⚡ Bot Speed":
                    alert("⚡ Response Time: <50ms\nStatus: Optimal\nOGGY AI: Connected");
                    break;
                case "📊 Statistics":
                    showStats();
                    break;
                case "💳 Subscriptions":
                    alert("💳 Premium Plans:\n🔹 Basic: Free - 512MB RAM\n🔹 Pro: $5/mo - 2GB RAM\n🔹 Ultra: $15/mo - 8GB RAM");
                    break;
                case "📢 Broadcast":
                    let msg = prompt("Enter broadcast message:");
                    if(msg) sendBroadcast(msg);
                    break;
                case "🔒 Lock Bot":
                    toggleLock();
                    break;
                case "🔄 File Upload ON/OFF":
                    let toggle = document.getElementById('fileToggle');
                    toggle.checked = !toggle.checked;
                    toggleFileUpload();
                    break;
                case "👑 Admin Panel":
                    window.open('/admin_panel', '_blank');
                    break;
                case "📞 Contact Owner":
                    alert("📞 Contact Owner:\n📱 Telegram: @OGGY\n✉️ Email: oggy@hosting.com");
                    break;
                case "🤖 OGGY AI":
                    let q = prompt("Ask OGGY AI (Your Personal AI Assistant):");
                    if(q) document.getElementById('aiPrompt').value = q, askOGGY();
                    break;
                case "🗑 Clear Logs":
                    if(confirm("Clear all logs?")) {
                        document.getElementById('logsBody').innerHTML = '<div class="log-line">[INFO] Logs cleared</div>';
                        addLog("Logs cleared by admin");
                    }
                    break;
            }
        }
        
        async function refreshFileList() {
            let res = await fetch('/api/list_files');
            let data = await res.json();
            let container = document.getElementById('fileListContainer');
            if(data.files.length === 0) {
                container.style.display = 'none';
                return;
            }
            container.style.display = 'block';
            let html = '<h4>📁 Your Files:</h4>';
            data.files.forEach(file => {
                html += `<div class="file-item">
                    <span>📄 ${file}</span>
                    <div>
                        <button onclick="downloadFile('${file}')">📥</button>
                        <button onclick="deleteFile('${file}')">🗑</button>
                    </div>
                </div>`;
            });
            container.innerHTML = html;
        }
        
        async function downloadFile(filename) {
            window.open(`/api/download/${filename}`, '_blank');
            addLog(`Downloaded: ${filename}`);
        }
        
        async function deleteFile(filename) {
            if(!confirm(`Delete ${filename}?`)) return;
            let res = await fetch('/api/delete_file', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({filename: filename})
            });
            let data = await res.json();
            alert(data.message);
            refreshFileList();
            updateStats();
            addLog(`Deleted: ${filename}`);
        }
        
        async function showStats() {
            let res = await fetch('/api/stats');
            let data = await res.json();
            alert(`📊 OGGY HOSTING Statistics:\n
👥 Total Users: ${data.total_users}
✅ Approved: ${data.approved_users}
⏳ Pending: ${data.pending_users}
📁 Total Uploads: ${data.total_uploads}
📂 Files Stored: ${data.file_count}
🔒 Bot Locked: ${data.bot_locked ? 'Yes' : 'No'}
📁 Upload Enabled: ${data.upload_enabled ? 'Yes' : 'No'}`);
        }
        
        async function sendBroadcast(msg) {
            let res = await fetch('/api/broadcast', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: msg})
            });
            alert("✅ Broadcast sent");
            addLog(`Broadcast sent: ${msg.substring(0, 50)}...`);
        }
        
        async function toggleLock() {
            let res = await fetch('/api/lock_bot', {method: 'POST'});
            let data = await res.json();
            alert(data.locked ? "🔒 Bot locked" : "🔓 Bot unlocked");
            addLog(`Bot ${data.locked ? 'locked' : 'unlocked'}`);
        }
        
        async function updateStats() {
            let res = await fetch('/api/server_stats');
            let data = await res.json();
            document.getElementById('cpuRam').innerHTML = `${data.cpu}% / ${data.ram}MB`;
            document.getElementById('serverStatus').innerHTML = data.running ? '🟢 Running' : '🔴 Stopped';
            document.getElementById('fileCount').innerHTML = data.file_count;
        }
        
        function refreshStats() {
            updateStats();
            refreshFileList();
            addLog("Stats refreshed");
        }
        
        document.getElementById('fileInput')?.addEventListener('change', async (e) => {
            let files = e.target.files;
            if(!files.length) return;
            
            let enabled = document.getElementById('fileToggle').checked;
            if(!enabled) {
                alert("❌ File upload is disabled!");
                return;
            }
            
            for(let file of files) {
                let formData = new FormData();
                formData.append('file', file);
                let res = await fetch('/api/upload', {method: 'POST', body: formData});
                let data = await res.json();
                addLog(`Uploaded: ${file.name} - ${data.message}`);
            }
            alert(`Uploaded ${files.length} file(s)`);
            refreshFileList();
            updateStats();
            document.getElementById('fileInput').value = '';
        });
        
        async function askOGGY() {
            let prompt = document.getElementById('aiPrompt').value;
            if(!prompt) return;
            document.getElementById('aiResponse').innerHTML = '🤖 OGGY AI is thinking... 🧠';
            let res = await fetch('/api/oggy_ai', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({prompt: prompt})
            });
            let data = await res.json();
            document.getElementById('aiResponse').innerHTML = `💬 ${data.response}`;
            addLog(`OGGY AI Query: ${prompt.substring(0, 50)}...`);
        }
        
        function logout() {
            if(uptimeInterval) clearInterval(uptimeInterval);
            fetch('/api/logout');
            location.reload();
        }
        
        setInterval(updateStats, 5000);
        setInterval(refreshFileList, 10000);
    </script>
</body>
</html>
"""

# ========== ADMIN PANEL ==========
ADMIN_PANEL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>OGGY - Admin Control Panel 🔥</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: linear-gradient(135deg, #0a0a0a, #1a0033);
            color: #00ff9d;
            font-family: monospace;
            padding: 20px;
        }
        h1, h2 { margin-bottom: 20px; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            background: rgba(0,0,0,0.8);
        }
        th, td {
            border: 1px solid #00ff9d;
            padding: 12px;
            text-align: left;
        }
        th { background: #00ff9d; color: #000; }
        button {
            background: #00ff9d;
            color: #000;
            padding: 8px 15px;
            border: none;
            cursor: pointer;
            margin: 5px;
            border-radius: 5px;
            font-weight: bold;
        }
        button:hover { background: #ff00ff; color: #fff; }
        .approved { color: #00ff9d; }
        .pending { color: #ffaa00; }
        .stats-panel {
            background: rgba(0,0,0,0.8);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
        }
        .back-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #ff0040;
        }
    </style>
</head>
<body>
    <a href="/"><button class="back-btn">← Back to Home</button></a>
    <h1>👑 OGGY ADMIN PANEL</h1>
    <div class="stats-panel"><h3>📊 Stats</h3><div id="quickStats"></div></div>
    <h2>⏳ Pending Approvals</h2>
    <table id="pendingTable"><tr><th>Username</th><th>Email</th><th>Date</th><th>Action</th></tr></table>
    <h2>✅ All Users</h2>
    <table id="usersTable"><tr><th>Username</th><th>Status</th><th>Created</th><th>Action</th></tr></table>
    <script>
        async function load() {
            let res = await fetch('/api/admin_data');
            let data = await res.json();
            document.getElementById('quickStats').innerHTML = `👥 Total: ${data.total_users} | ✅ Approved: ${data.approved_count} | ⏳ Pending: ${data.pending_count} | 📁 Uploads: ${data.total_uploads}`;
            let pendingHtml = '';
            data.pending.forEach(u => { pendingHtml += `<tr><td>${u.username}</td><td>${u.email || '-'}</td><td>${u.date}</td><td><button onclick="approve('${u.username}')">✅ Approve</button><button onclick="reject('${u.username}')" style="background:#ff0040">❌ Reject</button></td></tr>`; });
            document.getElementById('pendingTable').innerHTML = '<tr><th>Username</th><th>Email</th><th>Date</th><th>Action</th></tr>' + (pendingHtml || '<tr><td colspan="4">No pending requests</td></tr>');
            let usersHtml = '';
            data.users.forEach(u => { usersHtml += `<tr><td>${u.username}</td><td class="${u.approved ? 'approved' : 'pending'}">${u.approved ? '✅ Approved' : '⏳ Pending'}</td><td>${u.date || '-'}</td><td>${!u.approved ? `<button onclick="approve('${u.username}')">Approve</button>` : ''}<button onclick="removeUser('${u.username}')" style="background:#ff0040">🗑 Remove</button></td></tr>`; });
            document.getElementById('usersTable').innerHTML = '<tr><th>Username</th><th>Status</th><th>Created</th><th>Action</th></tr>' + usersHtml;
        }
        async function approve(user) { await fetch('/api/approve_user', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:user})}); load(); }
        async function reject(user) { if(confirm(`Reject ${user}?`)){ await fetch('/api/reject_user', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:user})}); load(); } }
        async function removeUser(user) { if(confirm(`Remove ${user}?`)){ await fetch('/api/remove_user', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:user})}); load(); } }
        load(); setInterval(load, 5000);
    </script>
</body>
</html>
"""

# ========== FLASK ROUTES ==========
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
    settings = load_json(SETTINGS_FILE)
    user_list = [{'username': k, 'approved': v.get('approved', False), 'date': v.get('date', '')} for k, v in users.items()]
    pending_list = [{'username': k, 'email': v.get('email', ''), 'date': v.get('date', '')} for k, v in pending.items()]
    return jsonify({
        'users': user_list, 'pending': pending_list,
        'total_users': len(users), 'approved_count': sum(1 for u in users.values() if u.get('approved')),
        'pending_count': len(pending), 'total_uploads': settings.get('total_uploads', 0)
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No file selected'})
    if allowed_file(file.filename):
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        settings = load_json(SETTINGS_FILE)
        settings['total_uploads'] = settings.get('total_uploads', 0) + 1
        save_json(SETTINGS_FILE, settings)
        return jsonify({'message': f'Uploaded: {file.filename}'})
    return jsonify({'message': 'File type not allowed'})

@app.route('/api/list_files')
def list_files():
    if not os.path.exists(UPLOAD_FOLDER):
        return jsonify({'files': []})
    files = os.listdir(UPLOAD_FOLDER)
    return jsonify({'files': files})

@app.route('/api/download/<filename>')
def download_file(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/delete_file', methods=['POST'])
def delete_file():
    data = request.json
    filename = data.get('filename')
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
        return jsonify({'message': f'Deleted {filename}'})
    return jsonify({'message': 'File not found'})

@app.route('/api/file_upload_status')
def file_upload_status():
    settings = load_json(SETTINGS_FILE)
    return jsonify({'enabled': settings.get('file_upload_enabled', True)})

@app.route('/api/toggle_file_upload', methods=['POST'])
def toggle_file_upload():
    data = request.json
    settings = load_json(SETTINGS_FILE)
    settings['file_upload_enabled'] = data.get('enabled', True)
    save_json(SETTINGS_FILE, settings)
    return jsonify({'enabled': settings['file_upload_enabled']})

@app.route('/api/stats')
def stats():
    users = load_json(USERS_FILE)
    pending = load_json(PENDING_FILE)
    settings = load_json(SETTINGS_FILE)
    file_count = len(os.listdir(UPLOAD_FOLDER)) if os.path.exists(UPLOAD_FOLDER) else 0
    approved = sum(1 for u in users.values() if u.get('approved'))
    return jsonify({
        'total_users': len(users), 'approved_users': approved, 'pending_users': len(pending),
        'total_uploads': settings.get('total_uploads', 0), 'file_count': file_count,
        'bot_locked': settings.get('bot_locked', False), 'upload_enabled': settings.get('file_upload_enabled', True)
    })

@app.route('/api/server_stats')
def server_stats():
    file_count = len(os.listdir(UPLOAD_FOLDER)) if os.path.exists(UPLOAD_FOLDER) else 0
    return jsonify({'cpu': round(os.cpu_count() * 0.5, 1) if os.cpu_count() else 25, 'ram': 512, 'running': True, 'file_count': file_count})

@app.route('/api/oggy_ai', methods=['POST'])
def oggy_ai():
    data = request.json
    prompt = data.get('prompt', '')
    response = call_oggy_ai(prompt)
    return jsonify({'response': response})

@app.route('/api/add_log', methods=['POST'])
def add_log():
    return jsonify({'success': True})

@app.route('/api/logout')
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/broadcast', methods=['POST'])
def broadcast():
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
    ║  🤖 OGGY AI: Connected to DeepAI API                 ║
    ║  📁 File Upload: ON/OFF Toggle Available             ║
    ║  🔥 Developer: OGGY | SIN: 159357                    ║
    ╚══════════════════════════════════════════════════════╝
    """)
    app.run(debug=False, host='0.0.0.0', port=5000)