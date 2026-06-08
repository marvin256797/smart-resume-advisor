def sign_up(email, password):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        # Create profile
        supabase.table("profiles").insert({
            "id": response.user.id,
            "email": email
        }).execute()
        return True, response
    except Exception as e:
        return False, str(e)

def sign_in(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return True, response
    except Exception as e:
        return False, str(e)