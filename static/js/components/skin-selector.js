/**
 * SkinSelector.js
 * Logic for skin selection with preview
 */

class SkinSelector {
    constructor(options = {}) {
        this.containerId = options.containerId || 'skinSelectorContainer';
        this.previewId = options.previewId || 'skinPreview';
        this.onSelect = options.onSelect || (() => {});
        this.skins = options.skins || this.generateSkinList();
        this.currentSkin = options.currentSkin || '009';
        this.animatedCharacter = null;
        
        this.init();
    }

    generateSkinList() {
        const skins = [];
        for (let i = 1; i <= 83; i++) {
            skins.push(String(i).padStart(3, '0'));
        }
        return skins;
    }

    init() {
        this.container = document.getElementById(this.containerId);
        if (!this.container) {
            console.error(`Container ${this.containerId} not found`);
            return;
        }

        this.renderSkinGrid();
        this.setupPreview();
    }

    renderSkinGrid() {
        const grid = document.createElement('div');
        grid.className = 'grid grid-cols-6 md:grid-cols-8 lg:grid-cols-10 gap-3';
        
        this.skins.forEach(skin => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = `skin-option border-2 rounded-lg p-2 hover:border-blue-500 transition ${
                skin === this.currentSkin ? 'border-blue-600 bg-blue-50' : 'border-gray-300'
            }`;
            button.dataset.skin = skin;
            
            const img = document.createElement('img');
            img.src = `/static/sprites/characters/Character_${skin}.png`;
            img.alt = `Skin ${skin}`;
            img.className = 'w-full h-full object-contain';
            
            const label = document.createElement('p');
            label.className = 'text-xs text-center mt-1';
            label.textContent = skin;
            
            button.appendChild(img);
            button.appendChild(label);
            button.addEventListener('click', () => this.selectSkin(skin));
            
            grid.appendChild(button);
        });
        
        this.container.innerHTML = '';
        this.container.appendChild(grid);
    }

    setupPreview() {
        const previewElement = document.getElementById(this.previewId);
        if (previewElement && typeof AnimatedCharacter !== 'undefined') {
            this.animatedCharacter = new AnimatedCharacter(this.previewId, this.currentSkin);
        }
    }

    selectSkin(skin) {
        this.currentSkin = skin;
        
        // Update button styles
        this.container.querySelectorAll('.skin-option').forEach(btn => {
            if (btn.dataset.skin === skin) {
                btn.classList.remove('border-gray-300');
                btn.classList.add('border-blue-600', 'bg-blue-50');
            } else {
                btn.classList.remove('border-blue-600', 'bg-blue-50');
                btn.classList.add('border-gray-300');
            }
        });

        // Update animated preview
        if (this.animatedCharacter) {
            this.animatedCharacter.setSkin(skin);
        }

        // Callback
        this.onSelect(skin);
    }

    getCurrentSkin() {
        return this.currentSkin;
    }

    destroy() {
        if (this.animatedCharacter) {
            this.animatedCharacter.destroy();
        }
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SkinSelector;
}
