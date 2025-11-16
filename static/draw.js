/**
 * Canvas drawing functionality
 * NOTE: This handles mouse and touch events for drawing
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('canvas');
    if (!canvas) {
        console.error('Canvas element not found!');
        return; // Exit if canvas doesn't exist
    }
    
    const ctx = canvas.getContext('2d');
    if (!ctx) {
        console.error('Could not get canvas context!');
        return;
    }
    const colorPicker = document.getElementById('colorPicker');
    const brushSize = document.getElementById('brushSize');
    const brushSizeValue = document.getElementById('brushSizeValue');
    const clearBtn = document.getElementById('clearBtn');
    const saveBtn = document.getElementById('saveBtn');
    const saveMessage = document.getElementById('saveMessage');
    
    let isDrawing = false;
    let lastX = 0;
    let lastY = 0;
    
    // Set canvas background to transparent (no fill)
    // This way only the drawing lines are saved, not a white background
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Set initial drawing style
    ctx.strokeStyle = colorPicker.value;
    ctx.fillStyle = colorPicker.value;
    ctx.lineWidth = brushSize.value;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    // Update brush size display
    brushSize.addEventListener('input', function() {
        brushSizeValue.textContent = this.value;
    });
    
    // Clear canvas
    clearBtn.addEventListener('click', function() {
        if (confirm('Clear the entire canvas?')) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        }
    });
    
    // Get mouse/touch position relative to canvas
    function getPos(e) {
        const rect = canvas.getBoundingClientRect();
        const scaleX = canvas.width / rect.width;
        const scaleY = canvas.height / rect.height;
        
        if (e.touches) {
            // Touch event
            return {
                x: (e.touches[0].clientX - rect.left) * scaleX,
                y: (e.touches[0].clientY - rect.top) * scaleY
            };
        } else {
            // Mouse event
            return {
                x: (e.clientX - rect.left) * scaleX,
                y: (e.clientY - rect.top) * scaleY
            };
        }
    }
    
    // Start drawing
    function startDraw(e) {
        e.preventDefault();
        isDrawing = true;
        const pos = getPos(e);
        lastX = pos.x;
        lastY = pos.y;
        
        // Draw a dot at the start position
        ctx.strokeStyle = colorPicker.value;
        ctx.lineWidth = brushSize.value;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, brushSize.value / 2, 0, Math.PI * 2);
        ctx.fillStyle = colorPicker.value;
        ctx.fill();
    }
    
    // Draw
    function draw(e) {
        if (!isDrawing) return;
        e.preventDefault();
        
        const pos = getPos(e);
        
        ctx.strokeStyle = colorPicker.value;
        ctx.lineWidth = brushSize.value;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        
        ctx.beginPath();
        ctx.moveTo(lastX, lastY);
        ctx.lineTo(pos.x, pos.y);
        ctx.stroke();
        
        lastX = pos.x;
        lastY = pos.y;
    }
    
    // Stop drawing
    function stopDraw(e) {
        if (isDrawing) {
            e.preventDefault();
            isDrawing = false;
        }
    }
    
    // Mouse events
    canvas.addEventListener('mousedown', startDraw);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDraw);
    canvas.addEventListener('mouseleave', stopDraw);
    
    // Touch events
    canvas.addEventListener('touchstart', startDraw);
    canvas.addEventListener('touchmove', draw);
    canvas.addEventListener('touchend', stopDraw);
    canvas.addEventListener('touchcancel', stopDraw);
    
    // Save drawing
    saveBtn.addEventListener('click', function() {
        // Check if background should be included
        const includeBackground = document.getElementById('includeBackground').checked;
        const message = document.getElementById('drawingMessage').value.trim();
        
        // Save current canvas state
        const currentImageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        
        // If background is included, draw white background first
        let imageData;
        if (includeBackground) {
            // Create temporary canvas with white background
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = canvas.width;
            tempCanvas.height = canvas.height;
            const tempCtx = tempCanvas.getContext('2d');
            
            // Fill with white
            tempCtx.fillStyle = 'white';
            tempCtx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
            
            // Draw the original drawing on top
            tempCtx.drawImage(canvas, 0, 0);
            
            // Get the image data
            imageData = tempCanvas.toDataURL('image/png');
        } else {
            // Save as-is (transparent background)
            imageData = canvas.toDataURL('image/png');
        }
        
        // Show loading
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';
        saveMessage.innerHTML = '';
        
        // Send to server
        fetch('/save-drawing', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image_data: imageData,
                message: message || null,
                has_background: includeBackground
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                saveMessage.innerHTML = '<div class="alert alert-success">' + data.message + '</div>';
                // Reload page after 2 seconds to update drawing count
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            } else {
                saveMessage.innerHTML = '<div class="alert alert-danger">' + data.message + '</div>';
                saveBtn.disabled = false;
                saveBtn.textContent = 'Save Drawing';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            saveMessage.innerHTML = '<div class="alert alert-danger">Error saving drawing. Please try again.</div>';
            saveBtn.disabled = false;
            saveBtn.textContent = 'Save Drawing';
        });
    });
    
    console.log('Drawing canvas initialized successfully!');
}); // End DOMContentLoaded

