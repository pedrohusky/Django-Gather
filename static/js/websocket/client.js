// WebSocket client for Django Channels
class WSClient {
    constructor() {
        this.ws = null;
        this.connected = false;
        this.handlers = {};
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/game/`;
        
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.connected = true;
            window.signal.emit('ws-connected');
        };

        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (e) {
                console.error('Failed to parse WebSocket message:', e);
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            window.signal.emit('ws-error', error);
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.connected = false;
            window.signal.emit('ws-disconnected');
        };
    }

    send(type, data = {}) {
        if (this.ws && this.connected) {
            this.ws.send(JSON.stringify({
                type: type,
                ...data
            }));
        } else {
            console.warn('WebSocket not connected');
        }
    }

    handleMessage(data) {
        const type = data.type;
        
        // Emit to signal for component handling
        window.signal.emit(`ws:${type}`, data);

        // Call registered handlers
        if (this.handlers[type]) {
            this.handlers[type].forEach(handler => handler(data));
        }
    }

    on(eventType, handler) {
        if (!this.handlers[eventType]) {
            this.handlers[eventType] = [];
        }
        this.handlers[eventType].push(handler);
    }

    off(eventType, handler) {
        if (this.handlers[eventType]) {
            this.handlers[eventType] = this.handlers[eventType].filter(h => h !== handler);
        }
    }

    // Game-specific methods
    joinRealm(realmId, shareId) {
        this.send('joinRealm', { realmId, shareId });
    }

    movePlayer(x, y) {
        this.send('movePlayer', { x, y });
    }

    teleport(roomIndex, x, y) {
        this.send('teleport', { roomIndex, x, y });
    }

    changeSkin(skin) {
        this.send('changedSkin', { skin });
    }

    sendMessage(message) {
        this.send('sendMessage', { message });
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

const wsClient = new WSClient();
window.wsClient = wsClient;
