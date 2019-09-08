#Imports
import serial
import time
import threading
import keyboard

################################################################################
#Global variables
des_forward = 0
des_back = 0
des_left = 0
des_right = 0
des_a = 0
des_b = 0
des_x = 0
des_y = 0
des_slow = 0
des_sharing = 0
des_priority = 0
des_sel = [0, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
sync_byte = 0b10101010

cur_forward = 0
cur_back = 0
cur_left = 0
cur_right = 0
cur_a = 0
cur_b = 0
cur_x = 0
cur_y = 0
cur_slow = 0
cur_sharing = 0
cur_sel = bytes([0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])

################################################################################
keep_going = True
ser = serial.Serial(port='COM15', baudrate=115200)
time.sleep(3)

def read_state():
	while keep_going:
		sync_count = 0
		while keep_going and sync_count < 2:
			if ser.in_waiting:
				val = int.from_bytes(ser.read(), 'big')
				if val == sync_byte:
					sync_count += 1
				else:
					sync_count = 0
		while keep_going and ser.in_waiting < 18:
			pass
		val = ser.read(18)
		print(val)

def sync_state():
	while keep_going:
		to_write = [
			sync_byte,
			sync_byte,
			des_forward,
			des_back,
			des_left,
			des_right,
			des_a,
			des_b,
			des_x,
			des_y,
			des_slow,
			des_sharing,
			des_priority,
		]
		to_write = bytes(to_write + des_sel)
		ser.write(to_write)
		time.sleep(0.04)

################################################################################
sync_state_thread = threading.Thread(target=sync_state)
sync_state_thread.start()

print("Start")
try:
	while True:
		if keyboard.is_pressed('up arrow'):
			des_forward = 1
		else:
			des_forward = 0
		if keyboard.is_pressed('down arrow'):
			des_back = 1
		else:
			des_back = 0
		if keyboard.is_pressed('left arrow'):
			des_left = 1
		else:
			des_left = 0
		if keyboard.is_pressed('right arrow'):
			des_right = 1
		else:
			des_right = 0
		if keyboard.is_pressed('w'):
			des_b = 1
		else:
			des_b = 0
		if keyboard.is_pressed('s'):
			des_a = 1
		else:
			des_a = 0
		if keyboard.is_pressed('a'):
			des_x = 1
		else:
			des_x = 0
		if keyboard.is_pressed('d'):
			des_y = 1
		else:
			des_y = 0
		if keyboard.is_pressed('q'):
			des_slow = 1
		else:
			des_slow = 0
except KeyboardInterrupt as e:
	pass

keep_going = False
sync_state_thread.join()
ser.close()