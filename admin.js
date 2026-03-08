const API_URL = 'http://localhost:8080/api';

async function loadDashboard() {
    try {
        const response = await fetch(`${API_URL}/admin/dashboard`);
        const data = await response.json();
        
        document.getElementById('totalPassengers').textContent = data.total_passengers;
        document.getElementById('ticketsToday').textContent = data.tickets_today;
        document.getElementById('revenueToday').textContent = `₹${data.revenue_today.toFixed(2)}`;
        document.getElementById('currentPassengers').textContent = data.current_passengers;
        
        const busStatsBody = document.getElementById('busStatsBody');
        busStatsBody.innerHTML = '';
        
        data.bus_stats.forEach(bus => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${bus.bus_number}</td>
                <td>${bus.route_name}</td>
                <td>${bus.current_passengers}</td>
                <td>${bus.total_trips}</td>
                <td>₹${bus.revenue.toFixed(2)}</td>
            `;
            busStatsBody.appendChild(row);
        });
        
        const recentTicketsBody = document.getElementById('recentTicketsBody');
        recentTicketsBody.innerHTML = '';
        
        if (data.recent_tickets.length === 0) {
            recentTicketsBody.innerHTML = '<tr><td colspan="6">No tickets found</td></tr>';
        } else {
            data.recent_tickets.forEach(ticket => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${ticket.ticket_number}</td>
                    <td>${ticket.passenger_name}</td>
                    <td>${ticket.bus_number}</td>
                    <td>${ticket.route_name}</td>
                    <td>₹${ticket.fare_amount.toFixed(2)}</td>
                    <td>${new Date(ticket.boarding_time).toLocaleString()}</td>
                `;
                recentTicketsBody.appendChild(row);
            });
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

loadDashboard();
setInterval(loadDashboard, 30000);
