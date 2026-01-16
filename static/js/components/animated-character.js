/**
 * AnimatedCharacter.js
 * Component for rendering animated character sprites
 */

class AnimatedCharacter {
    constructor(containerId, skin = '009') {
        this.container = document.getElementById(containerId);
        this.skin = skin;
        this.frame = 0;
        this.direction = 'down';
        this.animationInterval = null;
        this.frameWidth = 32;
        this.frameHeight = 32;
        this.framesPerDirection = 3;
        
        this.init();
    }

    init() {
        if (!this.container) {
            console.error(`Container ${this.containerId} not found`);
            return;
        }

        // Create canvas element
        this.canvas = document.createElement('canvas');
        this.canvas.width = this.frameWidth * 2;
        this.canvas.height = this.frameHeight * 2;
        this.ctx = this.canvas.getContext('2d');
        
        this.container.innerHTML = '';
        this.container.appendChild(this.canvas);

        // Load sprite sheet
        this.spriteSheet = new Image();
        this.spriteSheet.src = `/static/sprites/characters/Character_${this.skin}.png`;
        this.spriteSheet.onload = () => {
            this.startAnimation();
        };
    }

    startAnimation() {
        if (this.animationInterval) {
            clearInterval(this.animationInterval);
        }

        this.animationInterval = setInterval(() => {
            this.frame = (this.frame + 1) % this.framesPerDirection;
            this.render();
        }, 200); // Update every 200ms

        this.render();
    }

    render() {
        if (!this.ctx || !this.spriteSheet.complete) {
            return;
        }

        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        // Calculate source position in sprite sheet
        // Assuming sprite sheet layout: down, left, right, up (rows)
        const directionMap = { down: 0, left: 1, right: 2, up: 3 };
        const row = directionMap[this.direction] || 0;
        
        const sx = this.frame * this.frameWidth;
        const sy = row * this.frameHeight;

        // Draw scaled up sprite
        this.ctx.imageSmoothingEnabled = false;
        this.ctx.drawImage(
            this.spriteSheet,
            sx, sy, this.frameWidth, this.frameHeight,
            0, 0, this.canvas.width, this.canvas.height
        );
    }

    setSkin(skin) {
        this.skin = skin;
        this.spriteSheet.src = `/static/sprites/characters/Character_${this.skin}.png`;
    }

    setDirection(direction) {
        this.direction = direction;
        this.render();
    }

    destroy() {
        if (this.animationInterval) {
            clearInterval(this.animationInterval);
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AnimatedCharacter;
}
