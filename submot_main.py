import RPi.GPIO as GPIO
import time

class SubMot:
	def start_submot(this, input):
		pin=18
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pin,GPIO.OUT)
		p=GPIO.PWM(pin,50)
		p.start(0)
		cnt=0
		try:
			if input =='start':
				print("Main Start!")
			if input == "L":
				while True:
					p.ChangeDutyCycle(12.5)
					print('angle:12.5')
					p.stop()
					break
			elif input == "R":
				while True:
					p.ChangeDutyCycle(2.5)
					print('angle:12.5')
					p.stop()
					break
		except KeyboardInterrupt:
			p.stop()
			
		GPIO.cleanup()

# subobj = SubMot()
# subobj.start_submot()