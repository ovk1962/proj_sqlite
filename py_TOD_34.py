#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  py_TOD_34.py
#  
#=======================================================================
import os, sys, math, time, sqlite3, logging
from datetime import datetime, timezone
import math
import matplotlib as mpl
import PySimpleGUI as sg    # vers >= 4.29
from ipdb import set_trace as bp    # to set breakpoints just -> bp()
#=======================================================================
print("Вы используете Python {}.{}.".format( sys.version_info.major,  sys.version_info.minor))
print("PySimpleGUI {}".format(sg.version))
print("Matplotlib {}".format(mpl.__version__))

#=======================================================================
s_lmb   = lambda s: '\n' + str(s)
err_lmb = lambda st,s: sg.PopupError(s, title=st,
    background_color = 'Coral', no_titlebar = False, keep_on_top=True)
#
locationXY = (300, 50)
DelayMainCycle = 2500   # delay of main cycle, 1 msec
#
def test_msg_lmb():
    #bp()
    vrs_python = str(sys.version_info.major) + '.' + str(sys.version_info.minor)
    vrs_PySimpleGUI = str(sg.version)
    err_lmb('Versions', 'Python ' + vrs_python + '\n' + vrs_PySimpleGUI)
    sg.popup_ok('Python ' + vrs_python + '\n' + vrs_PySimpleGUI, background_color='LightGreen', title='Versions')
#=======================================================================
class Class_CNST():
    # cfg_soft
    titul, path_file_DATA, path_file_HIST, dt_start, path_file_TXT = range(5)
    head_cfg_soft  = ['name', 'val']
    # account
    head_data_acnt = ['name', 'val']
    #
    head_data_fut  = ['P_code', 'Rest', 'Var_mrg', 'Open_prc', 'Last_prc',
                'Ask', 'Buy_qty', 'Bid', 'Sell_qty', 'Fut_go', 'Open_pos' ]
    sP_code, sRest, sVar_mrg, sOpen_prc, sLast_prc, sAsk, sBuy_qty, sBid, sSell_qty, sFut_go, sOpen_pos  = range(11)
    # hist_fut
    head_data_hst  = ['name', 'val']
    fAsk, fBid = range(2)
    # account
    aBal, aPrf, aGo, aDep = range(4)
#=======================================================================
class Class_LGR():
    def __init__(self, path_log):
        #self.logger = logging.getLogger(__name__)
        self.logger = logging.getLogger('__main__')
        self.logger.setLevel(logging.INFO)
        # create a file handler
        self.handler = logging.FileHandler(path_log)
        self.handler.setLevel(logging.INFO)
        # create a logging format
        #self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(self.formatter)

        # add the handlers to the logger
        self.logger.addHandler(self.handler)
    #-------------------------------------------------------------------
    def wr_log_info(self, msg):
        self.logger.info(msg)
    #-------------------------------------------------------------------
    def wr_log_error(self, msg):
        self.logger.error(msg)
