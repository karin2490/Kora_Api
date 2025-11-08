import bcrypt

password = "Kora2024*"
salt = bcrypt.gensalt()
hash_generado = bcrypt.hashpw(password.encode('utf-8'), salt)

print("=" * 50)
print("NUEVO HASH PARA LA BASE DE DATOS")
print("=" * 50)
print(hash_generado.decode('utf-8'))
print("=" * 50)