from app.utils.supabase import get_supabase_client
from flask import session

def fetch_all_users():
    try:
        response = supabase.table("users").select("*").execute()

        if response.data:
            print("Users Table Content:")
            for user in response.data:
                print(user)
        else:
            print("No users found.")
    except Exception as e:
        print("Error fetching users:", str(e))

if __name__ == "__main__":
    # Create the Supabase client
    supabase = get_supabase_client()
    user_email = session['email']
    gmail_address = session['gmail_address']
    access_token = session['token']
    refresh_token = session['refresh_token']
    token_expiry = session['token_expiry']  # Should be a datetime string
    history_id = session.get('history_id')  # Optional
    print(user_email, gmail_address, access_token, refresh_token, token_expiry, history_id)
    fetch_all_users()


    # Simple test: Fetch from any table (like 'users' if you already have one)
    try:
        response = supabase.table("users").select("*").limit(1).execute()
        print("Connection Successful ✅")
        print("Sample Data:", response.data)
    except Exception as e:
        print("Connection Failed ❌")
        print("Error:", str(e))
