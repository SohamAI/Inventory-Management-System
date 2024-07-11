import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
from tkcalendar import DateEntry
from tkinter import constants as tk_constants
import sqlite3

conn = sqlite3.connect("stkmanage.db")
cursor = conn.cursor()
today = datetime.today().strftime('%d-%m-%Y')


def update_out_stock_state(*args):
    # Callback to update the state of Out Stock entry based on In Stock value
    if in_stock_var.get() == '':
        out_stock_entry.config(state=tk.NORMAL)
    else:
        in_stock_value = int(in_stock_var.get())
        out_stock_entry.config(state=tk.NORMAL if in_stock_value == 0 else tk.DISABLED)

    if out_stock_var.get() == '':
        in_stock_entry.config(state=tk.NORMAL)
    else:
        out_stock_value = int(out_stock_var.get())
        in_stock_entry.config(state=tk.NORMAL if out_stock_value == 0 else tk.DISABLED)

def load_transactions():
    # Load transactions from the database and populate the Treeview
    try:
        cursor.execute("SELECT item_name, party_name, item_date, item_size, item_in_stock, item_out_stock, balance FROM transactions ORDER BY item_id ASC")
        transactions = cursor.fetchall()

        try:
            for item in tree.get_children():
                tree.delete(item)
        except:
            print("error")
        
        for transaction in transactions:
            tree.insert("", "end", values=transaction)

    except Exception as e:
        print("Error loading transactions:", e)

def update_out_stock_transact():
    try:
        cursor.execute("SELECT item_name, item_date, item_size, item_in_stock, item_out_stock, balance FROM transactions WHERE item_out_stock > 0 AND item_date = ?", (today,))
        transactions = cursor.fetchall()

         # Clear existing data in the treeview
        for item in tree.get_children():
            tree.delete(item)
        
        for transaction in transactions:
            tree.insert("", "end", values=transaction)

    except Exception as e:
        print(e)


def update_in_stock_transact():
    try:
        cursor.execute("SELECT item_name, item_date, item_size, item_in_stock, item_out_stock, balance FROM transactions WHERE item_in_stock > 0 AND item_date = ?", (today,))
        transactions = cursor.fetchall()

         # Clear existing data in the treeview
        for item in tree.get_children():
            tree.delete(item)
        
        for transaction in transactions:
            tree.insert("", "end", values=transaction)

    except Exception as e:
        print(e)


def on_tree_select(event):
    # When a record is clicked, fill the form fields with the selected record's values
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item, "values")
        cal.set_date(item[2])
        item_name_entry.delete(0, tk.END)
        item_name_entry.insert(0, item[0])
        party_name_entry.delete(0, tk.END)
        party_name_entry.insert(0, item[1])
        size_combobox.set(item[3])
        in_stock_var.set(item[4])
        out_stock_var.set(item[5])
        


