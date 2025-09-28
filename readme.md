Poultry Farm Business Manager
A simple, effective, and custom-built web application to manage the daily sales, transactions, and customer records for a family-run poultry farm business. This application replaces the need for manual ledgers by providing a clean, digital interface for all record-keeping tasks.
Overview
This project was designed to solve the specific challenges of a poultry business that sells different types of birds (per unit and per kg) to traders across various delivery routes. It streamlines the process of creating daily bills, tracking payments, and managing outstanding debt for each trader, all while accounting for fluctuating daily rates.
Features
●	Trader Management: Full CRUD (Create, Read, Update, Delete) functionality for managing your list of traders. You can easily add new traders, edit their details, or remove them from the system.
●	Daily Rate Management: A dedicated page to set the day's selling rates for each bird type ("Minar", "Broiler", "Parent") across all five delivery lines.
●	Dynamic Billing System: An intuitive billing form on each trader's ledger that automatically calculates subtotals and the total bill in real-time as you enter quantities.
●	Comprehensive Transaction Ledger: Each trader has a chronological ledger showing every purchase and every standalone payment, giving you a complete financial history.
●	Reporting Dashboard: A summary page that provides valuable business insights, including:
○	Total revenue over the last 7 days.
○	Top 5 traders by outstanding debt.
○	Sales performance broken down by delivery line.
●	Database Persistence: All data is securely stored in a local SQLite database file (poultry.db), ensuring your records are safe and permanent.
●	User-Friendly Feedback: The application provides clear success and error messages for all actions, making it intuitive to use.
Technology Stack
●	Backend: Python with the Flask web framework.
●	Database: SQLite for simple, file-based data storage.
●	Frontend: Standard HTML5.
●	Styling: Tailwind CSS for a clean and modern user interface.
Setup and Installation
Follow these steps to get the application running on your local machine.
1. Prerequisites
●	Ensure you have Python 3 installed. You can check this by opening a terminal or command prompt and running:
python --version


2. Get the Code
●	Download all the project files (app.py, database_setup.py, the templates folder, etc.) and place them together in a single project folder.
3. Set Up a Virtual Environment (Recommended)
●	A virtual environment keeps your project's dependencies isolated.
●	On Windows:
python -m venv venv
venv\Scripts\activate


●	On macOS/Linux:
python3 -m venv venv
source venv/bin/activate


4. Install Dependencies
●	With your virtual environment active, install Flask:
pip install Flask


5. Initialize the Database
●	This is a one-time step. Run the setup script to create the poultry.db file and all the necessary tables.
python database_setup.py


●	You will see messages confirming that the database and tables were created successfully.
6. Run the Application
●	Now, you can start the web server:
python app.py


●	Open your web browser and navigate to the following address: http://127.0.0.1:5000
How to Use the Application
1.	Set Daily Rates: At the start of the day, go to the Manage Daily Rates page from the homepage and enter the prices for each bird and line.
2.	Manage Traders: If you have a new customer, go to the Manage Traders page to add them to the system.
3.	Create a Bill: Navigate to a specific trader's ledger by clicking on their delivery line and then their name. Use the billing form to enter the quantities of birds sold. The rates will be pre-filled, but you can adjust them if needed.
4.	Record a Payment: Use the "Record Standalone Payment" form on a trader's ledger to log any payments made to clear past dues.
5.	Check Reports: Visit the View Reports page at any time to get an overview of your business performance.
