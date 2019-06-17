import hashlib, binascii,time

dk = hashlib.pbkdf2_hmac('md5', b'password', b'saleetxx', 1)
print len(dk),binascii.hexlify(dk)
  