def submit_form():
    # Get data from the form
    date = cal.get_date().strftime("%d-%m-%Y")
    item_name = item_name_entry.get().upper()
    party_name = party_name_entry.get().upper()
    size = size_combobox.get()
    in_stock = 0 if in_stock_var.get() == '' else int(in_stock_var.get())
    out_stock = 0 if out_stock_var.get() == '' else int(out_stock_var.get())

    # Connect to the database
    conn = sqlite3.connect("stkmanage.db")
    cursor = conn.cursor()

    balance = 0

    data = (item_name, party_name, date, size, in_stock, out_stock, balance)
    # print(data)

    #--> add the data into Database
    if item_name != '' and party_name!='' and size != '' and (in_stock or out_stock) != '':
        try:
            cursor.execute("SELECT * FROM transactions WHERE item_name = ? AND item_size = ? AND party_name = ? ORDER BY item_id DESC LIMIT 1", (item_name, size, party_name))
            transactions = cursor.fetchall()

            if transactions:
                if in_stock > 0:
                    new_bal = in_stock + transactions[0][7]
                    add_data = (item_name, party_name, date, size, in_stock, out_stock, new_bal)
                    cursor.execute("INSERT INTO transactions (item_name, party_name,item_date, item_size, item_in_stock, item_out_stock, balance) VALUES (?, ?, ?, ?, ?, ?, ?)", add_data)
                    conn.commit()
                    print("Data Added Successfully")
                    messagebox.showinfo("Success", "Data Added Successfully")
                    conn.close()

                elif out_stock > 0:

                    #--> the balance should be sufficient
                    if(out_stock <= transactions[0][7]):
                        new_bal = transactions[0][7] - out_stock
                        add_data = (item_name, party_name, date, size, in_stock, out_stock, new_bal)
                        cursor.execute("INSERT INTO transactions (item_name, party_name, item_date, item_size, item_in_stock, item_out_stock, balance) VALUES (?, ?, ?, ?, ?, ?, ?)", add_data)
                        conn.commit()
                        print("Data Added Successfully")
                        messagebox.showinfo("Success", "Data Added Successfully")
                        conn.close()
                    else:
                        messagebox.showerror("Error", "Not Sufficient Balance")

            else:
                if in_stock > 0:
                    balance = in_stock
                    add_data = (item_name, party_name, date, size, in_stock, out_stock, balance)
                    cursor.execute("INSERT INTO transactions (item_name, party_name , item_date, item_size, item_in_stock, item_out_stock, balance) VALUES (?, ?, ?, ?, ?, ?, ?)", add_data)
                    conn.commit()
                    print("Data Added Successfully")
                    messagebox.showinfo("Success", "Data Added Successfully")
                    conn.close()

        except Exception as e:
            print("Error submitting form:", e)     

        # Clear and reload the Treeview
        tree.delete(*tree.get_children())
        load_transactions()
    else:
        messagebox.showerror("ERROR", "ENTER APPROPRIATE DATA")

def filter_transaction():
    print("Filter Transaction : ")

    selected_date = filter_date_entry.get_date().strftime("%d-%m-%Y")
    item_name = filter_item_name_entry.get().upper()

    print(selected_date, item_name)

    if(item_name != ''):
        try:
            cursor.execute("SELECT item_name, party_name ,item_date, item_size, item_in_stock, item_out_stock, balance FROM transactions WHERE item_name = ? AND item_date = ?", (item_name,selected_date,))
            transactions = cursor.fetchall()

            if(transactions != []):
                # Clear existing data in the treeview
                for item in tree.get_children():
                    tree.delete(item)
                
                for transaction in transactions:
                    tree.insert("", "end", values=transaction)
            else:
                messagebox.showerror("Error", "No Transactions")

        except Exception as e:
            print(e)
    else:
        messagebox.showerror("Error", "Enter the Item Name")

def load_all_transactions(tree):
    try:
        cursor.execute("SELECT item_name, party_name, item_date, item_size, item_in_stock, item_out_stock, balance FROM transactions ORDER BY item_id ASC")
        transactions = cursor.fetchall()

        for item in tree.get_children():
            tree.delete(item)

        for transaction in transactions:
            tree.insert("", "end", values=transaction)

    except Exception as e:
        print("Error loading transactions:", e)

def checkSize(size):
    sizes = ['M', 'L', 'XL', 'XXL', '3XL', '4XL', '5XL', 'Free', 'Plus']
    index_size = sizes.index(size) + 3
    return index_size



