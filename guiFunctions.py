
from alarmFunction import bpmAlarm
from matplotlib.figure import Figure
# import matplotlib.pyplot as plt
# import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib

matplotlib.use('TkAgg')
import time

from classDefine import data
from classDefine import alarm
import alarmFunction as alrm

## ********* Figure plotting parameter ***************
# set up GUI window size
WIN_WIDTH = 1200
WIN_HEIGHT = 750

# Initialise parameters
HIGH_BPM_DEFAULT = 90
LOW_BPM_DEFAULT = 40
HIGH_BPM_RANGE = [70,140]
LOW_BPM_RANGE = [20,50]

# Parameters for pulse waveform plotting
dt_w = 0.02
STEP = 50                   # how many points we move in each frame
DATALEN_w = STEP * 15         # how many points we print in one frame = window width

# For BPM
dt_b = 1
DATALEN_b = 15

def update_this_array(data_all,dt,DATALEN):
    '''
    Update the data to display in the cavas with the required length in this frame. For example data for 1~15 sec --> 2~16 sec
    Author: Yunyao Duan
    '''
    t_all      = [j*dt for j in range(len(data_all))]
    if len(data_all) > DATALEN:
        data_this = data_all[-DATALEN:]
        t_this = t_all[-DATALEN:]
    else:
        data_this = data_all
        t_this = t_all

    return data_this, t_this


def get_data_to_draw():
    '''
    Get both the BPM data to display and Pulse data to display
    Author: Yunyao Duan
    '''
    [pulse_this,t_w_this] = update_this_array(data.pulse,dt_w,DATALEN_w)
    [bpm_this,t_b_this] = update_this_array(data.bpm,dt_b,DATALEN_b)
    # [mean_bpm_this,t_b_this] = update_this_array(data.mean_bpm,dt_b,DATALEN_b)

    return t_w_this, pulse_this, t_b_this, bpm_this

def draw_GUI_window():
    '''
    Create layout for the GUI window, and display the window
    the tab_layout contains 2 tabs and 2 canvas to display the BPM and Pulse waveform data, the tabs allow us to select which data type to display
    There should be title, button, current BPM and mean BPM, logtext, but haven't done yet 

    Author:Yunyao Duan
    '''
    tab_layout = [  
            # [sg.Button("Exit",key = "Exit",font=('Helvetica', 20))],
            [sg.TabGroup([[sg.Tab('Pulse Waveform', [[sg.Canvas(key="__CANVAS1__", size=(4,3))]]), sg.Tab('BPM', [[sg.Canvas(key="__CANVAS2__", size=(4,3))]])]])],        
            ]

    if data.this_bpm != []:
        current_bpm = data.this_bpm[-1]
    else: current_bpm = 0
    if data.mean_bpm != []:
        mean_bpm = data.mean_bpm[-1]
    else: mean_bpm = 0

    col_layout1 = [ 
                [sg.Button("Clear Display", key = "__CLEAR__", font=('Helvetica', 20)), sg.Button("Exit",key="EXIT", font=('Helvetica', 20))],
                
                [sg.HorizontalSeparator(),],

                [sg.Checkbox("High BPM Alarm", key = "__CHECK1__", font=('Helvetica', 20))],
                [sg.Checkbox("Low BPM Alarm", key = "__CHECK2__", font=('Helvetica', 20))],


                [sg.HorizontalSeparator(),],
                [sg.T("Current BPM : {:.1}".format(float(current_bpm)), font=('Helvetica', 20))],
                [sg.T("Mean BPM : {:.1}".format(float(mean_bpm)), font=('Helvetica', 20))],

                # [sg.HorizontalSeparator(),],

                # [sg.Button("Clear Data", key = "__CLEARDATA__", font=('Helvetica', 20))],
                # [sg.Button("Exit",key="EXIT", font=('Helvetica', 20))],

                [sg.HorizontalSeparator(),],

                [sg.T("highBPM", font=('Helvetica', 20)),sg.Slider(range=(HIGH_BPM_RANGE), key = "__HIGH_THRESHOLD__",default_value=HIGH_BPM_DEFAULT, size=(20,15), orientation='horizontal', font=('Helvetica', 20))],
                [sg.T("lowBPM", font=('Helvetica', 20)),sg.Slider(range=(LOW_BPM_RANGE), key = "__LOW_THRESHOLD__",default_value=LOW_BPM_DEFAULT, size=(20,15), orientation='horizontal', font=('Helvetica', 20))],

                [sg.HorizontalSeparator(),],
        
                [sg.Text("Choose a data type:", font=('Helvetica', 20))],
                [sg.Combo(['BPM','Pulse Waveform'], key = "__DATA_TYPE__", font=('Helvetica', 20),default_value = 'Pulse Waveform')],

               ]


    layout = [
        # Row 1: Text, name of our company
        [sg.Text("Remote Biosenser System (Wed-09)", size = (60,1), justification = 'c', font = ('Any 40 bold'))],

        # Row 2: a windown to display graph | a column which contains 2 check boxes
        # [sg.Canvas(key="-CANVAS-",size = (5,4)), sg.Frame('',col_layout1)],
        [sg.Frame('',tab_layout), sg.Frame('',col_layout1)],

        [sg.T("Log text:", font=('Helvetica bold', 28))],
    
        [sg.MLine(key='-MLINE-'+sg.WRITE_ONLY_KEY, size=(100,8))],
    ]

    window = sg.Window("Window name", layout, size = (WIN_WIDTH,WIN_HEIGHT),finalize=True,element_justification='center', font='Helvetica 16')
    return window

