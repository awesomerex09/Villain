document.addEventListener('DOMContentLoaded', () => {
    // --- Elements ---
    const targetNameInput = document.getElementById('target-name');
    const llmProviderSelect = document.getElementById('llm-provider');
    const apiKeyGroup = document.getElementById('api-key-group');
    const apiKeyInput = document.getElementById('api-key');
    const baseUrlInput = document.getElementById('base-url');
    const modelNameInput = document.getElementById('model-name');
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const folderInput = document.getElementById('folder-input');
    const btnSelectFolder = document.getElementById('btn-select-folder');
    const fileList = document.getElementById('file-list');
    const btnBuild = document.getElementById('btn-build');
    const buildLog = document.getElementById('build-log');
    const setupSection = document.getElementById('setup-section');
    const chatSection = document.getElementById('chat-section');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const btnSend = document.getElementById('btn-send');
    const btnShutdown = document.getElementById('btn-shutdown');

    let uploadedFiles = [];

    // --- Provider Selection ---
    llmProviderSelect.addEventListener('change', (e) => {
        apiKeyInput.placeholder = e.target.value === 'anthropic' ? 'sk-ant-...' : 'sk-proj-...';
    });

    // --- Drag & Drop Upload ---
    uploadArea.addEventListener('click', () => fileInput.click());

    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        handleFiles(e.dataTransfer.files);
    });

    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    btnSelectFolder.addEventListener('click', () => folderInput.click());

    folderInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files).filter(f => f.name.endsWith('.txt') || f.name.endsWith('.log') || f.name.endsWith('.csv'));
        if (files.length === 0) {
            alert('資料夾中沒有找到支援的對話紀錄檔 (.txt, .log, .csv)');
            return;
        }
        handleFiles(files);
    });

    function handleFiles(files) {
        if (files.length === 0) return;
        
        const formData = new FormData();
        Array.from(files).forEach(file => {
            formData.append('files', file);
            uploadedFiles.push(file.name);
        });

        // Upload to server
        fetch('/api/upload_chats', {
            method: 'POST',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                renderFileList();
                btnBuild.disabled = false;
            } else {
                alert('上傳失敗: ' + data.error);
            }
        })
        .catch(err => {
            console.error(err);
            alert('上傳發生錯誤');
        });
    }

    function renderFileList() {
        fileList.innerHTML = '';
        uploadedFiles.forEach(name => {
            const el = document.createElement('div');
            el.className = 'file-item';
            el.innerHTML = `<span>${name}</span><span>✓</span>`;
            fileList.appendChild(el);
        });
    }

    // --- Build Twin ---
    btnBuild.addEventListener('click', async () => {
        const name = targetNameInput.value.trim() || 'Villain';
        const provider = llmProviderSelect.value;
        const key = apiKeyInput.value.trim();
        const baseUrl = baseUrlInput.value.trim();
        const modelName = modelNameInput.value.trim();

        if (!key) {
            alert('請輸入 API Key！');
            return;
        }

        btnBuild.disabled = true;
        btnBuild.textContent = '建置中...這可能需要幾分鐘';
        buildLog.style.display = 'block';
        buildLog.textContent = '> 初始化建置流程...\n';

        try {
            const res = await fetch('/api/build', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    target_name: name,
                    llm_provider: provider,
                    api_key: key,
                    base_url: baseUrl,
                    model: modelName
                })
            });
            const data = await res.json();
            
            if (data.success) {
                buildLog.textContent += data.output;
                buildLog.textContent += '\n\n>>> 建置完成！準備進入對話介面...';
                
                setTimeout(() => {
                    setupSection.style.display = 'none';
                    chatSection.style.display = 'block';
                }, 2000);
            } else {
                buildLog.textContent += '\n[錯誤] ' + data.error;
                btnBuild.disabled = false;
                btnBuild.textContent = '重新建置';
            }
        } catch (err) {
            buildLog.textContent += '\n[錯誤] 網路請求失敗';
            btnBuild.disabled = false;
            btnBuild.textContent = '重新建置';
        }
    });

    // --- Chat Logic ---
    function appendMessage(sender, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        
        const bubble = document.createElement('div');
        bubble.className = 'bubble';
        bubble.textContent = text;
        
        msgDiv.appendChild(bubble);
        chatMessages.appendChild(msgDiv);
        
        // Auto scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        // Display user message
        appendMessage('user', text);
        chatInput.value = '';
        btnSend.disabled = true;

        // Show typing indicator
        const typingId = 'typing-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.id = typingId;
        msgDiv.className = `message twin`;
        msgDiv.innerHTML = `<div class="bubble">...</div>`;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    target_name: targetNameInput.value.trim() || 'Villain',
                    llm_provider: llmProviderSelect.value,
                    api_key: apiKeyInput.value.trim(),
                    base_url: baseUrlInput.value.trim(),
                    model: modelNameInput.value.trim(),
                    message: text
                })
            });
            const data = await res.json();
            
            document.getElementById(typingId).remove();
            
            if (data.success) {
                appendMessage('twin', data.response);
            } else {
                appendMessage('system', '發生錯誤: ' + data.error);
            }
        } catch (err) {
            document.getElementById(typingId).remove();
            appendMessage('system', '網路錯誤');
        }
        
        btnSend.disabled = false;
        chatInput.focus();
    }

    btnSend.addEventListener('click', sendMessage);
    
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // --- Shutdown ---
    btnShutdown.addEventListener('click', () => {
        if (confirm('確定要關閉 Self-Mirror 伺服器嗎？網頁將無法繼續操作。')) {
            fetch('/api/shutdown', { method: 'POST' })
            .then(() => {
                document.body.innerHTML = '<div style="display:flex; height:100vh; align-items:center; justify-content:center; color:#86868b; font-family:sans-serif;">伺服器已安全關閉。您可以關閉此視窗。</div>';
            });
        }
    });
});
