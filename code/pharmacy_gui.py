from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret_key_for_flash_messages"
DB_NAME = "pharmacy.db"
ALERT_THRESHOLD = 50

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Inventory Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            batch_no TEXT NOT NULL, 
            qty INTEGER NOT NULL,
            price REAL NOT NULL,
            expiry_date TEXT NOT NULL
        )
    ''')
    
    # History Log Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expiry_history (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            check_date TEXT NOT NULL,
            name TEXT NOT NULL,
            batch_no TEXT NOT NULL,
            expiry_date TEXT NOT NULL,
            days_left INTEGER NOT NULL,
            status TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# --- HOMEPAGE (VIEW & SEARCH) ---
@app.route('/')
def index():
    search_query = request.args.get('search', '').strip().upper()
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    if search_query:
        # Search Logic
        cursor.execute("SELECT * FROM medicines WHERE name LIKE ? OR batch_no LIKE ? ORDER BY expiry_date ASC", 
                       ('%' + search_query + '%', '%' + search_query + '%'))
    else:
        # Show All
        cursor.execute("SELECT * FROM medicines ORDER BY expiry_date ASC")
        
    data = cursor.fetchall()
    conn.close()
    
    # Calculate Days Left for display
    processed_data = []
    today = datetime.now()
    
    for row in data:
        db_id, name, batch, qty, price, exp_str = row
        try:
            exp_date = datetime.strptime(exp_str, "%Y-%m-%d")
            days_left = (exp_date - today).days
            
            # Determine Status Class for CSS
            if days_left < 0: status_class = "expired"
            elif days_left <= ALERT_THRESHOLD: status_class = "warning"
            else: status_class = "safe"
            
            processed_data.append({
                "id": db_id, "name": name, "batch": batch, "qty": qty, 
                "price": price, "expiry": exp_str, "days": days_left, "class": status_class
            })
        except ValueError:
            continue

    return render_template('index.html', medicines=processed_data)

# --- ADD MEDICINE ---
@app.route('/add', methods=['POST'])
def add_medicine():
    name = request.form['name'].strip().upper()
    batch = request.form['batch'].strip().upper()
    qty = request.form['qty']
    price = request.form['price']
    expiry = request.form['expiry']

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Duplicate Check
    cursor.execute("SELECT * FROM medicines WHERE name = ? AND batch_no = ?", (name, batch))
    if cursor.fetchone():
        flash(f"Error: {name} with Batch {batch} already exists!", "error")
    else:
        cursor.execute("INSERT INTO medicines (name, batch_no, qty, price, expiry_date) VALUES (?, ?, ?, ?, ?)",
                       (name, batch, qty, price, expiry))
        conn.commit()
        flash(f"Success: Added {name} (Batch {batch})", "success")
        
    conn.close()
    return redirect(url_for('index'))

# --- EVALUATE & LOG ---
@app.route('/evaluate')
def evaluate():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, batch_no, expiry_date FROM medicines")
    inventory = cursor.fetchall()
    
    today = datetime.now()
    check_date_str = today.strftime("%Y-%m-%d %H:%M:%S")
    today_date_only = today.strftime("%Y-%m-%d")
    
    saved_count = 0
    
    for name, batch, exp_str in inventory:
        exp_date = datetime.strptime(exp_str, "%Y-%m-%d")
        days_left = (exp_date - today).days
        
        status = ""
        if days_left < 0: status = "EXPIRED"
        elif days_left <= ALERT_THRESHOLD: status = "CRITICAL"
        
        if status:
            # Check if logged today
            cursor.execute("SELECT report_id FROM expiry_history WHERE name = ? AND batch_no = ? AND check_date LIKE ?", 
                           (name, batch, today_date_only + '%'))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO expiry_history (check_date, name, batch_no, expiry_date, days_left, status) VALUES (?, ?, ?, ?, ?, ?)",
                               (check_date_str, name, batch, exp_str, days_left, status))
                saved_count += 1
                
    conn.commit()
    conn.close()
    
    if saved_count > 0:
        flash(f"Evaluation Complete: Saved {saved_count} new risks to History Log.", "warning")
    else:
        flash("Evaluation Complete: No new risks found.", "success")
        
    return redirect(url_for('index'))

# --- DELETE EXPIRED ---
@app.route('/delete_expired')
def delete_expired():
    today_str = datetime.now().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM medicines WHERE expiry_date < ?", (today_str,))
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    if deleted_count > 0:
        flash(f"Deleted {deleted_count} expired medicines.", "error")
    else:
        flash("No expired medicines found.", "success")
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)