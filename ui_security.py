# ui_security.py
def get_visitor_details(plate):
    print("\n[SECURITY INPUT REQUIRED]")
    print(f"Auto-detected Plate: {plate}")
    name = input("Enter visitor name: ")
    purpose = input("Enter purpose of visit: ")
    flat = input("Enter flat number: ")
    return {
        'name': name,
        'purpose': purpose,
        'flat': flat,
        'plate': plate
    }
