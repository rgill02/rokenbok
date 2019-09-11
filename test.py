#Imports
from Rokenbok_Hub import Rokenbok_Hub
from Rokenbok_Controller import Rokenbok_Controller
from Keyboard_Listener import Keyboard_Listener
import time

################################################################################
#Create hub
rh = Rokenbok_Hub()

#Create controller
rc = Rokenbok_Controller(1, rh)

#Create keyboard listener
kl = Keyboard_Listener()

#Attach key events
kl.set_press_cb(rc.press_key)
kl.set_release_cb(rc.release_key)

#Start keyboard listener
kl.start()

#Show current selection
try:
	while True:
		print("Selected = %d" % rc.get_sel())
		time.sleep(5)
except KeyboardInterrupt as e:
	pass

#Stop keyboard listener
kl.stop()
#Stop hub
rh.stop()