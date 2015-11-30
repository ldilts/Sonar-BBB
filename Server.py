#!/usr/bin/python

import socket
import sys
import requests
import json
import datetime
import time
import threading
import urllib2
# from pytz import timezone

class Server:
	'''demonstration class only
		- coded for clarity, not efficiency
	'''
	
	# Constants
	MSGLEN = 16
	# SERVER_URL = 'https://httpbin.org'
	SERVER_URL = 'http://localhost:8000/log/'

	max_distance = 20.0
	current_distance = 0.0
	was_open = False

	ID = 12345

	def __init__(self, sock=None):
		if sock is None:
			self.sock = socket.socket(
				socket.AF_INET, socket.SOCK_STREAM)
		else:
			self.sock = sock

	def connect(self, host, port):
		#self.sock.connect((host, port))
		server_address = (host, port)
		print >>sys.stderr, 'starting up on %s port %s' % server_address
		self.sock.bind(server_address)
		self.sock.listen(1)
		
	def loop(self, arg1, stop_event):
		while (not stop_event.is_set()):
			# Wait for a connection
			print >>sys.stderr, 'waiting for a connection'
			connection, client_address = self.sock.accept()
			
			try:
				print >>sys.stderr, 'connection from', client_address

				# Receive the data in small chunks and retransmit it
				while True:
					data = connection.recv(16)
					print >>sys.stderr, 'received "%s"' % data
					data = data.rstrip('\n')
					if data:
						# print >>sys.stderr, 'sending data back to the client'
						connection.sendall('ok')

						payload = {}

						if float(data) < self.max_distance:
							# door is closed
							if self.was_open == True:
								#Door state has changed!!
								self.was_open = False
								payload = self.pack_json(False)

								#print payload
								self.server_post(payload)
						else:
							#door is open!
							if self.was_open == False:
								#Door state has changed!!
								self.was_open = True
								payload = self.pack_json(True)

								#print payload
								self.server_post(payload)
						
					else:
						print >>sys.stderr, 'no more data from', client_address
						break

			finally:
				# Clean up the connection
				connection.close()
			pass

	# Create JSON file to send to Django				
	def pack_json(self, open):

		# Get current time
		date = datetime.datetime.now()
		# t = pytz.timezone('America/Fortaleza').localize(date)
		
		# Create payload data
		data = {
		  "log_id": self.ID,
		  "log_open": open,
		  "log_date": str(date)
		}
		
		# return json.dumps(data)
		return data
				
	def server_post(self, payload):
		print str(payload)
		r = requests.post(self.SERVER_URL, json = payload)
		print "Status: ", r.status_code
		#print r.content

	def get_stuff(self, arg1, stop_event):
		pass
		# while (not stop_event.is_set()):
		# 	r = requests.get(self.SERVER_URL)
		# 	decoded = json.loads(r.text)
		# 	print >>sys.stderr, 'Got "%s"\n' % decoded
		# 	time.sleep(5)
		# 	pass

# 	def mysend(self, msg, connection):
# 		totalsent = 0
# 		while totalsent < self.MSGLEN:
# 			sent = self.sock.send(msg[totalsent:])
# 			if sent == 0:
# 				raise RuntimeError("socket connection broken")
# 			totalsent = totalsent + sent

	# def myreceive(self, connection):
# 		data = connection.recv(16)
# 		print >>sys.stderr, 'received "%s"' % data
# 		if data:
# 			print >>sys.stderr, 'sending data back to the client'
# 			connection.sendall(data)
# 		else:
# 			print >>sys.stderr, 'no more data from', client_address

while True:
	a_socket = Server()
	a_socket.connect('localhost', 10500)

	threads = [] 

	t1_stop = threading.Event()
	t1 = threading.Thread(target = a_socket.loop, args=(1, t1_stop))

	t2_stop = threading.Event()
	t2 = threading.Thread(target = a_socket.get_stuff, args=(2, t2_stop))

	t1.setDaemon(True)
	t2.setDaemon(True)

	threads.append(t1)
	threads.append(t2)

	t1.start()
	t2.start()

	for x in threads: 
		x.join()
		
	print "Done"
	time.sleep(120)
