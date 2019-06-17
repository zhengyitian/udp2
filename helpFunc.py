import hashlib, binascii,time,uuid,redis
bufferSize = 1000
conn = redis.Redis(host='localhost', port=6379, db=0)
import re as re3
def cut_text(text,lenth): 
    textArr = re3.findall('.{'+str(lenth)+'}', text) 
    textArr.append(text[(len(textArr)*lenth):]) 
    return textArr

def re_get(k):
    global conn
    try:
        return conn.get(k)
    except:
        conn = redis.Redis(host='localhost', port=6379, db=0)
        return conn.get(k)        

def re_set(k,s):
    global conn
    try:
        conn.set(k,s)
    except:
        conn = redis.Redis(host='localhost', port=6379, db=0)
        conn.set(k,s)
def re_del(k):
    global conn
    try:
        conn.delete(k)
    except:
        conn = redis.Redis(host='localhost', port=6379, db=0)
        conn.delete(k)


def makePack(s,salt):
    u = str(uuid.uuid1())
    u2 = binascii.unhexlify(u.replace('-',''))
    s1 = u2+s
    dk = hashlib.pbkdf2_hmac('md5', s1, salt, 2)
    s2 = s1+dk
    return u,s2
def checkPackValid(s,u,salt):
    if len(s)<16:
        return ''
    s1 = s[-16:]
    s2 = s[:-16]
    uuid = binascii.unhexlify(u.replace('-',''))
    dk = hashlib.pbkdf2_hmac('md5', s2, salt, 2)
    if dk != s1:
        return ''
    if s2[:16] != uuid:
        return ''
    return s2[16:]
def circleBig(a,b,bufferSize=bufferSize):
    if a==b:
        return False
    if a>b and (a-b)<(bufferSize/2):
        return True
    if a<b and (b-a)>(bufferSize/2):
        return True
    return False

def circleRange(a,b,bufferSize=bufferSize):  # return [,)  same as range
    temp = a
    ret = []
    while True:
        if not circleBig(b,temp):
            break
        ret.append(temp)
        temp = circleAdd(temp,1)
    return ret
def circleMax(l,bufferSize=bufferSize):
    ret = None
    k = l.keys()
    for i in k:
        if ret==None:
            ret = i
        if circleBig(i,ret):
            ret = i
    return ret


def circleAddOne(a,bufferSize=bufferSize):
    if a == bufferSize-1:
        return 0
    return a+1

def circleAdd(a,b,bufferSize=bufferSize):
    ret = a
    for i in range(b):
        ret = circleAddOne(ret)
    return ret


if __name__ == '__main__':
    u,s = makePack('sdfew','salt')
    print u,s
    s2 = checkPackValid(s, u, 'salt')
    print s2

          