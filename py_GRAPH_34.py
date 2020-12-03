#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  py_GRAPH_34.py
#  
#=======================================================================
import os, sys, math, time, sqlite3, logging
from datetime import datetime, timezone
import math
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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
hist_day_load  = 2     # ARCHIV history from 23 March
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
    # cfg_pck
    kNm, kKoef, kNul, kEma, kGo, kPos, kNeg = range(7)
    head_cfg_pack  = ['nm', 'koef', 'nul', 'ema', 'go', 'pos', 'neg', 'ratio']
    # arr_fut_a  arr_fut_t
    fAsk, fBid = range(2)
    # data_pck
    head_data_pack = ['nm', 'Ask', 'Bid', 'ema', 'ema_r', 'cnt']
    # arr_pck_a  arr_pck_t
    pAsk, pBid, pEMAf, pEMAf_r, pCnt_EMAf_r = range(5)
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
class Class_str_FUT_PCK(): # Class_str_FUT  Class_str_PCK  Class_cfg_PCK
    def __init__(self):
        self.ind_s, self.dt = 0, ''
        self.arr = []
    def __retr__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
    def __str__(self):
        return 'ind_s = {}, dt = {}{} arr={}'.format(self.ind_s, self.dt, '\n', str(self.arr))
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
class Class_GLBL():
    def __init__(self):
        #self.trm = Class_TRMN()
        c_dir    = os.path.abspath(os.curdir)
        self.lg_file  = Class_LGR      (c_dir + '\\LOG\\py_ARC.log')
        self.db_ARCHV = Class_DB_SQLite(c_dir + '\\DB\\db_ARCH.sqlite')
        self.db_TODAY = Class_DB_SQLite(c_dir + '\\DB\\db_TODAY.sqlite')
        self.cfg_soft = [] # list of table 'cfg_SOFT'
        #
        self.wndw_menu   = ''
        self.stastus_bar = ''
        #
        self.cfg_soft = []          # list of table 'cfg_SOFT'
        self.cfg_pck  = []          # list of table 'cfg_PACK' (unpack)
        self.dt_fut   = []          # list obj FUTs from table 'data_FUT'
        self.account  = Class_ACNT()# obj Class_ACNT()
        #
        self.len_arr_fut_t = 0
        self.arr_fut_t = []
        self.arr_pck_t = []
        self.arr_fut_a = []
        self.arr_pck_a = []
        #
        self.dt_db_TODAY = 0     # time modificated of file db_TODAY (seconds)
        #
        self.err_status  = 0
    #-------------------------------------------------------------------
    def err_DB(self, err_pop = False, err_log = False):
        #self.cnt_errors += 1
        if err_pop:
            err_lmb('err_rd_term',
                s_lmb(bin(self.err_status) + str(5*' ') + str(self.err_status)) )
        if err_log:
            self.lg_file.wr_log_error('err_rd_term => ' + str(self.err_status))
    #-------------------------------------------------------------------
    def prn_arr(self, name_arr, arr):
        print('len(' + name_arr + ')   => ' + str(len(arr)) + '\n' )
        if len(arr) > 4:
            for i in [0,1]: print(arr[i],'\n')
            print('+++++++++++++++++++++++++\n')
            for i in [-2,-1]: print(arr[i],'\n')
        else:
            for item in arr: print(item, '\n')
    #-------------------------------------------------------------------
    def read_unpack_TODAY(self):
        print('=> _GLBL read_unpack_TODAY')
        try:
            # read ALL tables in db_TODAY
            tbl = self.db_TODAY.read_all_tbl()
            if tbl[0] > 0:
                self.err_status = 'read_unpack_TODAY   ' + s_lmb(tbl[1])
                self.err_DB(err_log = True)
                return [2, tbl[1]]
            tbls = tbl[1]
            # unpack ALL tables in db_TODAY
            for item in tbls:
                # unpack data_TICKS --------------------------------------
                if item[0] == 'data_TICKS':
                    pass
                # unpack cfg_SOFT --------------------------------------
                if item[0] == 'cfg_SOFT':
                    self.cfg_soft = item[1]
                    #tbl = self.db_TODAY.read_tbl('cfg_SOFT')
                    #if tbl[0] > 0:
                    #    err_lmb('read_cfg_soft', tbl[1])
                    #    return [2, tbl[1]]
                    #self.cfg_soft = tbl[1]
                    # frm = '%Y-%m-%d %H:%M:%S'
                    # self.dt_start_sec = \
                        # int(datetime.strptime(self.dt_start, frm).replace(tzinfo=timezone.utc).timestamp())
                    for item in self.cfg_soft: print(item)
                    #self.trm.path_file_DATA = self.cfg_soft[Class_CNST.path_file_DATA][1]
                    #self.trm.path_file_HIST = self.cfg_soft[Class_CNST.path_file_HIST][1]
            
                # unpack cfg_PACK --------------------------------------
                if item[0] == 'cfg_PACK':
                    try:
                        self.cfg_pck = []
                        for item in item[1]:
                            arr_k    = item[Class_CNST.kKoef].split(',')
                            arr_koef, buf = [], []
                            for item_k in arr_k:             # '0:2:SR' => [0, 32, 'SR']
                                arr_koef.append([int(f) if f.replace('-','').isdigit() else f for f in item_k.split(':')])
                            buf = [item[Class_CNST.kNm],
                                    arr_koef,
                                    int(item[Class_CNST.kNul]),
                                    [int(e) for e in item[Class_CNST.kEma].split(':')],
                                    int(item[Class_CNST.kGo]),
                                    int(item[Class_CNST.kPos]),
                                    int(item[Class_CNST.kNeg])]
                            while len(Class_CNST.head_cfg_pack)-1 > len(buf):
                                buf.append('')
                            self.cfg_pck.append(buf)
                        # calc_cfg_pack  +++++++++++++++++++++++++++++++
                        mtrx = []
                        for item in self.dt_fut:
                            mtrx.append([item.sP_code] + item.arr)
                        # kNm, kKoef, kNul, kEma, kGo, kPos, kNeg = range(7)
                        # kKoef => [0, 2, 'SR'] =>  list =>
                        #           0 -index FUT   1 - number fut's  2 - name fut
                        cfg_go_pos_neg = []
                        for item in self.cfg_pck:
                            pck_go, pck_pos, pck_neg = 0, 0, 0
                            for pck in item[Class_CNST.kKoef]:
                                prc = int((mtrx[pck[0]][Class_CNST.sAsk] + mtrx[pck[0]][Class_CNST.sBid])/2)
                                if pck[0] != 9:
                                    pck_go += int(abs(pck[1]) * mtrx[pck[0]][Class_CNST.sFut_go])
                                else:
                                    pck_go += int(abs(pck[1]/10) * mtrx[pck[0]][Class_CNST.sFut_go])
                                if pck[1] > 0:  pck_pos += int(prc * pck[1])
                                else:           pck_neg += int(prc * abs(pck[1]))
                            cfg_go_pos_neg.append( [pck_go, pck_pos, pck_neg] )
                        for i, item in enumerate(cfg_go_pos_neg):
                            self.cfg_pck[i][-3:] = item

                    except Exception as ex:
                        self.err_status = 'read_cfg_PACK / try  ' + s_lmb(ex)
                        self.err_DB(err_log = True)
                        return [3, ex]
                # unpack data_FUT --------------------------------------
                if item[0] == 'data_FUT':
                    try:
                        self.dt_fut = []
                        acc = self.account
                        for i, item in enumerate(item[1]):
                            lst = ''.join(item).replace(',','.').split('|')
                            del lst[-1]
                            if   i == 0:
                                acc.dt  = lst[0]
                            elif i == 1:
                                acc.arr = [float(j) for j in lst]
                            else:
                                b_fut = Class_FUT()
                                b_fut.sP_code = lst[0]
                                b_fut.arr     = [float(k) for k in lst[1:]]
                                self.dt_fut.append(b_fut)
                        # print(self.account)
                        # for i in self.dt_fut:   print(i)

                    except Exception as ex:
                        self.err_status = 'read_data_FUT / try  ' + s_lmb(ex)
                        self.err_DB(err_log = True)
                        return [4, ex]
                # unpack hist_FUT --------------------------------------
                if item[0] == 'hist_FUT':
                    try:
                        hist_fut = item[1]
                        self.arr_fut_t = []
                        for cnt, i_str in enumerate(hist_fut):
                            mn_pr, mn_cr = '', ''
                            if cnt == 0 :
                                mn_pr, mn_cr = '', '00'
                            else:
                                mn_pr = hist_fut[cnt-1][1][14:16]
                                mn_cr = hist_fut[cnt-0][1][14:16]
                            if mn_pr != mn_cr:
                                s = Class_str_FUT_PCK()
                                s.ind_s = i_str[0]
                                s.dt    = i_str[1].split('|')[0].split(' ')
                                arr_buf = i_str[1].replace(',', '.').split('|')[1:-1]
                                for item in (zip(arr_buf[::2], arr_buf[1::2])):
                                    s.arr.append([float(item[Class_CNST.fAsk]), float(item[Class_CNST.fBid])])
                                self.arr_fut_t.append(s)
                            if len(self.arr_fut_t) % 1000 == 0:  print(len(self.arr_fut_t), end='\r')
                        # self.prn_arr('arr_fut_t', self.arr_fut_t)
                        # ok_lmb('unpack hist_FUT', s_lmb('unpack hist_FUT TODAY successfully !'))
                    except Exception as ex:
                        self.err_status = 'unpack_hist_FUT / try  ' + s_lmb(ex)
                        self.err_DB(err_log = True)
                        return [5, ex]
                # unpack hist_PACK -------------------------------------
                if item[0] == 'hist_PACK':
                    pass
        except Exception as ex:
            err_lmb('read_unpack_TODAY   ', str(ex))
            return [1, ex]

        return [0, tbls]
    #-------------------------------------------------------------------
