
import tkinter as tk
from tkinter import messagebox

class BankApp:
    def __init__(self, master):
        self.master = master
        master.title("Banking System")
        self.num_accounts = 0
        self.accounts = []
        self.create_start_frame()

    def create_start_frame(self):
        self.start_frame = tk.Frame(self.master, padx=20, pady=20)
        self.start_frame.pack()
        tk.Label(self.start_frame, text="How many accounts would you like to open?").grid(row=0, column=0, sticky="w")
        self.num_entry = tk.Entry(self.start_frame)
        self.num_entry.grid(row=0, column=1)
        tk.Button(self.start_frame, text="Next", command=self.setup_balances).grid(row=1, column=0, columnspan=2, pady=10)

    def setup_balances(self):
        try:
            n = int(self.num_entry.get())
            if n <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number.")
            return
        self.num_accounts = n
        self.start_frame.destroy()

        self.balance_frame = tk.Frame(self.master, padx=20, pady=20)
        self.balance_frame.pack()
        self.balance_entries = []
        for i in range(n):
            tk.Label(self.balance_frame, text=f"Starting balance for Account {i+1}:").grid(row=i, column=0, sticky="w")
            entry = tk.Entry(self.balance_frame)
            entry.grid(row=i, column=1)
            self.balance_entries.append(entry)
        tk.Button(self.balance_frame, text="Save", command=self.init_main_ui).grid(row=n, column=0, columnspan=2, pady=10)

    def init_main_ui(self):
        try:
            balances = [int(e.get()) for e in self.balance_entries]
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric balances for all accounts.")
            return
        self.accounts = balances
        self.balance_frame.destroy()

        self.main_frame = tk.Frame(self.master, padx=20, pady=20)
        self.main_frame.pack()

        tk.Label(self.main_frame, text="Current Account Balances:").grid(row=0, column=0, columnspan=4, sticky="w")
        self.account_labels = []
        for i, bal in enumerate(self.accounts):
            lbl = tk.Label(self.main_frame, text=f"Account {i+1}: {bal}")
            lbl.grid(row=i+1, column=0, columnspan=2, sticky="w")
            self.account_labels.append(lbl)

        tk.Label(self.main_frame, text="Transaction:").grid(row=0, column=2, sticky="w")
        self.op_var = tk.StringVar(value="Deposit")
        op_menu = tk.OptionMenu(self.main_frame, self.op_var, "Deposit", "Withdraw", "Transfer", command=self.on_op_change)
        op_menu.grid(row=0, column=3, sticky="w")

        tk.Label(self.main_frame, text="Account:").grid(row=1, column=2, sticky="w")
        ids = [str(i+1) for i in range(self.num_accounts)]
        self.acc_var = tk.StringVar(value=ids[0])
        self.acc_menu = tk.OptionMenu(self.main_frame, self.acc_var, *ids)
        self.acc_menu.grid(row=1, column=3, sticky="w")

        self.acc2_label = tk.Label(self.main_frame, text="Target Account:")
        self.acc2_var = tk.StringVar(value=ids[1] if self.num_accounts>1 else ids[0])
        self.acc2_menu = tk.OptionMenu(self.main_frame, self.acc2_var, *ids)
        self.acc2_label.grid(row=2, column=2, sticky="w")
        self.acc2_menu.grid(row=2, column=3, sticky="w")

        tk.Label(self.main_frame, text="Amount:").grid(row=3, column=2, sticky="w")
        self.amount_entry = tk.Entry(self.main_frame)
        self.amount_entry.grid(row=3, column=3, sticky="w")

        tk.Button(self.main_frame, text="Execute", command=self.process_txn).grid(row=4, column=2, columnspan=2, pady=10)

        self.log_frame = tk.LabelFrame(self.main_frame, text="Transaction Log", padx=10, pady=10)
        self.log_frame.grid(row=5, column=0, columnspan=4, pady=10, sticky="nsew")
        self.log_text = tk.Text(self.log_frame, height=10, state="disabled")
        self.log_text.pack(fill="both", expand=True)
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("fail", foreground="red")

        self.on_op_change(self.op_var.get())

    def on_op_change(self, value):
        if value == "Transfer":
            self.acc2_label.grid()
            self.acc2_menu.grid()
        else:
            self.acc2_label.grid_remove()
            self.acc2_menu.grid_remove()

    def process_txn(self):
        op = self.op_var.get()
        try:
            acc = int(self.acc_var.get()) - 1
            amt = int(self.amount_entry.get())
            if not (0 <= acc < self.num_accounts): raise IndexError
            if op == "Transfer":
                acc2 = int(self.acc2_var.get()) - 1
                if not (0 <= acc2 < self.num_accounts): raise IndexError
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values.")
            return
        except IndexError:
            messagebox.showerror("Error", "Account not found.")
            return

        success = True
        if op == "Deposit":
            self.accounts[acc] += amt
            details = f"Deposited {amt} to Account {acc+1}"
        elif op == "Withdraw":
            if self.accounts[acc] >= amt:
                self.accounts[acc] -= amt
                details = f"Withdrew {amt} from Account {acc+1}"
            else:
                success = False
                details = f"Failed to withdraw {amt} from Account {acc+1}"
        else:  # Transfer
            if self.accounts[acc] >= amt:
                self.accounts[acc] -= amt
                self.accounts[acc2] += amt
                details = f"Transferred {amt} from Account {acc+1} to Account {acc2+1}"
            else:
                success = False
                details = f"Failed to transfer {amt} from Account {acc+1} to Account {acc2+1}"

        self.update_labels()
        tag = "success" if success else "fail"
        status = "Success" if success else "Failed"
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"{details} ({status})\n", tag)
        self.log_text.config(state="disabled")
        self.log_text.see("end")

    def update_labels(self):
        for i, lbl in enumerate(self.account_labels):
            lbl.config(text=f"Account {i+1}: {self.accounts[i]}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BankApp(root)
    root.mainloop()