#--> Purchase Report Data
def purchase_report(tree, input_date):
    try:
        cursor.execute("SELECT item_name, party_name, item_date, item_size, item_in_stock, item_out_stock, balance FROM transactions WHERE item_date = ?", (input_date,))
        transactions = cursor.fetchall()


        if (transactions != []):
            data_format = [0,0,0,0,0,0,0,0,0,0,0,0,0]
            main_data = []
            unique_items =  []
            party_names = []
            for x in range(len(transactions)):
                if transactions[x][0] not in unique_items:
                    unique_items.append(transactions[x][0])
                if transactions[x][1] not in party_names:
                    party_names.append(transactions[x][1])

         

            for i in range(len(unique_items)):
                for j in range(len(party_names)):
                    for k in range(len(transactions)):
                        if((unique_items[i] == transactions[k][0]) and (party_names[j] == transactions[k][1]) and (transactions[k][4] > 0)):
                            size_index = checkSize(transactions[k][3])
                            data_format[size_index] = data_format[size_index] + transactions[k][4]
                            data_format[12] = data_format[12] + transactions[k][4]

                            data_format[0] = transactions[k][2] #--> date
                            data_format[1] = transactions[k][0] #--> item_name
                            data_format[2] = transactions[k][1] #--> Party_name
                            # print(data_format)
                    if(data_format!=[0,0,0,0,0,0,0,0,0,0,0,0,0]):   
                        main_data.append(data_format)
                    data_format = [0,0,0,0,0,0,0,0,0,0,0,0,0]

            #--> clear existing data
            for item in tree.get_children():
                tree.delete(item)

            #--> add data to the tree
            for transaction in main_data:
                tree.insert("", "end", values=transaction)

        else:
            messagebox.showerror("Error", "No Transactions")
    
    except Exception as e:
        print("Error loading transactions:", e)

#--> Sales Report Data
def sales_report(tree, input_date):
    try:
        cursor.execute("SELECT item_name, party_name, item_date, item_size, item_in_stock, item_out_stock, balance FROM transactions WHERE item_date = ?", (input_date,))
        transactions = cursor.fetchall()


        if (transactions != []):
            data_format = [0,0,0,0,0,0,0,0,0,0,0,0,0]
            main_data = []
            unique_items =  []
            party_names = []
            for x in range(len(transactions)):
                if transactions[x][0] not in unique_items:
                    unique_items.append(transactions[x][0])
                if transactions[x][1] not in party_names:
                    party_names.append(transactions[x][1])

         

            for i in range(len(unique_items)):
                for j in range(len(party_names)):
                    for k in range(len(transactions)):
                        if((unique_items[i] == transactions[k][0]) and (party_names[j] == transactions[k][1]) and (transactions[k][5] > 0)):
                            size_index = checkSize(transactions[k][3])
                            data_format[size_index] = data_format[size_index] + transactions[k][5]
                            data_format[12] = data_format[12] + transactions[k][5]

                            data_format[0] = transactions[k][2] #--> date
                            data_format[1] = transactions[k][0] #--> item_name
                            data_format[2] = transactions[k][1] #--> Party_name
                            # print(data_format)
                    if(data_format!=[0,0,0,0,0,0,0,0,0,0,0,0,0]):   
                        main_data.append(data_format)
                    data_format = [0,0,0,0,0,0,0,0,0,0,0,0,0]


            #--> clear existing data
            for item in tree.get_children():
                tree.delete(item)

            #--> add data to the tree
            for transaction in main_data:
                tree.insert("", "end", values=transaction)

        else:
            messagebox.showerror("Error", "No Transactions")
    
    except Exception as e:
        print("Error loading transactions:", e)



def delete_record():
    
    selected_item = tree.selection()
    if selected_item:
        item = tree.item(selected_item, "values")
        # ('A', 'ABC Pvt Ltd', '17-01-2024', 'L', '100', '0', '100')
    
    if(item):
        if(int(item[4]) > 0):
            temp_data = (item[0], item[1], item[2], item[3], int(item[4]), int(item[6]))
            confirmation = messagebox.askyesno("Delete Record", "Are you sure you want to delete this record?")
            if confirmation:
                cursor.execute("DELETE FROM transactions WHERE item_name = ? AND party_name = ? AND item_date = ? AND item_size = ? AND item_in_stock = ? AND balance = ?", (temp_data))
                conn.commit()
                load_transactions()
                messagebox.showinfo("Success", "Record Deleted Successfully")
        elif(int(item[5]) > 0):
            temp_data = (item[0], item[1], item[2], item[3], int(item[5]), int(item[6]))
            confirmation = messagebox.askyesno("Delete Record", "Are you sure you want to delete this record?")
            if confirmation:
                cursor.execute("DELETE FROM transactions WHERE item_name = ? AND party_name = ? AND item_date = ? AND item_size = ? AND item_out_stock = ? AND balance = ?", (temp_data))
                conn.commit()
                load_transactions()
                messagebox.showinfo("Success", "Record Deleted Successfully")
        else:
            messagebox.showerror("Error", "Please Enter Appropriate Data")


