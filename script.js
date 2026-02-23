/**
 * LoKal - Offline AI Learning Assistant
 * Frontend JavaScript - Connected to Django Backend
 */

// ========================================
// API Configuration
// ========================================
const API_BASE_URL = '/api';
let currentConversationId = null;

// DOM Elements
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebarToggle');
const newChatBtn = document.getElementById('newChatBtn');
const chatHistory = document.getElementById('chatHistory');
const welcomeScreen = document.getElementById('welcomeScreen');
const chatContainer = document.getElementById('chatContainer');
const messagesContainer = document.getElementById('messages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const voiceBtn = document.getElementById('voiceBtn');
const voiceOverlay = document.getElementById('voiceOverlay');
const stopListeningBtn = document.getElementById('stopListeningBtn');
const quickActionBtns = document.querySelectorAll('.quick-action-btn');

// State
let isListening = false;
let conversationHistory = [];
let currentUser = null;

// ========================================
// Auth Functions
// ========================================

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/user/`, {
            method: 'GET',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();

        const userProfile = document.getElementById('userProfile');
        const loginLinkBtn = document.getElementById('loginLinkBtn');
        const userName = document.getElementById('userName');
        const newChatBtn = document.getElementById('newChatBtn');

        if (data.authenticated) {
            currentUser = data.user;
            if (userProfile) userProfile.style.display = 'flex';
            if (loginLinkBtn) loginLinkBtn.style.display = 'none';
            if (userName) userName.textContent = currentUser.username;
            if (newChatBtn) newChatBtn.style.display = 'flex';

            // Allow access to chat interface
        } else {
            currentUser = null;
            if (userProfile) userProfile.style.display = 'none';
            if (loginLinkBtn) loginLinkBtn.style.display = 'flex';
            if (newChatBtn) newChatBtn.style.display = 'none'; // Hide new chat if not logged in

            // Show login prompt in chat area if needed
        }
        return data.authenticated;
    } catch (error) {
        console.warn('Auth check failed:', error);
        return false;
    }
}

async function logout() {
    try {
        await fetch(`${API_BASE_URL}/auth/logout/`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        window.location.reload();
    } catch (error) {
        console.error('Logout failed:', error);
    }
}

// ========================================
// API Functions
// ========================================

async function askQuestion(question, enableTts = false) {
    try {
        const response = await fetch(`${API_BASE_URL}/ask/`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                question: question,
                conversation_id: currentConversationId,
                enable_tts: enableTts
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        currentConversationId = data.conversation_id;
        return data;
    } catch (error) {
        console.error('API Error:', error);
        return {
            answer: getFallbackResponse(question),
            error: true
        };
    }
}

async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health/`, {
            method: 'GET',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' }
        });
        return response.ok;
    } catch (error) {
        console.warn('Backend not available:', error);
        return false;
    }
}

// ========================================
// Conversation Management API Functions
// ========================================

async function loadConversations() {
    try {
        const response = await fetch(`${API_BASE_URL}/conversations/`, {
            method: 'GET',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' }
        });
        if (response.ok) {
            const data = await response.json();
            renderConversationList(data);
            return data;
        }
    } catch (error) {
        console.warn('Failed to load conversations:', error);
    }
    return [];
}

async function loadConversation(conversationId) {
    try {
        const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}/`, {
            method: 'GET',
            credentials: 'include',
            headers: { 'Content-Type': 'application/json' }
        });
        if (response.ok) {
            const data = await response.json();
            return data;
        }
    } catch (error) {
        console.warn('Failed to load conversation:', error);
    }
    return null;
}

async function deleteConversation(conversationId) {
    try {
        const response = await fetch(`${API_BASE_URL}/conversations/${conversationId}/`, {
            method: 'DELETE',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        if (response.ok) {
            // If we deleted the current conversation, start a new chat
            if (currentConversationId === conversationId) {
                startNewChat();
            }
            // Reload the conversation list
            await loadConversations();
            return true;
        }
    } catch (error) {
        console.warn('Failed to delete conversation:', error);
    }
    return false;
}

function renderConversationList(conversations) {
    chatHistory.innerHTML = '';

    if (conversations.length === 0) {
        chatHistory.innerHTML = `
            <li class="chat-item empty">
                <span>No conversations yet</span>
            </li>
        `;
        return;
    }

    conversations.forEach(conv => {
        const li = document.createElement('li');
        li.className = `chat-item${conv.id === currentConversationId ? ' active' : ''}`;
        li.dataset.conversationId = conv.id;

        const title = conv.title || 'New Conversation';
        const truncatedTitle = title.length > 25 ? title.substring(0, 25) + '...' : title;

        li.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            <span class="chat-title">${truncatedTitle}</span>
            <button class="delete-chat-btn" title="Delete conversation" onclick="event.stopPropagation(); confirmDeleteConversation(${conv.id})">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
            </button>
        `;

        // Click to switch conversation
        li.addEventListener('click', () => switchConversation(conv.id));

        chatHistory.appendChild(li);
    });
}