#=======================================================================
class Class_DB_SQLite():
    def __init__(self, path_db):
        self.path_db  = path_db

    def read_all_tbl(self):
        print('=> _SQLite read_all_tbl ')
        try:
            conn = sqlite3.connect(self.path_db)
            with conn:
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cur.fetchall()
                all_tbls = []
                for table_name in tables:
                    cur.execute('SELECT * from ' + table_name[0])
                    arr = cur.fetchall()
                    all_tbls.append([table_name[0], list(arr)])
                    print(table_name, 5*' ', len(arr))
                    #ok_lmb('read_all_tbl', table_name[0])
        except Exception as ex:
            return [1, ex]
        return [0, all_tbls]
        
    def read_tbl(self, nm_tbl):
        print('=> _SQLite read_tbl ', nm_tbl)
        try:
            conn = sqlite3.connect(self.path_db)
            with conn:
                cur = conn.cursor()
                #--- read  table   ---------------------------------
                cur.execute('SELECT * from ' + nm_tbl)
                arr = cur.fetchall()    # read LIST arr from TABLE nm_tbl
                lst_arr = []
                for item in arr: lst_arr.append(list(item))
        except Exception as ex:
            return [1, ex]
        #print('stop READ')
        return [0, lst_arr]

    def read_tbl_between(self, nm_tbl, sec_FROM, sec_TO):
        print('=> _SQLite read_tbl_between ', nm_tbl)
        try:
            conn = sqlite3.connect(self.path_db)
            with conn:
                cur = conn.cursor()
                #--- read  table   ---------------------------------
                cur.execute('SELECT * from ' + nm_tbl + ' WHERE ind_sec > ' + str(sec_FROM) + ' AND ind_sec < ' + str(sec_TO))
                arr = cur.fetchall()    # read LIST arr from TABLE nm_tbl
                lst_arr = []
                for item in arr: lst_arr.append(list(item))
        except Exception as ex:
            return [1, ex]
        #print('stop READ')
        return [0, lst_arr]

    def update_tbl(self, nm_tbl, buf_arr, val = ' VALUES(?,?)', p_append = False):
        print('=> _SQLite update_tbl ', nm_tbl)
        try:
            conn = sqlite3.connect(self.path_db)
            with conn:
                cur = conn.cursor()
                #--- update table nm_tbl ---------------------------
                if p_append == False:
                    cur.execute('DELETE FROM ' + nm_tbl)
                cur.executemany('INSERT INTO ' + nm_tbl + val, buf_arr)
                conn.commit()
                #--- read  table   ---------------------------------
                cur.execute('SELECT * from ' + nm_tbl)
                arr = cur.fetchall()    # read LIST arr from TABLE nm_tbl
        except Exception as ex:
            return [1, ex]
        return [0, arr]

    def update_2_tbl(self,
                    nm_tbl_1, buf_arr_1,
                    nm_tbl_2, buf_arr_2,
                    val1 = ' VALUES(?)', val2 = ' VALUES(?,?)'):
        print('=> _SQLite update_2_tbl ', nm_tbl_1, '   ', nm_tbl_2)
        try:
            conn = sqlite3.connect(self.path_db)
            with conn:
                cur = conn.cursor()
                #--- update table nm_tbl ---------------------------
                cur.execute('DELETE FROM ' + nm_tbl_1)
                cur.execute('DELETE FROM ' + nm_tbl_2)
                cur.executemany('INSERT INTO ' + nm_tbl_1 + val1, buf_arr_1)
                cur.executemany('INSERT INTO ' + nm_tbl_2 + val2, buf_arr_2)
                conn.commit()
                #--- read  table   ---------------------------------
                #cur.execute('SELECT * from ' + nm_tbl_1)
                #arr = cur.fetchall()    # read LIST arr from TABLE nm_tbl
        except Exception as ex:
            return [1, ex]
        return [0, 'ok']
#=======================================================================
class Class_FUT():
    def __init__(self):
        self.sP_code, self.arr = '', []
    def __retr__(self):
        return  '{} {}'.format(self.sP_code,  str([int(k) for k in self.arr]))
    def __str__(self):
        return  '{} {}'.format(self.sP_code,  str([int(k) for k in self.arr]))
#=======================================================================
class Class_ACNT():
    def __init__(self):
        self.ss = '        bal,      prf,      go,       dep'
        self.dt, self.arr  = '', []
    def __retr__(self):
        return 'dt = {}\n{}\narr={}\n'.format(self.dt, self.ss, str(self.arr))
    def __str__(self):
        return 'dt = {}\n{}\narr={}\n'.format(self.dt, self.ss, str(self.arr))
