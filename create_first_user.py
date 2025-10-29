from db import users_col
from auth import hash_password

# --- !! CUSTOMIZE YOUR ADMIN DETAILS HERE !! ---
username = "admin"
password = "adminpassword123" # Use a strong, memorable password
email = "admin@example.com"
role = "admin"
employee_id = "A001"
# ------------------------------------------------

def create_admin_user():
    """Checks if the admin user exists, and if not, creates one."""
    
    # This is the line that will fail if your DB connection is broken
    if users_col is None:
        print("❌ ERROR: Database connection failed. Cannot create user.")
        print("Please check your .env file and MongoDB IP Whitelist.")
        return

    # Check if a user with this username already exists
    if users_col.find_one({"username": username}):
        print(f"User '{username}' already exists.")
        return

    # Hash the password
    hashed_pass = hash_password(password)
    
    # Create the user document
    user_document = {
        "username": username,
        "email": email,
        "password_hash": hashed_pass,
        "role": role,
        "employee_id": employee_id
    }
    
    # Insert the new user into the 'users' collection
    users_col.insert_one(user_document)
    print(f"✅ Admin user '{username}' created successfully!")
    print("You can now run 'streamlit run app.py' and log in.")

# Run the function
if __name__ == "__main__":
    create_admin_user()