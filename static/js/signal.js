// Simple event emitter for inter-component communication
class Signal {
    constructor() {
        this.listeners = {};
    }

    on(name, callback) {
        if (!this.listeners[name]) {
            this.listeners[name] = [];
        }
        this.listeners[name].push(callback);
    }

    off(name, callback) {
        if (this.listeners[name]) {
            this.listeners[name] = this.listeners[name].filter(fn => fn !== callback);
        }
    }

    emit(name, data) {
        if (this.listeners[name]) {
            this.listeners[name].forEach(callback => callback(data));
        }
    }
}

const signal = new Signal();
window.signal = signal;
