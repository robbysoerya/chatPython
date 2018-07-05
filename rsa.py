from Crypto.Util.number import *

p = getStrongPrime(512)
q = getStrongPrime(512)
e = 0x10001
N = p * q
M = (p - 1) * (q - 1)
d = inverse(e,M)

def key():
	priv = open('priv.pem','wb').write(str(d))
	pub = open('pub.pem','wb').write(str(N))
	return N

def encrypt(message,public):
	cipher = int(message.strip().encode('hex'),16)
	c = pow(cipher,e,public)
	return c

def decrypt(cipher):
	priv = open('priv.pem','rb').read()
	pub = open('pub.pem','rb').read()
	plain = pow(cipher,int(priv),int(pub))
	return '{0:2x}'.format(plain).decode('hex')