def addFigure(canvasElement):
    ''' Create a figure and add the figure to the canvas we created in draw_GUI_window
        return the ax for the figure, ax will be changed in plotFigure() to change data to display
    '''
    # create a figure
    fig = Figure()
    # create a set of axes on the figure 
    ax = fig.add_subplot(1,1,1)

    # place the figure on the canvas
    canvas = canvasElement.TKCanvas
    figAgg = FigureCanvasTkAgg(fig, canvas)
    figAgg.draw()
    figAgg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return ax, figAgg

def plotFigure(ax,fig,t,ydata,dataType,DATALEN):
    ''' This function is to display the pulse / BPM data in the canvas by updating the axes we created
        Author: Yunyao Duan
    '''
    # Clear the current axes
    ax.cla()

    if dataType == 'W':
        # If this is pulse waveform data, display the waveform and set the ylabel for this
        ax.plot(t,ydata,linewidth =1)
        ax.set_ylabel('Pulse Waveform')

    elif dataType == 'B':
        # Display the current BPM
        ax.bar(t,ydata)

        # Get the current BPM thresholds and display them in the graph
        h_thre = [alarm.highBpmThreshold] * len(t)
        l_thre = [alarm.lowBpmThreshold] * len(t)
        line1, = ax.plot(t,h_thre,color = 'red',label = 'High BPM Threshold')
        line2, = ax.plot(t,l_thre,color = 'orange',label = 'Low BPM Threshold')

        # Display the mean BPM
        [mean_bpm_draw,t_b_draw] = update_this_array(data.mean_bpm,dt_b,DATALEN_b)
        line3, = ax.plot(t_b_draw,mean_bpm_draw,"k*-",label ='Mean BPM' )

        # Set ylabel and legend for BPM window
        ax.set_ylabel('BPM')
        ax.legend(handles=[line1,line2,line3],loc = 'upper right')

    ax.set_xlabel("time")
    ax.set_ylim([min(ydata)*0.95-1,max(ydata)*1.05+1])

    # If the lenth of the data to display is less than 15 seconds, we still set up the window width as 15 seconds
    if len(t) < DATALEN:
        ax.set_xlim([0,15])

    # current_bpm = 0
    # mean_bpm = 0
    # if data.this_bpm != []:
    #     current_bpm = data.this_bpm[-1]

    # if data.mean_bpm != []:
    #     mean_bpm = data.mean_bpm[-1]

    # tx = "Current BPM : {:.1}".format(float(current_bpm))
    # # t = "Current BPM : {:.1f}".format(float(current_bpm))
    # ax.text(5, 10, tx, fontsize=18, style='oblique', ha='center',
    #      va='top', wrap=True)
    # # Refresh this frame of figure
    fig.draw()
    
    return ax


def guiAction(window,current,values,t_w_this,pulse_this,t_b_this,bpm_this,ax1,ax2,fig1,fig2):  
    
    for k in values.keys():
        current[k] = values[k]

    if True: 
        print("The GUI window is open")
        timestamp = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())
        # Read the event and values
        event, values = window.read(0.1)

        # Action 1: exit the window when we click the close or exit button
        if event == sg.WIN_CLOSED or event == 'Exit':
            return 'exit'

        # Action 2: Display the 
        if len(pulse_this)!= 0:
            plotFigure(ax1, fig1,t_w_this,pulse_this,"W",DATALEN_w)

        if len(bpm_this) != 0:
            plotFigure(ax2, fig2,t_b_this,bpm_this,"B",DATALEN_b)
        
        # If there's any changes
        for k in values.keys():         
            if current[k] != values[k]:
                current[k] = values[k]
                window['-MLINE-'+sg.WRITE_ONLY_KEY].print("{}: {} -> {}".format(timestamp,k, values[k]))
                print("{} -> {}".format(k, values[k]))

                # Action 3: change the BPM threshold
                if k == '__HIGH_THRESHOLD__':
                    alarm.highBpmThreshold = current[k]
                    print("high threshold: ", alarm.highBpmThreshold)
                    # if alrm.bpmAlarm(data.this_bpm) == True:
                    #     print(timestamp, ": ", alarm.alarm_string)
                    #     window['-MLINE-'+sg.WRITE_ONLY_KEY].print("{}: {}".format(timestamp,alarm.alarm_string)

                if k == '__LOW_THRESHOLD__':
                    alarm.lowBpmThreshold = current[k]
                    print("low threshold: ", alarm.lowBpmThreshold)
        
        if data.this_bpm != []:
            if alrm.bpmAlarm(data.this_bpm) == True:
                print(timestamp, ": ", alarm.alarm_string)
                window['-MLINE-'+sg.WRITE_ONLY_KEY].print("{}: {}".format(timestamp,alarm.alarm_string))


        # canvasElement = '__CANVAS2__'
        # canvas = canvasElement.TKCanvas
        # canvas.create_text(100,10,fill="darkblue",font="Times 20 italic bold",
        #                 text="Click the bubbles that are multiples of two.")
       


        # canvas = '__CANVAS1__'
        # legend_text = """
        #         -------------------
        #         |   ------     line1    |
        #         |   ------     line2    |
        #         |   ------     line3    |
        #         -------------------"""
        # legend_frame = LabelFrame(canvas,text='Legend',padx=5, pady=5)
        # legend_label = Label(legend_frame,text=legend_text)
        # legend_label.pack()
        # canvas.create_window(120,200,window=legend_frame)
        
