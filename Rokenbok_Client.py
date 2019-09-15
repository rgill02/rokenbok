#Imports
from enum import Enum
from Keyboard_Listener import Keyboard_Listener
import threading
import time
from Fixed_Len_Socket import Fixed_Len_Socket
import sys
import queue

################################################################################
MSG_LEN = 3	#bytes per message

################################################################################
class Message_Type(Enum):
	START = 1	#server sends at the beginning of a connection if a controller is available
	FULL = 2	#server sends at the beginning of a conneciton (right before closing the connection) if a controller is unavailable
	KEY_PRESS = 3	#client sends to indicate they pressed a key
	TRUE_SEL = 4	#server sends to update client on their selected value
	END = 5	#client or server sends to indicate connection is closing

################################################################################
class Rokenbok_Client:
	"""
	The client that connects to a server to control the cars
	"""
	############################################################################
	def __init__(self, ip='127.0.0.1', port=8080):
		"""
		PURPOSE: creates a new Rokenbok_Client
		ARGS:
			ip (str): ip address of server to connect to
			port (int): the port to connect to the server on
		RETURNS: new instance of a Rokenbok_Client
		NOTES:
		"""
		#Save arguments
		self.ip = str(ip)
		self.port = int(port)

		#Connect to server and receive opening message
		self.sock = Fixed_Len_Socket(MSG_LEN)
		try:
			self.sock.connect(self.ip, self.port)
			msg = self.sock.recv()
			if msg[0] == Message_Type.FULL.value:
				print("Server is full, try again later...")
				self.sock.send(bytes([Message_Type.END.value, 0, 0]))
				self.sock.close()
				sys.exit()
			elif msg[0] != Message_Type.START.value:
				print("Received unknown message from server, closing connection...")
				self.sock.send(bytes[Message_Type.END.value, 0, 0])
				self.sock.close()
				sys.exit()
		except Exception as e:
			print("Could not connect to server...")
			sys.exit()

		#We have a controller allocated to us on the server so start the 
		#communication threads
		self.keep_going = threading.Event()
		self.keep_going.set()
		self.key_q = queue.Queue()
		self.update_time = 1
		self.listen_thread = threading.Thread(target=self.listen)
		self.transmit_thread = threading.Thread(target=self.transmit)
		self.listen_thread.start()
		self.transmit_thread.start()

		#Start keyboard listener
		self.kl = Keyboard_Listener()
		self.kl.set_press_cb(self.key_pressed)
		self.kl.set_release_cb(self.key_released)
		self.kl.start()

	############################################################################
	def listen(self):
		"""
		PURPOSE: listens for updates from the server
		ARGS: none
		RETURNS: none
		NOTES: should be called in a seperate thread
		"""
		print("DEBUG: listen thread starting...")
		read_time = 0

		try:
			while self.keep_going.is_set():
				cur_time = time.time()
				if (cur_time - read_time) > self.update_time:
					msg = self.sock.recv()
					if msg[0] == Message_Type.TRUE_SEL.value:
						print("Selected = %d" % msg[1])
					elif msg[0] == Message_Type.END.value:
						self.keep_going.clear()
					read_time = cur_time
				time.sleep(0.2)
		except Exception as e:
			print("DEBUG: exception '%s' in listen thread!" % type(e))
			print(e)

		self.keep_going.clear()
		print("DEBUG: listen thread ending...")

	############################################################################
	def transmit(self):
		"""
		PURPOSE: sends key presses to the server
		ARGS: none
		RETURNS: none
		NOTES:
		"""
		print("DEUBG: transmit thread starting...")
		try:
			while self.keep_going.is_set():
				while self.key_q.qsize():
					k = self.key_q.get()
					self.sock.send(bytes([Message_Type.KEY_PRESS.value, k[0], k[1]]))
				time.sleep(0.01)
		except Exception as e:
			print("DEBUG: exception '%s' in transmit thread!" % type(e))
			print(e)

		self.keep_going.clear()
		print("DEBUG: transmit thread ending...")

	############################################################################
	def key_pressed(self, ascii_code):
		"""
		PURPOSE: callback for when a key is pressed
		ARGS:
			ascii_code (int): the ascii code representing the pressed key
		RETURNS: none
		NOTES:
		"""
		self.key_q.put((ascii_code, 1))

	############################################################################
	def key_released(self, ascii_code):
		"""
		PURPOSE: callback for when a key is released
		ARGS:
			ascii_code (int): the ascii code representing the released key
		RETURNS: none
		NOTES:
		"""
		self.key_q.put((ascii_code, 0))

	############################################################################
	def stop(self):
		"""
		PURPOSE: closes connection to the server
		ARGS: none
		RETURNS: none
		NOTES:
		"""
		self.kl.stop()
		self.keep_going.clear()
		if self.listen_thread:
			self.listen_thread.join()
			self.listen_thread = None
		if self.transmit_thread:
			self.transmit_thread.join()
			self.transmit_thread = None
		try:
			self.sock.send(bytes([Message_Type.END.value, 0, 0]))
		except Exception as e:
			pass
		self.sock.close()

	############################################################################

################################################################################
if __name__ == "__main__":
	client = Rokenbok_Client("192.168.1.198")
	print("Connected to client")

	try:
		while client.keep_going.is_set():
			time.sleep(1)
	except KeyboardInterrupt as e:
		pass

	print("Closing connection...")
	client.stop()
