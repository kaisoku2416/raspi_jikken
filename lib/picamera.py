# -*- coding: utf-8 -*-
from picamera import PiCamera


# 写真を撮影＋保存した写真のパスを文字列で返す関数
def camera_picture():
    with PiCamera(resolution=(640, 360)) as cam:
        name = "/home/pi/jikken_codes/pictures/pic.png"
        cam.capture(name)
        return name