async function switchConversation(conversationId) {
    const conversation = await loadConversation(conversationId);
    if (!conversation) return;

    currentConversationId = conversationId;
    conversationHistory = [];
    messagesContainer.innerHTML = '';

    // Hide welcome screen, show chat
    welcomeScreen.classList.add('hidden');
    chatContainer.classList.add('active');

    // Load messages
    if (conversation.messages && conversation.messages.length > 0) {
        conversation.messages.forEach(msg => {
            const sender = msg.role === 'user' ? 'user' : 'ai';
            appendMessage(msg.content, sender);
        });
    }

    // Update sidebar active state
    document.querySelectorAll('.chat-item').forEach(item => {
        item.classList.remove('active');
        if (parseInt(item.dataset.conversationId) === conversationId) {
            item.classList.add('active');
        }
    });

    // Close sidebar on mobile
    if (window.innerWidth <= 768) {
        sidebar.classList.remove('open');
    }
}

function confirmDeleteConversation(conversationId) {
    deleteConversation(conversationId);
}

// Fallback responses when backend is unavailable
function getFallbackResponse(query) {
    const lowerQuery = query.toLowerCase();

    if (lowerQuery.includes('science') || lowerQuery.includes('biology')) {
        return `🔬 **Science** is the study of the world around us!\n\nIt helps us understand how things work through observation, questions, and experiments.\n\n*Note: I'm currently offline. Connect to the backend for full AI responses.*`;
    } else if (lowerQuery.includes('math') || lowerQuery.includes('number')) {
        return `📐 **Math** is like a superpower for solving problems!\n\nBasics: Addition (+), Subtraction (-), Multiplication (×), Division (÷)\n\n*Note: I'm currently offline. Connect to the backend for full AI responses.*`;
    } else if (lowerQuery.includes('english') || lowerQuery.includes('grammar')) {
        return `📚 **English** helps us communicate!\n\nParts of speech: Nouns, Verbs, Adjectives\n\n*Note: I'm currently offline. Connect to the backend for full AI responses.*`;
    } else {
        return `👋 I received your question: "${query}"\n\n*The backend server is not connected. Please start the Django server:*\n\n\`\`\`\ncd raspi\\ LoKAl\npython manage.py runserver 0.0.0.0:8000\n\`\`\`\n\nOnce connected, I'll use the local AI to give you a full answer!`;
    }
}

// ========================================
// Chat Functions
// ========================================

async function sendMessage(text) {
    if (!text.trim()) return;

    // Hide welcome screen, show chat
    welcomeScreen.classList.add('hidden');
    chatContainer.classList.add('active');

    // Add user message
    appendMessage(text, 'user');
    messageInput.value = '';
    updateSendButton();

    // Show typing indicator
    showTypingIndicator();

    // Call backend API
    const response = await askQuestion(text, false);

    // Hide typing and show response
    hideTypingIndicator();
    appendMessage(response.answer, 'ai', response.audio_url);

    // Refresh conversation list in sidebar
    await loadConversations();
}

function appendMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.innerHTML = sender === 'user' ? '👤' : '🤖';

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Format message text
    let messageHTML = formatMessage(text);

    // Add speaker button for AI messages
    if (sender === 'ai') {
        const uniqueId = 'msg-' + Date.now();
        messageHTML += `
            <div class="message-actions">
                <button class="message-speaker-btn" onclick="speakText(this, '${uniqueId}')">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                        <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                    </svg>
                    Listen
                </button>
                <div id="${uniqueId}" style="display:none">${text}</div>
            </div>
        `;
    }

    contentDiv.innerHTML = messageHTML;

    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    // Save to history
    conversationHistory.push({ sender, text });
}

function formatMessage(text) {
    // Convert markdown-like formatting to HTML
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>')
        .replace(/• /g, '&bull; ');
}

// ========================================
// Text-to-Speech Functions (Server-Side)
// ========================================

let currentAudio = null;
let currentPlayingBtn = null;