#=======================================================================
class Class_TRMN():
    #---------------------------  err_status  --------------------------
    err_try  = 128      #
    err_file = 1        # can not find file => path_file_DATA
    err_size = 2        # size DATA file is 0
    err_mdf_time  = 4   # FILE is not modificated
    err_file_size = 8   # FILE size is NULL
    #err_mrkt_time = 16  # size buf_str is NULL
    err_update_db = 32  #  can not update info in DB
    #-------------------------------------------------------------------
    def __init__(self):
        self.path_file_DATA = ''
        self.path_file_HIST = ''
        c_dir    = os.path.abspath(os.curdir)
        self.lg_file =    Class_LGR(c_dir + '\\LOG\\py_TERM.log')
        #
        self.dt_file = 0        # curv stamptime data file path_file_DATA
        self.dt_data = 0        # curv stamptime DATA/TIME from TERM
        self.data_in_file = []  # list of strings from path_file_DATA
        self.hist_in_file = []  # list of strings from path_file_HIST
        #
        self.dt_fut      = []    # list of Class_FUT()
        #self.data_Class_str_FUT  = []    # list of Class_str_FUT()
        self.account = Class_ACNT()  # obj Class_ACCOUNT()
        #
        self.time_1_min = 0
        #
        self.err_status  = 0
        self.cnt_errors  = 0
    #-------------------------------------------------------------------
    def err_rd_term(self, err_pop = False, err_log = False):
        self.cnt_errors += 1
        if err_pop:
            err_lmb('err_rd_term',
                s_lmb(bin(self.err_status) + str(5*' ') + str(self.err_status)) +
                s_lmb('----------------------------------------------------') +
                s_lmb('0b001      1   # can not find file => path_file_DATA') +
                s_lmb('0b010      2   # size DATA file is 0                ') +
                s_lmb('0b100      4   # FILE is not modificated            ') +
                s_lmb('0b1000     8   # FILE size is NULL                  ') +
                s_lmb('0b100000   32  # can not update info in DB          ') +
                s_lmb('0b10000000 128 # error of TRY                       ')
                )
        if err_log:
            self.lg_file.wr_log_error('err_rd_term => ' + str(self.err_status))
    #-------------------------------------------------------------------
    def check_MARKET_time(self, term_dt):
        try:
            dtt = datetime.strptime(term_dt, "%d.%m.%Y %H:%M:%S")
            cur_time = dtt.second + 60 * dtt.minute + 60 * 60 * dtt.hour
            if (
                (cur_time > 35995  and # from 09:59:55 to 14:00:05
                cur_time < 50415) or   #
                (cur_time > 50685  and # from 14:04:55 to 18:45:05
                cur_time < 67505) or
                (cur_time > 68695  and # from 19:04:55 to 23:50:05
                cur_time < 85805)):
                    return True
        except Exception as ex:
            print('ERROR term_dt = ', term_dt)
        return False
    #-------------------------------------------------------------------
    def rd_term_FUT(self):
        # read data FUT from file 'path_file_DATA'----------------------
        print('=> _TERM rd_term_FUT')
        self.err_status  = 0
        try:
            #--- check file self.file_path_DATA ------------------------
            if not os.path.isfile(self.path_file_DATA):
                self.err_status += self.err_file
                return
            buf_stat = os.stat(self.path_file_DATA)
            #--- check size of file ------------------------------------
            if buf_stat.st_size == 0:
                self.err_status += self.err_size
                return
            #--- check time modificated of file ------------------------
            print('self.dt_file       ', self.dt_file)
            print('buf_stat.st_mtime  ', int(buf_stat.st_mtime))
            if int(buf_stat.st_mtime) == self.dt_file:
                #str_dt_file = datetime.fromtimestamp(self.dt_file).strftime('%H:%M:%S')
                self.err_status += self.err_mdf_time
                return
            else:
                self.dt_file = int(buf_stat.st_mtime)
            #--- read TERM file ----------------------------------------
            buf_str = []
            with open(self.path_file_DATA,"r") as fh:
                buf_str = fh.read().splitlines()
            #--- check size of list/file -------------------------------
            if len(buf_str) == 0:
                self.err_status += self.err_file_size
                return
            self.data_in_file = buf_str[:]
            #for i in self.data_in_file:   print(i)
            #
            self.dt_fut = []
            acc = self.account
            for i, item in enumerate(self.data_in_file):
                lst = ''.join(item).replace(',','.').split('|')
                del lst[-1]
                if   i == 0:
                    acc.dt  = lst[0]
                    dtt = datetime.strptime(acc.dt, "%d.%m.%Y %H:%M:%S")
                elif i == 1:
                    acc.arr = [float(j) for j in lst]
                else:
                    b_fut = Class_FUT()
                    b_fut.sP_code = lst[0]
                    b_fut.arr     = [float(k) for k in lst[1:]]
                    self.dt_fut.append(b_fut)
        except Exception as ex:
            self.err_status += self.err_try
        return
    #-------------------------------------------------------------------
    def rd_term_HST(self):
        # read HIST from file 'path_file_HIST'--------------------------
        print('=> _TERM rd_term_HST')
        self.err_status  = 0
        try:
            path_hist = self.path_file_HIST
            #--- check file self.path_file_HIST ------------------------
            if not os.path.isfile(path_hist):
                self.err_status += self.err_file # can not find path_file_HIST
                return
            buf_stat = os.stat(path_hist)
            #--- check size of file ------------------------------------
            if buf_stat.st_size == 0:
                self.err_status += self.err_size # size HIST file is NULL
                return
            #--- read HIST file ----------------------------------------
            buf_str = []
            with open(path_hist,"r") as fh:
                buf_str = fh.read().splitlines()
            #--- check size of list/file -------------------------------
            if len(buf_str) == 0:
                self.err_status += self.err_file_size # the size buf_str(HIST) is NULL
                return
            #--- check MARKET time from 10:00 to 23:45 -----------------
            self.hist_in_file = []
            error_MARKET_time = False
            for i, item in enumerate(buf_str):
                term_dt = item.split('|')[0]
                if self.check_MARKET_time(term_dt):
                    self.hist_in_file.append(item)
                else:
                    error_MARKET_time = True
                    print('error string is ',i)
            #--- repeir file 'path_file_HIST' --------------------------
            if error_MARKET_time:
                with open(path_hist, 'w') as file_HIST:
                    for item in self.hist_in_file:
                        file_HIST.write(item+'\n')
            #
        except Exception as ex:
            print('rd_term_HST\n' + str(ex))
            self.err_status += self.err_try
        return
