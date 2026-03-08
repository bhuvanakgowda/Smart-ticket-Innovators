from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import sqlite3
import random
import string
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# Get the frontend folder path
FRONTEND_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend')

@app.route('/')
def home():
    return send_from_directory(FRONTEND_PATH, 'index.html')

@app.route('/login')
def login_page():
    return send_from_directory(FRONTEND_PATH, 'login.html')

@app.route('/scan')
def scan_page():
    return send_from_directory(FRONTEND_PATH, 'scan.html')

@app.route('/wallet')
def wallet_page():
    return send_from_directory(FRONTEND_PATH, 'wallet.html')

@app.route('/ticket')
def ticket_page():
    return send_from_directory(FRONTEND_PATH, 'ticket.html')

@app.route('/admin')
def admin_page():
    return send_from_directory(FRONTEND_PATH, 'admin.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(FRONTEND_PATH, filename)

DATABASE = 'bus_system.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Create passengers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS passengers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            face_id TEXT UNIQUE,
            qr_code TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add password column if it doesn't exist (for existing databases)
    try:
        cursor.execute('SELECT password FROM passengers LIMIT 1')
    except sqlite3.OperationalError:
        cursor.execute('ALTER TABLE passengers ADD COLUMN password TEXT NOT NULL DEFAULT "password123"')
        # Update existing records with default password
        cursor.execute('UPDATE passengers SET password = "password123" WHERE password IS NULL')
    
    # Add missing columns to existing tables
    try:
        cursor.execute('SELECT face_id FROM passengers LIMIT 1')
    except sqlite3.OperationalError:
        cursor.execute('ALTER TABLE passengers ADD COLUMN face_id TEXT UNIQUE')
    
    try:
        cursor.execute('SELECT qr_code FROM passengers LIMIT 1')
    except sqlite3.OperationalError:
        cursor.execute('ALTER TABLE passengers ADD COLUMN qr_code TEXT UNIQUE')
    
    # Add route_from and route_to to passengers
    try:
        cursor.execute('SELECT route_from FROM passengers LIMIT 1')
    except sqlite3.OperationalError:
        cursor.execute('ALTER TABLE passengers ADD COLUMN route_from TEXT NOT NULL DEFAULT "City Center"')
        cursor.execute('ALTER TABLE passengers ADD COLUMN route_to TEXT NOT NULL DEFAULT "Destination"')
        # Update existing passengers with default routes
        cursor.execute("UPDATE passengers SET route_from = 'City Center', route_to = 'Airport' WHERE id = 1")
        cursor.execute("UPDATE passengers SET route_from = 'City Center', route_to = 'Mall' WHERE id = 2")
        cursor.execute("UPDATE passengers SET route_from = 'University', route_to = 'Tech Park' WHERE id = 3")
        cursor.execute("UPDATE passengers SET route_from = 'Central Station', route_to = 'Airport' WHERE id = 4")
        
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wallets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            passenger_id INTEGER UNIQUE NOT NULL,
            balance REAL DEFAULT 0,
            FOREIGN KEY (passenger_id) REFERENCES passengers(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS buses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bus_number TEXT UNIQUE NOT NULL,
            route_name TEXT NOT NULL,
            route_from TEXT NOT NULL,
            route_to TEXT NOT NULL,
            fare_per_km REAL DEFAULT 2.0,
            total_distance REAL DEFAULT 10.0,
            current_passengers INTEGER DEFAULT 0
        )
    ''')
    
    # Add route_from and route_to columns if they don't exist
    try:
        cursor.execute('SELECT route_from FROM buses LIMIT 1')
    except sqlite3.OperationalError:
        cursor.execute('ALTER TABLE buses ADD COLUMN route_from TEXT NOT NULL DEFAULT "City Center"')
        cursor.execute('ALTER TABLE buses ADD COLUMN route_to TEXT NOT NULL DEFAULT "Destination"')
    
    # Update existing buses with route_from and route_to
    cursor.execute("UPDATE buses SET route_from = 'City Center', route_to = 'Airport' WHERE route_name = 'Downtown - Airport'")
    cursor.execute("UPDATE buses SET route_from = 'Central Station', route_to = 'Mall' WHERE route_name = 'Central Station - Mall'")
    cursor.execute("UPDATE buses SET route_from = 'University', route_to = 'Tech Park' WHERE route_name = 'University - Tech Park'")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_number TEXT UNIQUE NOT NULL,
            passenger_id INTEGER NOT NULL,
            bus_id INTEGER NOT NULL,
            passenger_name TEXT NOT NULL,
            bus_number TEXT NOT NULL,
            route_name TEXT NOT NULL,
            route_from TEXT NOT NULL,
            route_to TEXT NOT NULL,
            fare_amount REAL NOT NULL,
            boarding_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            FOREIGN KEY (passenger_id) REFERENCES passengers(id),
            FOREIGN KEY (bus_id) REFERENCES buses(id)
        )
    ''')
    
    # Add route_from and route_to columns to tickets if they don't exist
    try:
        cursor.execute('SELECT route_from FROM tickets LIMIT 1')
    except sqlite3.OperationalError:
        cursor.execute('ALTER TABLE tickets ADD COLUMN route_from TEXT NOT NULL DEFAULT "City Center"')
        cursor.execute('ALTER TABLE tickets ADD COLUMN route_to TEXT NOT NULL DEFAULT "Destination"')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            passenger_id INTEGER NOT NULL,
            bus_id INTEGER NOT NULL,
            scan_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (passenger_id) REFERENCES passengers(id),
            FOREIGN KEY (bus_id) REFERENCES buses(id)
        )
    ''')
    
    # Create login_logs table to track login history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            passenger_id INTEGER NOT NULL,
            email TEXT NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            FOREIGN KEY (passenger_id) REFERENCES passengers(id)
        )
    ''')
    
    cursor.execute("SELECT COUNT(*) as count FROM passengers")
    if cursor.fetchone()['count'] == 0:
        passengers = [
            ('John Doe', 'john@example.com', '1234567890', 'password123', 'FACE001', 'QR001'),
            ('Jane Smith', 'jane@example.com', '0987654321', 'password123', 'FACE002', 'QR002'),
            ('Mike Johnson', 'mike@example.com', '5551234567', 'password123', 'FACE003', 'QR003'),
            ('Sarah Williams', 'sarah@example.com', '5559876543', 'password123', 'FACE004', 'QR004'),
        ]
        cursor.executemany('INSERT INTO passengers (name, email, phone, password, face_id, qr_code) VALUES (?, ?, ?, ?, ?, ?)', passengers)
        
        for i in range(1, 5):
            cursor.execute('INSERT INTO wallets (passenger_id, balance) VALUES (?, ?)', (i, 500.0))
        
        buses = [
            ('BUS101', 'Downtown - Airport', 'City Center', 'Airport', 2.5, 15.0),
            ('BUS202', 'Central Station - Mall', 'Central Station', 'Mall', 2.0, 10.0),
            ('BUS303', 'University - Tech Park', 'University', 'Tech Park', 3.0, 20.0),
        ]
        cursor.executemany('INSERT INTO buses (bus_number, route_name, route_from, route_to, fare_per_km, total_distance) VALUES (?, ?, ?, ?, ?, ?)', buses)
    
    conn.commit()
    conn.close()
    print("✓ Database initialized successfully!")

