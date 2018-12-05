import RPi.GPIO as GPIO
import time

class SubMot:
	def start_submot(this, inp):
		pin=18

		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pin,GPIO.OUT)
		p=GPIO.PWM(pin,50)
		p.start(0)
		try:
			while True:
				# inp=input("L/R/C : ")
				if inp == "L":
					p.ChangeDutyCycle(12.5)
					time.sleep(0.05)
					p.stop()
					break
				elif inp == "R":
					p.ChangeDutyCycle(2.5)
					time.sleep(0.05)
					p.stop()
					break
		except KeyboardInterrupt:
			p.stop()
		GPIO.cleanup()

#subobj = SubMot()
#subobj.start_submot("L")
#time.sleep(1)
#subobj.start_submot("R")
#time.sleep(1)
#subobj.start_submot("L")
#time.sleep(1)
#subobj.start_submot("R")
#time.sleep(1)
#subobj.start_submot("L")
#time.sleep(1)
#subobj.start_submot("R")
