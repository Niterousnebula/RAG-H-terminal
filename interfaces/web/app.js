document.addEventListener('DOMContentLoaded', () => {
    // --- UI Elements ---
    const loadingScreen = document.getElementById('loading-screen');
    const appContainer = document.getElementById('app-container');
    const progressBar = document.getElementById('progress-bar');
    const statusText = document.getElementById('loading-status');
    
    // Required Constraints
    const chatBox = document.getElementById('chat-box');
    const inputField = document.getElementById('input');
    
    // Controls
    const sendBtn = document.getElementById('send-btn');
    const stopBtn = document.getElementById('stop-button');
    const uploadBtn = document.getElementById('upload-btn');
    const fileInput = document.getElementById('file-upload');
    const filePreview = document.getElementById('file-preview');

    // State
    let isStreaming = false;
    let abortController = null;
    let uploadedFilePath = null; // Stores ref to attach to next message

    // --- Boot Sequence & Health Sync ---
    async function executeBootSequence() {
        let progress = 0;
        let isBackendReady = false;
        
        // 30-second smooth progression simulation
        const progressInterval = setInterval(() => {
            if (progress < 95 && !isBackendReady) {
                progress += (100 / 300);
                progressBar.style.width = `${progress}%`;
            }
        }, 100);

        // Async polling for /health endpoint constraint
        const pollBackend = async () => {
            while (!isBackendReady) {
                try {
                    const response = await fetch('/health');
                    if (response.ok) {
                        isBackendReady = true;
                        clearInterval(progressInterval);
                        
                        progressBar.style.width = '100%';
                        statusText.innerText = 'DATA_LINK_ESTABLISHED';
                        
                        setTimeout(() => {
                            loadingScreen.classList.add('hidden');
                            appContainer.classList.remove('hidden');
                            setTimeout(() => loadingScreen.style.display = 'none', 600);
                            inputField.focus();
                        }, 800);
                        break;
                    }
                } catch (e) {
                    statusText.innerText = 'Awaiting connection target...';
                }
                await new Promise(r => setTimeout(r, 2000));
            }
        };

        pollBackend();
    }

    // --- Configure Marked.js ---
    marked.setOptions({
        highlight: function(code, lang) {
            if (lang && hljs.getLanguage(lang)) {
                return hljs.highlight(code, { language: lang }).value;
            }
            return hljs.highlightAuto(code).value;
        }
    });

    // --- File Upload Integration (JSON Rules) ---
    uploadBtn.addEventListener('click', () => fileInput.click());
    
    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        filePreview.textContent = `[UPLOADING: ${file.name}...]`;
        const formData = new FormData();
        formData.append('file', file);

        try {
            // Constraint: MUST use /upload endpoint
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                uploadedFilePath = file.name; // Store for the chat payload if needed
                filePreview.textContent = `[PAYLOAD READY: ${file.name}]`;
                appendSystemMessage(`Payload [${file.name}] successfully injected into context.`);
            } else {
                throw new Error('Upload rejected by server');
            }
        } catch (error) {
            filePreview.textContent = `[ERR: UPLOAD FAILED]`;
            appendSystemMessage(`[ERROR: Payload delivery failed]`);
        }
        
        fileInput.value = ''; // Reset DOM element
    });

    // --- Input Handling ---
    inputField.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight < 150 ? this.scrollHeight : 150) + 'px';
    });

    inputField.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey && !isStreaming) {
            e.preventDefault();
            transmitMessage();
        }
    });

    sendBtn.addEventListener('click', () => {
        if (!isStreaming) transmitMessage();
    });

    stopBtn.addEventListener('click', () => {
        if (isStreaming && abortController) {
            abortController.abort();
        }
    });

    // --- Message Processing & Streaming ---
    async function transmitMessage() {
        const payload = inputField.value.trim();
        
        if (!payload && !uploadedFilePath || isStreaming) return;

        // Constraint: Clear input and lock UI
        inputField.value = '';
        inputField.style.height = 'auto';
        filePreview.textContent = '';
        
        const pathToSend = uploadedFilePath;
        uploadedFilePath = null; // Clear the stored file reference

        lockInterface(true);
        appendUserMessage(payload, pathToSend);

        const assistantMessageEl = createMessageElement('assistant');
        const contentContainer = assistantMessageEl.querySelector('.message-content');
        contentContainer.classList.add('typing-cursor');
        chatBox.appendChild(assistantMessageEl);
        autoScroll();

        abortController = new AbortController();

        try {
            // Constraint: Non-blocking async fetch to /chat/stream
            const response = await fetch('/chat/stream', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: payload,
                    file_path: pathToSend 
                }),
                signal: abortController.signal
            });

            if (!response.ok) throw new Error('Transmission rejected');

            // Constraint: ReadableStream architecture preservation
            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let accumulatedText = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value, { stream: true });
                accumulatedText += chunk;
                
                contentContainer.innerHTML = formatAssistantContent(accumulatedText);
                autoScroll();
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                contentContainer.innerHTML += `<br><br><span style="color: var(--error-color);">[SYS_WARN] - Transmission manually severed.</span>`;
            } else {
                console.error('Stream failure:', error);
                contentContainer.innerHTML += `<br><span style="color: var(--error-color);">[ERROR_COMM_FAIL] - Connection lost or refused.</span>`;
            }
        } finally {
            contentContainer.classList.remove('typing-cursor');
            lockInterface(false);
            abortController = null;
            inputField.focus();
        }
    }

    // --- Helpers ---
    function lockInterface(locked) {
        isStreaming = locked;
        inputField.disabled = locked;
        uploadBtn.disabled = locked;
        
        if (locked) {
            sendBtn.style.display = 'none';
            stopBtn.style.display = 'inline-block';
        } else {
            sendBtn.style.display = 'inline-block';
            stopBtn.style.display = 'none';
        }
    }

    function formatAssistantContent(text) {
        const textWithTagsStyled = text.replace(/\[([A-Z0-9_-]+)\]/g, '<span class="model-tag">[$1]</span>');
        return marked.parse(textWithTagsStyled);
    }

    function createMessageElement(role) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        msgDiv.appendChild(contentDiv);
        return msgDiv;
    }

    function appendUserMessage(text, filePath) {
        const el = createMessageElement('user');
        const contentContainer = el.querySelector('.message-content');
        
        let displayHtml = '';
        if (filePath) {
            const filename = filePath.replace(/</g, "&lt;");
            displayHtml += `<div style="font-size: 0.8rem; opacity: 0.8; margin-bottom: 5px; color: var(--text-dim);">📎 Attached: [${filename}]</div>`;
        }
        
        const escapedText = text.replace(/</g, "&lt;").replace(/>/g, "&gt;");
        displayHtml += `<span>${escapedText}</span>`;
        
        contentContainer.innerHTML = displayHtml;
        chatBox.appendChild(el);
        autoScroll();
    }

    function appendSystemMessage(text) {
        const el = createMessageElement('system');
        el.querySelector('.message-content').textContent = text;
        chatBox.appendChild(el);
        autoScroll();
    }

    function autoScroll() {
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Init
    executeBootSequence();
});