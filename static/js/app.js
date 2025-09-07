// ColorMind AI Application JavaScript

class ColorMindApp {
    constructor() {
        this.currentPalette = null;
        this.isProcessing = false;
        this.lockedColors = new Set();
        
        this.initializeEventListeners();
        this.initializeFeatherIcons();
    }

    initializeEventListeners() {
        // File upload events
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('uploadArea');
        
        uploadArea.addEventListener('click', () => fileInput.click());
        uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        
        fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        
        // Remove image button
        document.getElementById('removeImage').addEventListener('click', this.removeImage.bind(this));
        
        // Generate button
        document.getElementById('generateBtn').addEventListener('click', this.generatePalette.bind(this));
        
        // Palette actions
        document.getElementById('shuffleBtn').addEventListener('click', this.shufflePalette.bind(this));
        document.getElementById('exportBtn').addEventListener('click', this.showExportModal.bind(this));
        document.getElementById('copyHexBtn').addEventListener('click', this.copyHexCodes.bind(this));
        
        // Export modal
        document.getElementById('confirmExport').addEventListener('click', this.exportPalette.bind(this));
        
        // Settings changes
        document.querySelectorAll('input[name="mood"]').forEach(radio => {
            radio.addEventListener('change', this.onSettingsChange.bind(this));
        });
        
        document.querySelectorAll('input[name="lighting"]').forEach(radio => {
            radio.addEventListener('change', this.onLightingChange.bind(this));
        });
        
        document.getElementById('styleSelect').addEventListener('change', this.onSettingsChange.bind(this));
        document.getElementById('harmonySelect').addEventListener('change', this.onSettingsChange.bind(this));
    }

    initializeFeatherIcons() {
        // Reinitialize Feather icons after dynamic content changes
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }

    handleDragOver(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        document.getElementById('uploadArea').classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    processFile(file) {
        if (!this.isValidImageFile(file)) {
            this.showAlert('Please select a valid image file (JPG or PNG)', 'error');
            return;
        }

        if (file.size > 16 * 1024 * 1024) {
            this.showAlert('File size must be less than 16MB', 'error');
            return;
        }

        // Show image preview
        this.showImagePreview(file);
        
        // Enable generate button
        document.getElementById('generateBtn').disabled = false;
    }

    isValidImageFile(file) {
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
        return validTypes.includes(file.type);
    }

    showImagePreview(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const previewImg = document.getElementById('previewImg');
            const imagePreview = document.getElementById('imagePreview');
            const uploadArea = document.getElementById('uploadArea');
            
            previewImg.src = e.target.result;
            imagePreview.classList.remove('d-none');
            uploadArea.classList.add('d-none');
        };
        reader.readAsDataURL(file);
    }

    removeImage() {
        const imagePreview = document.getElementById('imagePreview');
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        
        imagePreview.classList.add('d-none');
        uploadArea.classList.remove('d-none');
        fileInput.value = '';
        
        // Clear palette if it was generated from this image
        if (this.currentPalette) {
            this.clearPalette();
        }
    }

    async generatePalette() {
        if (this.isProcessing) return;
        
        this.isProcessing = true;
        this.showLoadingOverlay();
        
        try {
            const fileInput = document.getElementById('fileInput');
            const hasImage = fileInput.files.length > 0;
            
            if (hasImage) {
                await this.generateFromImage();
            } else {
                await this.generateFromSettings();
            }
            
        } catch (error) {
            console.error('Error generating palette:', error);
            this.showAlert('Error generating palette: ' + error.message, 'error');
        } finally {
            this.isProcessing = false;
            this.hideLoadingOverlay();
        }
    }

    async generateFromImage() {
        const fileInput = document.getElementById('fileInput');
        const formData = new FormData();
        
        formData.append('file', fileInput.files[0]);
        formData.append('style', this.getSelectedValue('styleSelect'));
        formData.append('mood', this.getSelectedValue('input[name="mood"]:checked'));
        formData.append('lighting', this.getSelectedValue('input[name="lighting"]:checked'));
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await this.handleResponse(response);
        this.displayPalette(data.palette);
    }

    async generateFromSettings() {
        // Generate base colors from style preferences
        const style = this.getSelectedValue('styleSelect');
        const baseColors = this.generateBaseColors(style);
        
        const requestData = {
            colors: baseColors,
            style: style,
            mood: this.getSelectedValue('input[name="mood"]:checked'),
            lighting: this.getSelectedValue('input[name="lighting"]:checked'),
            harmony: this.getSelectedValue('harmonySelect')
        };
        
        const response = await fetch('/generate_palette', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await this.handleResponse(response);
        this.displayPalette(data.palette);
    }

    generateBaseColors(style) {
        // Generate some base colors based on style
        const styleColorMaps = {
            'scandinavian': [[240, 244, 248], [219, 234, 254], [254, 249, 195]],
            'japandi': [[245, 245, 220], [210, 180, 140], [176, 196, 222]],
            'minimalist': [[248, 250, 252], [226, 232, 240], [71, 85, 105]],
            'industrial': [[100, 116, 139], [148, 163, 184], [203, 213, 225]],
            'mediterranean': [[254, 240, 138], [147, 197, 253], [34, 197, 94]]
        };
        
        return styleColorMaps[style] || styleColorMaps['scandinavian'];
    }

    async onLightingChange() {
        if (!this.currentPalette) return;
        
        const lighting = this.getSelectedValue('input[name="lighting"]:checked');
        
        try {
            const response = await fetch('/adjust_lighting', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    colors: this.currentPalette.colors,
                    lighting: lighting
                })
            });
            
