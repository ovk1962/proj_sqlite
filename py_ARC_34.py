#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  py_ARC_34.py
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
    def update_tbl_cfg_pack(self):
        print('=> _GL update_tbl_cfg_pack ')
        try:
            cfg_lst, cfg = [], self.cfg_pck
            #  ['pack1', [[0, 3, 'SR'], [1, 2, 'GZ']], 7517, [1111, 150], 0, 0, 0]
            #  ['pack1', '0:3:SR,1:2:GZ', 7517, '1111:150', 0, 0, 0]
            for j in range(len(cfg)):
                str_koef = ''
                for ss in cfg[j][Class_CNST.kKoef]:
                    str_koef += ':'.join((str(s) for s in ss)) + ','
                cfg_lst.append([cfg[j][Class_CNST.kNm],       # kNm
                                str_koef[:-1],          # kKoef
                                cfg[j][Class_CNST.kNul],      # kNul
                                ':'.join(str(s) for s in cfg[j][Class_CNST.kEma]),
                                cfg[j][Class_CNST.kGo],       # kGo
                                cfg[j][Class_CNST.kPos],      # kPos
                                cfg[j][Class_CNST.kNeg]       # kNeg
                                ])
            rep = self.db_TODAY.update_tbl('cfg_PACK', cfg_lst, val = ' VALUES(?,?,?,?,?,?,?)')
            if rep[0] > 0:
                self.err_status = 'update_tbl_cfg_pack   ' + s_lmb(rep[1])
                self.err_DB(err_log = True)
                return [2, rep[1]]
        except Exception as ex:
            self.err_status = 'update_tbl_cfg_pack / try  ' + s_lmb(ex)
            self.err_DB(err_log = True)
            return [1, ex]
        return [0, cfg_lst]
    #-------------------------------------------------------------------
    def unpack_str_fut(self, hist_fut):
        print('=> _GL unpack_str_fut ', len(hist_fut))
        try:
            arr_fut = []
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
                    arr_fut.append(s)
                if len(arr_fut) % 1000 == 0:  print(len(arr_fut), end='\r')

        except Exception as ex:
            self.err_status = 'unpack_str_fut / try  ' + s_lmb(ex)
            self.err_DB(err_log = True)
            return [1, ex]

        return [0, arr_fut]
    #-------------------------------------------------------------------
    def pack_arr_pck(self, arr_pk, db_pk, nm_tbl_pk):
        print('=> _PACK pack_arr_pck ', nm_tbl_pk, len(arr_pk))
        try:
            pck_list = []
            #pAsk, pBid, EMAf, EMAf_r, cnt_EMAf_r = range(5)
            if len(arr_pk) > 0:
                for i_hist, item_hist in enumerate(arr_pk):
                    if i_hist % 1000 == 0:  print(str(i_hist), end='\r')
                    #bp()
                    buf_dt = item_hist.dt[0] + ' ' + item_hist.dt[1] + ' '
                    buf_s = ''
                    for i_pack, item_pack in enumerate(item_hist.arr):
                        buf_s += str(item_pack[Class_CNST.pAsk]) + ' ' + str(item_pack[Class_CNST.pBid])   + ' '
                        buf_s += str(item_pack[Class_CNST.pEMAf]) + ' ' + str(item_pack[Class_CNST.pEMAf_r]) + ' '
                        buf_s += str(item_pack[Class_CNST.pCnt_EMAf_r]) + '|'
                    pck_list.append((item_hist.ind_s, buf_dt + buf_s.replace('.', ',')))
            ''' rewrite data from table ARCHIV_PACK & PACK_TODAY & DATA ----'''
            r_update = db_pk.update_tbl(nm_tbl_pk, pck_list, val = ' VALUES(?,?)')
            if r_update[0] > 0:
                self.err_status = 'pack_arr_pck / Did not update *hist_PACK*!  ' + s_lmb(r_update[1])
                self.err_DB(err_pop = True, err_log = True)
                return [2, self.err_status]
        except Exception as ex:
            self.err_status = 'pack_arr_pck / Try error !  ' + str(ex)
            self.err_DB(err_pop = True, err_log = True)
            return [1, self.err_status]

        return [0, pck_list]
    #-------------------------------------------------------------------
    def unpack_str_pck(self, hist_pck):
        print('=> _GL unpack_str_pck ', len(hist_pck))
        try:
            arr_pck = []
            for cnt, i_str in enumerate(hist_pck):
                buf = i_str[1].replace(',','.').split('|')
                del buf[-1]
                s = Class_str_FUT_PCK()
                s.ind_s = i_str[0]
                for cn, item in enumerate(buf):
                    if cn == 0 : s.dt = item.split(' ')[0:2]
                    ind_0 = 0 if cn != 0 else 2
                    s.arr.append([int(float(f)) for f in item.split(' ')[ind_0:]])
                arr_pck.append(s)
                if len(arr_pck) % 1000 == 0:  print(len(arr_pck), end='\r')

                if (len(arr_pck) == 0):
                    #for item in self.nm:
                    for item in self.cfg_pck:  arr_pck.append([])
        except Exception as ex:
            return [1, ex]
        return [0, arr_pck]
    #-------------------------------------------------------------------
    def get_hist_pck_period(self, dt_from, dt_to):
        print('=> _GL get_hist_pck_period ', dt_from, dt_to)
        # STRINGS dt_from  &  dt_to  should has format  "%Y-%m-%d %H:%M:%S"
        try:
            arr_pck = []
            dtt_from_sec  = int(dt_from.replace(tzinfo=timezone.utc).timestamp())
            dtt_to_sec    = int(dt_to.replace(tzinfo=timezone.utc).timestamp())
            if dtt_from_sec < dtt_to_sec:
                rep = self.db_ARCHV.read_tbl_between('hist_PACK', dtt_from_sec, dtt_to_sec)
                if rep[0] != 0:
                    return [1, 'Error - get_hist_pck_period']

                for cnt, i_str in enumerate(rep[1]):
                    buf = i_str[1].replace(',','.').split('|')
                    del buf[-1]
                    s = Class_str_FUT_PCK()
                    s.ind_s = i_str[0]
                    for cn, item in enumerate(buf):
                        if cn == 0 : s.dt = item.split(' ')[0:2]
                        ind_0 = 0 if cn != 0 else 2
                        s.arr.append([int(float(f)) for f in item.split(' ')[ind_0:]])
                    arr_pck.append(s)
                    if len(arr_pck) % 1000 == 0:  print(len(arr_pck), end='\r')

        except Exception as ex:
            return [1, ex]
        return [0, arr_pck]
    #-------------------------------------------------------------------
    def clc_ASK_BID(self, arr_FUT):
        print('=> _GL clc_ASK_BID ', len(arr_FUT))
        try:
            b_null = True if (self.cfg_pck[0][Class_CNST.kNul] == 0) else False
            ''' init  table ARCHIV_PACK  --------------------'''
            arr_pk  = []  # list of Class_str_FUT_PCK()
            nm_pcks = len(self.cfg_pck)
            for idx, item in enumerate(arr_FUT): # change STRINGs
                if idx % 1000 == 0:  print(idx, end='\r')
                arr_bb = Class_str_FUT_PCK()
                arr_bb.ind_s, arr_bb.dt  = item.ind_s, item.dt
                for p in range(nm_pcks):        # change PACKETs
                    ask_p, bid_p, arr_pp = 0, 0, [0, 0, 0, 0, 0]
                    for jdx, jtem in enumerate(self.cfg_pck[p][Class_CNST.kKoef]): # calc PACK
                        i_koef, k_koef = jtem[0], jtem[1]
                        if k_koef > 0 :
                            ask_p +=  k_koef * item.arr[i_koef][Class_CNST.fAsk]
                            bid_p +=  k_koef * item.arr[i_koef][Class_CNST.fBid]
                        if k_koef < 0 :
                            ask_p +=  k_koef * item.arr[i_koef][Class_CNST.fBid]
                            bid_p +=  k_koef * item.arr[i_koef][Class_CNST.fAsk]

                    if idx == 0 and b_null:
                        arr_pp = [0, 0, 0, 0, 0]
                        self.cfg_pck[p][Class_CNST.kNul]= int((ask_p + bid_p)/2)
                        arr_bb.arr.append(arr_pp)
                        continue
                    arr_pp = [int(ask_p - self.cfg_pck[p][Class_CNST.kNul]), int(bid_p - self.cfg_pck[p][Class_CNST.kNul]), 0, 0, 0]
                    arr_bb.arr.append(arr_pp)
                arr_pk.append(arr_bb)

        except Exception as ex:
            self.err_status = 'clc_ASK_BID / try  ' + s_lmb(ex)
            self.err_DB(err_log = True)
            return [1, ex]

        return [0, arr_pk]
    #-------------------------------------------------------------------
    def clc_EMA(self, arr_pk, last_pk):
        print('=> _GL clc_EMA ', len(arr_pk))
        b_null = True if (last_pk.ind_s == 0) else False
        try:
            nm_pcks = len(self.cfg_pck)
            koef_EMA, k_EMA_rnd = [], []
            for kdx in range(nm_pcks):
                k_ema = self.cfg_pck[kdx][Class_CNST.kEma]
                koef_EMA.append(round(2/(1+int(k_ema[0])),5))
                k_EMA_rnd.append(int(k_ema[1]))
            for idx, item in enumerate(arr_pk):
                if idx % 1000 == 0:  print(idx, end='\r')
                if idx == 0:
                    if not b_null:
                        arr_pk[0] = last_pk
                else:
                    for pdx, ptem in enumerate(item.arr):
                        cr = arr_pk[idx].arr[pdx]
                        pr = arr_pk[idx-1].arr[pdx]
                        cr[Class_CNST.pEMAf]  = round(pr[Class_CNST.pEMAf] + (int((ptem[Class_CNST.pAsk] + ptem[Class_CNST.pBid])/2) - pr[Class_CNST.pEMAf]) * koef_EMA[pdx], 1)
                        cr[Class_CNST.pEMAf_r]= k_EMA_rnd[pdx] * math.ceil(cr[Class_CNST.pEMAf] / k_EMA_rnd[pdx] )
                        if pr[Class_CNST.pEMAf_r] > cr[Class_CNST.pEMAf_r]:
                            cr[Class_CNST.pCnt_EMAf_r] = 0 if pr[Class_CNST.pCnt_EMAf_r] > 0 else pr[Class_CNST.pCnt_EMAf_r]-1
                        elif pr[Class_CNST.pEMAf_r] < cr[Class_CNST.pEMAf_r]:
                            cr[Class_CNST.pCnt_EMAf_r] = 0 if pr[Class_CNST.pCnt_EMAf_r] < 0 else pr[Class_CNST.pCnt_EMAf_r]+1
                        else:
                            cr[Class_CNST.pCnt_EMAf_r] = pr[Class_CNST.pCnt_EMAf_r]
        except Exception as ex:
            self.err_status = 'clc_EMA / try  ' + s_lmb(ex)
            self.err_DB(err_log = True)
            return [1, ex]

        return [0, arr_pk]
    #-------------------------------------------------------------------
    def calc_arr_pck(self, last_sz = 100000):
        print('=> _GL calc_arr_pck ')
        try:
            #start_time = datetime.now()
            #--- read ALL hist_FUT archiv  -----------------------------
            rep = self.db_ARCHV.read_tbl('hist_FUT')
            if rep[0] > 0:
                self.err_status = 'calc_arr_pck / Not read db_ARCHV *hist_FUT*!  ' + s_lmb(rep[1])
                self.err_DB(err_pop = True, err_log = True)
                return [1, self.err_status]
            # self.prn_arr('arr_fut_a', rep[1])
            # ok_lmb('read_tbl arr_fut_a', '2 cfg_pck')
            #--- Speed of Unpack is about 1500 str/per 1 sec -----------
            #--- unpack_str_fut hist_FUT archiv  -----------------------
            rep = self.unpack_str_fut(rep[1][-(last_sz):])
            if rep[0] > 0:
                err_lmb('main', s_lmb('Did not unpack *hist_FUT* from ARCH!') + s_lmb(rep[1]))
                self.err_status = 'calc_arr_pck / Not unpack *hist_FUT* from ARCH!  ' + s_lmb(rep[1])
                self.err_DB(err_pop = True, err_log = True)
                return [2, self.err_status]
            self.arr_fut_a = rep[1]
            # self.prn_arr('arr_fut_a', rep[1])
            # ok_lmb('unpack_str_fut arr_fut_a', 'arr_fut_a')
            #--- prepair kNul to calc hist_PACK archiv -----------------
            for i in range(len(self.cfg_pck)):
                self.cfg_pck[i][Class_CNST.kNul] = 0
            # ok_lmb('read_cfg_PACK', '1 cfg_pck')
            #--- calc ASK_BID hist_PACK archiv  ------------------------
            rep = self.clc_ASK_BID(self.arr_fut_a)
            if rep[0] > 0:
                self.err_status = 'calc_arr_pck / Did not CALC ASK_BID *hist_PACK*!  ' + s_lmb(rep[1])
                self.err_DB(err_pop = True, err_log = True)
                return [3, self.err_status]
            self.arr_pck_a = rep[1]
            # ok_lmb('clc_ASK_BID arr_fut_a', 'arr_pck_a')
            #--- update kNul in cfg_pack  ------------------------------
            self.update_tbl_cfg_pack()
            # self.read_cfg_PACK()
            #--- calc EMA hist_PACK archiv  ----------------------------
            rep = self.clc_EMA(self.arr_pck_a, Class_str_FUT_PCK())
            if rep[0] > 0:
                self.err_status = 'calc_arr_pck / Did not CALC EMA *hist_PACK*!  ' + s_lmb(rep[1])
                self.err_DB(err_pop = True, err_log = True)
                return [4, self.err_status]
            self.arr_pck_a = rep[1]
            #print('Time delay calc_arr_pck = ', datetime.now() - start_time)
            #self.prn_arr('arr_pck_a', rep[1])
            #ok_lmb('clc_EMA arr_pck_a', 'arr_pck_a')
            #--- pack hist_PACK archiv  --------------------------------
            rep = self.pack_arr_pck(self.arr_pck_a, self.db_ARCHV, 'hist_PACK')
            if rep[0] > 0:
                self.err_status = 'calc_arr_pck / Did not update *hist_PACK* db_ARCHV!  ' + s_lmb(rep[1])
                self.err_DB(err_pop = True, err_log = True)
                return [5, self.err_status]
        except Exception as ex:
            self.err_status = 'calc_arr_pck / Try error!  ' + str(ex)
            self.err_DB(err_pop = True, err_log = True)
            return [1, self.err_status]

        return [0, 'ok']
    #-------------------------------------------------------------------
    def calc_arr_pck_today(self):
        print('=> _GL calc_arr_pck_today ')
        try:
            rep = self.clc_ASK_BID(self.arr_fut_t)
            if rep[0] > 0:
                self.err_status = 'calc_arr_pck_today / Did not CALC ASK_BID *hist_PACK* today!  ' + s_lmb(rep[1])
                self.err_DB(err_log = True)
                return [2, self.err_status]
            self.arr_pck_t = rep[1]

            rep = self.clc_EMA(self.arr_pck_t, self.arr_pck_a[-1])
            if rep[0] > 0:
                self.err_status = 'calc_arr_pck_today / Did not CALC EMA *hist_PACK* today!  ' + s_lmb(rep[1])
                self.err_DB(err_log = True)
                return [3, self.err_status]
            self.arr_pck_t = rep[1][1:]

            # pck_t = self.pack_arr_pck(self.arr_pck_t, self.db_TODAY, 'hist_PACK')
            # if pck_t[0] > 0:
            #     return [7, 'Problem of pack_arr_pck!\n' + pck_t[1]]

        except Exception as ex:
            self.err_status = 'calc_arr_pck_today / Try error!  ' + str(ex)
            self.err_DB(err_log = True)
            return [1, self.err_status]

        return [0, 'ok']
