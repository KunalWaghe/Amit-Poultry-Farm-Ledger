import sqlite3
import webview  # <-- ADD THIS IMPORT
from flask import Flask, render_template, request, redirect, url_for, g, flash
from datetime import date, timedelta
from threading import Thread # <-- ADD THIS IMPORT

# --- ALL YOUR EXISTING FLASK CODE REMAINS EXACTLY THE SAME ---
# (Initialize app, database functions, all the routes, etc.)

app = Flask(__name__)
app.secret_key = 'your_super_secret_key_change_this_later'

DATABASE = 'poultry.db'

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        # This is key! It makes database rows accessible like dictionaries.
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()

# --- STATIC DATA ---
lines = ["Pati", "Amjhera+Gandhwani", "Anjad", "Dahi", "Local"]
bird_types = ["Minar", "Broiler", "Parent"]
# New list of drivers
drivers = ["Deepu", "Firoj", "Ritesh", "Akram", "Kanha", "Rahul", "Other"]


# --- CORE ROUTES ---

@app.route('/')
def home():
    """Renders the homepage."""
    return render_template('home.html', lines=lines)

@app.route('/line/<line_name>')
def view_line(line_name):
    """Displays all traders for a specific line."""
    db = get_db()
    traders_in_line = db.execute('SELECT * FROM traders WHERE line = ? ORDER BY name', (line_name,)).fetchall()
    return render_template('line_traders.html', line_name=line_name, traders_in_line=traders_in_line)

@app.route('/trader/<int:trader_id>')
def view_trader(trader_id):
    """Displays the ledger for an individual trader."""
    db = get_db()
    selected_trader = db.execute('SELECT * FROM traders WHERE id = ?', (trader_id,)).fetchone()
    if not selected_trader:
        flash(f"Trader with ID {trader_id} not found.", 'error')
        return redirect(url_for('home'))
    
    today_str = date.today().isoformat()
    rates_from_db = db.execute('SELECT bird_type, rate FROM daily_rates WHERE date = ? AND line = ?', (today_str, selected_trader['line'])).fetchall()
    current_rates = {r['bird_type']: r['rate'] for r in rates_from_db}
    
    trader_transactions = db.execute('SELECT * FROM transactions WHERE trader_id = ? ORDER BY date DESC, id DESC', (trader_id,)).fetchall()
    # Pass the list of drivers to the template
    return render_template('trader_ledger.html', trader=selected_trader, transactions=trader_transactions, rates=current_rates, drivers=drivers)

# --- TRANSACTION ROUTES ---

@app.route('/trader/<int:trader_id>/add_bill', methods=['POST'])
def add_bill(trader_id):
    """Processes and saves a new bill for a trader, now including the driver's name."""
    db = get_db()
    today_str = date.today().isoformat()
    
    quantities = {'Minar': float(request.form.get('minar_qty') or 0), 'Broiler': float(request.form.get('broiler_qty') or 0), 'Parent': float(request.form.get('parent_qty') or 0)}
    rates_from_form = {'Minar': float(request.form.get('minar_rate') or 0), 'Broiler': float(request.form.get('broiler_rate') or 0), 'Parent': float(request.form.get('parent_rate') or 0)}
    # Get the driver's name from the form
    driver_name = request.form.get('driver_name')
    
    total_bill, bill_details = 0, []
    for bird, qty in quantities.items():
        if qty > 0:
            rate = rates_from_form.get(bird)
            if not rate:
                flash(f"Error: Rate for {bird} was not provided.", 'error')
                return redirect(url_for('view_trader', trader_id=trader_id))
            total_bill += qty * rate
            bill_details.append(f"{bird}: {qty} {'units' if bird == 'Minar' else 'kg'} @ {'%.2f' % rate}")
            
    if total_bill == 0:
        flash("No quantities entered, bill not created.", 'info')
        return redirect(url_for('view_trader', trader_id=trader_id))
        
    amount_paid = float(request.form.get('amount_paid') or 0)
    remaining_due = total_bill - amount_paid
    
    db.execute('UPDATE traders SET total_debt = total_debt + ? WHERE id = ?', (remaining_due, trader_id))
    # Insert the driver's name into the database with the transaction
    db.execute(
        'INSERT INTO transactions (trader_id, type, date, details, driver_name, total_amount, amount_paid) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (trader_id, 'Purchase', today_str, "\n".join(bill_details), driver_name, total_bill, amount_paid)
    )
    db.commit()
    
    flash(f"New bill totaling ₹{total_bill:.2f} added successfully!", 'success')
    return redirect(url_for('view_trader', trader_id=trader_id))

@app.route('/trader/<int:trader_id>/add_payment', methods=['POST'])
def add_payment(trader_id):
    """Processes and saves a standalone payment."""
    db = get_db()
    amount_paid = float(request.form.get('amount_paid') or 0)
    
    if amount_paid > 0:
        db.execute('UPDATE traders SET total_debt = total_debt - ? WHERE id = ?', (amount_paid, trader_id))
        db.execute('INSERT INTO transactions (trader_id, type, date, details, total_amount, amount_paid) VALUES (?, ?, ?, ?, ?, ?)',(trader_id, 'Payment', date.today().isoformat(), 'Standalone Payment', 0, amount_paid))
        db.commit()
        flash(f"Payment of ₹{amount_paid:.2f} recorded successfully!", 'success')
    else:
        flash("Payment amount must be greater than zero.", 'error')
        
    return redirect(url_for('view_trader', trader_id=trader_id))

# --- MANAGEMENT ROUTES ---
@app.route('/manage_traders')
def manage_traders():
    """Displays the trader management page."""
    db = get_db()
    all_traders = db.execute('SELECT * FROM traders ORDER BY line, name').fetchall()
    return render_template('manage_traders.html', traders=all_traders, lines=lines)

