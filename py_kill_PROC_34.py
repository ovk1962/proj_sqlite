#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  py_kill_PROC_34.py
#
import PySimpleGUI as sg    # vers >= 4.29
import os, sys
PROCNAME = "tSync.exe" # should be locate in the same DIR
print("PySimpleGUI {}".format(sg.version))
#=======================================================================
s_lmb   = lambda s: '\n' + str(s)
err_lmb = lambda st,s: sg.PopupError(s, title=st,
    background_color = 'Coral', no_titlebar = False, keep_on_top=True)
#
locationXY = (150, 100)
DelayMainCycle = 2500   # delay of main cycle, 1 msec
#hist_day_load  = 2     # ARCHIV history from 23 March
#
def test_msg_lmb():
    #bp()
    vrs_python = str(sys.version_info.major) + '.' + str(sys.version_info.minor)
    vrs_PySimpleGUI = str(sg.version)
    err_lmb('Versions', 'Python ' + vrs_python + '\n' + vrs_PySimpleGUI)
    sg.popup_ok('Python ' + vrs_python + '\n' + vrs_PySimpleGUI, background_color='LightGreen', title='Versions')
#=======================================================================
#os.system("TASKKILL /F /IM " + PROCNAME)
#print("Success KILL => " + PROCNAME)
#input()
#os.system('start ' + PROCNAME)
#print("Success START => " + PROCNAME)
#input()
#=======================================================================    
def main():
    sg.theme('DefaultNoMoreNagging')     # Please always add color to your window DefaultNoMoreNagging
    test_msg_lmb()
    while True: #--- Menu & Tab Definition ----------------------------#
        layout = [[sg.StatusBar(text= '_gl.account.dt' + '  wait ...', size=(40,1),
                                key='-STATUS_BAR-'),
                    sg.Exit(auto_size_button=True)]]
        window = sg.Window('My window with tabs', layout, finalize=True, no_titlebar=False, location=locationXY)
        window.set_title('TM_control_34')
        break
    #txt = ''
    #txt = sg.PopupGetText('', default_text = 'c:\\')
    txt = sg.PopupGetFile('c:', title = 'Control TIME file')
    print(txt)
        
    while True: #--- Main Cycle ---------------------------------------#
        event, values = window.read(timeout = DelayMainCycle)
        print(event, values)    # type(event): str,   type(values):dict
        if event in [sg.WIN_CLOSED, 'Exit']:  break
                        
    window.close()
    return 0
if __name__ == '__main__':
    main()
    
