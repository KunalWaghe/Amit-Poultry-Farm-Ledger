# Import the Flask framework and the render_template function.
from flask import Flask, render_template

# Initialize our Flask application.
app = Flask(__name__)

# --- DATA STORAGE (Our In-Memory Database) ---
# In a real application, this data would be in a database.
# For now, we'll keep it in lists and dictionaries to keep things simple.

# A simple list of the 5 lines/routes for the business.
lines = ["Pati", "Amjhera+Gandhwani", "Anjad", "Dahi", "Local"]

# A list of traders. Each trader is a dictionary.
# 'id' must be unique.
# 'total_debt' is the total amount of money they currently owe.
traders = [
    {'id': 1, 'name': 'Rajesh Kumar', 'line': 'Pati', 'total_debt': 5400.50},
    {'id': 2, 'name': 'Suresh Patel', 'line': 'Pati', 'total_debt': 0.00},
    {'id': 3, 'name': 'Amit Singh', 'line': 'Anjad', 'total_debt': 1230.00},
    {'id': 4, 'name': 'Deepak Jain', 'line': 'Dahi', 'total_debt': 7800.00},
    {'id': 5, 'name': 'Local Customer 1', 'line': 'Local', 'total_debt': 250.00}
]

# A list of daily rates. This shows how prices change per day and per line.
daily_rates = [
    # Rates for today (September 28, 2025)
    {'date': '2025-09-28', 'line': 'Pati', 'bird_type': 'Minar', 'rate': 85.00},
    {'date': '2025-09-28', 'line': 'Pati', 'bird_type': 'Broiler', 'rate': 112.50},
    {'date': '2025-09-28', 'line': 'Pati', 'bird_type': 'Parent', 'rate': 105.00},

    {'date': '2025-09-28', 'line': 'Anjad', 'bird_type': 'Minar', 'rate': 86.00},
    {'date': '2025-09-28', 'line': 'Anjad', 'bird_type': 'Broiler', 'rate': 114.00},
    
    # Rates for a previous day (for historical records)
    {'date': '2025-09-27', 'line': 'Pati', 'bird_type': 'Broiler', 'rate': 110.00},
]

# A list of all transactions. This is the master ledger for everyone.
transactions = [
    {'id': 1, 'trader_id': 1, 'type': 'Purchase', 'date': '2025-09-27', 'bird_type': 'Broiler', 'weight': 50, 'rate_applied': 110.00, 'total_amount': 5500.50, 'amount_paid': 100.00},
    {'id': 2, 'trader_id': 3, 'type': 'Purchase', 'date': '2025-09-26', 'bird_type': 'Minar', 'units': 15, 'rate_applied': 82.00, 'total_amount': 1230.00, 'amount_paid': 0.00},
    {'id': 3, 'trader_id': 1, 'type': 'Payment', 'date': '2025-09-28', 'amount_paid': 2000.00},
]


# --- WEB PAGES (Routes) ---

# This is the main homepage of our application.
@app.route('/')
def home():
    """
    This function runs when someone visits the homepage.
    It now renders the home.html template and passes our 'lines' list to it.
    Flask will look for 'home.html' inside the 'templates' folder.
    """
    return render_template('home.html', lines=lines)
# Import the Flask framework and the render_template function.


# This is our new dynamic route to show traders for a specific line.
@app.route('/line/<line_name>')
def view_line(line_name):
    """
    This function runs when a user visits a URL like /line/Pati.
    It finds all traders from that line and displays them.
    """
    # We use a list comprehension to create a new list containing
    # only the traders from the selected line.
    traders_in_line = [trader for trader in traders if trader['line'] == line_name]
    
    # We then render the new 'line_traders.html' template.
    # We pass the filtered list of traders and the line name itself to the template.
    return render_template('line_traders.html', line_name=line_name, traders_in_line=traders_in_line)

# This line allows us to run the app by running `python app.py` in the terminal.
if __name__ == '__main__':
    # debug=True means the server will automatically restart when we save changes.
    app.run(debug=True)

