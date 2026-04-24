'''
bl.py
Biwako Level: store water level data log of Biwako from MILT Japan system
by @pado3@fedibird.com
2026/04/25 r1.1 correct logical error, make data folder is not exist
2026/03/22 r1.0 initial release
'''
import requests
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.relativedelta import relativedelta
from time import sleep
import pandas as pd

# parts of URL
URL_PATH = 'https://www1.river.go.jp/cgi-bin/DspWaterData.exe'
URL_QUE1 = '?KIND=2&ID=306041286603280&ENDDATE=20261231&KAWABOU=NO&BGNDATE='
# data limit
YYYY_min = '1993'    # oldest year of MILT data (from 1993/01/01)
Month_min = 1
Month_max = 12


def get_bl(yyyymm: str):
    '''get Biwako surface Level from web and store CSV file'''
    url = URL_PATH + URL_QUE1 + yyyymm + '01'
    # set brwoser header
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) \
        AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/146.0.0.0 Safari/537.36'}
    # get data with dummy header
    res = requests.get(url, headers=headers)
    res.encoding = 'EUC-JP'  # from header of MILT site
    soup = BeautifulSoup(res.text, 'html.parser')
    # soup the table data
    tables = soup.find_all('table')
    # list for store the data
    data = []
    # analyze data table
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all(['td', 'th'])
            cols = [ele.text.strip() for ele in cols]
            data.append(cols)
    # make data frame
    df = pd.DataFrame(data)
    # store csv file
    fname = '_bl_data/bl' + yyyymm + '.csv'
    df.to_csv(fname, index=False, header=False)
    # print('saved the data : {}'.format(fname))
    return


def abort(mes):
    '''abort this program with error message'''
    print('{}'.format(mes), end='')
    sys.exit(' aborted')


def check_date(str_date: str):
    '''confirm args date format, return YYYYMM in int'''
    if len(str_date) != 6:  # is not YYYYMM
        abort('specified date [{}] is not in 6 char[YYYYMM].'.format(str_date))
    else:
        if int(str_date[0:4]) < int(YYYY_min):
            abort('specified year is before the first data, 199312.')
        if int(str_date[4:]) < Month_min or Month_max < int(str_date[4:]):
            abort('specified month is not in 01-12.')
    return int(str_date)


def check_dir():
    '''make data folder if not exist'''
    import os
    os.makedirs('_bl_data', exist_ok=True)


def check_args(args):
    '''confirm args'''
    if len(args) == 1:
        abort('usage: [' + args[0] + ' start finish] in YYYYMM.')
    elif len(args) == 2:
        sta = check_date(args[1])
        fin = sta
    elif len(args) >= 3:
        sta = check_date(args[1])
        fin = check_date(args[2])
        if fin < sta:
            abort('start date is after the finish date.')
    return (sta, fin)


def bl_body(args):
    '''control download loop'''
    (sta, fin) = check_args(args)
    check_dir()
    sta_year = int(sta/100)
    sta_month = sta - 100*sta_year
    fin_year = int(fin/100)
    fin_month = fin - 100*fin_year
    date_sta = datetime(sta_year, sta_month, 1)
    date_fin = datetime(fin_year, fin_month, 1)
    relyear_f2s = relativedelta(date_fin, date_sta).years
    relmon_f2s = relativedelta(date_fin, date_sta).months + 12*relyear_f2s + 1
    print('downloading Biwako water level data:')
    for rm in range(relmon_f2s):
        target_year = (date_sta + relativedelta(months=rm)).year
        target_month = (date_sta + relativedelta(months=rm)).month
        target_ym = target_year*100 + target_month
        print('{} '.format(target_ym), end='', flush=True)
        get_bl(str(target_ym))
        sleep(2)
    print('\nfinished')
    return


if __name__ == '__main__':
    '''main routine as usual'''
    args = sys.argv
    # args[0] : name of script, len(args) : number of args for OS
    bl_body(args)
