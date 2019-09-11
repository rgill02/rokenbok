#Imports
from Rokenbok_Hub import Rokenbok_Hub, Button

################################################################################
class Rokenbok_Controller:
	"""
	Represents a controller for the rokenbok hub, but for the computer. Maps 
	key presses to button pushes on the controller.
	"""
	############################################################################
	def __init__(self, player, hub):
		"""
		PURPOSE: creates a new Rokenbok_Controller
		ARGS:
			player (int): player number (1-8)
			hub (Rokenbok_Hub): the hub this controller belongs to
		RETURNS: new instance of a Rokenbok_Controller
		NOTES:
		"""
		#Save player
		if player < 1 or player > 8:
			raise ValueError("Argument 'player' must be between 1 and 8!")
		self.player = player

		#Save hub
		self.hub = hub

		#Define default keymapping
		self.key_map = {
			24 : Button.FORWARD,	#up arrow
			25 : Button.BACK,		#down arrow
			26 : Button.RIGHT,		#right arrow
			27 : Button.LEFT,		#left arrow
			ord('s') : Button.A,
			ord('w') : Button.B,
			ord('a') : Button.X,
			ord('d') : Button.Y,
			ord('q') : Button.SLOW
		}

	############################################################################
	def get_sel(self):
		"""
		PURPOSE: gets the current selection of this controller
		ARGS: none
		RETURNS: (int) current selection (1-8) or 0 if nothing is selected
		NOTES:
		"""
		#TODO change to current selection rather than desired
		cur_sel = self.hub.get_sels()[1][self.player - 1]
		if cur_sel == 0xFF:
			return 0
		return cur_sel + 1

	############################################################################
	def press_key(self, ascii_code):
		"""
		PURPOSE: reacts to a key press
		ARGS:
			ascii_code (int): the ascii code of the key pressed
		RETURNS: none
		NOTES:
		"""
		if ascii_code in self.key_map:
			self.hub.cmd(self.key_map[ascii_code], self.player, True)
		elif ascii_code >= 49 or ascii_code <= 56:
			#number keys 1 - 8 were pressed
			des_sel = ascii_code - 48
			self.hub.change_sel(self.player, des_sel)
		elif ascii_code == 114:
			#r
			self.hub.restart_arduino()

	############################################################################
	def release_key(self, ascii_code):
		"""
		PURPOSE: reacts to a key release
		ARGS:
			ascii_code (int): the ascii code of the key released
		RETURNS: none
		NOTES:
		"""
		if ascii_code in self.key_map:
			self.hub.cmd(self.key_map[ascii_code], self.player, False)

	############################################################################

################################################################################