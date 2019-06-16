import hashlib, binascii,time
while True:
    dk = hashlib.pbkdf2_hmac('sha256', b'password', b'saltxx', 1000)
    print time.time(),binascii.hexlify(dk)
b'0394a2ede332c9a13eb82e9b24631604c31df978b4e2f0fbd2c549944f9d79a5'