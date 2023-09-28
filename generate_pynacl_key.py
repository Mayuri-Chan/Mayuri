import nacl.utils
from base64 import b64encode
from colorama import Fore, Style
from nacl.public import PrivateKey, SealedBox
from nacl.encoding import Base64Encoder

print("Generating keys...")
sk = PrivateKey.generate()
pk = sk.public_key
pk = pk.encode(encoder=Base64Encoder).decode()

with open("private.key", 'w') as fs:
	fs.write(sk.encode(encoder=Base64Encoder).decode())

print(Fore.GREEN + "Secret key saved to private.key")
print(Fore.RED + "WARNING: Store this file in a secure place\nyou can't decrypt the encrypted backup file without this!")
print("And don't share it publicly, Treat this file like you treat your password")

with open("public.key", 'w') as fp:
	fp.write(pk)

print("")
print(Fore.GREEN + "Public key saved to public.key")
print(f"Your Public Key: {pk}")
