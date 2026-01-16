/**
 * SkinModal.js
 * Logic for the reusable skin selection modal
 */

class SkinModal {
    constructor(options = {}) {
        this.modalId = options.modalId || 'skinModal';
        this.onConfirm = options.onConfirm || (() => {});
        this.currentSkin = options.currentSkin || '009';
        this.selectedSkin = this.currentSkin;
        this.skins = this.generateSkinList();
        
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
        this.modal = document.getElementById(this.modalId);
        if (!this.modal) {
            console.error(`Modal ${this.modalId} not found`);
            return;
        }

        this.setupEventListeners();
        this.renderSkinGrid();
    }

    setupEventListeners() {
        const closeBtn = document.getElementById('closeSkinModal');
        const cancelBtn = document.getElementById('cancelSkinSelection');
        const confirmBtn = document.getElementById('confirmSkinSelection');

        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.hide());
        }

        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.hide());
        }

        if (confirmBtn) {
            confirmBtn.addEventListener('click', () => this.confirm());
        }

        // Close on outside click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.hide();
            }
        });

        // Close on ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && !this.modal.classList.contains('hidden')) {
                this.hide();
            }
        });
    }

    renderSkinGrid() {
        const gridContainer = this.modal.querySelector('.grid');
        if (!gridContainer) return;

        gridContainer.innerHTML = '';
        
        this.skins.forEach(skin => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = `skin-option border-2 rounded-lg p-2 hover:border-blue-500 transition ${
                skin === this.selectedSkin ? 'border-blue-600 bg-blue-50' : 'border-gray-300'
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
            
            gridContainer.appendChild(button);
        });
    }

    selectSkin(skin) {
        this.selectedSkin = skin;
        
        // Update button styles
        this.modal.querySelectorAll('.skin-option').forEach(btn => {
            if (btn.dataset.skin === skin) {
                btn.classList.remove('border-gray-300');
                btn.classList.add('border-blue-600', 'bg-blue-50');
            } else {
                btn.classList.remove('border-blue-600', 'bg-blue-50');
                btn.classList.add('border-gray-300');
            }
        });

        // Update preview
        const preview = document.getElementById('skinPreview');
        const label = document.getElementById('skinLabel');
        
        if (preview) {
            preview.innerHTML = `<img src="/static/sprites/characters/Character_${skin}.png" 
                                     alt="Preview" 
                                     class="w-32 h-32 object-contain">`;
        }
        
        if (label) {
            label.textContent = `Skin ${skin}`;
        }
    }

    show(currentSkin = null) {
        if (currentSkin) {
            this.currentSkin = currentSkin;
            this.selectedSkin = currentSkin;
        }
        
        this.renderSkinGrid();
        this.selectSkin(this.selectedSkin);
        this.modal.classList.remove('hidden');
    }

    hide() {
        this.modal.classList.add('hidden');
        this.selectedSkin = this.currentSkin; // Reset to current if cancelled
    }

    confirm() {
        this.currentSkin = this.selectedSkin;
        this.onConfirm(this.selectedSkin);
        this.hide();
    }

    getCurrentSkin() {
        return this.currentSkin;
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SkinModal;
}