            const data = await this.handleResponse(response);
            this.currentPalette.colors = data.colors;
            this.displayPalette(this.currentPalette);
            
        } catch (error) {
            console.error('Error adjusting lighting:', error);
        }
    }

    async onSettingsChange() {
        // Regenerate palette if one exists and settings change significantly
        if (this.currentPalette && !this.isProcessing) {
            await this.generatePalette();
        }
    }

    displayPalette(paletteData) {
        this.currentPalette = paletteData;
        const swatchesContainer = document.getElementById('colorSwatches');
        const paletteName = document.getElementById('paletteName');
        
        // Update palette name
        paletteName.textContent = paletteData.name || 'Your Color Palette';
        
        // Clear existing swatches
        swatchesContainer.innerHTML = '';
        
        // Create color swatches
        paletteData.colors.forEach((color, index) => {
            const swatchElement = this.createColorSwatch(color, index);
            swatchesContainer.appendChild(swatchElement);
        });
        
        // Update room preview
        this.updateRoomPreview(paletteData.colors);
        
        // Enable palette actions
        this.enablePaletteActions();
        
        // Add fade-in animation
        swatchesContainer.classList.add('fade-in');
        
        // Update Feather icons
        this.initializeFeatherIcons();
    }

    createColorSwatch(color, index) {
        const swatch = document.createElement('div');
        swatch.className = 'color-swatch';
        swatch.innerHTML = `
            <div class="color-preview" style="background-color: ${color.hex}">
                <button class="lock-button ${color.locked ? 'locked' : ''}" data-index="${index}">
                    <i data-feather="${color.locked ? 'lock' : 'unlock'}"></i>
                </button>
            </div>
            <div class="color-info">
                <div class="color-role">${color.role}</div>
                <div class="color-codes">
                    <div class="color-hex">${color.hex}</div>
                    <div class="color-rgb">RGB(${color.rgb.join(', ')})</div>
                    <div class="color-hsl">HSL(${color.hsl.h}°, ${color.hsl.s}%, ${color.hsl.l}%)</div>
                    <div class="color-cmyk">CMYK(${color.cmyk.c}%, ${color.cmyk.m}%, ${color.cmyk.y}%, ${color.cmyk.k}%)</div>
                </div>
            </div>
        `;
        
        // Add click event for color copying
        swatch.addEventListener('click', () => {
            this.copyColorToClipboard(color.hex);
        });
        
        // Add lock button event
        const lockButton = swatch.querySelector('.lock-button');
        lockButton.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleColorLock(index);
        });
        
        return swatch;
    }

    toggleColorLock(index) {
        if (!this.currentPalette) return;
        
        const color = this.currentPalette.colors[index];
        color.locked = !color.locked;
        
        // Update the lock button
        const lockButton = document.querySelector(`[data-index="${index}"]`);
        lockButton.classList.toggle('locked', color.locked);
        lockButton.innerHTML = `<i data-feather="${color.locked ? 'lock' : 'unlock'}"></i>`;
        
        this.initializeFeatherIcons();
    }

    updateRoomPreview(colors) {
        if (colors.length === 0) return;
        
        const roomWall = document.getElementById('roomWall');
        const roomFloor = document.getElementById('roomFloor');
        const roomFurniture = document.getElementById('roomFurniture');
        
        // Apply colors to room elements
        if (colors[0]) roomWall.style.backgroundColor = colors[0].hex;
        if (colors[1]) roomFloor.style.backgroundColor = colors[1].hex;
        if (colors[2]) roomFurniture.style.backgroundColor = colors[2].hex;
    }

    async shufflePalette() {
        if (!this.currentPalette || this.isProcessing) return;
        
        this.showLoadingOverlay();
        
        try {
            // Keep locked colors, shuffle others
            const unlockedColors = this.currentPalette.colors
                .map((color, index) => ({ color, index }))
                .filter(item => !item.color.locked);
            
            if (unlockedColors.length === 0) {
                this.showAlert('All colors are locked. Unlock some colors to shuffle.', 'info');
                return;
            }
            
            // Generate new palette keeping locked colors
            const baseColors = this.currentPalette.colors
                .filter(color => !color.locked)
                .map(color => color.rgb);
                
            if (baseColors.length > 0) {
                const requestData = {
                    colors: baseColors,
                    style: this.getSelectedValue('styleSelect'),
                    mood: this.getSelectedValue('input[name="mood"]:checked'),
                    lighting: this.getSelectedValue('input[name="lighting"]:checked'),
                    harmony: this.getSelectedValue('harmonySelect')
                };
                
                const response = await fetch('/generate_palette', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(requestData)
                });
                
                const data = await this.handleResponse(response);
                
                // Merge locked colors with new ones
                this.mergePaletteWithLocked(data.palette);
            }
            
        } catch (error) {
            console.error('Error shuffling palette:', error);
            this.showAlert('Error shuffling palette: ' + error.message, 'error');
        } finally {
            this.hideLoadingOverlay();
        }
    }

    mergePaletteWithLocked(newPalette) {
        const mergedColors = [];
        let newColorIndex = 0;
        
        this.currentPalette.colors.forEach((originalColor, index) => {
            if (originalColor.locked) {
                mergedColors.push(originalColor);
            } else {
                if (newColorIndex < newPalette.colors.length) {
                    mergedColors.push(newPalette.colors[newColorIndex]);
                    newColorIndex++;
                } else {
                    mergedColors.push(originalColor);
                }
            }
        });
        
        newPalette.colors = mergedColors;
        this.displayPalette(newPalette);
    }

    showExportModal() {
        if (!this.currentPalette) return;
        
        const exportName = document.getElementById('exportName');
        exportName.value = this.currentPalette.name || 'My ColorMind Palette';
        
        const modal = new bootstrap.Modal(document.getElementById('exportModal'));
        modal.show();
    }

    async exportPalette() {
        if (!this.currentPalette) return;
        
        const exportFormat = document.getElementById('exportFormat').value;
        const exportName = document.getElementById('exportName').value || 'ColorMind Palette';
        
        try {
            const requestData = {
                colors: this.currentPalette.colors,
                name: exportName,
                format: exportFormat
            };
            
            const response = await fetch('/export_palette', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            if (exportFormat === 'png') {
                // Handle file download
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${exportName.replace(/ /g, '_')}_palette.png`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            } else {
                // Handle JSON data
                const data = await response.json();
                this.downloadJSON(data, `${exportName.replace(/ /g, '_')}_palette.json`);
            }
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('exportModal'));
            modal.hide();
            
            this.showAlert('Palette exported successfully!', 'success');
            
        } catch (error) {
            console.error('Error exporting palette:', error);
            this.showAlert('Error exporting palette: ' + error.message, 'error');
        }
    }

    downloadJSON(data, filename) {
        const jsonStr = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonStr], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    copyHexCodes() {
        if (!this.currentPalette) return;
        
        const hexCodes = this.currentPalette.colors.map(color => color.hex).join(', ');
        
        navigator.clipboard.writeText(hexCodes).then(() => {
            this.showAlert('HEX codes copied to clipboard!', 'success');
        }).catch((error) => {
            console.error('Error copying to clipboard:', error);
            this.showAlert('Error copying to clipboard', 'error');
        });
    }

    copyColorToClipboard(hex) {
        navigator.clipboard.writeText(hex).then(() => {
            this.showAlert(`Color ${hex} copied to clipboard!`, 'success');
        }).catch((error) => {
            console.error('Error copying color:', error);
        });
    }

    enablePaletteActions() {
        document.getElementById('shuffleBtn').disabled = false;
        document.getElementById('exportBtn').disabled = false;
        document.getElementById('copyHexBtn').disabled = false;
    }

    clearPalette() {
        this.currentPalette = null;
        document.getElementById('colorSwatches').innerHTML = `
            <div class="empty-state">
                <i data-feather="image" class="empty-icon"></i>
                <h4>Ready to Create</h4>
                <p>Upload a room photo or select your preferences to generate a beautiful color palette</p>
            </div>
        `;
        
        document.getElementById('paletteName').textContent = 'Your Color Palette';
        
        // Disable palette actions
        document.getElementById('shuffleBtn').disabled = true;
        document.getElementById('exportBtn').disabled = true;
        document.getElementById('copyHexBtn').disabled = true;
        
        this.initializeFeatherIcons();
    }

    getSelectedValue(selector) {
        const element = document.querySelector(selector);
        return element ? element.value : '';
    }

    async handleResponse(response) {
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'Network error' }));
            throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }

    showLoadingOverlay() {
        document.getElementById('loadingOverlay').classList.add('show');
    }

    hideLoadingOverlay() {
        document.getElementById('loadingOverlay').classList.remove('show');
    }

    showAlert(message, type = 'info') {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at the top of main content
        const mainContent = document.querySelector('.main-content');
        const container = mainContent.querySelector('.container-fluid');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Global functions
function initializeColorMindApp() {
    window.colorMindApp = new ColorMindApp();
}

// Export for use in templates
window.initializeColorMindApp = initializeColorMindApp;
