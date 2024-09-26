import tkinter as tk
from tkinter import messagebox, font, filedialog
import json
import os
import csv
from twilio.rest import Client

class PhoneBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phone Book")
        self.root.geometry("600x400")
        self.root.config(bg="#212121")  # Dark background

        # Load contacts from file and initialize the phone book
        self.phone_book = self.load_contacts()

        # Twilio Credentials (replace with your credentials)
        self.twilio_account_sid = 'your_account_sid'
        self.twilio_auth_token = 'your_auth_token'
        self.twilio_phone_number = 'your_twilio_number'
        self.client = Client(self.twilio_account_sid, self.twilio_auth_token)

        # Create UI components
        self.create_widgets()

    def create_widgets(self):
        # Title
        title_font = font.Font(size=20, weight='bold')
        title_label = tk.Label(self.root, text="Phone Book", font=title_font, bg="#212121", fg="#ffffff")
        title_label.pack(pady=10)

        # Frame for input fields
        input_frame = tk.Frame(self.root, bg="#424242")
        input_frame.pack(pady=10, padx=10, fill='x')

        # Entry for name
        self.name_label = tk.Label(input_frame, text="Name:", bg="#424242", fg="#ffffff")
        self.name_label.grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(input_frame, width=30, font=('Arial', 12), bg="#616161", fg="#ffffff", bd=2)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Entry for number
        self.number_label = tk.Label(input_frame, text="Number:", bg="#424242", fg="#ffffff")
        self.number_label.grid(row=1, column=0, padx=5, pady=5)
        self.number_entry = tk.Entry(input_frame, width=30, font=('Arial', 12), bg="#616161", fg="#ffffff", bd=2)
        self.number_entry.grid(row=1, column=1, padx=5, pady=5)

        # Buttons
        button_frame = tk.Frame(self.root, bg="#424242")
        button_frame.pack(pady=10)

        button_style = {'bg': '#1e88e5', 'fg': 'white', 'font': ('Arial', 10, 'bold'), 'padx': 10, 'pady': 5}

        # Create buttons with improved design
        self.add_button = self.create_button(button_frame, "Add Contact", self.add_contact)
        self.edit_button = self.create_button(button_frame, "Edit Contact", self.edit_contact)
        self.remove_button = self.create_button(button_frame, "Remove Contact", self.remove_contact)
        self.search_button = self.create_button(button_frame, "Search Contact", self.search_contact)
        self.display_button = self.create_button(button_frame, "Display All Contacts", self.display_contacts)
        self.call_button = self.create_button(button_frame, "Call Contact", self.call_contact)
        self.import_button = self.create_button(button_frame, "Import Contacts", self.import_contacts)
        self.export_button = self.create_button(button_frame, "Export Contacts", self.export_contacts)
        self.clear_button = self.create_button(button_frame, "Clear Fields", self.clear_fields)
        self.quit_button = self.create_button(button_frame, "Exit", self.root.quit)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bg="#424242", fg="#ffffff", anchor='w')
        self.status_bar.pack(side='bottom', fill='x')

    def create_button(self, parent, text, command):
        button = tk.Button(parent, text=text, command=command, bg='#1e88e5', fg='white', font=('Arial', 10, 'bold'), padx=10, pady=5)
        button.bind("<Enter>", lambda e: button.config(bg="#1565c0"))
        button.bind("<Leave>", lambda e: button.config(bg="#1e88e5"))
        button.pack(side='left', padx=5, pady=5)
        return button

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.number_entry.delete(0, tk.END)
        self.status_var.set("")

    def add_contact(self):
        name = self.name_entry.get().strip()
        number = self.number_entry.get().strip()
        if name and number:
            lower_name = name.lower()
            self.phone_book[lower_name] = number
            self.save_contacts()  # Save contacts to file
            self.status_var.set(f"Contact {name} added.")
            self.clear_fields()
        else:
            messagebox.showwarning("Input Error", "Please enter both name and number.")

    def edit_contact(self):
        name = self.name_entry.get().strip()
        lower_name = name.lower()
        if lower_name in self.phone_book:
            new_number = self.number_entry.get().strip()
            if new_number:
                self.phone_book[lower_name] = new_number
                self.save_contacts()
                self.status_var.set(f"Contact {name} updated.")
                self.clear_fields()
            else:
                messagebox.showwarning("Input Error", "Please enter a new number.")
        else:
            messagebox.showwarning("Not Found", f"Contact {name} not found.")

    def remove_contact(self):
        name = self.name_entry.get().strip()
        lower_name = name.lower()
        if lower_name in self.phone_book:
            del self.phone_book[lower_name]
            self.save_contacts()  # Save contacts to file
            self.status_var.set(f"Contact {name} removed.")
            self.clear_fields()
        else:
            messagebox.showwarning("Input Error", f"Contact {name} not found.")

    def search_contact(self):
        name = self.name_entry.get().strip()
        lower_name = name.lower()
        if lower_name in self.phone_book:
            number = self.phone_book[lower_name]
            messagebox.showinfo("Contact Found", f"{name}: {number}")
            self.status_var.set(f"Found contact: {name}")
        else:
            messagebox.showwarning("Not Found", f"Contact {name} not found.")

    def display_contacts(self):
        contacts = "\n".join([f"{name.title()}: {number}" for name, number in self.phone_book.items()])
        if contacts:
            messagebox.showinfo("All Contacts", contacts)
        else:
            messagebox.showinfo("Phone Book", "Phone book is empty.")
        self.status_var.set("Displayed all contacts.")

    def call_contact(self):
        name = self.name_entry.get().strip()
        lower_name = name.lower()
        if lower_name in self.phone_book:
            number = self.phone_book[lower_name]
            try:
                call = self.client.calls.create(
                    to=number,
                    from_=self.twilio_phone_number,
                    url='http://demo.twilio.com/docs/voice.xml'  # Use Twilio's demo URL or your own
                )
                messagebox.showinfo("Calling", f"Calling {name}...")
                self.status_var.set(f"Calling {name}...")
            except Exception as e:
                messagebox.showerror("Call Error", str(e))
        else:
            messagebox.showwarning("Not Found", f"Contact {name} not found.")

    def import_contacts(self):
        file_path = filedialog.askopenfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) == 2:
                        name, number = row
                        self.phone_book[name.lower()] = number
            self.save_contacts()
            self.status_var.set("Contacts imported successfully.")

    def export_contacts(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                for name, number in self.phone_book.items():
                    writer.writerow([name.title(), number])
            self.status_var.set("Contacts exported successfully.")

    def save_contacts(self):
        with open('contacts.json', 'w') as f:
            json.dump(self.phone_book, f)

    def load_contacts(self):
        contacts = {}
        if os.path.exists('contacts.json'):
            with open('contacts.json', 'r') as f:
                contacts = json.load(f)
        return {**contacts}  # Keep existing contacts intact

if __name__ == "__main__":
    root = tk.Tk()
    app = PhoneBookApp(root)
    root.mainloop()
