# -*- coding: utf-8 -*-
"""
main()
-> pir()    センサ監視用(常時実行)
-> check()  変数counter_people_now監視用(常時実行)
-> cleanup() atexitに登録。終了時のGPIO.cleanup()
"""


import RPi.GPIO as GPIO
from time import sleep
from time import time
import concurrent.futures
import atexit
from lib.line import line_send_message, line_send_picture
from lib.picamera import camera_picture
from lib.googlesheet import googlesheet_init, googlesheet_readsetting, googlesheet_update
counter_people_now = 0  # グローバル変数
counter_people_old = 0  # グローバル変数
VALUE_FROM_GREEN_TO_YELLOW = 5  # LED切り替えタイミングに関する定数
VALUE_FROM_YELLOW_TO_MAGENTA = 10  # LED切り替えタイミングに関する定数
VALUE_TAKE_PICTURE = 5
VALUE_SEND_LINE = 5

pin_pir_left = 6
pin_pir_right = 5
pin_7seg = [16, 20, 22, 27, 17, 23, 24, 26]
pin_7seg_all = [[16, 17, 20, 22, 23, 27], [20, 22], [16, 17, 20, 24, 27], [16, 20, 22, 27, 24], [20, 22, 23, 24], [
    16, 22, 23, 24, 27], [16, 17, 22, 23, 24, 27], [16, 20, 22, 23], [16, 17, 20, 22, 23, 24, 27], [16, 20, 22, 23, 24, 27]]
pin_redled = 25
pin_fullcolorled = [13, 12, 18]  # R,G,B


# 各種初期設定をする関数
def init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin_pir_left, GPIO.IN)
    GPIO.setup(pin_pir_right, GPIO.IN)
    GPIO.setup(pin_7seg, GPIO.OUT)
    GPIO.output(pin_7seg_all[8], GPIO.LOW)
    GPIO.output(pin_7seg_all[0], GPIO.HIGH)
    #GPIO.output(pin_7seg_new_dig[0], GPIO.HIGH)
    #GPIO.output(pin_7seg_new_all[0], GPIO.HIGH)
    #GPIO.output(pin_7seg_new_dig[0], GPIO.LOW)
    GPIO.setup(pin_redled, GPIO.OUT)
    GPIO.setup(pin_fullcolorled, GPIO.OUT)
    GPIO.output(pin_fullcolorled[0], 0)
    GPIO.output(pin_fullcolorled[1], 1)
    GPIO.output(pin_fullcolorled[2], 0)
    global VALUE_FROM_GREEN_TO_YELLOW, VALUE_FROM_YELLOW_TO_MAGENTA, VALUE_TAKE_PICTURE, VALUE_SEND_LINE
    [VALUE_FROM_GREEN_TO_YELLOW, VALUE_FROM_YELLOW_TO_MAGENTA,
        VALUE_TAKE_PICTURE, VALUE_SEND_LINE] = map(int, googlesheet_readsetting())
    googlesheet_init()


def pir2():
    global counter_people_now

    while True:
        while GPIO.input(pin_pir_right) == True:
            if GPIO.input(pin_pir_left) == True:
                counter_people_now += 1
                print("right to left moving detected: ",
                      counter_people_now, "people now")
            while GPIO.input(pin_pir_left) == True:
                sleep(0.2)
        while GPIO.input(pin_pir_left) == True:
            if GPIO.input(pin_pir_right) == True:
                counter_people_now -= 1
                print("left to right moving detected: ",
                      counter_people_now, "people now")
            while GPIO.input(pin_pir_right) == True:
                sleep(0.2)


# counter_people_nowを監視する関数
def check():
    global counter_people_now, counter_people_old
    global VALUE_FROM_GREEN_TO_YELLOW, VALUE_FROM_YELLOW_TO_MAGENTA, VALUE_TAKE_PICTURE, VALUE_SEND_LINE
    picture_pass = ""

    while True:
        # counter_people_oldとの差分を検知して動作させる
        if counter_people_now != counter_people_old:
            print("counter change detected")
            # 7segのコード。1の位を表示。
            GPIO.output(pin_7seg_all[counter_people_old % 10], GPIO.LOW)
            GPIO.output(pin_7seg_all[counter_people_now % 10], GPIO.HIGH)
            

            # フルカラーLEDのコード。定数VALUE_*に依存。
            GPIO.output(pin_fullcolorled[0], 0)
            GPIO.output(pin_fullcolorled[1], 0)
            GPIO.output(pin_fullcolorled[2], 0)
            if counter_people_now >= VALUE_FROM_YELLOW_TO_MAGENTA:
                GPIO.output(pin_fullcolorled[0], 1)
                GPIO.output(pin_fullcolorled[1], 0)
                GPIO.output(pin_fullcolorled[2], 1)
            elif counter_people_now >= VALUE_FROM_GREEN_TO_YELLOW:
                GPIO.output(pin_fullcolorled[0], 1)
                GPIO.output(pin_fullcolorled[1], 1)
                GPIO.output(pin_fullcolorled[2], 0)
            else:
                GPIO.output(pin_fullcolorled[0], 0)
                GPIO.output(pin_fullcolorled[1], 1)
                GPIO.output(pin_fullcolorled[2], 0)

            # 単色LEDのコード。検知時に1秒光らせる。
            GPIO.output(pin_redled, GPIO.HIGH)

            # 写真を撮影(実験では5の倍数の時だけ)
            if counter_people_now % VALUE_TAKE_PICTURE == 0:
                picture_pass = camera_picture()
                print("took a picture")

            # counter_people_nowが5の倍数になったらLINE送信
            if counter_people_now % VALUE_SEND_LINE == 0:
                line_send_message(counter_people_now)
                line_send_picture(picture_pass)
                print("sent LINE messages")

            # Google Sheetの更新
            googlesheet_update(counter_people_now)

            # counter_people_oldをcounter_people_nowに更新
            counter_people_old = counter_people_now

            # sleep後に単色LEDを消灯
            sleep(1)
            GPIO.output(pin_redled, GPIO.LOW)


# main関数
def main():
    init()
    print("Successfully Started")
    executer = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    executer.submit(pir2)
    executer.submit(check)


# except KeyboardInterruptはThreadPoolExecutorで捉えられないのでatexitを使用
def cleanup():
    GPIO.cleanup()


atexit.register(cleanup)

if __name__ == "__main__":
    main()
