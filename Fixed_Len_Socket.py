#Imports
import socket

################################################################################
class Fixed_Len_Socket:
	"""
	Implements a socket that always sends a message of a fixed length
	"""
	############################################################################
	def __init__(self, msg_len, sock=None):
		"""
		PURPOSE: creates a new Fixed_Len_Socket
		ARGS:
			msg_len (int): number of bytes in each message
			sock (socket): socket to use, if None then creates one
		RETURNS: new instance of a Fixed_Len_Socket
		NOTES:
		"""
		#Save arguments
		self.msg_len = int(msg_len)
		if sock:
			self.sock = sock
		else:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	############################################################################
	def __del__(self):
		"""
		PURPOSE: performs any necessary cleanup
		ARGS: none
		RETURNS: none
		NOTES:
		"""
		self.close()

	############################################################################
	def connect(self, ip, port):
		"""
		PURPOSE: connects to an open socket on the other end
		ARGS:
			ip (str): ip address of the socket to connec to
			port (int): the port to connect with
		RETURNS: none
		NOTES:
		"""
		self.sock.connect((ip, port))

	############################################################################
	def send(self, msg):
		"""
		PURPOSE: sends an entire fixed length message
		ARGS:
			msg (bytes): message to send
		RETURNS: none
		NOTES: raises a RuntimeError if socket connection breaks
		"""
		bytes_sent = 0
		while bytes_sent < self.msg_len:
			sent = self.sock.send(msg[bytes_sent:])
			if sent == 0:
				raise RuntimeError("Socket broken")
			bytes_sent += sent

	############################################################################
	def recv(self):
		"""
		PURPOSE: receives an entire fixed length message
		ARGS: none
		RETURNS (bytes): array of bytes representing message
		NOTES: raises a RuntimeError is socket conneciton breaks
		"""
		chunks = bytes()
		bytes_recvd = 0
		while bytes_recvd < self.msg_len:
			chunk = self.sock.recv(self.msg_len)
			if chunk == b'':
				raise RuntimeError("Socket broken")
			chunks += chunk
			bytes_recvd += len(chunk)
		return chunks

	############################################################################
	def close(self):
		"""
		PURPOSE: closes the socket if its open
		ARGS: none
		RETURNS: none
		NOTES:
		"""
		self.sock.close()

	############################################################################

################################################################################