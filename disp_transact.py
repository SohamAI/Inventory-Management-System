import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime

def retrieve_all_transactions():
    try:
        # Connect to SQLite database
        conn = sqlite3.connect("stkmanage.db")
        cursor = conn.cursor()

        # Retrieve all transactions from the database
        cursor.execute("SELECT * FROM transactions")
        transactions = cursor.fetchall()

        return transactions

    except sqlite3.Error as e:
        print(f"Error connecting to the database: {e}")

    finally:
        # Close the connection in the finally block to ensure it's always closed
        if conn:
            conn.close()

def display_transactions():
    # Retrieve all transactions
    transactions = retrieve_all_transactions()

    # Clear existing data in the treeview
    for item in transaction_tree.get_children():
        transaction_tree.delete(item)

    # Display transactions in the treeview
    for transaction in transactions:
        transaction_tree.insert("", tk.END, values=transaction)


def update_out_stock_transact():
        # Connect to SQLite database
        conn = sqlite3.connect("stkmanage.db")
        cursor = conn.cursor()
        today = datetime.today().strftime('%d-%m-%Y')

        # Retrieve all transactions from the database
        cursor.execute("SELECT item_name, item_date, item_size, item_in_stock, item_out_stock, balance FROM transactions WHERE item_out_stock > 0 AND item_date = ?", (today,))
        transactions = cursor.fetchall()

        for item in transaction_tree.get_children():
            transaction_tree.delete(item)

        # Display transactions in the treeview
        for transaction in transactions:
            transaction_tree.insert("", tk.END, values=transaction)
    




def update_in_stock_transact():
        conn = sqlite3.connect("stkmanage.db")
        cursor = conn.cursor()
        today = datetime.today().strftime('%d-%m-%Y')

        # Retrieve all transactions from the database
        cursor.execute("SELECT item_name, item_date, item_size, item_in_stock, item_out_stock, balance FROM transactions WHERE item_in_stock > 0 AND item_date = ?", (today,))
        transactions = cursor.fetchall()

        for item in transaction_tree.get_children():
            transaction_tree.delete(item)

        # Display transactions in the treeview
        for transaction in transactions:
            transaction_tree.insert("", tk.END, values=transaction)

# Create the main window
root = tk.Tk()
root.title("Transaction Viewer")

# Create a Treeview for displaying transactions
transaction_tree = ttk.Treeview(root, columns=("ID", "Date", "Item ID", "Item Name", "Size", "In Stock", "Out Stock", "Balance"))
transaction_tree.heading("#0", text="Transaction ID")
transaction_tree.column("#0", anchor=tk.W, width=80)
transaction_tree.heading("ID", text="ID")
transaction_tree.column("ID", anchor=tk.W, width=80)
transaction_tree.heading("Date", text="Date")
transaction_tree.column("Date", anchor=tk.W, width=100)
transaction_tree.heading("Item ID", text="Item ID")
transaction_tree.column("Item ID", anchor=tk.W, width=80)
transaction_tree.heading("Item Name", text="Item Name")
transaction_tree.column("Item Name", anchor=tk.W, width=150)
transaction_tree.heading("Size", text="Size")
transaction_tree.column("Size", anchor=tk.W, width=80)
transaction_tree.heading("In Stock", text="In Stock")
transaction_tree.column("In Stock", anchor=tk.W, width=80)
transaction_tree.heading("Out Stock", text="Out Stock")
transaction_tree.column("Out Stock", anchor=tk.W, width=80)
transaction_tree.heading("Balance", text="Balance")
transaction_tree.column("Balance", anchor=tk.W, width=80)

transaction_tree.grid(row=0, column=0, padx=10, pady=10, columnspan=2, sticky="nsew")

# Add a vertical scrollbar to the treeview
scrollbar = ttk.Scrollbar(root, orient="vertical", command=transaction_tree.yview)
scrollbar.grid(row=0, column=2, pady=10, sticky="ns")
transaction_tree.configure(yscrollcommand=scrollbar.set)

# Display Button
display_button = tk.Button(root, text="Display Transactions", command=lambda: display_transactions())
display_button.grid(row=1, column=0, pady=10, padx=(10, 5), sticky='w')

update_button = tk.Button(root, text="Update Out stock Transactions", command=lambda: update_out_stock_transact())
update_button.grid(row=2, column=0, pady=10, padx=(5, 15), sticky='w')

update_button = tk.Button(root, text="Update In stock Transactions", command=lambda: update_in_stock_transact())
update_button.grid(row=3, column=0, pady=10, padx=(5, 15), sticky='w')

# Exit Button
exit_button = tk.Button(root, text="Exit", command=root.destroy)
exit_button.grid(row=1, column=1, pady=10, padx=10, sticky='e')

# Configure row and column weights
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)



# Run the Tkinter event loop
root.mainloop()