#=======================================================================
def GRAPH_One_PACK(_gl, wndw, ev, val, period_days = 1):
    sg.ChangeLookAndFeel('BlueMono')
    def draw_figure(canvas, figure):
        figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
        figure_canvas_agg.draw()
        figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
        return figure_canvas_agg
    choices = []
    for item in _gl.cfg_pck:
        choices.append(item[Class_CNST.kNm])

    layout = [
                [sg.Canvas(size=(640, 480), key='-CANVAS-')],
                [sg.Button(' REFRESH ', key='-REFRESH_GRAPH_One_PACK-'),
                 sg.T('  Select PACKET '),
                 sg.Combo(choices, default_value=choices[0], size=(15, len(choices)), key='-NUM_PACK-'),
                 #sg.T('    Select Period Days '),
                 #sg.Slider(range=(1, hist_day_load), orientation='h', size=(11, 15), key='-SLIDER_GRAPH_TOD-'),
                 #sg.Input(key='-IN_CALENDAR-', size=(20,1)),
                 #sg.CalendarButton('Calendar', target='-IN_CALENDAR-', format='%d.%m.%Y', no_titlebar=False, begin_at_sunday_plus=1,),
                 # sg.Button('Date Popup'),
                 #sg.T(25*' '),
                 sg.Button('Close')],
             ]
    wnd_5 = sg.Window('GRAPH / One PACK', layout, no_titlebar=False, modal=False, finalize=True, location=(150, 100))

    canvas_elem = wnd_5['-CANVAS-']
    canvas = canvas_elem.TKCanvas
    # draw the intitial scatter plot
    fig = Figure(figsize=(10, 5), dpi=100)
    fig.subplots_adjust(left=0.07, right=0.94, bottom=0.1, top=0.9)
    ax  = fig.add_subplot(111)
    ax2 = ax.twinx()
    #ax.set_xticks([])
    fig_agg = draw_figure(canvas, fig)

    while True: #--- Main Cycle ---------------------------------------#
        e, v = wnd_5.read()
        if e in [sg.WIN_CLOSED, 'Close']:
            break

        elif e == '-REFRESH_GRAPH_One_PACK-':
            #--- fix number packets in GRAPHik
            num_packet = 0
            if v['-NUM_PACK-'][2] == '_':
                num_packet = int(v['-NUM_PACK-'][1])
            else:
                num_packet = int(v['-NUM_PACK-'][1:3])
            print('    -NUM_PACK-    ', num_packet )
            arr_num_pack = [num_packet]

            #--- read ALL hist_FUT archiv  -----------------------------
            req = _gl.db_TODAY.read_tbl('hist_PACK')
            if req[0] > 0:
                _gl.err_status = 'GRAPH_One_PACK / Not read db_ARCHV *hist_PACK*!  ' + s_lmb(req[1])
                _gl.err_DB(err_pop = True, err_log = True)
                return
            rep = _gl.db_ARCHV.read_tbl('hist_PACK')
            if rep[0] > 0:
                _gl.err_status = 'GRAPH_One_PACK / Not read db_ARCHV *hist_PACK*!  ' + s_lmb(rep[1])
                _gl.err_DB(err_pop = True, err_log = True)
                return
            #_gl.prn_arr('db_ARCHV=>hist_PACK=>',rep[1][-1])
            #
            period_tm = period_days
            index_last_day = len(rep[1])
            df = rep[1][-1][1].split('|')[0].split(' ')[0]
            #print('df = ', df)
            for item in reversed(rep[1]):
                index_last_day -= 1
                if item[1].split('|')[0].split(' ')[0] != df:
                    df = item[1].split('|')[0].split(' ')[0]
                    period_tm -= 1
                if period_tm == 0:
                    break
            index_last_day += 1

            req = _gl.unpack_str_pck(rep[1][index_last_day:] + req[1])
            #print('req[1][0] => ',req[1][0])
            if req[0] > 0:
                err_lmb('main', s_lmb('Error unpack_str_pck!') + s_lmb(req[1]))
                return
            else:
                _gl.arr_pck_a = req[1]
            
            arr_pk_graph = []
            for item in _gl.arr_pck_a:
                arr_bb = Class_str_FUT_PCK()
                arr_bb.ind_s, arr_bb.dt  = item.ind_s, item.dt
                for ktem in arr_num_pack:
                    arr_bb.arr.append(item.arr[ktem])
                arr_pk_graph.append(arr_bb)
            #print('arr_pk_graph=>',arr_pk_graph[0])
            #
            if len(arr_pk_graph) > 0:
                print('len(arr_pk_graph) = ', len(arr_pk_graph))
                print('arr_pk_graph[0]  = ', arr_pk_graph[0])
                print('arr_pk_graph[-1] = ', arr_pk_graph[-1])
            #
            x, y_ASK, y_BID, y_EMA, y_EMAr, y_CNT = [], [], [], [], [], []
            for cnt, item in enumerate(arr_pk_graph):
                x.append(item.dt[1] + '\n' + item.dt[0])
                y_ASK.append(item.arr[0][0])
                y_BID.append(item.arr[0][1])
                y_EMA.append(item.arr[0][2])
                y_EMAr.append(item.arr[0][3])
                y_CNT.append(item.arr[0][4])

            ax.cla()
            ax2.cla()

            ax.scatter(x, y_ASK, c='red',   label='ASK', s=1) # alpha=0.3, edgecolors='none')
            ax.scatter(x, y_BID, c='blue',  label='BID', s=1) # alpha=0.3, edgecolors='none')
            ax.scatter(x, y_EMAr, c='lightgreen', label='y_EMAr', alpha=0.25,  s=3) # alpha=0.5, edgecolors='none')

            ax2.plot(x, y_CNT, color = (0.1, 0.2, 0.9, 0.5), linewidth = 5, label='CNT')
            #ax2.scatter(x, y_CNT, c='green', label='CNT', alpha=0.75,  s=3) # alpha=0.3, edgecolors='none')
            ax2.grid(False)
            ax2.set_xticks([])

            ax.tick_params(axis='x', which='major', labelsize=6)
            ax.tick_params(axis='y', which='major', labelsize=10)
            ax.xaxis.set_major_locator(plt.MaxNLocator(10))
            #ax.locator_params(tight=True, nbins = 5)
            ax.grid(axis = 'both')

            ax.legend(loc='upper left')
            ax2.legend(loc='upper right')
            fig_agg.draw()

        print(e, v)    # type(event): str,   type(values):dict
    wnd_5.close()
    sg.ChangeLookAndFeel('SystemDefault')
