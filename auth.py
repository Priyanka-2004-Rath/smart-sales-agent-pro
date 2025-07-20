import bcrypt
import pandas as pd
import os

USER_CSV = "users.csv"

def load_users():
    if os.path.exists(USER_CSV):
        try:
            return pd.read_csv(USER_CSV)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=["username", "password"])
    else:
        return pd.DataFrame(columns=["username", "password"])


def save_user(username, hashed_pw):
    df = load_users()
    new_user = pd.DataFrame([[username, hashed_pw]], columns=["username", "password"])
    df = pd.concat([df, new_user], ignore_index=True)
    df.to_csv(USER_CSV, index=False)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def user_exists(username):
    df = load_users()
    return username in df["username"].values

def validate_user(username, password):
    df = load_users()
    user_row = df[df["username"] == username]
    if user_row.empty:
        return False
    return check_password(password, user_row.iloc[0]["password"])
