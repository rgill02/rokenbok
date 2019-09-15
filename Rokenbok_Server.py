#Imports
#from Rokenbok_Hub import Rokenbok_Hub
from Rokenbok_Hub import Rokenbok_Hub
from Rokenbok_Controller import Rokenbok_Controller
import queue
import socket
import time
import threading
import sys
from Rokenbok_Client import Message_Type

################################################################################
MSG_LEN = 3	#bytes per message
UPDATE_TIME = 1

################################################################################
class Rokenbok_Server:
	"""
	The server that accepts client connections and lets them control the cars 
	remotely
	"""
	############################################################################
	def __init__(self, ip='127.0.0.1', port=8080):
		"""
		PURPOSE: creates a new Rokenbok_Server
		ARGS:
			ip (str): ip address of server
			port (int): port of server
		RETURNS: new instance of a Rokenbok_Server
		NOTES:
		"""
		#Save arguments
		self.ip = str(ip)
		self.port = int(port)

		#Create hub
		self.rh = Rokenbok_Hub()
		
		#Create controllers
		self.avail_controllers = queue.LifoQueue()
		for ii in range(8):
			rc = Rokenbok_Controller(8 - ii, self.rh)
			self.avail_controllers.put(rc)
		
		#Create listener socket
		self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.listen_socket.bind((self.ip, self.port))
		#Start listening for connections
		self.listen_socket.listen(8)

		#Create variables for handler threads
		self.run_threads = threading.Event()
		self.run_threads.set()
		self.threads = [None] * 8
		self.thread_times = [0] * 8

		#Thread for accepting connections
		self.listen_thread = threading.Thread(target=self.accept_connections)
		self.listen_thread.start()

		print("Starting server at ip %s on port %d..." % (self.ip, self.port))

	############################################################################
	def __del__(self):
		"""
		PURPOSE: performs any necessary cleanup
		ARGS: none
		RETURNS: none
		NOTES:
		"""
		if self.listen_thread:
			self.stop()

	############################################################################
	def sock_send(self, sock, msg):
		"""
		PURPOSE: sends an entire fixed length message
		ARGS:
			sock (socket): socket to send on
			msg (bytes): message to send
		RETURNS: none
		NOTES: raises a RuntimeError if socket connection breaks
		"""
		bytes_sent = 0
		while bytes_sent < MSG_LEN:
			sent = sock.send(msg[bytes_sent:])
			if sent == 0:
				raise RuntimeError("Socket broken")
			bytes_sent += sent

	############################################################################
	def sock_recv(self, sock):
		"""
		PURPOSE: receives an entire fixed length message
		ARGS:
			sock (socket): socket to receive on
		RETURNS (bytes): array of bytes representing message
		NOTES: riases a RuntimeError is socket conneciton breaks
		"""
		chunks = bytes()
		bytes_recvd = 0
		while bytes_recvd < MSG_LEN:
			chunk = sock.recv(MSG_LEN)
			if chunk == b'':
				raise RuntimeError("Socket broken")
			chunks += chunk
			bytes_recvd += len(chunk)
		return chunks

	############################################################################
	def handle_client(self, conn, addr, rc):
		"""
		PURPOSE: handles a client who gets a controller
		ARGS:
			conn (socket): the socket to communicate to the client on
			addr (str): the ip address of the client
			rc (Rokenbok_Controller): the controller the client gets
		RETURNS: none
		NOTES: should be run in a seperate thread
		"""
		my_idx = rc.player - 1
		conn_alive = True

		#Send and receive to and from client
		while conn_alive and self.run_threads.is_set():
			try:
				#Handle message from client
				msg = self.sock_recv(conn)
				if msg[0] == Message_Type.KEY_PRESS.value:
					#Handle key press
					if msg[2]:
						rc.press_key(msg[1])
					else:
						rc.release_key(msg[1])
				elif msg[0] == Message_Type.END.value:
					#Handle end of connection
					self.sock_send(conn, bytes([Message_Type.END.value, 0, 0]))
					conn_alive = False
				#Send update to client if needed
				cur_time = time.time()
				if (cur_time - self.thread_times[my_idx]) > UPDATE_TIME:
					msg = bytes([Message_Type.TRUE_SEL.value, rc.get_sel(), 0])
					self.sock_send(conn, msg)
					self.thread_times[my_idx] = cur_time
			except Exception as e:
				conn_alive = False
				print("Exception in %s" % addr)
				print(e)
			time.sleep(0.01)

		#Connection is no longer alive
		try:
			self.sock_send(conn, bytes([Message_Type.END.value, 0, 0]))
		except:
			pass
		conn.close()
		rc.release_all_and_deselect()
		self.avail_controllers.put(rc)
		print("Closing connection %s" % addr)
		#Kill thread
		sys.exit()

	############################################################################
	def accept_connections(self):
		"""
		PURPOSE: waits for and accepts connections
		ARGS: none
		RETURNS: none
		NOTES: runs in an infinite loop, may want to wrap in try catch and 
			   catch keyboard interrupt to kill it
		"""
		print("Listening for connecitons...")
		while True:
			try:
				conn, addr = self.listen_socket.accept()
				addr = addr[0]
			except:
				break
			print("Got connection from %s" % addr)
			if self.avail_controllers.empty():
				print("No available controllers. Closing connection %s" % addr)
				self.sock_send(conn, bytes([Message_Type.FULL.value, 0, 0]))
				conn.close()
			else:
				rc = self.avail_controllers.get()
				idx = rc.player - 1
				client = threading.Thread(target=self.handle_client, args=(conn, addr, rc))
				self.threads[idx] = client
				self.sock_send(conn, bytes([Message_Type.START.value, 0, 0]))
				client.start()

	############################################################################
	def stop(self):
		"""
		PURPOSE: closes all connections to client
		ARGS: none
		RETURNS: none
		NOTES:
		"""
		print("Shutting down")
		self.run_threads.clear()
		#Wait for threads to die
		time.sleep(0.2)
		#Close listening socket
		self.listen_socket.close()
		#Stop hub
		self.rh.stop()
		#Join listen thread
		if self.listen_thread:
			self.listen_thread.join()
			self.listen_thread = None

	############################################################################

################################################################################
if __name__ == "__main__":
	server = Rokenbok_Server("192.168.1.198")

	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt as e:
		pass

	server.stop()