#=======================================================================
class Class_GLBL():
    def __init__(self):
        self.trm = Class_TRMN()
        c_dir    = os.path.abspath(os.curdir)
        self.db_ARCHV = Class_DB_SQLite(c_dir + '\\DB\\db_ARCH.sqlite')
        self.db_TODAY = Class_DB_SQLite(c_dir + '\\DB\\db_TODAY.sqlite')
        self.cfg_soft = [] # list of table 'cfg_SOFT'
        self.wndw_menu   = ''
        self.stastus_bar = ''
    #-------------------------------------------------------------------
    def read_cfg_soft(self):
        print('=> _GLBL read_cfg_soft')
        try:
            tbl = self.db_TODAY.read_tbl('cfg_SOFT')
            if tbl[0] > 0:
                err_lmb('read_cfg_soft', tbl[1])
                return [2, tbl[1]]
            self.cfg_soft = tbl[1]
            # frm = '%Y-%m-%d %H:%M:%S'
            # self.dt_start_sec = \
                # int(datetime.strptime(self.dt_start, frm).replace(tzinfo=timezone.utc).timestamp())
            for item in self.cfg_soft: print(item)
            self.trm.path_file_DATA = self.cfg_soft[Class_CNST.path_file_DATA][1]
            self.trm.path_file_HIST = self.cfg_soft[Class_CNST.path_file_HIST][1]
            #sg.popup_ok(self.cfg_soft, background_color='LightGreen', title='read_cfg_soft')
        except Exception as ex:
            err_lmb('read_cfg_soft', str(ex))
            return [1, ex]
        return [0, tbl[1]]
#=======================================================================


#=======================================================================
def tabs_layout(nmb_tab, tab_tabs):
    if nmb_tab > len(tab_tabs): nmb_tab = 0
    if   nmb_tab == 0:  # Data_PRFT
        tabs = [[sg.Text('0000.00', font= 'ANY 60', key='_txt_PROFIT_', justification = 'center')],
               ]
    elif nmb_tab == 1:  # File_HIST
        mtrx = [['first' ,35*'-',],
                ['second',35*'-',],
                [14*'-',35*'-',],
                ['last'  ,35*'-',],
                ['lench' ,35*'-',]]
        tabs = [[sg.Table(
                    values   = mtrx,
                    num_rows = min(len(mtrx), 30),
                    headings = Class_CNST.head_data_hst,
                    key      = '_DATA_HIST_FILE_table_',
                    auto_size_columns     = True,
                    justification         = 'center',
                    alternating_row_color = 'darkgrey',
                    )],
               ]
    elif nmb_tab == 2:  # Tbl_HIST
        mtrx = [['first' ,35*'-',],
                ['second',35*'-',],
                [14*'-',35*'-',],
                ['last'  ,35*'-',],
                ['lench' ,35*'-',]]
        tabs = [[sg.Table(
                    values   = mtrx,
                    num_rows = min(len(mtrx), 30),
                    headings = Class_CNST.head_data_hst,
                    key      = '_DATA_HIST_FILE_table_DB_',
                    auto_size_columns     = True,
                    justification         = 'center',
                    alternating_row_color = 'darkgrey',
                    )],
               ]
    elif nmb_tab == 3:  # CFG_SOFT
        mtrx = [['titul         ',35*'-',],
                ['path_file_DATA',35*'-',],
                ['path_file_HIST',35*'-',],
                ['   dt_start   ',35*'-',],
                ['path_file_TXT ',35*'-',]]
        tabs = [[sg.Table(
                    values   = mtrx,
                    num_rows = min(len(mtrx), 10),
                    headings = Class_CNST.head_cfg_soft,
                    key      = '_CFG_SOFT_table_',
                    auto_size_columns     = True,
                    justification         = 'center',
                    alternating_row_color = 'thistle',
                    hide_vertical_scroll  = True,
                    )],
               ]
    elif nmb_tab == 4:  # Data_ACNT
        mtrx = [['Date/Tm','01.01.2020 10:10:10',],
                [14*'-',35*'-',],
                ['BALANCE','',],
                ['PROFIT ','',],
                ['GO     ','',],
                ['DEPOSIT','',]]
        tabs = [[sg.Table(
                    values   = mtrx,
                    num_rows = min(len(mtrx), 30),
                    headings = Class_CNST.head_data_acnt,
                    key      = '_DATA_ACNT_table_',
                    auto_size_columns     = True,
                    justification         = 'center',
                    alternating_row_color = 'lavender',
                    hide_vertical_scroll  = True
                    )]
               ]

    return tabs
