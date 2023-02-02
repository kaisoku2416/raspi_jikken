# -*- coding: utf-8 -*-
"""
===このプログラムの説明===
Google Sheet を操作するためのツールが各関数にまとめられています。

googlesheet_readsetting():  Google Sheetの「setting」シートから設定値を読み出す。
googlesheet_init():         Google Sheetのヘッダを生成。強制的に上書きされる。
googlesheet_update():       Google Sheetにデータをappendする。
"""

import gspread
import datetime
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]
cred = ServiceAccountCredentials.from_json_keyfile_name('jikken.json', scope)
gc = gspread.authorize(cred)
sh_name = 'jikken_ss'
sh = gc.open(sh_name)
wks_1 = sh.worksheet('detected_datas')
wks_2 = sh.worksheet('setting')


def googlesheet_readsetting():
    print("reading setting values from spreadsheet...")
    return wks_2.col_values(3)


def googlesheet_init():
    wks_1.update('A1', 'number of detected people')
    wks_1.update('A2:G2', [['year', 'month', 'day',
                 'hour', 'minute', 'str_disp_date', 'people']])
    # wks_1.update(A3:D3', [[dt_now.year, dt_now.month, dt_now.day, dt_now.hour]])


def googlesheet_update(counter_people_now):
    # 同時間がすでに記録されていたらそこに上書き。なければ新規行をappendする。
    dt_now = datetime.datetime.now()
    num_last_row = len(wks_1.col_values(1))
    num_check_day = wks_1.cell(num_last_row, 3).value
    num_check_hour = wks_1.cell(num_last_row, 4).value
    num_check_minute = wks_1.cell(num_last_row, 5).value
    if num_check_day != str(dt_now.day) or num_check_hour != str(dt_now.hour) or num_check_minute != str(dt_now.minute):
        wks_1.update_cell(num_last_row+1, 1, dt_now.year)
        wks_1.update_cell(num_last_row+1, 2, dt_now.month)
        wks_1.update_cell(num_last_row+1, 3, dt_now.day)
        wks_1.update_cell(num_last_row+1, 4, dt_now.hour)
        wks_1.update_cell(num_last_row+1, 5, dt_now.minute)
        str_disp_date = f'{dt_now.year:02}/{dt_now.month:02}/{dt_now.day:02} {dt_now.hour:02}:{dt_now.minute:02}'
        wks_1.update_cell(num_last_row+1, 6, str_disp_date)
        wks_1.update_cell(num_last_row+1, 7, counter_people_now)
        print("updated Google Sheet, appended a new line")
    else:
        # 値は最大値を保持(maxのところ)
        wks_1.update_cell(num_last_row, 7, max(
            int(wks_1.cell(num_last_row, 7).value), counter_people_now))
        print("updated Google Sheet, updated an existing cell")
