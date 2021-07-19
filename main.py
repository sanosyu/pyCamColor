import cv2
import time
import datetime
import numpy as np
import tkinter as Tk
import PySimpleGUI as sg
from matplotlib import pyplot as plt
from matplotlib import cm
from PIL import ImageFont, ImageDraw, Image


# function to draw histgram
def draw_plot(img_f):
    plt.clf()   # initialize plot
    for i, channel in enumerate(("r", "g", "b")):
            histgram = cv2.calcHist([img_f], [i], None, [256], [0, 256])
            plt.plot(histgram, color = channel)
            plt.xlim([0, 256])    
    plt.pause(0.01) # refresh rate


def draw_heatmap_hsv(img_f, channel):
    plt.clf()
    z = img_f[:,:,channel]
    z.reshape(img_f.shape[0], img_f.shape[1])
    plt.imshow(z, cmap=cm.jet)
    plt.colorbar()
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.pause(0.01)


### Window Color ###
sg.theme('Dark Grey 13')


### UI parts ###

## radio, slider, text
myFont = 'Ricty Diminished Discord Regular'

radio_none = sg.Radio('None', 'Radio', True, size=(10, 1), font=(myFont, 12))
radio_filter = sg.Radio('Filter', 'Radio', size=(10, 1), key='-HSV FILTER-', font=(myFont, 12))
txt_B = sg.Text('Blue', size=(10,1), font=(myFont, 12))
sli_Bmin = sg.Slider((0,255), 50, 1, orientation='h', size=(25,15), key='-BGR B MIN-')
sli_Bmax = sg.Slider((0,255), 255, 1, orientation='h', size=(25,15), key='-BGR B MAX-')
txt_G = sg.Text('Green', size=(10,1), font=(myFont, 12))
sli_Gmin = sg.Slider((0,255), 50, 1, orientation='h', size=(25,15), key='-BGR G MIN-')
sli_Gmax = sg.Slider((0,255), 255, 1, orientation='h', size=(25,15), key='-BGR G MAX-')
txt_R = sg.Text('Red', size=(10,1), font=(myFont, 12))
sli_Rmin = sg.Slider((0,255), 140, 1, orientation='h', size=(25,15), key='-BGR R MIN-')
sli_Rmax = sg.Slider((0,255), 255, 1, orientation='h', size=(25,15), key='-BGR R MAX-')
radio_hsv = sg.Radio('HSV', 'Radio', size=(10,1), key='-HSV PLOT-', font=(myFont, 12))
txt_hsv_plot = sg.Text('', size=(10,1))
radio_hsv_h = sg.Radio('Hue', 'radio_hsv', size=(10,1), key='-HSV PLOT H-', font=(myFont, 12))
radio_hsv_s = sg.Radio('Saturation', 'radio_hsv', True, size=(10,1), key='-HSV PLOT S-', font=(myFont, 12))
radio_hsv_v = sg.Radio('Value', 'radio_hsv', size=(10,1), key='-HSV PLOT V-', font=(myFont, 12)) 
radio_hist = sg.Radio('Histgram', 'Radio', size=(10, 1), key='-hist-', font=(myFont, 12))

## btn
btn_cap_img = sg.Submit('Capture Image', size=(20,10), font=(myFont, 12))
btn_cap_hsv = sg.Submit('Capture HSV', size=(20,10), font=(myFont, 12))
btn_cap_hist = sg.Submit('Capture Histgram', size=(20,10), font=(myFont, 12))
btn_quit = sg.Submit('QUIT', size=(20,10), button_color=('black', '#4adcd6'), font=(myFont, 12))

## image
frame4 = sg.Image(filename='', key='-IMAGE-')
canvas_rgb = sg.Canvas(size=(1, 1), key='canvas')

## ui group
frame_image = sg.Frame(layout=[[frame4]],
                        title='Image',
                        title_color='white',
                        font=('Ricty Diminished Discord Regular', 12),
                        relief=sg.RELIEF_SUNKEN,
                        element_justification='left')

frame_settings = sg.Frame(layout=[
                            [radio_none],
                            [radio_filter],
                            [txt_B, sli_Bmin, sli_Bmax],
                            [txt_G, sli_Gmin, sli_Gmax],
                            [txt_R, sli_Rmin, sli_Rmax],
                            [radio_hsv],
                            [txt_hsv_plot, radio_hsv_h, radio_hsv_s, radio_hsv_v],
                            [radio_hist]
                            ],
                        title='Parameter',
                        title_color='white',
                        font=('Ricty Diminished Discord Regular', 12),
                        relief=sg.RELIEF_SUNKEN,
                        element_justification='left')

