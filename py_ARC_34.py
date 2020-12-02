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
        self.lg_file  = Class_LGR      (c_dir + '\\LOG\\py_TABS.log')
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
        
        #---------------------------------------------------------------
        break
    return 0

if __name__ == '__main__':
    main()

