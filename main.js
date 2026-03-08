const API_URL = 'http://localhost:8080/api';

async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/admin/dashboard`);
        const data = await response.json();
        
        document.getElementById('totalPassengers').textContent = data.total_passengers;
        document.getElementById('ticketsToday').textContent = data.tickets_today;
        document.getElementById('revenueToday').textContent = `₹${data.revenue_today.toFixed(2)}`;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

loadStats();
setInterval(loadStats, 30000);