#=======================================================================
def event_TIMEOUT(_gl, wndw, ev, val):
    event_TABGROUP(_gl, wndw, ev, val)  # just for refresh UI
    os.system('cls')  # on windows
#=======================================================================

#=======================================================================
def event_MENU(_gl, wndw, ev, val):
    #----------------------------------------
    if ev == 'PACK GRAPH':
        pass
    #----------------------------------------
    if ev == 'About...':
        wndw.disappear()
        sg.popup('About this program  Ver 1.0',
                 'Python ' + str(sys.version_info.major) + '.' + str(sys.version_info.minor),
                 'PySimpleGUI Ver  ' + str(sg.version),
                 '"Matplotlib Ver  ' + str(mpl.__version__),
                 grab_anywhere=True)
        wndw.reappear()
#=======================================================================
def event_TABGROUP(_gl, wndw, ev, val):     #--- refresh TABGROUP ---
    #-------------------------------------------------------------------
    if val['-TABGROUP-'] == '-CFG_SOFT-':
        wndw['_CFG_SOFT_table_'].Update(_gl.cfg_soft)
    #-------------------------------------------------------------------
    if val['-TABGROUP-'] == '-FUT_TOD-':
        rep = _gl.db_TODAY.read_tbl('hist_FUT')
        if rep[0] == 0:
            if len(rep[1]) > 1:
                mtrx_db = [['first', rep[1][0][1].split('|')[0],],
                           ['second',rep[1][1][1].split('|')[0],],
                           [14*'-',35*'-',],
                           ['last' , rep[1][-1][1].split('|')[0],],
                           ['lench', len(rep[1]),]]
            else:
                mtrx_db = [['first', '',],
                           ['second','',],
                           [14*'-',35*'-',],
                           ['last' , '',],
                           ['lench', len(rep[1]),]]
        wndw['_HIST_FUT_TOD_table_DB_'].Update(mtrx_db)
    #-------------------------------------------------------------------
    if  val['-TABGROUP-'] == '-FUT_ARC-':
        rep = _gl.db_ARCHV.read_tbl('hist_FUT')
        if rep[0] == 0:
            if len(rep[1]) > 1:
                mtrx_db = [['first', rep[1][0][1].split('|')[0],],
                           ['second',rep[1][1][1].split('|')[0],],
                           [14*'-',35*'-',],
                           ['last' , rep[1][-1][1].split('|')[0],],
                           ['lench', len(rep[1]),]]
            else:
                mtrx_db = [['first', '',],
                           ['second','',],
                           [14*'-',35*'-',],
                           ['last' , '',],
                           ['lench', len(rep[1]),]]
        wndw['_HIST_FUT_ARC_table_DB_'].Update(mtrx_db)
    #-------------------------------------------------------------------
    if  val['-TABGROUP-'] == '-PCK_TOD-':
        rep = _gl.db_TODAY.read_tbl('hist_PACK')
        if rep[0] == 0:
            if len(rep[1]) > 1:
                mtrx_db = [['first', rep[1][0][1].split(' ')[0]  + ' ' + rep[1][0][1].split(' ')[1],],
                           ['second',rep[1][1][1].split(' ')[0]  + ' ' + rep[1][1][1].split(' ')[1],],
                           [14*'-',35*'-',],
                           ['last' , rep[1][-1][1].split(' ')[0] + ' ' + rep[1][-1][1].split(' ')[1],],
                           ['lench', len(rep[1]),]]
            else:
                mtrx_db = [['first', '',],
                           ['second','',],
                           [14*'-',35*'-',],
                           ['last' , '',],
                           ['lench', len(rep[1]),]]
        wndw['_HIST_PCK_TOD_table_DB_'].Update(mtrx_db)
    #-------------------------------------------------------------------
    if  val['-TABGROUP-'] == '-PCK_ARC-':
        rep = _gl.db_ARCHV.read_tbl('hist_PACK')
        if rep[0] == 0:
            if len(rep[1]) > 1:
                mtrx_db = [['first', rep[1][0][1].split(' ')[0]  + ' ' + rep[1][0][1].split(' ')[1],],
                           ['second',rep[1][1][1].split(' ')[0]  + ' ' + rep[1][1][1].split(' ')[1],],
                           [14*'-',35*'-',],
                           ['last' , rep[1][-1][1].split(' ')[0] + ' ' + rep[1][-1][1].split(' ')[1],],
                           ['lench', len(rep[1]),]]
            else:
                mtrx_db = [['first', '',],
                           ['second','',],
                           [14*'-',35*'-',],
                           ['last' , '',],
                           ['lench', len(rep[1]),]]
        wndw['_HIST_PCK_ARC_table_DB_'].Update(mtrx_db)
    #-------------------------------------------------------------------
    else:
        pass
