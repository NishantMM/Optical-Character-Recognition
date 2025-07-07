# notifier.py
import random
import time

# In a real system, this would send a Telegram/email and wait for reply
def request_approval(info):
    print(f"\n[REQUEST] Asking approval for flat {info['flat']}...")
    print(f"Visitor: {info['name']}, Purpose: {info['purpose']}, Plate: {info['plate']}")
    print("(Simulating message sent to resident app...)\n")

# Simulated approval logic (randomly allow or deny)
def get_approval_status(flat):
    time.sleep(2)
    return random.choice(["Approved", "Denied"])