#=======================================================================
def event_TIMEOUT(_gl, wndw, ev, val):
    event_TABGROUP(_gl, wndw, ev, val)  # just for refresh UI
    os.system('cls')  # on windows
#=======================================================================
def event_MENU(_gl, wndw, ev, val):
    #----------------------------------------
    if ev == 'CFG_SOFT':
        if val['-TABGROUP-'] == '-CFG_SOFT-':
            if len(val['_CFG_SOFT_table_']) == 0:
                sg.popup_ok('You MUST choise ROW', background_color='LightGrey', title=ev)
            else:
                slct = _gl.cfg_soft[val['_CFG_SOFT_table_'][0]]
                #--- you can change ONLY parametrs from list 'slct_val'  ---------------
                slct_val = ['titul', 'path_file_DATA', 'path_file_HIST', 'path_file_TXT']
                if slct[0] in slct_val:
                    for item in slct_val:
                        if item == slct[0]:
                            if item == 'titul':
                                txt = sg.PopupGetText(slct[0], default_text = slct[1])
                            else:
                                txt = sg.PopupGetFile( slct[1], title = slct[0])
                            if txt != None:
                                _gl.cfg_soft[val['_CFG_SOFT_table_'][0]] = (item, txt)
                                wndw.FindElement('_CFG_SOFT_table_').Update(_gl.cfg_soft)
                                #---  update tale 'cfg_SOFT' -----------------------------
                                rq = _gl.db_TODAY.update_tbl('cfg_SOFT',
                                                        _gl.cfg_soft, val = ' VALUES(?,?)')
                                if rq[0] > 0:
                                    #err_lmb('event_menu_CFG_SOFT',
                                    #    s_lmb('Did not update cfg_SOFT!') + s_lmb(rep[1]))
                                    sg.popup_ok('Did not update cfg_SOFT!', s_lmb(rep[1]), background_color='Coral', title=ev)
                                else:
                                    sg.popup_ok('Updated *cfg_SOFT* successfully !',
                                        background_color='LightGreen', title=ev)
                else:
                    #err_lmb(ev, s_lmb(slct[0]) + s_lmb('Sorry, can not change'))
                    sg.popup_ok(slct[0], 'Sorry, can not change', background_color='Coral', title=ev)
        else:
            sg.popup_ok('You MUST choise tab CFG_SOFT', background_color='LightGrey', title=ev)
    #----------------------------------------
    if ev == 'CFG_PACK':
        #wndw.disappear()

        mtrx = []
        for item in _gl.cfg_pck:
            ratio = str(round(item[Class_CNST.kPos]/item[Class_CNST.kNeg],2))
            mtrx.append(item + [ratio])

        layout = [[sg.Table(
                            values   = mtrx,
                            num_rows = min(len(mtrx), 35),
                            headings = Class_CNST.head_cfg_pack,
                            key      = '_CFG_PACK_table_',
                            auto_size_columns     = True,
                            justification         = 'center',
                            alternating_row_color = 'coral',
                            )],
                        [#sg.Button(' READ ', key='-READ_CFG_PACK-'),
                         sg.Button(' EDIT ', key='-EDIT_CFG_PACK-'),
                         sg.Button(' ADD  ', key='-ADD_CFG_PACK-' ),
                         sg.Button(' DEL  ', key='-DEL_CFG_PACK-' ),
                         sg.Button(' SAVE ', key='-SAVE_CFG_PACK-'),
                         sg.T(90*' '), sg.Button('Close')],]

        wnd_4 = sg.Window('DB_TABL / CONF_PACK_TABL', layout, no_titlebar=False, modal=True)
        while True: #--- Main Cycle ---------------------------------------#
            e, v = wnd_4.read()
            if e in [sg.WIN_CLOSED, 'Close']:  break
            #-------------------------------------------------------------------
            # You must calc_cfg_pack After EDIT/CHANGE parametrs PACKET
            #-------------------------------------------------------------------
            if e == '-EDIT_CFG_PACK-':
                print('-EDIT_CFG_PACK-')
                if len(v['_CFG_PACK_table_']) == 0:
                    #wrn_lmb('event_menu_CFG_PACK', '\n You MUST choise ROW !\n')
                    sg.PopupOK('\n You MUST choise ROW !\n',
                        title='event_menu_CFG_PACK', background_color = 'Gold',
                        no_titlebar = False, keep_on_top=True)
                else:
                    slct = _gl.cfg_pck[v['_CFG_PACK_table_'][0]]
                    chng = Class_CNST.head_cfg_pack[:]
                    for i, item in enumerate(slct):
                        if i in [Class_CNST.kNm, Class_CNST.kKoef, Class_CNST.kEma]:
                            pop_txt = item
                            if i == Class_CNST.kKoef:
                                pop_txt = ''
                                for ss in item:
                                    pop_txt += ':'.join((str(s) for s in ss)) + ','
                                pop_txt = pop_txt[:-1]
                            if i == Class_CNST.kEma:
                                pop_txt = ':'.join(str(s) for s in item)
                            txt = sg.PopupGetText( Class_CNST.head_cfg_pack[i], size=(95,1), default_text = pop_txt)
                            if (txt == None) or (txt == pop_txt): chng[i] = item
                            else:
                                if i == Class_CNST.kNm:
                                    chng[i] = txt
                                if i == Class_CNST.kKoef:
                                    arr_k    = txt.split(',')
                                    arr_koef = []
                                    for item_k in arr_k:
                                        arr_koef.append([int(f) if f.replace('-','').isdigit() else f for f in item_k.split(':')])
                                    chng[i] = arr_koef
                                if i == Class_CNST.kNul or i == Class_CNST.kGo or i == Class_CNST.kPos or i == Class_CNST.kNeg:
                                    if txt.isdigit():   chng[i] = int(txt)
                                    else:               chng[i] = item
                                if i == Class_CNST.kEma:
                                    chng[i] = [int(e) for e in txt.split(':')]
                        else:
                            chng[i] = item
                    _gl.cfg_pck[v['_CFG_PACK_table_'][0]] = chng
                    wnd_4.FindElement('_CFG_PACK_table_').Update(_gl.cfg_pck)
                    slct = _gl.cfg_pck[v['_CFG_PACK_table_'][0]]
                    e = '-SAVE_CFG_PACK-'
            #-------------------------------------------------------------------
            if e == '-ADD_CFG_PACK-':
                print('-ADD_CFG_PACK-')
                if len(v['_CFG_PACK_table_']) == 0:
                    #wrn_lmb('event_menu_CFG_PACK', '\n You MUST choise ROW !\n')
                    sg.PopupOK('\n You MUST choise ROW !\n',
                        title='event_menu_CFG_PACK', background_color = 'Gold',
                        no_titlebar = False, keep_on_top=True)
                else:
                    slct = _gl.cfg_pck[v['_CFG_PACK_table_'][0]]
                    _gl.cfg_pck.append(slct)
                    print('append slct  ', slct)
                    print('len _gl.cfg_pck => ', len(_gl.cfg_pck))
                    wnd_4.FindElement('_CFG_PACK_table_').Update(_gl.cfg_pck)
                    e = '-SAVE_CFG_PACK-'
            #-------------------------------------------------------------------
            if e == '-DEL_CFG_PACK-':
                print('-DEL_CFG_PACK-')
                if len(v['_CFG_PACK_table_']) == 0:
                    #wrn_lmb('event_menu_CFG_PACK', '\n You MUST choise ROW !\n')
                    sg.PopupOK('\n You MUST choise ROW !\n',
                        title='event_menu_CFG_PACK', background_color = 'Gold',
                        no_titlebar = False, keep_on_top=True)
                else:
                    del _gl.cfg_pck[v['_CFG_PACK_table_'][0]]
                    wnd_4.FindElement('_CFG_PACK_table_').Update(_gl.cfg_pck)
                    e = '-SAVE_CFG_PACK-'
            #-------------------------------------------------------------------
            if e == '-SAVE_CFG_PACK-':
                print('-SAVE_CFG_PACK-')
                rep = _gl.update_tbl_cfg_pack()
                if rep[0] > 0:
                    err_lmb('event_menu_CFG_PACK', s_lmb('Did not update cfg_PACK!') + s_lmb(rep[1]))
                else:
                    #ok_lmb('event_menu_CFG_PACK','Updated *cfg_PACK* successfully !')
                    sg.popup_ok(s_lmb('Updated *cfg_PACK* successfully !'),
                            background_color='LightGreen', title='main')
            #-------------------------------------------------------------------
        wnd_4.close()
        #wndw.reappear()
    #----------------------------------------
    if ev == 'PACK GRAPH':
        GRAPH_One_PACK(_gl, wndw, ev, val)
    #----------------------------------------
    if ev == 'Clr HIST tbl TODAY':
        rep = _gl.db_TODAY.update_tbl('hist_PACK', [])
        if rep[0] == 0:
            sg.popup_ok('OK, clear table *hist_PACK* successfully !', background_color='LightGreen', title=ev)
        else:
            err_lmb(ev,'Could not clear table *hist_PACK* !' + rep[1])
        rep = _gl.db_TODAY.update_tbl('hist_FUT', [])
        if rep[0] == 0:
            sg.popup_ok('OK, clear table *hist_FUT* successfully !', background_color='LightGreen', title=ev)
        else:
            err_lmb(ev,'Could not clear table *hist_FUT* !' + rep[1])
    #----------------------------------------
    if ev == 'Clr HIST tbl FIRST':
        #--- read ALL hist_FUT archiv  -----------------------------
        rep = _gl.db_ARCHV.read_tbl('hist_FUT')
        if rep[0] > 0:
            _gl.err_status = 'Clr HIST tbl FIRST / Not read db_ARCHV *hist_FUT*!  ' + s_lmb(rep[1])
            _gl.err_DB(err_pop = True, err_log = True)
            return
            #return [1, self.err_status]
        _gl.prn_arr('db_ARCHV=>hist_FUT=>',rep[1][0])
        #
        cnt_first_day = 0
        df = rep[1][0][1].split('|')[0].split(' ')[0]
        print('df = ', df)
        for item in rep[1]:
            if item[1].split('|')[0].split(' ')[0] == df:
                 cnt_first_day += 1
            else:
                break
        print('cnt_first_day = ', cnt_first_day)
        
        #
        rq = _gl.db_ARCHV.update_tbl('hist_FUT',
                                rep[1][cnt_first_day:-1], val = ' VALUES(?,?)')
        if rq[0] > 0:
            _gl.err_status = 'Clr HIST tbl FIRST / Not update_tbl db_ARCHV *hist_FUT*!  ' + s_lmb(rq[1])
            _gl.err_DB(err_pop = True, err_log = True)
            return
        _gl.prn_arr('db_ARCHV=>hist_FUT=>',rq[1][0])
    #----------------------------------------
    if ev == 'Clr HIST tbl LAST':
        #--- read ALL hist_FUT archiv  -----------------------------
        rep = _gl.db_ARCHV.read_tbl('hist_FUT')
        if rep[0] > 0:
            _gl.err_status = 'Clr HIST tbl LAST / Not read db_ARCHV *hist_FUT*!  ' + s_lmb(rep[1])
            _gl.err_DB(err_pop = True, err_log = True)
            return
            #return [1, self.err_status]
        _gl.prn_arr('db_ARCHV=>hist_FUT=>',rep[1][-1])
        #
        cnt_last_day = len(rep[1])
        df = rep[1][-1][1].split('|')[0].split(' ')[0]
        print('df = ', df)
        for item in reversed(rep[1]):
            if item[1].split('|')[0].split(' ')[0] == df:
                 cnt_last_day -= 1
            else:
                break
        print('cnt_last_day = ', cnt_last_day)
        _gl.prn_arr('db_ARCHV=>hist_FUT=>',rep[1][cnt_last_day])
        #
        rq = _gl.db_ARCHV.update_tbl('hist_FUT',
                                rep[1][0:cnt_last_day], val = ' VALUES(?,?)')
        if rq[0] > 0:
            _gl.err_status = 'Clr HIST tbl LAST / Not update_tbl db_ARCHV *hist_FUT*!  ' + s_lmb(rq[1])
            _gl.err_DB(err_pop = True, err_log = True)
            return
        _gl.prn_arr('db_ARCHV=>hist_FUT=>',rq[1][-1])
    # append hist file from TXT in table -------------------------------
    if ev == 'APPEND':
        #--- read HIST file ---
        buf_hist_arch, buf_str, frm = [], [], '%d.%m.%Y %H:%M:%S'
        path_hist = sg.PopupGetFile( 'select TXT hist file',
                title = 'append hist file from TXT in table')
        if path_hist != None:
            try:
                with open(path_hist,"r") as fh:
                    buf_str = fh.read().splitlines()
                #--- create list 'buf_hist' HIST 1 minute 10.00 ... 18.45
                mn_pr, mn_cr, buf_hist = '', '00', []
                for cnt, item in enumerate(buf_str):
                    h_m_s = item.split('|')[0].split(' ')[1].split(':')
                    mn_cr = h_m_s[1]
                    if int(h_m_s[0]) < 10: continue
                    if int(h_m_s[0]) > 18: break
                    if mn_pr != mn_cr:
                        buf_hist.append(item)
                    mn_pr = mn_cr
                #--- prepaire 'buf_hist' for update table 'hist_fut' ---
                for item in buf_hist:
                    dtt_cr = datetime.strptime(item.split('|')[0], frm)
                    ind_sec = int(dtt_cr.replace(tzinfo=timezone.utc).timestamp())
                    buf_hist_arch.append([ind_sec, item])
                #--- db_ARCHV.update_tbl -------------------------------
                rep = _gl.db_ARCHV.update_tbl('hist_FUT', buf_hist_arch, val = ' VALUES(?,?)', p_append = True)

            except Exception as ex:
                err_lmb('event_menu_HIST_TABL_FUT_ARCH', s_lmb('Error  TRY!') + str(ex))
                return
    #----------------------------------------
    if ev == 'CALC':
        print('-CALC_UPDATE_PCK_ARCH-')
        rep = _gl.calc_arr_pck() # last_sz = 2600 => 5*520 per Week
        if rep[0] > 0:  return 0

        #--- refresh TABGROUP ---
        event_TABGROUP(_gl, wndw, ev, val)
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
    #test_msg_lmb()
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
        menu_def = [['HIST tbl',['Clr HIST tbl TODAY', 'Clr HIST tbl FIRST', 'Clr HIST tbl LAST', '---', 'APPEND', 'CALC', '---', 'Exit']],
                    ['Service', ['CFG_SOFT', 'CFG_PACK', '---', 'PACK GRAPH']],
                    ['Help',    ['About...']],]
        #
        tab_keys = ('-CFG_SOFT-', '-FUT_TOD-', '-FUT_ARC-', '-PCK_TOD-', '-PCK_ARC-')
        tab_tabs = ( 'Cfg SOFT' ,  'fut TOD' ,  'fut ARC',   'pck TOD' ,  'pck ARC')
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
        window.set_title(_gl.cfg_soft[0][1])
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
        if event in ['Clr HIST tbl TODAY', 'Clr HIST tbl FIRST', 'Clr HIST tbl LAST', 'APPEND', 'CALC',
                     'CFG_SOFT', 'CFG_PACK', 'PACK GRAPH',
                     'About...']:
            event_MENU(_gl, window, event, values)
    window.close()
    return 0

if __name__ == '__main__':
    main()

