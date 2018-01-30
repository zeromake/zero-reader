import hashlib
from datetime import datetime

paw = "123456".encode()

print("-----------sha-------------")
now = datetime.utcnow()
sha = hashlib.sha256()
sha.update(paw)
print(sha.digest().decode())
print(datetime.utcnow() - now)

print("-----------md5-------------")
now = datetime.utcnow()
md5 = hashlib.md5()
md5.update(paw)
print(md5.digest().decode())
print(datetime.utcnow() - now)

from passlib.hash import sha256_crypt, md5_crypt

paw = "123456"

print("-----------sha-------------")
now = datetime.utcnow()
print(sha256_crypt.hash(paw))
print(datetime.utcnow() - now)

print("-----------md5-------------")
now = datetime.utcnow()
print(md5_crypt.hash(paw))
print(datetime.utcnow() - now)
