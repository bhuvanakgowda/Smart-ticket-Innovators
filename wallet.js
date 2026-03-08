const API_URL = 'http://localhost:8080/api';
let currentPassengerId = null;

async function loadPassengerList() {
    try {
        const response = await fetch(`${API_URL}/passengers`);
        const passengers = await response.json();
        
        const select = document.getElementById('passengerSelect');
        select.innerHTML = '<option value="">Select a passenger...</option>';
        
        passengers.forEach(passenger => {
            const option = document.createElement('option');
            option.value = passenger.id;
            option.textContent = `${passenger.name} (${passenger.email})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading passengers:', error);
    }
}

async function loadWallet() {
    const passengerId = document.getElementById('passengerSelect').value;
    
    if (!passengerId) {
        document.getElementById('walletInfo').style.display = 'none';
        return;
    }
    
    currentPassengerId = passengerId;
    
    try {
        const response = await fetch(`${API_URL}/wallet/${passengerId}`);
        const data = await response.json();
        
        document.getElementById('walletName').textContent = data.name;
        document.getElementById('walletEmail').textContent = data.email;
        document.getElementById('walletBalance').textContent = `₹${data.balance.toFixed(2)}`;
        
        const tbody = document.getElementById('transactionTableBody');
        tbody.innerHTML = '';
        
        if (data.transactions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5">No transactions found</td></tr>';
        } else {
            data.transactions.forEach(transaction => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${transaction.ticket_number}</td>
                    <td>${transaction.bus_number}</td>
                    <td>${transaction.route_name}</td>
                    <td>₹${transaction.fare_amount.toFixed(2)}</td>
                    <td>${new Date(transaction.boarding_time).toLocaleString()}</td>
                `;
                tbody.appendChild(row);
            });
        }
        
        document.getElementById('walletInfo').style.display = 'block';
    } catch (error) {
        console.error('Error loading wallet:', error);
    }
}

function showRechargeModal() {
    document.getElementById('rechargeModal').style.display = 'block';
}

function closeRechargeModal() {
    document.getElementById('rechargeModal').style.display = 'none';
    document.getElementById('rechargeAmount').value = '';
}

function setAmount(amount) {
    document.getElementById('rechargeAmount').value = amount;
}

async function rechargeWallet() {
    const amount = parseFloat(document.getElementById('rechargeAmount').value);
    
    if (!amount || amount <= 0) {
        alert('Please enter a valid amount');
        return;
    }
    
    if (!currentPassengerId) {
        alert('Please select a passenger first');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/wallet/recharge`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                passenger_id: parseInt(currentPassengerId),
                amount: amount
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`Wallet recharged successfully! New balance: ₹${data.new_balance.toFixed(2)}`);
            closeRechargeModal();
            loadWallet();
        }
    } catch (error) {
        alert('Error recharging wallet');
        console.error('Error:', error);
    }
}

window.onclick = function(event) {
    const modal = document.getElementById('rechargeModal');
    if (event.target === modal) {
        closeRechargeModal();
    }
}

loadPassengerList();