#=======================================================================
def main():
    sg.theme('DefaultNoMoreNagging')     # Please always add color to your window DefaultNoMoreNagging
    #test_msg_lmb()
    _gl = Class_GLBL()
    while True: #--- INIT cycle ---------------------------------------#
        rep = _gl.read_cfg_soft()
        if rep[0] > 0:
            err_lmb('main', s_lmb('Could not read table *cfg_soft*!') + s_lmb(rep[1]))
            sg.popup_ok('Could not read table *cfg_soft*!', rep[1], background_color='Coral', title='main')
            return 0
        #bp()
        #
        _gl.trm.rd_term_FUT()
        if _gl.trm.err_status > 0:
            err_lmb('main', s_lmb('Could not read term *data_file*!') + s_lmb(_gl.trm.err_status))
            return 0
        else:
            #sg.popup_ok('Read term *data_file* successfully !', background_color='LightGreen', title='main')
            os.system('cls')  # on windows
        #
        _gl.trm.rd_term_HST()
        if _gl.trm.err_status > 0:
            err_lmb('main', s_lmb('Could not read term *hist_file*!') + s_lmb(_gl.trm.err_status))
        else:
            #sg.popup_ok('Read term *hist_file* successfully !', background_color='LightGreen', title='main')
            os.system('cls')  # on windows
        break
    while True: #--- Menu & Tab Definition ----------------------------#
        menu_def = [['File',    ['Save',     'Clr HIST file',    'Clr HIST table', '---', 'Exit']],
                    ['Service', ['CFG_SOFT', 'Command_2', '---', 'FUT File DAT']],
                    ['Help',    ['About...']],]
        #
        tab_keys = ('-Data_PRFT-', '-File_HIST-', '-Tbl_HIST-', '-CFG_SOFT-', '-Data_ACNT-')
        tab_tabs = ( 'Data PRFT',   'File HIST',   'Tabl HIST',   'Conf SOFT', 'Data ACNT')
        tab_group_layout = [[sg.Tab(tab_tabs[nm], tabs_layout(nm, tab_tabs), key=tab_keys[nm]) for nm in range(len(tab_keys))]]
        #
        layout = [[sg.Menu(menu_def, tearoff=False, pad=(200, 1), key='-MENU-')],
                  [sg.TabGroup(tab_group_layout, enable_events=True,
                               key='-TABGROUP-')],
                  #[sg.Button('Save TXT'), sg.Button('Clear TBL')],
                  [sg.StatusBar(text= '_gl.trm.account.dt' + '  wait ...', size=(40,1),
                                key='-STATUS_BAR-'),
                    sg.Exit(auto_size_button=True)]]
        window = sg.Window('My window with tabs', layout, finalize=True, no_titlebar=False, location=locationXY)
        window.set_title(_gl.cfg_soft[0][1])
        break
    while True: #--- Main Cycle ---------------------------------------#
        event, values = window.read(timeout = DelayMainCycle)
        print(event, values)    # type(event): str,   type(values):dict
        if event in [sg.WIN_CLOSED, 'Exit']:  break
        #
    window.close()
    return 0

if __name__ == '__main__':
    main()

