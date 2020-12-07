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
DelayMainCycle = 15000   # delay of main cycle, 15 sec
#hist_day_load  = 2      # ARCHIV history from 23 March
#
def test_msg_lmb():
    #bp()
    vrs_python = str(sys.version_info.major) + '.' + str(sys.version_info.minor)
    vrs_PySimpleGUI = str(sg.version)
    err_lmb('Versions', 'Python ' + vrs_python + '\n' + vrs_PySimpleGUI)
    sg.popup_ok('Python ' + vrs_python + '\n' + vrs_PySimpleGUI, background_color='LightGreen', title='Versions')
#
def reStart_tSync():
    os.system("TASKKILL /F /IM " + PROCNAME)
    print("Success KILL => " + PROCNAME)
    #input()
    os.system('start ' + PROCNAME)
    print("Success START => " + PROCNAME)
    #input()
#
def main():
    sg.theme('DefaultNoMoreNagging')     # Please always add color to your window DefaultNoMoreNagging
    #test_msg_lmb()
    while True: #--- Menu & Tab Definition ----------------------------#
        layout = [  [sg.Text('Time SERVER', pad=(0,0), key='-tm_server-')],
                    [sg.Text('Time PC' ,    pad=(0,0), key='-tm_pc-')],
                    [sg.StatusBar(text= '  wait ...', size=(20,1),  key='-STATUS_BAR-'),
                     sg.Exit(auto_size_button=True)]]
        window = sg.Window('My window with tabs', layout, finalize=True, no_titlebar=False, location=locationXY)
        window.set_title('TM_control_34')
        break

    path_file_TM = sg.PopupGetFile('c:', title = 'Control TIME file')
    print(path_file_TM)
    tm_hour = '00'

    while True: #--- Main Cycle ---------------------------------------#
        event, values = window.read(timeout = DelayMainCycle)
        print(event, values)    # type(event): str,   type(values):dict
        if event in [sg.WIN_CLOSED, 'Exit']:  break
        #
        if event in ['__TIMEOUT__']:
            os.system('cls')  # on windows
            #event_TIMEOUT(_gl, window, event, values)
            #--- read TERM file ----------------------------------------
            buf_str = []
            tm_srv, tm_cmp = '', ''
            try:
                with open(path_file_TM,"r") as fh:
                    buf_str = fh.read().splitlines()
                    #lst_tm = buf_str[0].split('|')

                tm_srv = buf_str[0].split('|')[0]
                tm_cmp = buf_str[0].split('|')[1]
                print(tm_srv + '\r' + tm_cmp)
                window['-tm_server-'].Update(tm_srv)
                window['-tm_pc-'].Update(tm_cmp)
                if tm_cmp[0:2] != tm_hour:
                    tm_hour = tm_cmp[0:2]
                    reStart_tSync()
                window['-STATUS_BAR-'].Update('ok', background_color = 'lightgreen')
            except Exception as ex:
                print('Exception = ', ex)
                window['-STATUS_BAR-'].update(ex, background_color = 'coral')

    window.close()
    return 0
if __name__ == '__main__':
    main()

