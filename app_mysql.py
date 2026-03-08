from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import random
import string

app = Flask(__name__)
CORS(app)

# MySQL Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Bhuvi@2411',
    'database': 'bus_ticket_system'
}

def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_db():
    try:
        # Connect without database to create it
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Bhuvi@2411'
        )
        cursor = conn.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS bus_ticket_system")
        cursor.execute("USE bus_ticket_system")
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS passengers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                phone VARCHAR(20) NOT NULL,
                password VARCHAR(255),
                face_id VARCHAR(50) UNIQUE,
                qr_code VARCHAR(50) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add password column if it doesn't exist (for existing databases)
        try:
            cursor.execute("ALTER TABLE passengers ADD COLUMN password VARCHAR(255)")
        except:
            pass  # Column already exists
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wallets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                passenger_id INT UNIQUE NOT NULL,
                balance DECIMAL(10, 2) DEFAULT 0,
                FOREIGN KEY (passenger_id) REFERENCES passengers(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS buses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bus_number VARCHAR(50) UNIQUE NOT NULL,
                route_name VARCHAR(255) NOT NULL,
                fare_per_km DECIMAL(10, 2) DEFAULT 2.0,
                total_distance DECIMAL(10, 2) DEFAULT 10.0,
                current_passengers INT DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                ticket_number VARCHAR(50) UNIQUE NOT NULL,
                passenger_id INT NOT NULL,
                bus_id INT NOT NULL,
                passenger_name VARCHAR(255) NOT NULL,
                bus_number VARCHAR(50) NOT NULL,
                route_name VARCHAR(255) NOT NULL,
                fare_amount DECIMAL(10, 2) NOT NULL,
                boarding_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'active',
                FOREIGN KEY (passenger_id) REFERENCES passengers(id),
                FOREIGN KEY (bus_id) REFERENCES buses(id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                passenger_id INT NOT NULL,
                bus_id INT NOT NULL,
                scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (passenger_id) REFERENCES passengers(id),
                FOREIGN KEY (bus_id) REFERENCES buses(id)
            )
        ''')
        
        # Insert sample data
        cursor.execute("SELECT COUNT(*) FROM passengers")
        count = cursor.fetchone()[0]
        
        if count == 0:
            passengers = [
                ('John Doe', 'john@example.com', '1234567890', 'password123', 'FACE001', 'QR001'),
                ('Jane Smith', 'jane@example.com', '0987654321', 'password123', 'FACE002', 'QR002'),
                ('Mike Johnson', 'mike@example.com', '5551234567', 'password123', 'FACE003', 'QR003'),
                ('Sarah Williams', 'sarah@example.com', '5559876543', 'password123', 'FACE004', 'QR004'),
            ]
            cursor.executemany('INSERT INTO passengers (name, email, phone, password, face_id, qr_code) VALUES (%s, %s, %s, %s, %s, %s)', passengers)
        else:
            # Update existing users with default password
            cursor.execute("UPDATE passengers SET password = 'password123' WHERE password IS NULL OR password = ''")
            
            for i in range(1, 5):
                cursor.execute('INSERT INTO wallets (passenger_id, balance) VALUES (%s, %s)', (i, 500.0))
            
            buses = [
                ('BUS101', 'Downtown - Airport', 2.5, 15.0),
                ('BUS202', 'Central Station - Mall', 2.0, 10.0),
                ('BUS303', 'University - Tech Park', 3.0, 20.0),
            ]
            cursor.executemany('INSERT INTO buses (bus_number, route_name, fare_per_km, total_distance) VALUES (%s, %s, %s, %s)', buses)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully!")
        
    except Error as e:
        print(f"Error initializing database: {e}")

init_db()

# Serve static frontend files
@app.route('/api/')
def api_home():
    return jsonify({
        'message': 'Smart Bus Ticket System API',
        'status': 'running',
        'endpoints': {
            'login': '/api/login (POST)',
            'signup': '/api/signup (POST)',
            'passengers': '/api/passengers (GET)',
            'buses': '/api/buses (GET)',
            'scan': '/api/scan (POST)',
            'wallet': '/api/wallet/<id> (GET)',
            'wallet_recharge': '/api/wallet/recharge (POST)',
            'tickets': '/api/tickets/<id> (GET)',
            'admin_dashboard': '/api/admin/dashboard (GET)'
        }
    })

@app.route('/frontend/<path:filename>')
def serve_frontend(filename):
    from flask import send_from_directory
    import os
    frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    return send_from_directory(frontend_path, filename)

@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart Bus Ticket System</title>
        <style>
            body { font-family: Arial; background: linear-gradient(135deg, #1e3c72, #2a5298); padding: 40px; color: white; }
            .container { max-width: 700px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 30px; border-radius: 15px; }
            h1 { text-align: center; font-size: 2.5em; }
            .login-box { background: rgba(0,0,0,0.3); padding: 20px; border-radius: 10px; margin: 20px 0; }
            .login-box h2 { margin-top: 0; color: #ffd700; }
            .user { background: rgba(255,255,255,0.1); padding: 12px; margin: 10px 0; border-radius: 5px; font-size: 1.1em; }
            .email { color: #90EE90; font-weight: bold; }
            .password { color: #FFB6C1; }
            .btn { display: inline-block; background: #ffd700; color: #1e3c72; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; margin: 10px; font-size: 1.1em; }
            .btn:hover { background: #fff; transform: scale(1.05); }
            .note { background: rgba(255,255,255,0.1); padding: 10px; border-radius: 5px; margin-top: 15px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚌 Smart Bus Ticket System</h1>
            <h2 style="text-align:center">✅ Backend Running Successfully!</h2>
            
            <div class="login-box">
                <h2>🔑 Login Credentials</h2>
                <p><strong>Use these to login:</strong></p>
                <div class="user">📧 Email: <span class="email">john@example.com</span> | 🔑 Password: <span class="password">password123</span></div>
                <div class="user">📧 Email: <span class="email">jane@example.com</span> | 🔑 Password: <span class="password">password123</span></div>
                <div class="user">📧 Email: <span class="email">mike@example.com</span> | 🔑 Password: <span class="password">password123</span></div>
                <div class="user">📧 Email: <span class="email">sarah@example.com</span> | 🔑 Password: <span class="password">password123</span></div>
            </div>
            
            <div style="text-align:center">
                <a href="/frontend/login.html" class="btn">🚀 Open Login Page</a>
            </div>
            
            <div class="note">
                <h3>📊 API Endpoints:</h3>
                <ul>
                    <li>/api/passengers - View all users</li>
                    <li>/api/buses - View all buses</li>
                    <li>/api/admin/dashboard - Admin stats</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

@app.route('/api/signup', methods=['POST'])
def signup():
    """Register a new user with email and password"""
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    
    if not all([name, email, phone, password]):
        return jsonify({'success': False, 'error': 'All fields are required'}), 400
    
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    # Check if email already exists
    cursor.execute('SELECT id FROM passengers WHERE email = %s', (email,))
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'error': 'Email already registered'}), 400
    
    # Generate unique QR code and Face ID
    qr_code = 'QR' + str(random.randint(1000, 9999))
    face_id = 'FACE' + str(random.randint(1000, 9999))
    
    try:
        # Insert new user
        cursor.execute('''
            INSERT INTO passengers (name, email, phone, password, qr_code, face_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (name, email, phone, password, qr_code, face_id))
        
        passenger_id = cursor.lastrowid
        
        # Create wallet with ₹500 balance
        cursor.execute('INSERT INTO wallets (passenger_id, balance) VALUES (%s, %s)', (passenger_id, 500.0))
        
        conn.commit()
        
        # Get the created user
        cursor.execute('SELECT p.*, w.balance FROM passengers p LEFT JOIN wallets w ON p.id = w.passenger_id WHERE p.id = %s', (passenger_id,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'user': dict(user)})
        
    except Error as e:
        cursor.close()
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login with email and password"""
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password required'}), 400
    
    conn = get_db()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT p.*, w.balance FROM passengers p LEFT JOIN wallets w ON p.id = w.passenger_id WHERE p.email = %s AND p.password = %s', (email, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user:
        return jsonify({'success': True, 'user': dict(user)})
    else:
        return jsonify({'success': False, 'error': 'Invalid email or password'}), 401

@app.route('/api/passengers', methods=['GET'])
def get_passengers():
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT p.*, w.balance FROM passengers p LEFT JOIN wallets w ON p.id = w.passenger_id')
    passengers = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(passengers)

@app.route('/api/buses', methods=['GET'])
def get_buses():
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM buses')
    buses = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(buses)

@app.route('/api/scan', methods=['POST'])
def scan_passenger():
    data = request.json
    scan_type = data.get('scan_type')
    scan_value = data.get('scan_value')
    bus_id = data.get('bus_id')
    
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    if scan_type == 'qr':
        cursor.execute('SELECT * FROM passengers WHERE qr_code = %s', (scan_value,))
    else:
        cursor.execute('SELECT * FROM passengers WHERE face_id = %s', (scan_value,))
    
    passenger = cursor.fetchone()
    
    if not passenger:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Passenger not found'}), 404
    
    passenger_id = passenger['id']
    
    cursor.execute('''
        SELECT * FROM scan_logs 
        WHERE passenger_id = %s AND bus_id = %s 
        AND scan_time > DATE_SUB(NOW(), INTERVAL 2 HOUR)
    ''', (passenger_id, bus_id))
    
    if cursor.fetchone():
        cursor.close()
        conn.close()
        return jsonify({'error': 'Duplicate scan detected. You already boarded this bus recently.'}), 400
    
    cursor.execute('SELECT * FROM buses WHERE id = %s', (bus_id,))
    bus = cursor.fetchone()
    
    if not bus:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Bus not found'}), 404
    
    fare_amount = float(bus['fare_per_km']) * float(bus['total_distance'])
    
    cursor.execute('SELECT balance FROM wallets WHERE passenger_id = %s', (passenger_id,))
    wallet = cursor.fetchone()
    
    if not wallet or float(wallet['balance']) < fare_amount:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Insufficient wallet balance'}), 400
    
    new_balance = float(wallet['balance']) - fare_amount
    cursor.execute('UPDATE wallets SET balance = %s WHERE passenger_id = %s', (new_balance, passenger_id))
    
    ticket_number = 'TKT' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    cursor.execute('''
        INSERT INTO tickets (ticket_number, passenger_id, bus_id, passenger_name, bus_number, route_name, fare_amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (ticket_number, passenger_id, bus_id, passenger['name'], bus['bus_number'], bus['route_name'], fare_amount))
    
    cursor.execute('INSERT INTO scan_logs (passenger_id, bus_id) VALUES (%s, %s)', (passenger_id, bus_id))
    cursor.execute('UPDATE buses SET current_passengers = current_passengers + 1 WHERE id = %s', (bus_id,))
    
    conn.commit()
    
    cursor.execute('SELECT * FROM tickets WHERE ticket_number = %s', (ticket_number,))
    ticket = cursor.fetchone()
    ticket['new_balance'] = new_balance
    
    cursor.close()
    conn.close()
    return jsonify(ticket)

@app.route('/api/wallet/<int:passenger_id>', methods=['GET'])
def get_wallet(passenger_id):
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT p.name, p.email, w.balance FROM passengers p JOIN wallets w ON p.id = w.passenger_id WHERE p.id = %s', (passenger_id,))
    wallet = cursor.fetchone()
    
    if not wallet:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Wallet not found'}), 404
    
    cursor.execute('SELECT ticket_number, bus_number, route_name, fare_amount, boarding_time FROM tickets WHERE passenger_id = %s ORDER BY boarding_time DESC LIMIT 10', (passenger_id,))
    transactions = cursor.fetchall()
    
    wallet['transactions'] = transactions
    
    cursor.close()
    conn.close()
    return jsonify(wallet)

@app.route('/api/wallet/recharge', methods=['POST'])
def recharge_wallet():
    data = request.json
    passenger_id = data.get('passenger_id')
    amount = data.get('amount')
    
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('UPDATE wallets SET balance = balance + %s WHERE passenger_id = %s', (amount, passenger_id))
    cursor.execute('SELECT balance FROM wallets WHERE passenger_id = %s', (passenger_id,))
    new_balance = cursor.fetchone()['balance']
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({'success': True, 'new_balance': float(new_balance)})

@app.route('/api/tickets/<int:passenger_id>', methods=['GET'])
def get_passenger_tickets(passenger_id):
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM tickets WHERE passenger_id = %s ORDER BY boarding_time DESC', (passenger_id,))
    tickets = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(tickets)

@app.route('/api/admin/dashboard', methods=['GET'])
def admin_dashboard():
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT COUNT(*) as total FROM passengers')
    total_passengers = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM tickets WHERE DATE(boarding_time) = CURDATE()")
    tickets_today = cursor.fetchone()['total']
    
    cursor.execute("SELECT COALESCE(SUM(fare_amount), 0) as total FROM tickets WHERE DATE(boarding_time) = CURDATE()")
    revenue_today = float(cursor.fetchone()['total'])
    
    cursor.execute('SELECT COALESCE(SUM(current_passengers), 0) as total FROM buses')
    current_passengers = cursor.fetchone()['total']
    
    cursor.execute('SELECT * FROM tickets ORDER BY boarding_time DESC LIMIT 10')
    recent_tickets = cursor.fetchall()
    
    cursor.execute('''
        SELECT b.bus_number, b.route_name, b.current_passengers, 
               COUNT(t.id) as total_trips, COALESCE(SUM(t.fare_amount), 0) as revenue
        FROM buses b
        LEFT JOIN tickets t ON b.id = t.bus_id AND DATE(t.boarding_time) = CURDATE()
        GROUP BY b.id
    ''')
    bus_stats = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify({
        'total_passengers': total_passengers,
        'tickets_today': tickets_today,
        'revenue_today': revenue_today,
        'current_passengers': current_passengers,
        'recent_tickets': recent_tickets,
        'bus_stats': bus_stats
    })

if __name__ == '__main__':
    print('\n' + '='*60)
    print('   SMART BUS TICKET SYSTEM - BACKEND SERVER')
    print('='*60)
    print('\n✓ Server starting...')
    print('✓ Database: MySQL (bus_ticket_system)')
    print('✓ Server URL: http://localhost:5000')
    print('✓ API Endpoints: http://localhost:5000/api/')
    print('\n   Login Credentials:')
    print('   - john@example.com / password123')
    print('   - jane@example.com / password123')
    print('   - mike@example.com / password123')
    print('   - sarah@example.com / password123')
    print('\n' + '='*60)
    print('   KEEP THIS WINDOW OPEN!')
    print('='*60 + '\n')
    
    app.run(debug=True, port=5000)