#--> open transactions 
def open_transactions_page():

    global all_transactions_tree
    transactions_window = tk.Toplevel(root)
    transactions_window.title("Transaction Reports")

    # Set the window size to full page
    screen_width = transactions_window.winfo_screenwidth()
    screen_height = transactions_window.winfo_screenheight()
    transactions_window.geometry(f"{screen_width}x{screen_height}+0+0")

    # Create and place the frame in the new window
    all_transactions_frame = tk.Frame(transactions_window)
    all_transactions_frame.pack(expand=True, fill=tk_constants.BOTH, padx=10, pady=10)

    all_transactions_fields_frame = tk.Frame(all_transactions_frame)
    all_transactions_fields_frame.pack(side=tk.TOP, pady=10)

    # Create and place the date entry field
    tk.Label(all_transactions_fields_frame, text="Select Date:").grid(row=0, column=0, padx=5)
    date_entry = DateEntry(all_transactions_fields_frame, width=15, background='darkblue', foreground='white', date_pattern = 'dd-mm-yyyy', borderwidth=2)
    date_entry.grid(row=0, column=1, padx=5)

    Purchase_Report_Button = tk.Button(all_transactions_fields_frame, text="Purchase Report", command=lambda: purchase_report( all_transactions_tree, date_entry.get_date().strftime("%d-%m-%Y")))
    Purchase_Report_Button.grid(row=0, column=2, padx=5)

    Sales_Report_Button = tk.Button(all_transactions_fields_frame, text="Sales Report", command=lambda: sales_report(all_transactions_tree, date_entry.get_date().strftime("%d-%m-%Y")))
    Sales_Report_Button.grid(row=0, column=3, padx=5)

    # Create and place the Treeview for all transactions
    all_transactions_tree = ttk.Treeview(all_transactions_frame, columns=("item_date", "item_name", "party_name", "M", "L", "XL","XXL","3XL","4XL","5XL","FREE","PLUS", "Total"))
    all_transactions_tree.pack(expand=True, fill=tk_constants.BOTH, padx=10, pady=10)

    # Create a vertical scrollbar for the Treeview
    all_transactions_tree_yscrollbar = ttk.Scrollbar(all_transactions_frame, orient="vertical", command=all_transactions_tree.yview)
    all_transactions_tree_yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    all_transactions_tree.configure(yscrollcommand=all_transactions_tree_yscrollbar.set)


    columns = ("item_date", "item_name", "party_name", "M", "L", "XL","XXL","3XL","4XL","5XL","FREE","PLUS", "Total")
    column_widths = (140, 140, 140, 70, 70, 70, 70,70,70,70,70,70,120)

    # Set column headings and adjust column width
    for col, width in zip(columns, column_widths):
        all_transactions_tree.column(col, width=width)
        all_transactions_tree.heading(col, text=col.capitalize())

    # Set column headings
    all_transactions_tree.heading("item_name", text="Item Name")
    all_transactions_tree.heading("party_name", text="Party Name")
    all_transactions_tree.heading("item_date", text="Date")
    all_transactions_tree.heading("M", text="M")
    all_transactions_tree.heading("L", text="L")
    all_transactions_tree.heading("XL", text="XL")
    all_transactions_tree.heading("XXL", text="XXL")
    all_transactions_tree.heading("3XL", text="3XL")
    all_transactions_tree.heading("4XL", text="4XL")
    all_transactions_tree.heading("5XL", text="5XL")
    all_transactions_tree.heading("FREE", text="FREE")
    all_transactions_tree.heading("PLUS", text="PLUS")
    all_transactions_tree.heading("Total", text="Total")

    Balance_Report_Button = tk.Button(all_transactions_fields_frame, text="Balance Report", command=show_balance_report_window)
    Balance_Report_Button.grid(row=0, column=4, padx=5)



