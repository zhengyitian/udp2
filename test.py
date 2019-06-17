import uuid,binascii

b = str(uuid.uuid1())
print b
s = b.replace('-','')
s1 = binascii.unhexlify(s)
print len(s1)