@app.route('/add_trader', methods=['POST'])
def add_trader():
    name = request.form['name']
    line = request.form['line']
    if name and line:
        db = get_db()
        db.execute('INSERT INTO traders (name, line, total_debt) VALUES (?, ?, ?)', (name, line, 0.0))
        db.commit()
        flash(f"Trader '{name}' was added successfully.", 'success')
    return redirect(url_for('manage_traders'))

@app.route('/edit_trader/<int:trader_id>', methods=['GET', 'POST'])
def edit_trader(trader_id):
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        line = request.form['line']
        if name and line:
            db.execute('UPDATE traders SET name = ?, line = ? WHERE id = ?', (name, line, trader_id))
            db.commit()
            flash(f"Trader '{name}' updated successfully!", 'success')
            return redirect(url_for('manage_traders'))
    
    trader = db.execute('SELECT * FROM traders WHERE id = ?', (trader_id,)).fetchone()
    if not trader:
        flash("Trader not found.", 'error')
        return redirect(url_for('manage_traders'))
    return render_template('edit_trader.html', trader=trader, lines=lines)

@app.route('/delete_trader/<int:trader_id>', methods=['POST'])
def delete_trader(trader_id):
    db = get_db()
    trader = db.execute('SELECT name FROM traders WHERE id = ?', (trader_id,)).fetchone()
    if trader:
        db.execute('DELETE FROM traders WHERE id = ?', (trader_id,))
        db.execute('DELETE FROM transactions WHERE trader_id = ?', (trader_id,))
        db.commit()
        flash(f"Trader '{trader['name']}' and all their transactions have been deleted.", 'success')
    return redirect(url_for('manage_traders'))

@app.route('/manage_rates', methods=['GET', 'POST'])
def manage_rates():
    db = get_db()
    today_str = date.today().isoformat()
    if request.method == 'POST':
        for line in lines:
            for bird in bird_types:
                rate_value = request.form.get(f'rate-{line}-{bird}')
                if rate_value:
                    existing = db.execute('SELECT id FROM daily_rates WHERE date = ? AND line = ? AND bird_type = ?', (today_str, line, bird)).fetchone()
                    if existing:
                        db.execute('UPDATE daily_rates SET rate = ? WHERE id = ?', (float(rate_value), existing['id']))
                    else:
                        db.execute('INSERT INTO daily_rates (date, line, bird_type, rate) VALUES (?, ?, ?, ?)', (today_str, line, bird, float(rate_value)))
        db.commit()
        flash("Today's rates have been saved successfully!", 'success')
        return redirect(url_for('manage_rates'))

    rates_from_db = db.execute('SELECT line, bird_type, rate FROM daily_rates WHERE date = ?', (today_str,)).fetchall()
    current_rates = {line: {} for line in lines}
    for rate in rates_from_db: current_rates[rate['line']][rate['bird_type']] = rate['rate']
    return render_template('manage_rates.html', lines=lines, bird_types=bird_types, current_rates=current_rates, today_str=today_str)

# --- REPORTS ROUTE ---
@app.route('/reports')
def reports():
    db = get_db()
    seven_days_ago = (date.today() - timedelta(days=7)).isoformat()
    summary = db.execute("SELECT SUM(total_amount) as total_revenue, COUNT(id) as num_transactions FROM transactions WHERE type = 'Purchase' AND date >= ?", (seven_days_ago,)).fetchone()
    top_debtors = db.execute("SELECT * FROM traders WHERE total_debt > 0 ORDER BY total_debt DESC LIMIT 5").fetchall()
    line_performance = db.execute("SELECT t.line, SUM(tx.total_amount) as total_sales FROM transactions tx JOIN traders t ON tx.trader_id = t.id WHERE tx.type = 'Purchase' GROUP BY t.line ORDER BY total_sales DESC").fetchall()
    return render_template('reports.html', summary=summary, top_debtors=top_debtors, line_performance=line_performance)

# --- PRINTING ROUTES ---

@app.route('/bill/<int:transaction_id>/print')
def print_bill(transaction_id):
    """Generates a printable page for a single bill."""
    db = get_db()
    bill = db.execute('SELECT * FROM transactions WHERE id = ? AND type = "Purchase"', (transaction_id,)).fetchone()
    if not bill:
        flash("Bill not found.", 'error')
        return redirect(url_for('home'))
    
    trader = db.execute('SELECT * FROM traders WHERE id = ?', (bill['trader_id'],)).fetchone()
    return render_template('print_bill.html', bill=bill, trader=trader)

@app.route('/trader/<int:trader_id>/statement')
def print_statement(trader_id):
    """Generates a printable full account statement for a trader."""
    db = get_db()
    trader = db.execute('SELECT * FROM traders WHERE id = ?', (trader_id,)).fetchone()
    if not trader:
        flash("Trader not found.", 'error')
        return redirect(url_for('home'))
        
    transactions = db.execute('SELECT * FROM transactions WHERE trader_id = ? ORDER BY date, id', (trader_id,)).fetchall()
    return render_template('print_statement.html', trader=trader, transactions=transactions, today_date=date.today().strftime('%d-%b-%Y'))

# And REPLACE it with this new section:
def run_flask_app():
    """Runs the Flask app in a separate thread."""
    # We set 'use_reloader' to False to prevent issues with threading.
    app.run(port=5000, use_reloader=False)

if __name__ == '__main__':
    # Start the Flask server in a background thread
    flask_thread = Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()

    # Create and start the PyWebView window
    webview.create_window(
        'Poultry Farm Manager',  # The title of the window
        'http://127.0.0.1:5000/', # The URL of our Flask app
        width=1200,              # Optional: set a default window size
        height=800
    )
    webview.start()
