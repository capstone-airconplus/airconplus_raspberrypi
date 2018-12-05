import serial
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import RPi.GPIO as GPIO
import submot_main
from datetime import datetime

submot_obj = submot_main.SubMot()

class MainCode:
    def start_main(this):
        now = datetime.now()
        today_month = now.month
        today_year_month = str(now.year) +'-'+ str(now.month)
        today_day = now.day

        start_btn_pin = 16
        end_btn_pin = 12

        left_flag = True
        right_flag = True
        is_run = False
        is_out = False
        outdoor_fan_hum = 0
        outdoor_fan_temp = 0
        indoor_hum = 0
        indoor_temp = 0

        cred = credentials.Certificate('./capstone-df6bb-firebase-adminsdk-4tkb4-d38a37bfae.json')
        firebase_admin.initialize_app(cred,{
        'databaseURL' : 'https://capstone-df6bb.firebaseio.com/'
        })

        current = db.reference('/current').get()
        ref = db.reference(current)
        power = ref.child('aircon_power').get()

        print('current_user uid : {0}, aircon power : {1}'.format(current, power))
        port="/dev/ttyUSB0"
        serialFromArduino = serial.Serial(port, 9600)
        serialFromArduino.flushInput()
        while True:

            GPIO.setmode(GPIO.BCM)
            GPIO.setup(start_btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(end_btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

            start_input_state = GPIO.input(start_btn_pin)
            end_input_state = GPIO.input(end_btn_pin)

            # push start btn
            if start_input_state == False:
                print("=========================================")
                print('                   start                 ')
                print("=========================================")
                is_run = True
                is_out = False
                is_servo_open = False
                is_servo_close = False
                start_time = time.time()
                ref.update({
                    'on':1
                    })

            # push end btn
            if end_input_state == False:
                print("=========================================")
                print('                    end                  ')
                print("=========================================")
            
                ref.update({
                    'on':0
                    })
                is_run = False
                is_out = True
                end_time = time.time()
                total_time = round((end_time - start_time)/3600, 2)
                # reduction = cal_reduced_fee(power, outdoor_fan_temp, total_time)
                reduced_fee = 0.0

                if outdoor_fan_temp < 32:
                    reduced_fee = power * total_time
                elif 32 <= outdoor_fan_temp < 36:
                    reduced_fee = power * total_time *0.88
                elif 36 <= outdoor_fan_temp < 39:
                    reduced_fee = power * total_time *0.85
                elif outdoor_fan_temp >= 39:
                    reduced_fee = power * total_time *0.64

                print('total time : {} hours'.format(total_time))
                print('reduced_fee : {} won'.format(reduced_fee))

                use_data = ref.child('use_power').get()
                now_usage = use_data.get(today_year_month).get(str(today_day)).get('use')
                reduction_usage = use_data.get(today_year_month).get(str(today_day)).get('reduction')
                ref.child('use_power').child(today_year_month).child(str(today_day)).update({
                    'use' : now_usage + total_time,
                    'reduction' : reduction_usage + reduced_fee
                })
                print('success save db')
                if is_servo_open == True:
                    if is_servo_close == False:
                        submot_obj.start_submot("R")
                        is_servo_close = True
                        is_servo_open = False
                        print('close the door')
                is_servo_open = False
                is_servo_close = False
                
            if is_run:
                try:
                    input= serialFromArduino.readline()
                    input = str(input)
                    input = input.replace("b'","")
                    input = input.replace("\\r\\n'","")
                    data = input.split('/')
                    
                    print('data : {0},{1}'.format(data, len(data)))
                    if len(data) == 5:
                        outdoor_fan_hum = int(data[1])
                        outdoor_fan_temp = int(data[2])
                        indoor_hum = int(data[3])
                        indoor_temp = int(data[4])
                        print("======================")
                        print("height : {}".format(int(data[0])))
                        print("outdoor humidity : {}".format(outdoor_fan_hum))
                        print("outdoor temperature: {}".format(outdoor_fan_temp))
                        print("indoor humidity: {}".format(indoor_hum))
                        print("indoor temperature: {}".format(indoor_temp))
                        print("======================")
                        # ref_path = '/'+current
                        
                        ref.update({
                        'outdoor_fan_hum':outdoor_fan_hum,
                        'outdoor_fan_temp':outdoor_fan_temp,
                        'indoor_hum':indoor_hum,
                        'indoor_temp':indoor_temp
                        })
                        
                        print("success save db")

                        if int(data[0]) >=15:
                            print('first_data : 0')
                            if is_servo_open == False:
                                submot_obj.start_submot("L")
                                is_servo_open = True
                                is_servo_close = False
                                print('open the door')
                        else:
                            print('data < 15')
                            if is_servo_open == True:
                                if is_servo_close == False:
                                    submot_obj.start_submot("R")
                                    is_servo_close = True
                                    is_servo_open = False
                                    print('close the door')
                    time.sleep(5)
                except serial.SerialException:
                    pass
                except IndexError:
                    pass
                except ValueError:
                    pass




mainobj=MainCode()
mainobj.start_main()