init_db()

# ============ AUTHENTICATION ENDPOINTS ============

@app.route('/api/signup', methods=['POST'])
def signup():
    """Register a new user"""
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    name = data.get('name', email.split('@')[0])
    phone = data.get('phone', '0000000000')
    
    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password required'}), 400
    
    if len(password) < 6:
        return jsonify({'success': False, 'error': 'Password must be at least 6 characters'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if email already exists
    cursor.execute('SELECT id FROM passengers WHERE email = ?', (email,))
    existing = cursor.fetchone()
    
    if existing:
        conn.close()
        return jsonify({'success': False, 'error': 'Email already registered'}), 400
    
    try:
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Generate QR code and Face ID
        qr_code = 'QR' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        face_id = 'FACE' + ''.join(random.choices(string.digits, k=6))
        
        # Insert new user
        cursor.execute('''
            INSERT INTO passengers (name, email, phone, password, face_id, qr_code)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, phone, hashed_password, face_id, qr_code))
        
        passenger_id = cursor.lastrowid
        
        # Create wallet for new user
        cursor.execute('INSERT INTO wallets (passenger_id, balance) VALUES (?, ?)', (passenger_id, 500.0))
        
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully!',
            'user': {
                'id': passenger_id,
                'name': name,
                'email': email,
                'balance': 500.0
            }
        }), 201
    
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        conn.close()


@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'success': False, 'error': 'Email and password required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Find user by email
        cursor.execute('SELECT p.id, p.name, p.email, p.password, w.balance FROM passengers p LEFT JOIN wallets w ON p.id = w.passenger_id WHERE p.email = ?', (email,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
        
        # Verify password
        if not check_password_hash(user['password'], password):
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
        
        # Log the login
        cursor.execute('INSERT INTO login_logs (passenger_id, email) VALUES (?, ?)', (user['id'], email))
        conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Login successful!',
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'balance': user['balance'] or 0
            }
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
    finally:
        conn.close()


@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user profile"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, email, face_id, qr_code, created_at FROM passengers WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(dict(user))

# API endpoint to view login history
@app.route('/api/admin/login-history', methods=['GET'])
def get_login_history():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT l.id, l.email, l.login_time, l.ip_address, p.name, p.face_id, p.qr_code
        FROM login_logs l
        JOIN passengers p ON l.passenger_id = p.id
        ORDER BY l.login_time DESC
        LIMIT 50
    ''')
    login_history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(login_history)

@app.route('/api/passengers', methods=['GET'])
def get_passengers():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT p.id, p.name, p.email, p.phone, p.face_id, p.qr_code, p.route_from, p.route_to, p.created_at, w.balance FROM passengers p LEFT JOIN wallets w ON p.id = w.passenger_id')
    passengers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(passengers)

@app.route('/api/buses', methods=['GET'])
def get_buses():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM buses')
    buses = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(buses)

@app.route('/api/scan', methods=['POST'])
def scan_passenger():
    data = request.json
    scan_type = data.get('scan_type')
    scan_value = data.get('scan_value')
    bus_id = data.get('bus_id')
    
    conn = get_db()
    cursor = conn.cursor()
    
    if scan_type == 'qr':
        cursor.execute('SELECT * FROM passengers WHERE qr_code = ?', (scan_value,))
    else:
        cursor.execute('SELECT * FROM passengers WHERE face_id = ?', (scan_value,))
    
    passenger = cursor.fetchone()
    
    if not passenger:
        conn.close()
        return jsonify({'error': 'Passenger not found'}), 404
    
    passenger_id = passenger['id']
    
    cursor.execute('''
        SELECT * FROM scan_logs 
        WHERE passenger_id = ? AND bus_id = ? 
        AND scan_time > datetime('now', '-2 hours')
    ''', (passenger_id, bus_id))
    
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Duplicate scan detected. You already boarded this bus recently.'}), 400
    
    cursor.execute('SELECT * FROM buses WHERE id = ?', (bus_id,))
    bus = cursor.fetchone()
    
    if not bus:
        conn.close()
        return jsonify({'error': 'Bus not found'}), 404
    
    fare_amount = bus['fare_per_km'] * bus['total_distance']
    
    cursor.execute('SELECT balance FROM wallets WHERE passenger_id = ?', (passenger_id,))
    wallet = cursor.fetchone()
    
    if not wallet or wallet['balance'] < fare_amount:
        conn.close()
        return jsonify({'error': 'Insufficient wallet balance'}), 400
    
    new_balance = wallet['balance'] - fare_amount
    cursor.execute('UPDATE wallets SET balance = ? WHERE passenger_id = ?', (new_balance, passenger_id))
    
    ticket_number = 'TKT' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    cursor.execute('''
        INSERT INTO tickets (ticket_number, passenger_id, bus_id, passenger_name, bus_number, route_name, route_from, route_to, fare_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (ticket_number, passenger_id, bus_id, passenger['name'], bus['bus_number'], bus['route_name'], bus['route_from'], bus['route_to'], fare_amount))
    
    cursor.execute('INSERT INTO scan_logs (passenger_id, bus_id) VALUES (?, ?)', (passenger_id, bus_id))
    cursor.execute('UPDATE buses SET current_passengers = current_passengers + 1 WHERE id = ?', (bus_id,))
    
    conn.commit()
    
    cursor.execute('SELECT * FROM tickets WHERE ticket_number = ?', (ticket_number,))
    ticket = dict(cursor.fetchone())
    ticket['new_balance'] = new_balance
    
    conn.close()
    return jsonify(ticket)

# Face Recognition Scan Endpoint - Uses camera image
@app.route('/api/scan/face', methods=['POST'])
def scan_face_image():
    """Handle face recognition from camera image"""
    data = request.json
    image_data = data.get('image')  # Base64 encoded image
    bus_id = data.get('bus_id')
    
    if not image_data:
        return jsonify({'error': 'No image provided'}), 400
    
    if not bus_id:
        return jsonify({'error': 'Bus ID required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all passengers with face_id registered
    cursor.execute('SELECT * FROM passengers WHERE face_id IS NOT NULL')
    passengers = cursor.fetchall()
    
    if not passengers:
        conn.close()
        return jsonify({'error': 'No registered passengers found'}), 404
    
    # For demo purposes, we'll simulate face recognition
    # In production, you would use a proper face recognition library like face_recognition or OpenCV
    # Here we just randomly select a passenger (simulating successful recognition)
    # or you can match based on some simple criteria
    
    # Simulate: select first passenger as "recognized" for demo
    # In real implementation, you would:
    # 1. Decode the base64 image
    # 2. Use face_recognition library to get face encoding
    # 3. Compare with stored face encodings
    # 4. Return the matched passenger
    
    import base64
    import re
    
    # Check if image is valid (basic check)
    if not re.match(r'^data:image', image_data):
        conn.close()
        return jsonify({'error': 'Invalid image format'}), 400
    
    # For demo: use the first registered passenger
    # In production, implement actual face matching
    passenger = passengers[0]  # Simulate successful recognition
    passenger_id = passenger['id']
    
    # Check for duplicate scan
    cursor.execute('''
        SELECT * FROM scan_logs 
        WHERE passenger_id = ? AND bus_id = ? 
        AND scan_time > datetime('now', '-2 hours')
    ''', (passenger_id, bus_id))
    
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Duplicate scan detected. You already boarded this bus recently.'}), 400
    
    cursor.execute('SELECT * FROM buses WHERE id = ?', (bus_id,))
    bus = cursor.fetchone()
    
    if not bus:
        conn.close()
        return jsonify({'error': 'Bus not found'}), 404
    
    fare_amount = bus['fare_per_km'] * bus['total_distance']
    
    cursor.execute('SELECT balance FROM wallets WHERE passenger_id = ?', (passenger_id,))
    wallet = cursor.fetchone()
    
    if not wallet or wallet['balance'] < fare_amount:
        conn.close()
        return jsonify({'error': 'Insufficient wallet balance'}), 400
    
    new_balance = wallet['balance'] - fare_amount
    cursor.execute('UPDATE wallets SET balance = ? WHERE passenger_id = ?', (new_balance, passenger_id))
    
    ticket_number = 'TKT' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    cursor.execute('''
        INSERT INTO tickets (ticket_number, passenger_id, bus_id, passenger_name, bus_number, route_name, route_from, route_to, fare_amount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (ticket_number, passenger_id, bus_id, passenger['name'], bus['bus_number'], bus['route_name'], bus['route_from'], bus['route_to'], fare_amount))
    
    cursor.execute('INSERT INTO scan_logs (passenger_id, bus_id) VALUES (?, ?)', (passenger_id, bus_id))
    cursor.execute('UPDATE buses SET current_passengers = current_passengers + 1 WHERE id = ?', (bus_id,))
    
    conn.commit()
    
    cursor.execute('SELECT * FROM tickets WHERE ticket_number = ?', (ticket_number,))
    ticket = dict(cursor.fetchone())
    ticket['new_balance'] = new_balance
    ticket['face_recognized'] = True
    
    conn.close()
    return jsonify(ticket)

@app.route('/api/wallet/<int:passenger_id>', methods=['GET'])
def get_wallet(passenger_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT p.name, p.email, w.balance FROM passengers p JOIN wallets w ON p.id = w.passenger_id WHERE p.id = ?', (passenger_id,))
    wallet = cursor.fetchone()
    
    if not wallet:
        conn.close()
        return jsonify({'error': 'Wallet not found'}), 404
    
    cursor.execute('SELECT ticket_number, bus_number, route_name, fare_amount, boarding_time FROM tickets WHERE passenger_id = ? ORDER BY boarding_time DESC LIMIT 10', (passenger_id,))
    transactions = [dict(row) for row in cursor.fetchall()]
    
    result = dict(wallet)
    result['transactions'] = transactions
    
    conn.close()
    return jsonify(result)

@app.route('/api/wallet/recharge', methods=['POST'])
def recharge_wallet():
    data = request.json
    passenger_id = data.get('passenger_id')
    amount = data.get('amount')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE wallets SET balance = balance + ? WHERE passenger_id = ?', (amount, passenger_id))
    cursor.execute('SELECT balance FROM wallets WHERE passenger_id = ?', (passenger_id,))
    new_balance = cursor.fetchone()['balance']
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'new_balance': new_balance})

@app.route('/api/tickets/<int:passenger_id>', methods=['GET'])
def get_passenger_tickets(passenger_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tickets WHERE passenger_id = ? ORDER BY boarding_time DESC', (passenger_id,))
    tickets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(tickets)

@app.route('/api/admin/dashboard', methods=['GET'])
def admin_dashboard():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total FROM passengers')
    total_passengers = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as total FROM tickets WHERE DATE(boarding_time) = DATE('now')")
    tickets_today = cursor.fetchone()['total']
    
    cursor.execute("SELECT COALESCE(SUM(fare_amount), 0) as total FROM tickets WHERE DATE(boarding_time) = DATE('now')")
    revenue_today = cursor.fetchone()['total']
    
    cursor.execute('SELECT COALESCE(SUM(current_passengers), 0) as total FROM buses')
    current_passengers = cursor.fetchone()['total']
    
    cursor.execute('SELECT * FROM tickets ORDER BY boarding_time DESC LIMIT 10')
    recent_tickets = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute('''
        SELECT b.bus_number, b.route_name, b.current_passengers, 
               COUNT(t.id) as total_trips, COALESCE(SUM(t.fare_amount), 0) as revenue
        FROM buses b
        LEFT JOIN tickets t ON b.id = t.bus_id AND DATE(t.boarding_time) = DATE('now')
        GROUP BY b.id
    ''')
    bus_stats = [dict(row) for row in cursor.fetchall()]
    
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
    print('✓ Database: SQLite (bus_system.db)')
    print('✓ Server URL: http://localhost:8080')
    print('✓ API Endpoints: http://localhost:8080/api/')
    print('\n' + '='*60)
    print('   KEEP THIS WINDOW OPEN!')
    print('='*60 + '\n')
    
    app.run(debug=True, port=8080, host='0.0.0.0')
