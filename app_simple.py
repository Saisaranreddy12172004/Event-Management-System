from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'campus-event-management-2024'

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect('campus_events.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    # Create tables
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'STUDENT',
            student_id TEXT,
            department TEXT,
            year INTEGER,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS event_categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            event_type TEXT NOT NULL,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL,
            location TEXT NOT NULL,
            capacity INTEGER NOT NULL,
            status TEXT DEFAULT 'UPCOMING',
            requirements TEXT,
            creator_id INTEGER NOT NULL,
            category_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES users (id),
            FOREIGN KEY (category_id) REFERENCES event_categories (id)
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            event_id INTEGER NOT NULL,
            status TEXT DEFAULT 'CONFIRMED',
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (event_id) REFERENCES events (id)
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS check_ins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            event_id INTEGER NOT NULL,
            check_in_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            location TEXT,
            method TEXT DEFAULT 'MANUAL',
            metadata TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (event_id) REFERENCES events (id)
        )
    ''')
    
    # Insert sample data
    if conn.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 0:
        # Create categories
        categories = [
            ('Technology', 'Tech-related events'),
            ('Sports', 'Sports and fitness events'),
            ('Cultural', 'Cultural and arts events'),
            ('Academic', 'Academic and educational events'),
            ('Social', 'Social and networking events')
        ]
        conn.executemany('INSERT INTO event_categories (name, description) VALUES (?, ?)', categories)
        
        # Create users
        users = [
            ('Admin User', 'admin@campus.edu', hashlib.sha256('admin123'.encode()).hexdigest(), 'ADMIN'),
            ('Staff User', 'staff@campus.edu', hashlib.sha256('staff123'.encode()).hexdigest(), 'STAFF'),
            ('John Doe', 'student1@campus.edu', hashlib.sha256('student123'.encode()).hexdigest(), 'STUDENT'),
            ('Jane Smith', 'student2@campus.edu', hashlib.sha256('student123'.encode()).hexdigest(), 'STUDENT')
        ]
        conn.executemany('INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)', users)
        
        # Update student details
        conn.execute('UPDATE users SET student_id = ?, department = ?, year = ? WHERE email = ?', 
                    ('STU001', 'Computer Science', 3, 'student1@campus.edu'))
        conn.execute('UPDATE users SET student_id = ?, department = ?, year = ? WHERE email = ?', 
                    ('STU002', 'Engineering', 2, 'student2@campus.edu'))
        
        # Create sample events
        tech_category_id = conn.execute('SELECT id FROM event_categories WHERE name = ?', ('Technology',)).fetchone()[0]
        events = [
            ('Hackathon 2024', 'Annual coding competition with prizes', 'HACKATHON', 
             datetime.now() + timedelta(days=7), datetime.now() + timedelta(days=8), 
             'Main Campus - Computer Lab', 50, 'UPCOMING', None, 1, tech_category_id),
            ('Python Workshop', 'Learn Python programming basics', 'WORKSHOP',
             datetime.now() + timedelta(days=3), datetime.now() + timedelta(days=3, hours=3),
             'Library - Room 101', 30, 'UPCOMING', None, 2, tech_category_id),
            ('Tech Talk: AI & Machine Learning', 'Guest speaker on AI trends', 'TECH_TALK',
             datetime.now() + timedelta(days=5), datetime.now() + timedelta(days=5, hours=2),
             'Auditorium', 100, 'UPCOMING', None, 1, tech_category_id)
        ]
        conn.executemany('''INSERT INTO events (title, description, event_type, start_date, end_date, 
                         location, capacity, status, requirements, creator_id, category_id) 
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', events)
    
    conn.commit()
    conn.close()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    if user and user['password'] == hashlib.sha256(password.encode()).hexdigest():
        session['user_id'] = user['id']
        session['user_role'] = user['role']
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'role': user['role'],
                'student_id': user['student_id'],
                'department': user['department'],
                'year': user['year']
            }
        })
    else:
        return jsonify({'success': False, 'error': 'Invalid credentials'})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/events')
def get_events():
    conn = get_db_connection()
    events = conn.execute('''
        SELECT e.*, u.name as creator_name, ec.name as category_name,
               COUNT(r.id) as registrations_count
        FROM events e
        LEFT JOIN users u ON e.creator_id = u.id
        LEFT JOIN event_categories ec ON e.category_id = ec.id
        LEFT JOIN registrations r ON e.id = r.event_id AND r.status = 'CONFIRMED'
        GROUP BY e.id
        ORDER BY e.start_date
    ''').fetchall()
    conn.close()
    
    events_data = []
    for event in events:
        events_data.append({
            'id': event['id'],
            'title': event['title'],
            'description': event['description'],
            'event_type': event['event_type'],
            'start_date': event['start_date'],
            'end_date': event['end_date'],
            'location': event['location'],
            'capacity': event['capacity'],
            'status': event['status'],
            'requirements': event['requirements'],
            'creator': event['creator_name'],
            'category': event['category_name'],
            'registrations_count': event['registrations_count']
        })
    
    return jsonify({'events': events_data})

