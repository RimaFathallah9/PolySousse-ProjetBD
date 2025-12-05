from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from db import get_db, init_app

app = Flask(__name__)
app.secret_key = 'supersecretkey'  

# Initialize DB
init_app(app)

# --- Routes ---

@app.route('/')
def index():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Statistics
    cursor.execute("SELECT COUNT(*) as count FROM members")
    member_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM events")
    event_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT SUM(amount) as total FROM payments")
    total_revenue = cursor.fetchone()['total'] or 0
    
    cursor.close()
    return render_template('index.html', member_count=member_count, event_count=event_count, total_revenue=total_revenue)

# --- Members ---
@app.route('/members', methods=['GET', 'POST'])
def members():
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
    
    cursor.execute("SELECT * FROM members ORDER BY created_at DESC")
    members = cursor.fetchall()
    cursor.close()
    return render_template('members.html', members=members)

@app.route('/members/delete/<int:id>')
def delete_member(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM members WHERE id_member = %s", (id,))
    db.commit()
    cursor.close()
    flash('Member deleted.', 'warning')
    return redirect(url_for('members'))

# --- Events ---
@app.route('/events', methods=['GET', 'POST'])
def events():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    if request.method == 'POST':
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

    cursor.execute("SELECT * FROM events ORDER BY date_event DESC")
    events = cursor.fetchall()
    cursor.close()
    return render_template('events.html', events=events)

# --- Attendance ---
@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
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
    cursor.execute("SELECT * FROM members")
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
def payments():
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
    cursor.execute("SELECT * FROM members")
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
