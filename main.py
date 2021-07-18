import cv2
import time
import datetime
import numpy as np
import tkinter as Tk
import PySimpleGUI as sg
from matplotlib import pyplot as plt
from PIL import ImageFont, ImageDraw, Image


# function to draw histgram
def draw_plot(img_f):
    plt.clf()   # initialize plot
    for i, channel in enumerate(("r", "g", "b")):
            histgram = cv2.calcHist([img_f], [i], None, [256], [0, 256])
            plt.plot(histgram, color = channel)
            plt.xlim([0, 256])    
    plt.pause(0.01) # refresh rate


### Window Color ###
sg.theme('Dark Grey 13')


### UI parts ###

## radio, slider, text
radio_none = sg.Radio('None', 'Radio', True, size=(10, 1))
radio_hsv = sg.Radio('HSV', 'Radio', size=(10, 1), key='-HSV FILTER-')
txt_H = sg.Text('Hue', size=(10,1))
sli_Hmin = sg.Slider((0,255), 50, 1, orientation='h', size=(25,15), key='-HSV H MIN-')
sli_Hmax = sg.Slider((0,255), 180, 1, orientation='h', size=(25,15), key='-HSV H MAX-')
txt_S = sg.Text('Saturation', size=(10,1))
sli_Smin = sg.Slider((0,255), 50, 1, orientation='h', size=(25,15), key='-HSV S MIN-')
sli_Smax = sg.Slider((0,255), 255, 1, orientation='h', size=(25,15), key='-HSV S MAX-')
txt_V = sg.Text('Value', size=(10,1))
sli_Vmin = sg.Slider((0,255), 50, 1, orientation='h', size=(25,15), key='-HSV V MIN-')
sli_Vmax = sg.Slider((0,255), 255, 1, orientation='h', size=(25,15), key='-HSV V MAX-')
radio_hist = sg.Radio('Histgram', 'Radio', size=(10, 1), key='-hist-')

## btn
btn_cap_img = sg.Submit('Capture Image', size=(20, 10))
btn_cap_hist = sg.Submit('Capture Histgram', size=(20, 10))
btn_quit = sg.Submit('QUIT', size=(20, 10), button_color=('black', '#4adcd6'))

## image
frame4 = sg.Image(filename='', key='-IMAGE-')  # オリジナル映像
canvas_rgb = sg.Canvas(size=(1, 1), key='canvas')    # ヒストグラムを別画面で表示させるのに必要

## ui group
frame_image = sg.Frame(layout=[[frame4]],
                        title='Image',
                        title_color='white',
                        font=('メイリオ', 12),
                        relief=sg.RELIEF_SUNKEN,
                        element_justification='left')

frame_settings = sg.Frame(layout=[
                            [radio_none],
                            [radio_hsv],
                            [txt_H, sli_Hmin, sli_Hmax],
                            [txt_S, sli_Smin, sli_Smax],
                            [txt_V, sli_Vmin, sli_Vmax],
                            [radio_hist]
                            ],
                        title='parameter',
                        title_color='white',
                        font=('メイリオ', 12),
                        relief=sg.RELIEF_SUNKEN,
                        element_justification='left')

### layout ###
layout_1 = sg.Frame(layout=[[frame_image],
                            [frame_settings],
                            [canvas_rgb]],
                          title='',
                          title_color='white',
                          font=('メイリオ', 10),
                          relief=sg.RELIEF_SUNKEN)

layout_2 = sg.Column(layout=[[btn_cap_img],
                             [btn_cap_hist],
                             [btn_quit]],
                     vertical_alignment='top')

layout = [
          [layout_1, layout_2],
         ]


### window settigns ###
window = sg.Window('Viewer', 
                    layout,
                    size=(1000,700),
                    location=(10, 10),
                    alpha_channel=1.0,
                    no_titlebar=False,
                    grab_anywhere=True).Finalize()

# ヒストグラム表示の設定
canvas_elem = window['canvas']
canvas = canvas_elem.TKCanvas

### キャプチャ設定 ###
cap = cv2.VideoCapture(0)

W = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
H = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
# print(W, H)

# cap.set(3, 1920)
# cap.set(4, 1080)
# cap.set(5, 30)

# 初期値
fps = ""

while True:

    # 時間測定開始(FPS計算のため)
    t1 = time.perf_counter()

    event, values = window.read(timeout=20)

    if event == 'QUIT' or event == sg.WIN_CLOSED:
        break

    _, img = cap.read()

    img_1 = cv2.resize(img, (640,360))
    img_2 = img_1

        
    ### 変換後の画像 ###
    if values['-HSV FILTER-']:
        
        hmin = int(values['-HSV H MIN-'])
        hmax = int(values['-HSV H MAX-'])
        smin = int(values['-HSV S MIN-'])
        smax = int(values['-HSV S MAX-'])
        vmin = int(values['-HSV V MIN-'])
        vmax = int(values['-HSV V MAX-'])

        img_1 = cv2.cvtColor(img_1, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([hmin,smin,vmin])
        upper_blue = np.array([hmax,smax,vmax])
        mask = cv2.inRange(img_1, lower_blue, upper_blue)
        img_1 = cv2.bitwise_and(img_1, img_1, mask= mask)
        img_1 = cv2.cvtColor(img_1, cv2.COLOR_HSV2BGR)

    if values['-hist-']:
        # ヒストグラムは別画面で表示
        canvas.create_image(300, 300, image=draw_plot(img_1))

    ### 各種画像保存 ###
    # 日付の取得(ファイル名に使用する準備)
    d_today = datetime.date.today()
    dt_now = datetime.datetime.now()

    # ヒストグラム画像
    if event == 'Capture Histgram':
        plt.savefig('./' +
                       str(d_today) + str("_") +
                       str(dt_now.hour) + str("_") +
                       str(dt_now.minute) + str("_") +
                       str(dt_now.second) + '.png')
        
    # 変換後の画像
    if event == 'Capture Image':   
        cv2.imwrite('./' +
                       str(d_today) + str("_") +
                       str(dt_now.hour) + str("_") +
                       str(dt_now.minute) + str("_") +
                       str(dt_now.second) + '.jpg', img_1)

    ### FPS 計算 ###
    elapsedTime = time.perf_counter() - t1
    fps = "{:.0f}FPS".format(1/elapsedTime)

    ### 画面にFPS表示 ###
    frame_1 = cv2.putText(img_1, fps, (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2, cv2.LINE_AA)

    ### 画面更新 ###
    imgbytes = cv2.imencode('.png', img_1)[1].tobytes()
    window['-IMAGE-'].update(data=imgbytes)

window.close()