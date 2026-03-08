const API_URL = 'http://localhost:8080/api';
let busesData = [];
let videoStream = null;

// Camera Functions
async function startCamera() {
    const video = document.getElementById('video');
    const statusDiv = document.getElementById('cameraStatus');
    const startBtn = document.getElementById('startCameraBtn');
    const captureBtn = document.getElementById('captureFaceBtn');
    const stopBtn = document.getElementById('stopCameraBtn');
    
    try {
        videoStream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            } 
        });
        
        video.srcObject = videoStream;
        video.style.display = 'block';
        
        statusDiv.textContent = '📷 Camera is active - Position your face in the frame';
        statusDiv.className = 'camera-status success';
        
        startBtn.style.display = 'none';
        captureBtn.style.display = 'inline-block';
        stopBtn.style.display = 'inline-block';
        
    } catch (err) {
        console.error('Camera error:', err);
        statusDiv.textContent = '❌ Camera access denied. Please allow camera permissions.';
        statusDiv.className = 'camera-status error';
    }
}

function captureFace() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const statusDiv = document.getElementById('cameraStatus');
    const busId = document.getElementById('busSelect').value;
    
    if (!busId) {
        statusDiv.textContent = '⚠️ Please select a bus first';
        statusDiv.className = 'camera-status error';
        return;
    }
    
    // Capture frame from video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    // Get image as data URL
    const imageData = canvas.toDataURL('image/jpeg');
    
    statusDiv.textContent = '🔄 Processing face...';
    
    // Send to backend for face recognition
    performFaceScan(imageData, busId);
}

async function performFaceScan(imageData, busId) {
    const statusDiv = document.getElementById('cameraStatus');
    
    try {
        const response = await fetch(`${API_URL}/scan/face`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: imageData,
                bus_id: parseInt(busId)
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            statusDiv.textContent = '✅ Face recognized! Redirecting to ticket...';
            statusDiv.className = 'camera-status success';
            
            localStorage.setItem('currentTicket', JSON.stringify(data));
            setTimeout(() => {
                window.location.href = 'ticket.html';
            }, 2000);
        } else {
            statusDiv.textContent = `❌ ${data.error || 'Face not recognized'}`;
            statusDiv.className = 'camera-status error';
        }
    } catch (error) {
        statusDiv.textContent = '❌ Error processing face. Try manual Face ID entry.';
        statusDiv.className = 'camera-status error';
    }
}

function stopCamera() {
    const video = document.getElementById('video');
    const statusDiv = document.getElementById('cameraStatus');
    const startBtn = document.getElementById('startCameraBtn');
    const captureBtn = document.getElementById('captureFaceBtn');
    const stopBtn = document.getElementById('stopCameraBtn');
    
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }
    
    video.srcObject = null;
    video.style.display = 'none';
    
    statusDiv.textContent = '';
    statusDiv.className = 'camera-status';
    
    startBtn.style.display = 'inline-block';
    captureBtn.style.display = 'none';
    stopBtn.style.display = 'none';
}

async function loadBuses() {
    try {
        const response = await fetch(`${API_URL}/buses`);
        const buses = await response.json();
        busesData = buses;
        
        const select = document.getElementById('busSelect');
        select.innerHTML = '<option value="">Select a bus...</option>';
        
        buses.forEach(bus => {
            const option = document.createElement('option');
            option.value = bus.id;
            option.textContent = `${bus.bus_number} - ${bus.route_name}`;
            option.dataset.routeFrom = bus.route_from || 'City Center';
            option.dataset.routeTo = bus.route_to || bus.route_name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading buses:', error);
    }
}

function updateRouteInfo() {
    const select = document.getElementById('busSelect');
    const routeInfo = document.getElementById('routeInfo');
    const routeFrom = document.getElementById('routeFrom');
    const routeTo = document.getElementById('routeTo');
    
    const selectedOption = select.options[select.selectedIndex];
    
    if (select.value) {
        const from = selectedOption.dataset.routeFrom || 'City Center';
        const to = selectedOption.dataset.routeTo || select.options[select.selectedIndex].text.split(' - ')[1] || 'Destination';
        
        routeFrom.textContent = from;
        routeTo.textContent = to;
        routeInfo.style.display = 'block';
    } else {
        routeInfo.style.display = 'none';
    }
}

async function loadPassengers() {
    try {
        const response = await fetch(`${API_URL}/passengers`);
        const passengers = await response.json();
        
        const tbody = document.getElementById('passengerTableBody');
        tbody.innerHTML = '';
        
        passengers.forEach(passenger => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${passenger.name}</td>
                <td>${passenger.route_from || 'City Center'}</td>
                <td>${passenger.route_to || 'Destination'}</td>
                <td>${passenger.qr_code}</td>
                <td>${passenger.face_id}</td>
                <td>₹${passenger.balance ? passenger.balance.toFixed(2) : '0.00'}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error loading passengers:', error);
    }
}

async function scanQR() {
    const qrCode = document.getElementById('qrInput').value.trim();
    const busId = document.getElementById('busSelect').value;
    
    if (!qrCode) {
        showResult('Please enter a QR code', 'error');
        return;
    }
    
    if (!busId) {
        showResult('Please select a bus', 'error');
        return;
    }
    
    await performScan('qr', qrCode, busId);
}

async function scanFace() {
    const faceId = document.getElementById('faceInput').value.trim();
    const busId = document.getElementById('busSelect').value;
    
    if (!faceId) {
        showResult('Please enter a Face ID', 'error');
        return;
    }
    
    if (!busId) {
        showResult('Please select a bus', 'error');
        return;
    }
    
    await performScan('face', faceId, busId);
}

async function performScan(scanType, scanValue, busId) {
    try {
        const response = await fetch(`${API_URL}/scan`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                scan_type: scanType,
                scan_value: scanValue,
                bus_id: parseInt(busId)
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showResult(`✅ Ticket generated successfully! Ticket Number: ${data.ticket_number}`, 'success');
            localStorage.setItem('currentTicket', JSON.stringify(data));
            setTimeout(() => {
                window.location.href = 'ticket.html';
            }, 2000);
        } else {
            showResult(`❌ ${data.error}`, 'error');
        }
    } catch (error) {
        showResult('❌ Error connecting to server', 'error');
        console.error('Error:', error);
    }
}

function showResult(message, type) {
    const resultDiv = document.getElementById('scanResult');
    resultDiv.textContent = message;
    resultDiv.className = `scan-result ${type}`;
}

loadBuses();
loadPassengers();
