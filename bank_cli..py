
import sys
from multiprocessing import Process, Semaphore, shared_memory, Manager
import numpy as np

def worker(txn, accounts_shm_name, num_accounts, semaphores, log_list):
    shm = shared_memory.SharedMemory(name=accounts_shm_name)
    accounts = np.ndarray((num_accounts,), dtype=np.int64, buffer=shm.buf)
    success = False
    details = ''

    if txn['type'] == 'transfer':
        src, dst, amt = txn['from'], txn['to'], txn['amount']
        first, second = sorted([src, dst])
        semaphores[first].acquire()
        semaphores[second].acquire()
        if accounts[src] >= amt:
            accounts[src] -= amt
            accounts[dst] += amt
            success = True
            details = f"Transferred {amt} from Account {src+1} to Account {dst+1}"
        else:
            details = f"Failed transfer of {amt} from Account {src+1} (Insufficient funds)"
        semaphores[second].release()
        semaphores[first].release()

    elif txn['type'] == 'deposit':
        idx, amt = txn['account'], txn['amount']
        semaphores[idx].acquire()
        accounts[idx] += amt
        success = True
        details = f"Deposited {amt} to Account {idx+1}"
        semaphores[idx].release()

    elif txn['type'] == 'withdraw':
        idx, amt = txn['account'], txn['amount']
        semaphores[idx].acquire()
        if accounts[idx] >= amt:
            accounts[idx] -= amt
            success = True
            details = f"Withdrew {amt} from Account {idx+1}"
        else:
            details = f"Failed withdrawal of {amt} from Account {idx+1} (Insufficient funds)"
        semaphores[idx].release()

    log_list.append((txn, success, details))


def interactive_mode():
    while True:
        try:
            num_accounts = int(input("How many accounts would you like to open? "))
            if num_accounts <= 0:
                print("Please enter a positive number of accounts.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

    initial_balances = []
    for i in range(1, num_accounts+1):
        while True:
            try:
                bal = int(input(f"Enter starting balance for Account {i}: "))
                break
            except ValueError:
                print("Invalid amount. Please enter a numeric value.")
        initial_balances.append(bal)

    shm = shared_memory.SharedMemory(create=True, size=np.int64().nbytes * num_accounts)
    accounts = np.ndarray((num_accounts,), dtype=np.int64, buffer=shm.buf)
    accounts[:] = initial_balances
    semaphores = [Semaphore(1) for _ in range(num_accounts)]
    manager = Manager()
    log_list = manager.list()

    print("\nCommands: d=deposit, w=withdraw, t=transfer, e=exit")
    while True:
        cmd = input("Choose command (d/w/t/e): ").strip().lower()
        if cmd == 'e':
            break
        elif cmd == 'd':
            while True:
                try:
                    acc = int(input("Account ID (1-based): "))
                    if not (1 <= acc <= num_accounts):
                        print("Invalid account. Please try again.")
                        continue
                    amt = int(input("Amount to deposit: "))
                    break
                except ValueError:
                    print("Invalid input. Please enter numeric values.")
            txn = {'type': 'deposit', 'account': acc-1, 'amount': amt}

        elif cmd == 'w':
            while True:
                try:
                    acc = int(input("Account ID (1-based): "))
                    if not (1 <= acc <= num_accounts):
                        print("Invalid account. Please try again.")
                        continue
                    amt = int(input("Amount to withdraw: "))
                    break
                except ValueError:
                    print("Invalid input. Please enter numeric values.")
            txn = {'type': 'withdraw', 'account': acc-1, 'amount': amt}

        elif cmd == 't':
            if num_accounts < 2:
                print("Only one account exists. Transfer is not possible.")
                continue
            while True:
                try:
                    src = int(input("Source Account ID (1-based): "))
                    if not (1 <= src <= num_accounts):
                        print("Invalid account. Please try again.")
                        continue
                    dst = int(input("Target Account ID (1-based): "))
                    if not (1 <= dst <= num_accounts):
                        print("Invalid account. Please try again.")
                        continue
                    amt = int(input("Amount to transfer: "))
                    break
                except ValueError:
                    print("Invalid input. Please enter numeric values.")
            txn = {'type': 'transfer', 'from': src-1, 'to': dst-1, 'amount': amt}

        else:
            print("Unknown command. Please enter d, w, t, or e.")
            continue

        p = Process(target=worker, args=(txn, shm.name, num_accounts, semaphores, log_list))
        p.start()
        p.join()

        txn, success, details = log_list[-1]
        status = "Success" if success else "Failed"
        print(f"{details} ({status})")
        print("Updated balances:")
        for idx, bal in enumerate(accounts):
            print(f"  Account {idx+1}: {bal}")

    print("\n=== Summary ===")
    print("Final balances:")
    for idx, bal in enumerate(accounts):
        print(f"Account {idx+1}: {bal}")
    print("\nTransaction log:")
    for i, (txn, success, details) in enumerate(log_list, 1):
        status = "Success" if success else "Failed"
        print(f"{i}. {details} ({status})")

    shm.close()
    shm.unlink()

if __name__ == "__main__":
    interactive_mode()