### layout ###
layout_1 = sg.Frame(layout=[[frame_image],
                            [frame_settings],
                            [canvas_rgb]],
                          title='',
                          title_color='white',
                          font=('Ricty Diminished Discord Regular', 10),
                          relief=sg.RELIEF_SUNKEN)

layout_2 = sg.Column(layout=[[btn_cap_img],
                             [btn_cap_hist],
                             [btn_cap_hsv],
                             [btn_quit]],
                     vertical_alignment='top')

layout = [
          [layout_1, layout_2],
         ]


### window settigns ###
window = sg.Window('Viewer', 
                    layout,
                    size=(900,900),
                    location=(10, 10),
                    alpha_channel=1.0,
                    no_titlebar=False,
                    grab_anywhere=True).Finalize()

# Histgram
canvas_elem = window['canvas']
canvas = canvas_elem.TKCanvas

### capture settings  ###
cap = cv2.VideoCapture(0)

W = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
H = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
#print(W, H)

cap.set(3, 640)
cap.set(4, 480)
#cap.set(5, 30)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# initialize
fps = ""

while True:

    # start time for calc FPS
    t1 = time.perf_counter()

    event, values = window.read(timeout=20)

    if event == 'QUIT' or event == sg.WIN_CLOSED:
        break

    _, img = cap.read()

    img_1 = cv2.resize(img, (640,480))
    img_2 = img_1

        
    ### processed image  ###
    if values['-HSV FILTER-'] or values['-HSV PLOT-']:
        
        bmin = int(values['-BGR B MIN-'])
        bmax = int(values['-BGR B MAX-'])
        gmin = int(values['-BGR G MIN-'])
        gmax = int(values['-BGR G MAX-'])
        rmin = int(values['-BGR R MIN-'])
        rmax = int(values['-BGR R MAX-'])

        #img_1 = cv2.cvtColor(img_1, cv2.COLOR_BGR2HSV)
        lower_blue = np.array([bmin,gmin,rmin])
        upper_blue = np.array([bmax,gmax,rmax])
        threshold_img = cv2.inRange(img_1, lower_blue, upper_blue)
        threshold_img = cv2.cvtColor(threshold_img, cv2.COLOR_GRAY2BGR)

        mask = cv2.inRange(img_1, lower_blue, upper_blue)
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        masked_img = cv2.bitwise_and(img_1, mask)
        img_1 = masked_img

        if values['-HSV PLOT-']:
            masked_img_hsv = cv2.cvtColor(masked_img, cv2.COLOR_BGR2HSV)
            if values['-HSV PLOT H-']:
                canvas.create_image(300, 300, draw_heatmap_hsv(masked_img_hsv, 0))
            elif values['-HSV PLOT S-']:
                canvas.create_image(300, 300, draw_heatmap_hsv(masked_img_hsv, 1))
            elif values['-HSV PLOT V-']:
                canvas.create_image(300, 300, draw_heatmap_hsv(masked_img_hsv, 2))           


    if values['-hist-']:
        canvas.create_image(300, 300, image=draw_plot(img_1))

    ### save images  ###
    # for file name
    d_today = datetime.date.today()
    dt_now = datetime.datetime.now()

    # histgram
    if event == 'Capture Histgram':
        plt.savefig('./hist_' +
                       str(d_today) + str("_") +
                       str(dt_now.hour) + str("_") +
                       str(dt_now.minute) + str("_") +
                       str(dt_now.second) + '.png')
        
    # processed image
    if event == 'Capture Image':   
        cv2.imwrite('./' +
                       str(d_today) + str("_") +
                       str(dt_now.hour) + str("_") +
                       str(dt_now.minute) + str("_") +
                       str(dt_now.second) + '.jpg', img_1)

    if event == 'Capture HSV':
        plt.savefig('./hsv_' +
                        str(d_today) + str("_") +
                        str(dt_now.hour) + str("_") +
                        str(dt_now.minute) + str("_") +
                        str(dt_now.second) + '.png')


    ### calc FPS  ###
    elapsedTime = time.perf_counter() - t1
    fps = "{:.0f}FPS".format(1/elapsedTime)

    ### show FPS  ###
    frame_1 = cv2.putText(img_1, fps, (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2, cv2.LINE_AA)

    ### refresh image  ###
    imgbytes = cv2.imencode('.png', img_1)[1].tobytes()
    window['-IMAGE-'].update(data=imgbytes)

window.close()