async function speakText(btn, elementId) {
    // Stop any current audio
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }

    // Reset all buttons
    document.querySelectorAll('.message-speaker-btn').forEach(b => {
        b.classList.remove('speaking');
        b.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
            </svg>
            Listen
        `;
    });

    // Get text to speak (hidden div content to avoid reading HTML tags)
    const textToSpeak = document.getElementById(elementId).textContent;

    if (currentPlayingBtn === btn) {
        // If clicking same button, just stop (toggle off)
        currentPlayingBtn = null;
        return;
    }

    // Set button to loading state
    btn.classList.add('speaking');
    btn.innerHTML = `
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="spinning">
            <circle cx="12" cy="12" r="10"></circle>
            <path d="M12 6v6l4 2"></path>
        </svg>
        Loading...
    `;

    try {
        // Call server-side TTS API
        const response = await fetch(`${API_BASE_URL}/tts/`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ text: textToSpeak })
        });

        if (!response.ok) {
            throw new Error('TTS request failed');
        }

        const data = await response.json();

        if (data.audio_url) {
            // Create audio element and play
            currentAudio = new Audio(data.audio_url);
            currentPlayingBtn = btn;

            // Update button to playing state
            btn.innerHTML = `
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="6" y="4" width="4" height="16"></rect>
                    <rect x="14" y="4" width="4" height="16"></rect>
                </svg>
                Stop
            `;

            currentAudio.onended = () => {
                btn.classList.remove('speaking');
                btn.innerHTML = `
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                        <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                    </svg>
                    Listen
                `;
                currentAudio = null;
                currentPlayingBtn = null;
            };

            currentAudio.onerror = () => {
                console.error('Audio playback error');
                btn.classList.remove('speaking');
                btn.innerHTML = `
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                        <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                    </svg>
                    Listen
                `;
                currentAudio = null;
                currentPlayingBtn = null;
            };

            await currentAudio.play();
        } else {
            throw new Error('No audio URL returned');
        }
    } catch (error) {
        console.error('TTS error:', error);
        btn.classList.remove('speaking');
        btn.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
            </svg>
            Listen
        `;
        alert('Text-to-speech is not available. Please check the server.');
    }
}



function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message ai typing';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="message-avatar">🤖</div>
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// ========================================
// Voice Input Functions (Server-Side STT)
// ========================================

let mediaRecorder = null;
let audioChunks = [];

function toggleVoiceInput() {
    if (!isListening) {
        startListening();
    } else {
        stopListening();
    }
}

async function startListening() {
    // Clear previous transcript
    const transcriptText = document.getElementById('transcriptText');
    if (transcriptText) {
        transcriptText.textContent = 'Initializing microphone...';
    }
    messageInput.value = '';

    try {
        // Check if we are in a secure context or localhost
        if (!navigator.mediaDevices) {
            isListening = false;
            voiceOverlay.classList.remove('active');
            let errorMsg = 'Microphone access is not available.';
            if (!window.isSecureContext) {
                errorMsg = 'Microphone requires a secure connection (HTTPS) or localhost. Please use http://localhost:8000/ to access the site.';
            }
            alert(errorMsg);
            return;
        }

        // Request microphone access using standard MediaDevices API
        const stream = await navigator.mediaDevices.getUserMedia({
            audio: {
                echoCancellation: true,
                noiseSuppression: false, // Disabled for better fidelity on some mics
                autoGainControl: true
            }
        });

        isListening = true;
        voiceBtn.classList.add('listening');
        voiceOverlay.classList.add('active');
        audioChunks = [];

        // Update transcript text
        if (transcriptText) {
            transcriptText.textContent = 'Listening... Speak now!';
        }

        // Create MediaRecorder to capture audio
        // Try to use a format that works well across browsers
        const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
            ? 'audio/webm;codecs=opus'
            : MediaRecorder.isTypeSupported('audio/webm')
                ? 'audio/webm'
                : MediaRecorder.isTypeSupported('audio/mp4')
                    ? 'audio/mp4'
                    : 'audio/ogg';

        console.log('Using MIME type for recording:', mimeType);
        mediaRecorder = new MediaRecorder(stream, {
            mimeType,
            audioBitsPerSecond: 128000 // Higher bitrate for clearer audio
        });

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = async () => {
            // Stop the stream tracks
            stream.getTracks().forEach(track => track.stop());

            // Update transcript
            if (transcriptText) {
                transcriptText.innerHTML = '<span style="color: var(--accent-color);">Processing speech...</span>';
            }

            // Create blob from recorded chunks
            const audioBlob = new Blob(audioChunks, { type: mimeType });

            // Determine correct extension
            let extension = '.wav';
            if (mimeType.includes('webm')) extension = '.webm';
            else if (mimeType.includes('mp4')) extension = '.mp4';
            else if (mimeType.includes('ogg')) extension = '.ogg';
            else if (mimeType.includes('opus')) extension = '.opus';

            // Send to server for transcription
            await transcribeAudio(audioBlob, extension);
        };

        mediaRecorder.onerror = (event) => {
            console.error('MediaRecorder error:', event.error);
            stopListening();
            if (transcriptText) {
                transcriptText.textContent = 'Recording error. Please try again.';
            }
        };

        // Start recording
        mediaRecorder.start(1000); // Collect data every 1 second

    } catch (error) {
        console.error('Microphone access error:', error);
        isListening = false;
        voiceOverlay.classList.remove('active');

        if (transcriptText) {
            if (error.name === 'NotAllowedError') {
                transcriptText.textContent = 'Microphone access denied. Please allow microphone access.';
            } else if (error.name === 'NotFoundError') {
                transcriptText.textContent = 'No microphone found. Please connect a microphone.';
            } else {
                transcriptText.textContent = 'Could not access microphone: ' + error.message;
            }
        }

        // Hide overlay after showing error
        setTimeout(() => {
            voiceOverlay.classList.remove('active');
        }, 3000);
    }
}

