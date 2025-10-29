from db import users_col
from auth import hash_password
from datetime import datetime, timedelta

# List of all the dummy users with rich profile data
dummy_users = [
    {
        "username": "admin", "full_name": "Admin User", "email": "admin@example.com",
        "password": "adminpassword123", "role": "admin", "employee_id": "A001",
        "join_date": datetime.now() - timedelta(days=30), "job_title": "System Administrator",
        "department": "IT", "contact_number": "+91 9876543210",
        "profile_pic_url": "https://placehold.co/400x400/000000/FFFFFF/png?text=AU"
    },
    {
        "username": "hr", "full_name": "Harriet Ross", "email": "hr@example.com",
        "password": "hrpassword123", "role": "hr", "employee_id": "H001",
        "join_date": datetime.now() - timedelta(days=20), "job_title": "HR Manager",
        "department": "Human Resources", "contact_number": "+91 9876543211",
        "profile_pic_url": "https://placehold.co/400x400/3E3232/FFFFFF/png?text=HR"
    },
    {
        "username": "emily.jones", "full_name": "Emily Jones", "email": "emily.jones@example.com",
        "password": "password123", "role": "employee", "employee_id": "E002",
        "join_date": datetime.now() - timedelta(days=5), "job_title": "Frontend Developer",
        "department": "Engineering", "contact_number": "+91 9123456780",
        "profile_pic_url": "https://placehold.co/400x400/5B0888/FFFFFF/png?text=EJ"
    },
    {
        "username": "david.chen", "full_name": "David Chen", "email": "david.chen@example.com",
        "password": "password123", "role": "employee", "employee_id": "E003",
        "join_date": datetime.now() - timedelta(days=15), "job_title": "Backend Developer",
        "department": "Engineering", "contact_number": "+91 9123456781",
        "profile_pic_url": "https://placehold.co/400x400/E55604/FFFFFF/png?text=DC"
    },
    {
        "username": "sophia.patel", "full_name": "Sophia Patel", "email": "sophia.patel@example.com",
        "password": "password123", "role": "employee", "employee_id": "E004",
        "join_date": datetime.now() - timedelta(days=4), "job_title": "Marketing Specialist",
        "department": "Marketing", "contact_number": "+91 9123456782",
        "profile_pic_url": "https://placehold.co/400x400/26577C/FFFFFF/png?text=SP"
    },
    {
        "username": "ben.carter", "full_name": "Ben Carter", "email": "ben.carter@example.com",
        "password": "password123", "role": "employee", "employee_id": "E005",
        "join_date": datetime.now() - timedelta(days=60), "job_title": "Project Manager",
        "department": "Product", "contact_number": "+91 9123456783",
        "profile_pic_url": "https://placehold.co/400x400/508D69/FFFFFF/png?text=BC"
    },
    {
        "username": "olivia.wong", "full_name": "Olivia Wong", "email": "olivia.wong@example.com",
        "password": "password123", "role": "employee", "employee_id": "E006",
        "join_date": datetime.now() - timedelta(days=90), "job_title": "Content Strategist",
        "department": "Marketing", "contact_number": "+91 9123456784",
        "profile_pic_url": "https://placehold.co/400x400/C8A582/FFFFFF/png?text=OW"
    }
]

def setup_dummy_accounts():
    """Checks for each dummy user and creates them if they don't exist."""
    print("Setting up dummy accounts with rich profile data...")
    for user_data in dummy_users:
        if users_col.find_one({"username": user_data["username"]}):
            print(f"-> User '{user_data['username']}' already exists. Skipping.")
            continue
        hashed_pass = hash_password(user_data["password"])
        user_doc = user_data.copy()
        del user_doc["password"]
        user_doc["password_hash"] = hashed_pass
        users_col.insert_one(user_doc)
        print(f"✅ User '{user_data['username']}' created successfully!")
    print("\nDummy account setup complete.")

if __name__ == "__main__":
    setup_dummy_accounts()