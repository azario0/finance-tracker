import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import os

# Define the path for saving the data
data_file = 'finance_data.csv'

# Check if the data file exists; if not, create it
if not os.path.exists(data_file):
    with open(data_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Category', 'Amount'])

class FinanceManager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Finance Manager")
        self.geometry("600x800")
        self.resizable(True, True)

        # Initialize variables
        self.category = tk.StringVar()
        self.amount = tk.DoubleVar()
        self.budget = tk.DoubleVar()
        self.chart_type = tk.StringVar(value='Pie Chart')
        self.expenses = self.load_expenses()

        # Create GUI components
        self.create_widgets()
        self.update_chart()

    def create_widgets(self):
        # Category input
        input_frame = ttk.LabelFrame(self, text="Enter Expense Details")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        ttk.Label(input_frame, text="Category:").grid(row=0, column=0, padx=10, pady=10)
        ttk.Entry(input_frame, textvariable=self.category).grid(row=0, column=1, padx=10, pady=10)

        ttk.Label(input_frame, text="Amount:").grid(row=1, column=0, padx=10, pady=10)
        ttk.Entry(input_frame, textvariable=self.amount).grid(row=1, column=1, padx=10, pady=10)

        ttk.Label(input_frame, text="Budget:").grid(row=2, column=0, padx=10, pady=10)
        ttk.Entry(input_frame, textvariable=self.budget).grid(row=2, column=1, padx=10, pady=10)

        ttk.Button(input_frame, text="Add Expense", command=self.add_expense).grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(input_frame, text="Modify Dataset", command=self.modify_dataset).grid(row=4, column=0, columnspan=2, pady=10)

        # Chart type selection
        chart_frame = ttk.LabelFrame(self, text="Select Chart Type")
        chart_frame.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

        ttk.Radiobutton(chart_frame, text="Pie Chart", variable=self.chart_type, value='Pie Chart', command=self.update_chart).grid(row=0, column=0, padx=10, pady=10)
        ttk.Radiobutton(chart_frame, text="Bar Chart", variable=self.chart_type, value='Bar Chart', command=self.update_chart).grid(row=0, column=1, padx=10, pady=10)

        # Chart display
        self.figure = plt.Figure(figsize=(6, 4), dpi=100)
        self.chart = FigureCanvasTkAgg(self.figure, self)
        self.chart.get_tk_widget().grid(row=2, column=0, padx=10, pady=10, sticky='nsew')

    def load_expenses(self):
        expenses = {}
        with open(data_file, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                category, amount = row
                if category in expenses:
                    expenses[category] += float(amount)
                else:
                    expenses[category] = float(amount)
        return expenses

    def save_expenses(self):
        with open(data_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Category', 'Amount'])
            for category, amount in self.expenses.items():
                writer.writerow([category, amount])

    def add_expense(self):
        category = self.category.get().strip()
        amount = self.amount.get()
        if not category or amount <= 0:
            messagebox.showerror("Input Error", "Please enter a valid category and amount.")
            return

        if category in self.expenses:
            self.expenses[category] += amount
        else:
            self.expenses[category] = amount

        self.save_expenses()
        self.update_chart()
        self.category.set("")
        self.amount.set(0.0)

    def update_chart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        categories = list(self.expenses.keys())
        amounts = list(self.expenses.values())

        if self.chart_type.get() == 'Pie Chart':
            ax.pie(amounts, labels=categories, autopct='%1.1f%%')
        else:
            ax.bar(categories, amounts)
            ax.set_ylabel('Amount')
            ax.set_xlabel('Category')
            ax.set_title('Expenses by Category')

        self.chart.draw()

    def modify_dataset(self):
        modify_window = tk.Toplevel(self)
        modify_window.title("Modify Dataset")
        modify_window.geometry("400x300")
        modify_window.resizable(True, True)

        modify_frame = ttk.Frame(modify_window)
        modify_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tree = ttk.Treeview(modify_frame, columns=("Category", "Amount"), show='headings')
        tree.heading("Category", text="Category")
        tree.heading("Amount", text="Amount")
        tree.pack(fill=tk.BOTH, expand=True)

        for category, amount in self.expenses.items():
            tree.insert("", "end", values=(category, amount))

        def on_modify():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Selection Error", "Please select an item to modify.")
                return
            selected_item = selected_item[0]
            category, amount = tree.item(selected_item, "values")
            
            new_category = simpledialog.askstring("Input", f"New Category (current: {category}):", parent=modify_window)
            if new_category is None:
                return
            new_amount = simpledialog.askfloat("Input", f"New Amount (current: {amount}):", parent=modify_window)
            if new_amount is None:
                return
            
            del self.expenses[category]
            self.expenses[new_category] = new_amount
            
            self.save_expenses()
            self.update_chart()
            modify_window.destroy()

        def on_delete():
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Selection Error", "Please select an item to delete.")
                return
            selected_item = selected_item[0]
            category, _ = tree.item(selected_item, "values")

            del self.expenses[category]
            
            self.save_expenses()
            self.update_chart()
            modify_window.destroy()

        ttk.Button(modify_window, text="Modify", command=on_modify).pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Button(modify_window, text="Delete", command=on_delete).pack(side=tk.RIGHT, padx=10, pady=10)

if __name__ == "__main__":
    app = FinanceManager()
    app.mainloop()