def show_balance_report_window():
    # Create a new Toplevel window for the balance report
    balance_report_window = tk.Toplevel(root)
    balance_report_window.title("Balance Report")

    screen_width = balance_report_window.winfo_screenwidth()
    screen_height = balance_report_window.winfo_screenheight()
    balance_report_window.geometry(f"{screen_width}x{screen_height}+0+0")

    # Create and place the Treeview for the balance report
    balance_tree = ttk.Treeview(balance_report_window, columns=("item_date", "item_name", "party_name", "item_size",  "Balance"))
    balance_tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    # Set column headings and adjust column width
    for col, width in zip(("item_date", "item_name", "party_name", "item_size","Balance"), [140, 140, 140, 140, 140]):
        balance_tree.column(col, width=width)
        balance_tree.heading(col, text=col.capitalize())


    #---> collect the data : 
    cursor.execute("SELECT item_date, item_name, party_name, item_size, balance FROM transactions ORDER BY item_id DESC")
    transactions = cursor.fetchall()

    unique_items = []
    unique_parties = []
    sizes = ['M', 'L', 'XL', 'XXL', '3XL', '4XL', '5XL', 'Free', 'Plus']
    main_data = []

        
    #--> getting unique data
    for transaction in transactions:
        if transaction[1] not in unique_items:
            unique_items.append(transaction[1])
        if transaction[2] not in unique_parties:
            unique_parties.append(transaction[2])

        # print(unique_items)
    print("Unique Transactions")
    for item in unique_items:
        for party in unique_parties:
            for size in sizes:
                for transaction in transactions:
                    if(item == transaction[1] and size == transaction[3] and party == transaction[2]):
                        main_data.append(transaction)
                        break

    #--> add data to the table:
    for data in main_data:
        balance_tree.insert("", "end", values=data)
        
        

# Create the main window
root = tk.Tk()
root.title("Inventory Management")

# Create and place the form frame on the left
form_frame = tk.Frame(root)
form_frame.grid(row=0, rowspan=4, column=0, padx=10, pady=10, sticky="nsew")


tk.Label(form_frame, text="Date:").grid(row=0, column=0, sticky="e", pady=5)
cal = DateEntry(form_frame, width=15, background='darkblue', foreground='white', borderwidth=2, date_pattern = 'dd-mm-yyyy')
cal.grid(row=0, column=1, pady=5)
# cal.set_date(today) #--> set the inital date with the today's date in the specified format..
# cal.bind("<<DateEntrySelected>>", lambda event: update_date_entry(cal))



tk.Label(form_frame, text="Item Name:").grid(row=1, column=0, sticky="e", pady=5)
item_name_entry = tk.Entry(form_frame)
item_name_entry.grid(row=1, column=1, sticky="w", pady=5)

tk.Label(form_frame, text="Party_Name").grid(row=2, column=0, sticky="e", pady=5)
party_name_entry = tk.Entry(form_frame)
party_name_entry.grid(row=2, column=1, sticky="w", pady=5)

tk.Label(form_frame, text="Size:").grid(row=3, column=0, sticky="e", pady=5)
sizes = ['M', 'L', 'XL', 'XXL', '3XL', '4XL', '5XL', 'Free', 'Plus']
size_combobox = ttk.Combobox(form_frame, values=sizes)
size_combobox.grid(row=3, column=1, sticky="w", pady=5)

tk.Label(form_frame, text="In Stock:").grid(row=4, column=0, sticky="e", pady=5)
in_stock_var = tk.StringVar()
in_stock_var.trace_add('write', update_out_stock_state)  # Update Out Stock state when In Stock changes
in_stock_entry = tk.Entry(form_frame, textvariable=in_stock_var)
in_stock_entry.grid(row=4, column=1, sticky="w", pady=5)

tk.Label(form_frame, text="Out Stock:").grid(row=5, column=0, sticky="e", pady=5)
out_stock_var = tk.StringVar()
out_stock_var.trace_add('write', update_out_stock_state)  # Update In Stock state when Out Stock changes
out_stock_entry = tk.Entry(form_frame, textvariable=out_stock_var)
out_stock_entry.grid(row=5, column=1, sticky="w", pady=5)

# Configure row and column weights for the form frame
for i in range(6):
    form_frame.rowconfigure(i, weight=1)
form_frame.columnconfigure(0, weight=1)
form_frame.columnconfigure(1, weight=1)

