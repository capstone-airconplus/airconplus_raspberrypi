import serial
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import RPi.GPIO as GPIO
import submot_main
from datetime import datetime

submot_obj = submot_main('start')

class MainCode:
    def start_main(this):
        now = datetime.now()
        today_month = now.month
        today = str(now.year) +'-'+ str(now.month) +'-'+ str(now.day)

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

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(start_btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(end_btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        print('start')  
        cred = credentials.Certificate('./capstone-df6bb-firebase-adminsdk-4tkb4-d38a37bfae.json')
        firebase_admin.initialize_app(cred,{
        'databaseURL' : 'https://capstone-df6bb.firebaseio.com/'
        })

        ref = db.reference('/current')
        current = ref.get()
        ref_path = '/'+current
        power = db.reference('/aircon_power').get()

        print('current_user is {}'.format(current))

        port="/dev/ttyUSB0"
        serialFromArduino = serial.Serial(port, 9600)
        serialFromArduino.flushInput()
        while True:
            start_input_state = GPIO.input(start_btn_pin)
            end_input_state = GPIO.input(end_btn_pin)

            # push start btn
            if start_input_state == False:
                print('start!!!!')
                is_run = True
                is_out = False
                start_time = time.time()

            # push end btn
            if end_input_state == False:
                print('end!!!!!')
                is_run = False
                is_out = True
                end_time = time.time()
                total_time = round(end_time - start_time, 2)
                print('total time : {} hours'.format(total_time))
                reduction = cal_reduced_fee(power, outdoor_fan_temp, total_time)

                daily_ref_path = ref_path + '/' + today_month +'/' + today
                use_ref_path = daily_ref_path+'/use'
                reduction_ref_path = daily_ref_path+'/reduction'

                use_ref = db.reference(use_ref_path)
                now_usage = use_ref.get()

                daily_ref = db.reference(daily_ref_path)
                daily_ref.update({
                    'use' : now_usage + round(total_time,2)
                    'reduction' : reduction
                    })

            if is_run:
                try:
                    input= serialFromArduino.readline()
                    input = str(input)
                    input = input.replace("b'","")
                    input = input.replace("\\r\\n'","")
                    data = input.split('/')
                    
                    print('data : {0},{1}'.format(data, len(data)))
                    print("@@@@@@@@@@@@@@@@@@@@@@@@@")
                    if len(data) == 5:
                        outdoor_fan_hum = int(data[1])
                        outdoor_fan_temp = int(data[2])
                        indoor_hum = int(data[3])
                        indoor_temp = int(data[4])

                        print("height : {}".format(int(data[0])))
                        print("first_humidity : {}".format(outdoor_fan_hum))
                        print("first_temperature: {}".format(outdoor_fan_temp))
                        print("second_humidity: {}".format(indoor_hum))
                        print("second_temperature: {}".format(indoor_temp))
                        print("======================")
                        # ref_path = '/'+current
                        ref_ = db.reference(ref_path)
                        ref_.update({
                        'outdoor_fan_hum':outdoor_fan_hum,
                        'outdoor_fan_temp':outdoor_fan_temp,
                        'indoor_hum':indoor_hum,
                        'indoor_temp':indoor_temp
                        })
                        print("success")

                        if int(data[0]) == 0:
                            print('first_data : 0')
                            submot_obj.start_submot("L")
                        elif int(data[0]) > 100:
                            print('data > 100')
                    time.sleep(5)
                except serial.SerialException:
                    pass
                except IndexError:
                    pass
                except ValueError:
                    pass

    def cal_reduced_fee(power, out_door_temp, use_):
        reduced_fee = 0
        if out_door_temp < 32:
            reduced_fee = power * use_
        elif 32 <= out_door_temp < 36:
            reduced_fee = power * use_ *0.88
        elif 36 <= out_door_temp < 39:
            reduced_fee = power * use_ *0.85
        elif out_door_temp >= 39:
            reduced_fee = power * use_ *0.64
        return reduced_fee



mainobj=MainCode()
mainobj.start_main()