async function transcribeAudio(audioBlob, extension = '.webm') {
    const transcriptText = document.getElementById('transcriptText');

    try {
        // Create FormData with audio file
        const formData = new FormData();
        formData.append('audio', audioBlob, `recording${extension}`);

        // Send to STT endpoint
        const response = await fetch(`${API_BASE_URL}/stt/`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: formData
        });

        const data = await response.json();

        if (data.success && data.text) {
            // Update input field with transcribed text (user can edit before sending)
            messageInput.value = data.text;
            if (transcriptText) {
                transcriptText.textContent = data.text;
            }

            // Close overlay and focus on input field for editing
            voiceOverlay.classList.remove('active');
            messageInput.focus();
        } else {
            // Show error message
            const errorMsg = data.text || data.error || 'Could not understand the audio.';
            if (transcriptText) {
                transcriptText.innerHTML = `<span style="color: var(--error-color);">${errorMsg}</span>`;
            }

            // Auto-hide after showing error
            setTimeout(() => {
                voiceOverlay.classList.remove('active');
            }, 3000);
        }
    } catch (error) {
        console.error('STT request error:', error);
        if (transcriptText) {
            transcriptText.innerHTML = '<span style="color: var(--error-color);">Speech recognition failed. Please try typing instead.</span>';
        }

        // Auto-hide after showing error
        setTimeout(() => {
            voiceOverlay.classList.remove('active');
        }, 3000);
    }
}

function stopListening() {
    isListening = false;
    voiceBtn.classList.remove('listening');
    voiceOverlay.classList.remove('active');

    // Stop the MediaRecorder if it exists and is recording
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
    }
}

// ========================================
// New Chat Function
// ========================================

function startNewChat() {
    // Clear messages
    messagesContainer.innerHTML = '';
    conversationHistory = [];

    // Reset API conversation
    currentConversationId = null;

    // Show welcome screen
    welcomeScreen.classList.remove('hidden');
    chatContainer.classList.remove('active');

    // Clear input
    messageInput.value = '';
    updateSendButton();

    // Remove active state from all chat items
    document.querySelectorAll('.chat-item').forEach(item => {
        item.classList.remove('active');
    });

    // Close sidebar on mobile
    if (window.innerWidth <= 768) {
        sidebar.classList.remove('open');
    }
}

// ========================================
// UI Helper Functions
// ========================================

function updateSendButton() {
    if (messageInput.value.trim()) {
        sendBtn.classList.add('active');
    } else {
        sendBtn.classList.remove('active');
    }
}

function toggleSidebar() {
    sidebar.classList.toggle('open');
}

// ========================================
// Event Listeners
// ========================================

// Send message on button click
sendBtn.addEventListener('click', () => {
    sendMessage(messageInput.value);
});

// Send message on Enter key
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage(messageInput.value);
    }
});

// Update send button state
messageInput.addEventListener('input', updateSendButton);

// Voice input
voiceBtn.addEventListener('click', toggleVoiceInput);
stopListeningBtn.addEventListener('click', stopListening);

// Close voice overlay on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && isListening) {
        stopListening();
    }
});

// Quick action buttons
quickActionBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const query = btn.getAttribute('data-query');
        messageInput.value = query;
        sendMessage(query);
    });
});

// New chat button
newChatBtn.addEventListener('click', startNewChat);

// Sidebar toggle (mobile)
sidebarToggle.addEventListener('click', toggleSidebar);

// Close sidebar when clicking outside (mobile)
document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768) {
        if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    }
});

// ========================================
// Initialize
// ========================================

document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication
    await checkAuth();

    // Bind logout button if exists
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', logout);
    }

    // Focus on input
    if (messageInput) messageInput.focus();

    // Load conversations from database
    await loadConversations();

    // Log welcome message
    console.log('🎓 LoKal - Offline AI Learning Assistant');
    console.log('Ready to help students learn!');
});
