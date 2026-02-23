from pwdlib import PasswordHash

password_hash = PasswordHash.recommended() 

def hash_password(h_password: str):
    return password_hash.hash(h_password)

def verify_password(plain_password: str, hashed_password: str):
    return password_hash.verify(plain_password, hashed_password)