#=======================================================================
def tabs_layout(nmb_tab, tab_tabs):
    if nmb_tab == 'Cfg SOFT':  #---------------------------------------
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
    if nmb_tab == 'fut TOD':  #---------------------------------------
        mtrx = [['first' ,35*'-',],
                ['second',35*'-',],
                [14*'-',35*'-',],
                ['last'  ,35*'-',],
                ['lench' ,35*'-',]]
        tabs = [[sg.Table(
                    values   = mtrx,
                    num_rows = min(len(mtrx), 30),
                    headings = Class_CNST.head_data_hst,
                    key      = '_HIST_FUT_TOD_table_DB_',
                    auto_size_columns     = True,
                    justification         = 'center',
                    alternating_row_color = 'darkgrey',
                    )],
               ]
    if nmb_tab == 'fut ARC':  #---------------------------------------
        mtrx = [['first' ,35*'-',],
                ['second',35*'-',],
                [14*'-',35*'-',],
                ['last'  ,35*'-',],
                ['lench' ,35*'-',]]
        tabs = [[sg.Table(
                    values   = mtrx,
                    num_rows = min(len(mtrx), 35),
                    headings = Class_CNST.head_data_hst,
                    key      = '_HIST_FUT_ARC_table_DB_',
                    auto_size_columns     = True,
                    justification         = 'center',
                    alternating_row_color = 'darkgrey',
                    )],
                 #[sg.Button('APPEND', key='-APPEND_TXT_in_ARCH-')],
               ]
    if nmb_tab == 'pck TOD':  #---------------------------------------
        mtrx = [['first' ,35*'-',],
                ['second',35*'-',],
                [14*'-',35*'-',],
                ['last'  ,35*'-',],
                ['lench' ,35*'-',]]
        tabs = [[sg.Table(
                    values   = mtrx,
                    num_rows = min(len(mtrx), 35),
                    headings = Class_CNST.head_data_hst,
                    key      = '_HIST_PCK_TOD_table_DB_',
                    auto_size_columns     = True,
                    justification         = 'center',
                    alternating_row_color = 'darkgrey',
                    )],
                #[sg.Button('CALC', key='-CALC_UPDATE_PCK_ARCH-')],
               ]
        
    if nmb_tab == 'pck ARC':  #---------------------------------------
        mtrx = [['first' ,35*'-',],
                ['second',35*'-',],
                [14*'-',35*'-',],
                ['last'  ,35*'-',],
                ['lench' ,35*'-',]]
        tabs = [[sg.Table(
                    values   = mtrx,
                    num_rows = min(len(mtrx), 35),
                    headings = Class_CNST.head_data_hst,
                    key      = '_HIST_PCK_ARC_table_DB_',
                    auto_size_columns     = True,
                    justification         = 'center',
                    alternating_row_color = 'darkgrey',
                    )],
                #[sg.Button('CALC', key='-CALC_UPDATE_PCK_ARCH-')],
               ]
        
    return tabs
