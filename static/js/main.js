// Main game initialization
document.addEventListener('DOMContentLoaded', () => {
    console.log('Gather Clone - Initializing...');
    console.log('Realm Data:', window.REALM_DATA);

    // Connect WebSocket
    window.wsClient.connect();

    // Setup WebSocket event handlers
    setupWebSocketHandlers();

    // Setup UI handlers
    setupUIHandlers();

    // Join the realm once connected
    window.signal.on('ws-connected', () => {
        console.log('Joining realm:', window.REALM_DATA.realmId);
        window.wsClient.joinRealm(window.REALM_DATA.realmId, null);
    });

    // Initialize Pixi.js game (simplified for now)
    initializeGame();
});

function setupWebSocketHandlers() {
    // Handle successful join
    window.signal.on('ws:joinedRealm', (data) => {
        console.log('Joined realm successfully', data);
        updatePlayerCount(data.players ? data.players.length : 1);
    });

    // Handle failed join
    window.signal.on('ws:failedToJoinRoom', (data) => {
        alert('Failed to join room: ' + data.reason);
    });

    // Handle player joined
    window.signal.on('ws:playerJoinedRoom', (data) => {
        console.log('Player joined:', data.player);
        addChatMessage('System', `${data.player.username} joined the space`);
    });

    // Handle player left
    window.signal.on('ws:playerLeftRoom', (data) => {
        console.log('Player left:', data.uid);
        addChatMessage('System', 'A player left the space');
    });

    // Handle player moved
    window.signal.on('ws:playerMoved', (data) => {
        console.log('Player moved:', data);
        // Update player position in game
    });

    // Handle chat message
    window.signal.on('ws:receiveMessage', (data) => {
        addChatMessage(data.username, data.message);
    });

    // Handle proximity update
    window.signal.on('ws:proximityUpdate', (data) => {
        console.log('Proximity update:', data.proximityId);
        handleProximityChange(data.proximityId);
    });
}

function setupUIHandlers() {
    // Toggle camera
    const toggleCameraBtn = document.getElementById('toggleCamera');
    if (toggleCameraBtn) {
        toggleCameraBtn.addEventListener('click', async () => {
            const isMuted = await window.jitsiChat.toggleCamera();
            toggleCameraBtn.textContent = isMuted ? '📷 Camera (Off)' : '📷 Camera';
            toggleCameraBtn.classList.toggle('bg-red-600', isMuted);
            toggleCameraBtn.classList.toggle('bg-blue-600', !isMuted);
        });
    }

    // Toggle microphone
    const toggleMicBtn = document.getElementById('toggleMic');
    if (toggleMicBtn) {
        toggleMicBtn.addEventListener('click', async () => {
            const isMuted = await window.jitsiChat.toggleMicrophone();
            toggleMicBtn.textContent = isMuted ? '🎤 Mic (Muted)' : '🎤 Mic';
            toggleMicBtn.classList.toggle('bg-red-600', isMuted);
            toggleMicBtn.classList.toggle('bg-blue-600', !isMuted);
        });
    }

    // Send chat message
    const chatInput = document.getElementById('chat-input');
    const sendChatBtn = document.getElementById('send-chat');
    
    if (chatInput && sendChatBtn) {
        const sendMessage = () => {
            const message = chatInput.value.trim();
            if (message) {
                window.wsClient.sendMessage(message);
                addChatMessage('You', message);
                chatInput.value = '';
            }
        };

        sendChatBtn.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }
}

function addChatMessage(username, message) {
    const chatMessages = document.getElementById('chat-messages');
    if (!chatMessages) return;

    const messageEl = document.createElement('div');
    messageEl.className = 'text-sm';
    messageEl.innerHTML = `<strong>${escapeHtml(username)}:</strong> ${escapeHtml(message)}`;
    chatMessages.appendChild(messageEl);
    
    // Auto-scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Limit messages
    while (chatMessages.children.length > 50) {
        chatMessages.removeChild(chatMessages.firstChild);
    }
}

function updatePlayerCount(count) {
    const playerCountEl = document.getElementById('player-count');
    if (playerCountEl) {
        playerCountEl.textContent = count;
    }
}

function handleProximityChange(proximityId) {
    if (proximityId) {
        // Join video chat for this proximity group
        window.jitsiChat.joinChannel(
            proximityId,
            window.REALM_DATA.userId,
            window.REALM_DATA.realmId
        );
    } else {
        // Leave video chat
        window.jitsiChat.leaveChannel();
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function initializeGame() {
    // Simplified Pixi.js initialization for MVP
    const gameContainer = document.getElementById('game-container');
    if (!gameContainer) return;

    // Create Pixi application
    const app = new PIXI.Application();
    
    app.init({
        width: window.innerWidth,
        height: window.innerHeight,
        backgroundColor: 0x1a1a1a,
        resizeTo: window
    }).then(() => {
        gameContainer.appendChild(app.canvas);
        
        // Add placeholder text
        const text = new PIXI.Text({
            text: 'Game Canvas\n\nPixi.js game rendering will go here.\nFor now, WebSocket and Jitsi video chat are functional.',
            style: {
                fontFamily: 'Arial',
                fontSize: 24,
                fill: 0xffffff,
                align: 'center'
            }
        });
        text.anchor.set(0.5);
        text.x = app.screen.width / 2;
        text.y = app.screen.height / 2;
        app.stage.addChild(text);
        
        console.log('Pixi.js initialized (simplified)');
    });
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    window.wsClient.disconnect();
    window.jitsiChat.leaveChannel();
});
