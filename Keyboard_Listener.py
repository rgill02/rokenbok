#Imports
import keyboard

################################################################################
class Keyboard_Listener:
	"""
	I wanted a keyboard listener that when a key is pressed (and possibly held) 
	it would trigger one key press event and one only. Same for released. All
	listeners I could find would generate infinite key press events if the key
	was held. Since that behavior was undesireable I made this one which only
	generates a single key press event if the key is pressed and held
	"""
	############################################################################
	def __init__(self):
		"""
		PURPOSE: creates a new Keyboard_Listener
		ARGS: none
		RETURNS: new instance of a Keyboard_Listener
		NOTES:
		"""
		self.key_states = [False] * 255
		self.press_cb = None
		self.release_cb = None

	############################################################################
	def __del__(self):
		"""
		PURPOSE: performs any necessary cleanup
		ARGS: none
		RETURNS: none
		NOTES:
		"""
		self.stop()

	############################################################################
	def start(self):
		"""
		PURPOSE: starts the keyboard listener
		ARGS: none
		RETURNS: none
		NOTES:
		"""
		keyboard.hook(self.on_key_event)

	############################################################################
	def stop(self):
		"""
		PURPOSE: stops the keyboard listener
		ARGS: none
		RETURNS: none
		NOTES:
		"""
		keyboard.unhook_all()

	############################################################################
	def on_key_event(self, e):
		"""
		PURPOSE: keyboard module calls this on a key press event and this 
				 handles that event
		ARGS:
			e (KeyboardEvent): the keyboard event
		RETURNS: none
		NOTES:
		"""
		if len(e.name) == 1:
			code = ord(e.name)
		elif e.name == 'up':
			code = 24
		elif e.name == 'down':
			code = 25
		elif e.name == 'right':
			code = 26
		elif e.name == 'left':
			code = 27
		else:
			return

		if e.event_type == 'down':
			if not self.key_states[code]:
				self.key_states[code] = True
				if self.press_cb:
					self.press_cb(code)
		elif e.event_type == 'up':
			self.key_states[code] = False
			if self.release_cb:
				self.release_cb(code)

	############################################################################
	def set_press_cb(self, cb):
		"""
		PURPOSE: sets the callback function for when a key is pressed
		ARGS:
			cb (function): callback function that takes in scan code
		RETURNS: none
		NOTES:
		"""
		self.press_cb = cb

	############################################################################
	def set_release_cb(self, cb):
		"""
		PURPOSE: sets the callback function for when a key is released
		ARGS:
			cb (function): callback function that takes in scan code
		RETURNS: none
		NOTES:
		"""
		self.release_cb = cb

	############################################################################

################################################################################
if __name__ == "__main__":
	import time

	def key_pressed(scan_code):
		print("Pressed %d" % scan_code)

	def key_released(scan_code):
		print("Released %d" % scan_code)

	kl = Keyboard_Listener()
	kl.set_press_cb(key_pressed)
	kl.set_release_cb(key_released)

	kl.start()

	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt as e:
		pass

	kl.stop()
