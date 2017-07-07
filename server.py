#version 2

import socket
import threading
from merkle import MarkleTree

servsocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

host = socket.gethostname()

port = 9999

servsocket.bind((host,port))

servsocket.listen(1)

mt_a = MarkleTree('testA')

a_tophash = mt_a._tophash

def client1(mt_a, a_tophash, csocket, add):
	MTDiff1(mt_a, a_tophash, csocket, add)
	csocket.close()

def MTDiff1(mt_a,a_tophash,csocket,add):
	msg = a_tophash + " " + mt_a._root
	csocket.send(msg.encode('ascii'))
	msg_rcvd = csocket.recv(1024).decode('ascii').split()
	if msg_rcvd[0] != '0':
		print("Top hash is equal for %s and %s" % (mt_a._root, msg_rcvd[1]))
	else:
		a_value = mt_a._mt[a_tophash]
		a_child = a_value[1]    # retrive the child list for merkle tree a

		for itemhash, item in a_child.items():
			msg = itemhash + " " + item
			csocket.send(msg.encode('ascii'))
			msg_rcvd = csocket.recv(1024).decode('ascii').split()
			if msg_rcvd[0] != '0':
				print(add," : ","Info: SAME : %s" % item)
			else:
				print(add," : ","Info: DIFFERENT : %s" % item)
				temp_value = mt_a._mt[itemhash]
				if len(temp_value[1]) > 0:      # check if this is a directory
					MTDiff1(mt_a, itemhash, csocket, add)


while True: 
	
	clientsocket,addr = servsocket.accept()
	print("Got a connection from %s" % str(addr))

	t1 = threading.Thread(target = client1, args = (mt_a,a_tophash,clientsocket,addr))

	t1.start()