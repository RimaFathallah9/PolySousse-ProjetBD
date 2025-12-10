from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from db import get_db, init_app
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'supersecretkey'  

# Initialize DB
init_app(app)

# --- Authentication Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    if user_data:
        return User(user_data['id'], user_data['username'], user_data['role'])
    return None

# --- Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        cursor.close()
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            user = User(user_data['id'], user_data['username'], user_data['role'])
            login_user(user)
            flash('Logged in successfully.', 'success')
            if user.role == 'admin':
                return redirect(url_for('index'))
            else:
                return redirect(url_for('events'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    if current_user.role != 'admin':
        return redirect(url_for('events'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Cleanup Soft Deleted Members (> 24 hours)
    cleanup_time = datetime.now() - timedelta(hours=24)
    cursor.execute("DELETE FROM members WHERE deleted_at IS NOT NULL AND deleted_at < %s", (cleanup_time,))
    db.commit()

    # Statistics
    cursor.execute("SELECT COUNT(*) as count FROM members WHERE deleted_at IS NULL")
    member_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM events")
    event_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT SUM(amount) as total FROM payments")
    total_revenue = cursor.fetchone()['total'] or 0
    
    cursor.close()
    return render_template('index.html', member_count=member_count, event_count=event_count, total_revenue=total_revenue)

# --- Members ---
@app.route('/members', methods=['GET', 'POST'])
@login_required
def members():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('events'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        class_name = request.form['class_name']
        
        try:
            cursor.execute("INSERT INTO members (full_name, email, class_name) VALUES (%s, %s, %s)", 
                           (full_name, email, class_name))
            db.commit()
            flash('Member added successfully!', 'success')
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        
        return redirect(url_for('members'))
    
    # Show only active members
    cursor.execute("SELECT * FROM members WHERE deleted_at IS NULL ORDER BY created_at DESC")
    members = cursor.fetchall()
    cursor.close()
    return render_template('members.html', members=members)

@app.route('/members/delete/<int:id>')
@login_required
def delete_member(id):
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('events'))

    db = get_db()
    cursor = db.cursor()
    # Soft Delete
    now = datetime.now()
    cursor.execute("UPDATE members SET deleted_at = %s WHERE id_member = %s", (now, id))
    db.commit()
    cursor.close()
    flash('Member archived. Will be permanently deleted in 24 hours.', 'warning')
    return redirect(url_for('members'))

# --- Events ---
@app.route('/events', methods=['GET', 'POST'])
@login_required
def events():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        if current_user.role != 'admin':
            flash('Access denied.', 'danger')
            return redirect(url_for('events'))

        title = request.form['title']
        description = request.form['description']
        date_event = request.form['date_event']
        price = request.form['price']
        
        try:
            cursor.execute("INSERT INTO events (title, description, date_event, price) VALUES (%s, %s, %s, %s)", 
                           (title, description, date_event, price))
            db.commit()
            flash('Event created!', 'success')
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
            
        return redirect(url_for('events'))

    # Members see only upcoming events? User said "only see upcoming event and price"
    # Admin sees all? Or also upcoming? Usually Admin sees all.
    # User said: "those who are only members ... they can only see upcoming event and price"
    
    if current_user.role == 'member':
        now = datetime.now()
        cursor.execute("SELECT title, price, date_event, description FROM events WHERE date_event >= %s ORDER BY date_event ASC", (now,))
    else:
        cursor.execute("SELECT * FROM events ORDER BY date_event DESC")
        
    events = cursor.fetchall()
    cursor.close()
    return render_template('events.html', events=events)

# --- Attendance ---
@app.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('events'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        id_member = request.form['id_member']
        id_event = request.form['id_event']
        status = request.form['status']
        
        try:
            cursor.execute("INSERT INTO attendance (id_member, id_event, status) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE status=%s", 
                           (id_member, id_event, status, status))
            db.commit()
            flash('Attendance recorded.', 'success')
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        return redirect(url_for('attendance'))

    # Get lists for dropdowns
    cursor.execute("SELECT * FROM members WHERE deleted_at IS NULL")
    members = cursor.fetchall()
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()
    
    # Get recent attendance
    cursor.execute("""
        SELECT a.*, m.full_name, e.title as event_title 
        FROM attendance a 
        JOIN members m ON a.id_member = m.id_member 
        JOIN events e ON a.id_event = e.id_event 
        ORDER BY a.recorded_at DESC LIMIT 20
    """)
    attendance_records = cursor.fetchall()
    
    cursor.close()
    return render_template('attendance.html', members=members, events=events, attendance_records=attendance_records)

# --- Payments ---
@app.route('/payments', methods=['GET', 'POST'])
@login_required
def payments():
    if current_user.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('events'))

    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
        id_member = request.form['id_member']
        id_event = request.form['id_event']
        amount = request.form['amount']
        payment_method = request.form['payment_method']
        
        try:
            cursor.execute("INSERT INTO payments (id_member, id_event, amount, payment_method) VALUES (%s, %s, %s, %s)", 
                           (id_member, id_event, amount, payment_method))
            db.commit()
            flash('Payment recorded.', 'success')
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        return redirect(url_for('payments'))

    # Get lists for dropdowns
    cursor.execute("SELECT * FROM members WHERE deleted_at IS NULL")
    members = cursor.fetchall()
    cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()
    
    # Get recent payments
    cursor.execute("""
        SELECT p.*, m.full_name, e.title as event_title 
        FROM payments p 
        JOIN members m ON p.id_member = m.id_member 
        JOIN events e ON p.id_event = e.id_event 
        ORDER BY p.date_payment DESC LIMIT 20
    """)
    payments = cursor.fetchall()
    
    cursor.close()
    return render_template('payments.html', members=members, events=events, payments=payments)

if __name__ == '__main__':
    app.run(debug=True)
