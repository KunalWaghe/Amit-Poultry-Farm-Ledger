import sqlite3
from flask import Flask, render_template, request, redirect, url_for, g
from datetime import date

# Initialize our Flask application.
app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
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

# --- STATIC DATA (Can still be hardcoded) ---
lines = ["Pati", "Amjhera+Gandhwani", "Anjad", "Dahi", "Local"]

# --- WEB PAGES (Routes) ---

@app.route('/')
def home():
    """ Renders the homepage to select a line. """
    return render_template('home.html', lines=lines)
    
@app.route('/line/<line_name>')
def view_line(line_name):
    """ Renders the page showing all traders for a specific line from the database. """
    db = get_db()
    traders_in_line = db.execute(
        'SELECT * FROM traders WHERE line = ? ORDER BY name', (line_name,)
    ).fetchall()
    return render_template('line_traders.html', line_name=line_name, traders_in_line=traders_in_line)

@app.route('/trader/<int:trader_id>')
def view_trader(trader_id):
    """ Renders the ledger for a single trader by querying the database. """
    db = get_db()
    
    selected_trader = db.execute(
        'SELECT * FROM traders WHERE id = ?', (trader_id,)
    ).fetchone()
    
    if not selected_trader:
        return "Trader not found!", 404

    today_str = date.today().isoformat()
    
    rates_from_db = db.execute(
        'SELECT bird_type, rate FROM daily_rates WHERE date = ? AND line = ?',
        (today_str, selected_trader['line'])
    ).fetchall()
    current_rates = {r['bird_type']: r['rate'] for r in rates_from_db}

    trader_transactions = db.execute(
        'SELECT * FROM transactions WHERE trader_id = ? ORDER BY date DESC, id DESC', (trader_id,)
    ).fetchall()
    
    return render_template('trader_ledger.html', trader=selected_trader, transactions=trader_transactions, rates=current_rates)

@app.route('/trader/<int:trader_id>/add_bill', methods=['POST'])
def add_bill(trader_id):
    """ Processes the new bill and saves it to the database. """
    db = get_db()
    # Ensure the trader exists
    trader = db.execute('SELECT id FROM traders WHERE id = ?', (trader_id,)).fetchone()
    if not trader:
        return "Trader not found!", 404

    today_str = date.today().isoformat()
    # ... (Calculation logic is the same as before) ...
    quantities = {'Minar': float(request.form.get('minar_qty') or 0), 'Broiler': float(request.form.get('broiler_qty') or 0), 'Parent': float(request.form.get('parent_qty') or 0)}
    rates_from_form = {'Minar': float(request.form.get('minar_rate') or 0), 'Broiler': float(request.form.get('broiler_rate') or 0), 'Parent': float(request.form.get('parent_rate') or 0)}
    total_bill, bill_details = 0, []
    for bird, qty in quantities.items():
        if qty > 0:
            rate = rates_from_form.get(bird)
            if rate is None or rate == 0: return f"Error: Rate for {bird} was not provided or was zero.", 400
            total_bill += qty * rate
            bill_details.append(f"{bird}: {qty} {'units' if bird == 'Minar' else 'kg'} @ {'%.2f' % rate}")
    if total_bill == 0: return redirect(url_for('view_trader', trader_id=trader_id))
    amount_paid = float(request.form.get('amount_paid') or 0)
    remaining_due = total_bill - amount_paid

    # --- Database Operations ---
    db.execute('UPDATE traders SET total_debt = total_debt + ? WHERE id = ?', (remaining_due, trader_id))
    db.execute(
        'INSERT INTO transactions (trader_id, type, date, details, total_amount, amount_paid) VALUES (?, ?, ?, ?, ?, ?)',
        (trader_id, 'Purchase', today_str, "\n".join(bill_details), total_bill, amount_paid)
    )
    db.commit() # Commit the changes to the database
    
    return redirect(url_for('view_trader', trader_id=trader_id))

@app.route('/trader/<int:trader_id>/add_payment', methods=['POST'])
def add_payment(trader_id):
    """ Processes a simple payment and saves it to the database. """
    db = get_db()
    amount_paid = float(request.form.get('amount_paid') or 0)
    
    if amount_paid > 0:
        today_str = date.today().isoformat()
        db.execute('UPDATE traders SET total_debt = total_debt - ? WHERE id = ?', (amount_paid, trader_id))
        db.execute(
            'INSERT INTO transactions (trader_id, type, date, details, total_amount, amount_paid) VALUES (?, ?, ?, ?, ?, ?)',
            (trader_id, 'Payment', today_str, 'Standalone Payment', 0, amount_paid)
        )
        db.commit()
    
    return redirect(url_for('view_trader', trader_id=trader_id))

# --- NEW ROUTES FOR TRADER MANAGEMENT ---

@app.route('/manage_traders')
def manage_traders():
    """Displays the trader management page."""
    db = get_db()
    all_traders = db.execute('SELECT * FROM traders ORDER BY line, name').fetchall()
    return render_template('manage_traders.html', traders=all_traders, lines=lines)

@app.route('/add_trader', methods=['POST'])
def add_trader():
    """Adds a new trader to the database."""
    name = request.form['name']
    line = request.form['line']
    if name and line:
        db = get_db()
        db.execute('INSERT INTO traders (name, line, total_debt) VALUES (?, ?, ?)', (name, line, 0.0))
        db.commit()
    return redirect(url_for('manage_traders'))

@app.route('/delete_trader/<int:trader_id>', methods=['POST'])
def delete_trader(trader_id):
    """Deletes a trader from the database."""
    # In a real app, you might want to handle what happens to their transactions.
    # For now, we just delete the trader.
    db = get_db()
    db.execute('DELETE FROM traders WHERE id = ?', (trader_id,))
    # We should also delete their transactions to keep the database clean
    db.execute('DELETE FROM transactions WHERE trader_id = ?', (trader_id,))
    db.commit()
    return redirect(url_for('manage_traders'))

if __name__ == '__main__':
    app.run(debug=True)


