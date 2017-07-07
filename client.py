#version 2

import socket
import sys
import threading
from merkle import MarkleTree

hash_list = ['a5','b1','c1','d1','a2','b7','c2'] # this will be prepared by the merkle tree script

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = socket.gethostname()

port = 9999

s.connect((host,port))

print('connection established with host')

mt_b = MarkleTree('testB')

b_tophash = mt_b._tophash

def MTDiff1(mt_b,b_tophash,csocket):
	msg  = csocket.recv(1024).decode('ascii').split()
	a_tophash = msg[0]
	a_item = msg[1]
	if a_tophash == b_tophash:
		print("Top hash is equal for %s and %s" % (mt_b._root, a_item))
		msg = "1 " + mt_b._root
		csocket.send(msg.encode('ascii'))
	else:
		msg = "0 " + mt_b._root
		csocket.send(msg.encode('ascii'))

		b_value = mt_b._mt[b_tophash] 
		b_child = b_value[1]    # retrive the child list for merkle tree a

		for itemhash, item in b_child.items():
			msg = csocket.recv(1024).decode('ascii').split()
			a_hash = msg[0]
			a_item = msg[1]
			if a_hash == itemhash:
				msg = "1 " + item
				csocket.send(msg.encode('ascii'))
				print("Info: SAME : %s" % item)
			else:
				msg = "0 " + item
				csocket.send(msg.encode('ascii'))
				print("Info: DIFFERENT : %s" % item)
				temp_value = mt_b._mt[itemhash]
				if len(temp_value[1]) > 0:      # check if this is a directory
					MTDiff1(mt_b, itemhash, csocket)

MTDiff1(mt_b, b_tophash,s)