@app.route('/api/registrations/<int:event_id>', methods=['POST'])
def register_for_event(event_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    conn = get_db_connection()
    
    # Check if already registered
    existing = conn.execute('SELECT id FROM registrations WHERE user_id = ? AND event_id = ?', 
                          (session['user_id'], event_id)).fetchone()
    if existing:
        conn.close()
        return jsonify({'success': False, 'error': 'Already registered'})
    
    # Check event capacity
    event = conn.execute('SELECT capacity FROM events WHERE id = ?', (event_id,)).fetchone()
    if not event:
        conn.close()
        return jsonify({'success': False, 'error': 'Event not found'})
    
    current_registrations = conn.execute('SELECT COUNT(*) FROM registrations WHERE event_id = ? AND status = "CONFIRMED"', 
                                       (event_id,)).fetchone()[0]
    
    if current_registrations >= event['capacity']:
        conn.close()
        return jsonify({'success': False, 'error': 'Event is full'})
    
    # Register user
    conn.execute('INSERT INTO registrations (user_id, event_id, status) VALUES (?, ?, ?)', 
                (session['user_id'], event_id, 'CONFIRMED'))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Successfully registered'})

@app.route('/api/registrations/<int:event_id>', methods=['DELETE'])
def cancel_registration(event_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    conn = get_db_connection()
    conn.execute('DELETE FROM registrations WHERE user_id = ? AND event_id = ?', 
                (session['user_id'], event_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Registration cancelled'})

@app.route('/api/my-registrations')
def get_my_registrations():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    conn = get_db_connection()
    registrations = conn.execute('''
        SELECT r.*, e.title, e.description, e.start_date, e.end_date, 
               e.location, e.event_type, e.status as event_status
        FROM registrations r
        JOIN events e ON r.event_id = e.id
        WHERE r.user_id = ?
        ORDER BY r.registered_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    registrations_data = []
    for reg in registrations:
        registrations_data.append({
            'id': reg['id'],
            'status': reg['status'],
            'registered_at': reg['registered_at'],
            'event': {
                'id': reg['event_id'],
                'title': reg['title'],
                'description': reg['description'],
                'start_date': reg['start_date'],
                'end_date': reg['end_date'],
                'location': reg['location'],
                'event_type': reg['event_type'],
                'status': reg['event_status']
            }
        })
    
    return jsonify({'registrations': registrations_data})

@app.route('/api/analytics')
def get_analytics():
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    if session['user_role'] not in ['ADMIN', 'STAFF']:
        return jsonify({'success': False, 'error': 'Insufficient permissions'})
    
    conn = get_db_connection()
    
    # Event statistics
    total_events = conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]
    upcoming_events = conn.execute('SELECT COUNT(*) FROM events WHERE status = "UPCOMING"').fetchone()[0]
    ongoing_events = conn.execute('SELECT COUNT(*) FROM events WHERE status = "ONGOING"').fetchone()[0]
    completed_events = conn.execute('SELECT COUNT(*) FROM events WHERE status = "COMPLETED"').fetchone()[0]
    
    # Registration statistics
    total_registrations = conn.execute('SELECT COUNT(*) FROM registrations').fetchone()[0]
    confirmed_registrations = conn.execute('SELECT COUNT(*) FROM registrations WHERE status = "CONFIRMED"').fetchone()[0]
    
    # User statistics
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    student_users = conn.execute('SELECT COUNT(*) FROM users WHERE role = "STUDENT"').fetchone()[0]
    staff_users = conn.execute('SELECT COUNT(*) FROM users WHERE role = "STAFF"').fetchone()[0]
    
    # Popular events
    popular_events = conn.execute('''
        SELECT e.title, COUNT(r.id) as registration_count
        FROM events e
        LEFT JOIN registrations r ON e.id = r.event_id AND r.status = 'CONFIRMED'
        GROUP BY e.id, e.title
        ORDER BY registration_count DESC
        LIMIT 5
    ''').fetchall()
    
    conn.close()
    
    analytics_data = {
        'events': {
            'total': total_events,
            'upcoming': upcoming_events,
            'ongoing': ongoing_events,
            'completed': completed_events
        },
        'registrations': {
            'total': total_registrations,
            'confirmed': confirmed_registrations
        },
        'users': {
            'total': total_users,
            'students': student_users,
            'staff': staff_users
        },
        'popular_events': [
            {'title': event['title'], 'registrations': event['registration_count']} 
            for event in popular_events
        ]
    }
    
    return jsonify(analytics_data)

@app.route('/api/checkin/<int:event_id>', methods=['POST'])
def check_in(event_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not authenticated'})
    
    conn = get_db_connection()
    
    # Check if user is registered
    registration = conn.execute('SELECT id FROM registrations WHERE user_id = ? AND event_id = ?', 
                              (session['user_id'], event_id)).fetchone()
    if not registration:
        conn.close()
        return jsonify({'success': False, 'error': 'Not registered for this event'})
    
    # Check if already checked in
    existing_checkin = conn.execute('SELECT id FROM check_ins WHERE user_id = ? AND event_id = ?', 
                                  (session['user_id'], event_id)).fetchone()
    if existing_checkin:
        conn.close()
        return jsonify({'success': False, 'error': 'Already checked in'})
    
    data = request.get_json()
    
    # Check in user
    conn.execute('INSERT INTO check_ins (user_id, event_id, location, method) VALUES (?, ?, ?, ?)', 
                (session['user_id'], event_id, data.get('location', ''), data.get('method', 'MANUAL')))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Successfully checked in'})

if __name__ == '__main__':
    init_db()
    print("Database initialized with sample data!")
    print("Starting Campus Event Management System...")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
