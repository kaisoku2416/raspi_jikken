# -*- coding: utf-8 -*-
import requests
url = "https://notify-api.line.me/api/notify"
token = ""
headers = {"Authorization": "Bearer "+token}


def line_send_message(counter):
    message = "現在" + str(counter) + "人です"
    payload = {"message": message}
    requests.post(url, headers=headers, params=payload)


def line_send_picture(picture_pass):
    message = "室内の様子"
    payload = {"message": message}
    files = {"imageFile": open(picture_pass, "rb")}
    requests.post(url, headers=headers, params=payload, files=files)
