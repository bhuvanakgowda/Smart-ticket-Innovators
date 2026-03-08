const API_URL = 'http://localhost:8080/api';

function loadTicket() {
    const ticketData = localStorage.getItem('currentTicket');
    
    if (!ticketData) {
        document.getElementById('ticketDisplay').innerHTML = '<p>No ticket data found. Please scan a passenger first.</p>';
        return;
    }
    
    const ticket = JSON.parse(ticketData);
    
    document.getElementById('ticketNumber').textContent = ticket.ticket_number;
    document.getElementById('passengerName').textContent = ticket.passenger_name;
    document.getElementById('busNumber').textContent = ticket.bus_number;
    document.getElementById('routeFrom').textContent = ticket.route_from || 'City Center';
    document.getElementById('routeTo').textContent = ticket.route_to || ticket.route_name || 'Destination';
    document.getElementById('fareAmount').textContent = `₹${ticket.fare_amount.toFixed(2)}`;
    document.getElementById('boardingTime').textContent = new Date(ticket.boarding_time).toLocaleString();
    document.getElementById('walletBalance').textContent = `₹${ticket.new_balance.toFixed(2)}`;
}

loadTicket();
