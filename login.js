const API_URL = 'http://localhost:8080/api';

async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const messageDiv = document.getElementById('loginMessage');
    
    messageDiv.textContent = 'Logging in...';
    messageDiv.className = 'login-message';
    
    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Save user data to localStorage
            localStorage.setItem('currentUser', JSON.stringify(data.user));
            
            messageDiv.textContent = '✅ Login successful! Redirecting...';
            messageDiv.className = 'login-message success';
            
            // Redirect to home page after 1 second
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1000);
        } else {
            messageDiv.textContent = '❌ ' + data.error;
            messageDiv.className = 'login-message error';
        }
    } catch (error) {
        messageDiv.textContent = ' Server error. Make sure backend is running!';
        messageDiv.className = 'login-message error';
        console.error('Error:', error);
    }
}
