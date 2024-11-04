import secrets

def generate_secret_key(lenght=32):
    return secrets.token_hex(lenght)

secret_key = generate_secret_key()
print(f"{secret_key}")