# Create and place the submit button
submit_button = tk.Button(form_frame, text="Submit", command=submit_form)
submit_button.grid(row=6, column=0, columnspan=2, pady=10)

Delete_button = tk.Button(form_frame, text="Delete", command=delete_record)
Delete_button.grid(row=7, column=0, columnspan=2, pady=10)

# Create and place the panel frame on the right
panel_frame = tk.Frame(root)
panel_frame.grid(row=0, rowspan=5, column=1, padx=10, pady=10, sticky="nsew")

#--> Filters frame
filters_frame = tk.Frame(panel_frame)
filters_frame.grid(row=0, column=0, pady=10, sticky="nsew")

tk.Label(filters_frame, text="Filter by Date:").grid(row=1, column=0, padx=5, pady=5)
filter_date_entry = DateEntry(filters_frame, width=15, background='darkblue', foreground='white', borderwidth=2, state = "normal", date_pattern = 'dd-mm-yyyy')
filter_date_entry.grid(row=1, column=1, padx=5, pady=5)

tk.Label(filters_frame, text="Filter by Item Name:").grid(row=1, column=2, padx=5, pady=5)
filter_item_name_entry = tk.Entry(filters_frame)
filter_item_name_entry.grid(row=1, column=3, padx=5, pady=5)

filter_button = tk.Button(filters_frame, text="Filter Transactions", command=filter_transaction)
filter_button.grid(row=2, column=0, padx=5, pady=10)

# Create and place the Treeview for transactions
tree = ttk.Treeview(panel_frame, columns=("item_name", "party_name" , "item_date", "item_size", "item_in_stock", "item_out_stock", "balance"))
tree.grid(row=1, rowspan=6, column=0, padx=10, pady=10, sticky="nsew")

tree_yscrollbar = ttk.Scrollbar(panel_frame, orient="vertical", command=tree.yview)
tree_yscrollbar.grid(row=0, rowspan=7, column=1, sticky="ns")
tree.configure(yscrollcommand=tree_yscrollbar.set)

# Set column headings and adjust column width
columns = ("item_name", "party_name" , "item_date", "item_size", "item_in_stock", "item_out_stock", "balance")
column_widths = (140, 140, 140, 140, 140, 140, 140) # Adjust the widths as needed

for col, width in zip(columns, column_widths):
    tree.column(col, width=width)
    tree.heading(col, text=col.capitalize())

# Set column headings
tree.heading("item_name", text="Item Name")
tree.heading("party_name", text="Party Name")
tree.heading("item_date", text="Date")
tree.heading("item_size", text="Size")
tree.heading("item_in_stock", text="In Stock")
tree.heading("item_out_stock", text="Out Stock")
tree.heading("balance", text="Balance")

# Add event binding to handle record selection
tree.bind("<ButtonRelease-1>", on_tree_select)

totals_frame = tk.Frame(panel_frame)
totals_frame.grid(row=7, column=0, pady=10)

Total_In_Stock = tk.Button(totals_frame, text="Today In Stock", command=update_in_stock_transact)
Total_In_Stock.grid(row=0, column=0, pady=10)

Total_Out_Stock = tk.Button(totals_frame, text="Today Out Stock", command=update_out_stock_transact)
Total_Out_Stock.grid(row=0, column=1, pady=10)

Show_All_Transactions = tk.Button(totals_frame, text="All Transactions", command=load_transactions)
Show_All_Transactions.grid(row=0, column=2, pady=10)

Show_Reports = tk.Button(totals_frame, text="Show Reports", command=open_transactions_page)
Show_Reports.grid(row=0, column=3, pady=10)

# Configure row and column weights for the panel frame
for i in range(8):
    panel_frame.rowconfigure(i, weight=1)
panel_frame.columnconfigure(0, weight=1)

# Load initial transactions
load_transactions()

# Configure row and column weights for the main window
for i in range(6):
    root.rowconfigure(i, weight=1)
root.columnconfigure(0, weight=1)
root.columnconfigure(1, weight=1)

# Run the Tkinter event loop
root.mainloop()

conn.close()