#======================================================================= 
def main():
    sg.theme('DefaultNoMoreNagging')     # Please always add color to your window DefaultNoMoreNagging
    ##test_msg_lmb()
    _gl = Class_GLBL()
    while True: #--- INIT cycle ---------------------------------------#
        rep = _gl.read_unpack_TODAY()
        if rep[0] > 0:
            err_lmb('main', s_lmb('Error read_unpack_TODAY!') + s_lmb(rep[1]))
            return 0
        else:
            #sg.popup_ok(s_lmb('Read & unpack ALL tables TODAY successfully !'),
            #    background_color='LightGreen', title='main')
            os.system('cls')  # on windows
        #---------------------------------------------------------------
        pass
        #---------------------------------------------------------------
        break
    while True: #--- Menu & Tab Definition ----------------------------#
        menu_def = [['Service', ['PACK GRAPH', '---', 'Exit']],
                    ['Help',    ['About...']],]
        #
        tab_keys = ('-CFG_SOFT-', '-FUT_TOD-', '-PCK_TOD-', '-FUT_ARC-', '-PCK_ARC-')
        tab_tabs = ( 'Cfg SOFT' ,  'fut TOD' ,  'pck TOD' ,  'fut ARC',   'pck ARC')
        tab_group_layout = [[sg.Tab(tab_tabs[nm], tabs_layout(tab_tabs[nm], tab_tabs), key=tab_keys[nm]) for nm in range(len(tab_keys))]]
        #
        layout = [[sg.Menu(menu_def, tearoff=False, pad=(200, 1), key='-MENU-')],
                  [sg.TabGroup(tab_group_layout, enable_events=True,
                               key='-TABGROUP-')],
                  #[sg.Button('Save TXT'), sg.Button('Clear TBL')],
                  [sg.StatusBar(text= '_gl.account.dt' + '  wait ...', size=(40,1),
                                key='-STATUS_BAR-'),
                    sg.Exit(auto_size_button=True)]]
        window = sg.Window('My window with tabs', layout, finalize=True, no_titlebar=False, location=locationXY)
        window.set_title(_gl.cfg_soft[0][1] + '_GRAPH_34')
        break
    while True: #--- Main Cycle ---------------------------------------#
        event, values = window.read(timeout = DelayMainCycle)
        print(event, values)    # type(event): str,   type(values):dict
        if event in [sg.WIN_CLOSED, 'Exit']:  break
        #
        if event in ['__TIMEOUT__']:
            event_TIMEOUT(_gl, window, event, values)
        #
        if event in ['-TABGROUP-']:
            event_TABGROUP(_gl, window, event, values)
        #
        if event in ['PACK GRAPH',
                     'About...']:
            event_MENU(_gl, window, event, values)
    window.close()
    return 0

if __name__ == '__main__':
    main()

