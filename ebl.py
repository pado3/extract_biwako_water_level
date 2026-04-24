#!/usr/bin/env python3.13
'''
ebl.py
Extract the Biwako Level data of specified date from downloaded by bl.py
by @pado3@fedibird.com
2026/03/22 r1.0 initial release
'''
import os
import re
import sys
import pandas as pd
from datetime import datetime

# parts of file name ex. _bl_data/bl199301.csv
CSV_DIR = '_bl_data/'
CSV_HEAD = 'bl'
CSV_EXT = '.csv'
# data limit
Month_min = 1
Month_max = 12
Day_min = 1
Day_max = 31    # treat “short months” later
Hour_min = 1    # hour in data from 1 to 24 (not from 0 to 23)
Hour_max = 24
Blank = '欠測'


def ext_bl(str_ymd: str, hour: int):
    '''read csv and extract specified "MM/DD HH" level data.

    str_ymd : 'YYYY/MM/DD'
    hour: 1-24
    '''
    yyyy = str_ymd[0:4]
    mm = str_ymd[5:7]
    # fname = '_bl_data/bl' + yyyymm + '.csv'
    fname = CSV_DIR + CSV_HEAD + yyyy + mm + CSV_EXT
    df = pd.read_csv(fname, header=None)
    date_column = df[0]     # first column is YYYY/MM/DD
    target_line = df[date_column == str_ymd]
    if not target_line.empty:
        ext_data = target_line.iloc[:, hour].values[0]
    else:
        ext_data = Blank
    return ext_data


def abort(mes):
    '''abort this program with message'''
    print('{}'.format(mes), end='')
    sys.exit(' aborted')


def check_date(str_date: str):
    '''confirm args[1] date format, return MMDD in int'''
    try:
        int(str_date)
    except Exception:
        abort('please input date in MMDD, your value: [{}].'.format(str_date))
    if len(str_date) != 4:  # is not MMDD
        abort('specified date [{}] is not in 4 char[MMDD].'.format(str_date))
    else:
        if int(str_date[:2]) < Month_min | Month_max < int(str_date[:2]):
            abort('specified month is not {}-{}.'.format(Month_min, Month_max))
        if int(str_date[2:]) < Day_min | Day_max < int(str_date[2:]):
            abort('specified day is not {}-{}.'.format(Day_min, Day_max))
            # "small month" will treat at the datetime coonversion
    return int(str_date)


def check_hour(str_hour: str):
    '''confirm args hour value, return HH in int'''
    try:
        hour = int(str_hour)
        if hour < Hour_min | Hour_max < hour:
            abort('specified hour is not in 1-24. (cannot use 0)')
    except Exception:
        abort('please input hour in HH, your value: [{}].'.format(str_hour))
    return hour


def check_args(args):
    '''confirm args

    args[0] : name of command
    args[1] : extract date, in MMDD
    args[2] : extract hour, in H
    '''
    if len(args) <= 2:
        abort('usage: [' + args[0] + ' date hour] in MMDD H.')
    elif len(args) >= 3:
        date = check_date(args[1])  # int
        hour = check_hour(args[2])  # int
    return (date, hour)


def get_year(month: int):
    '''get year list of exisiting data

    month : int
    return : year_list which has specified month
    '''
    MM = str(month).zfill(2)
    # match pattern for data files (ex. _bl_data/bl199301.csv
    pattern = CSV_HEAD + '[0-9]{6}' + CSV_EXT
    re_part = re.compile(r'{}'.format(pattern))
    csv_list = [fn for fn in os.listdir(CSV_DIR) if re_part.match(fn)]
    year_list = [int(fn[2:6]) for fn in csv_list if fn[6:8] == MM]
    return sorted(year_list)


def ebl_body(args):
    '''control download loop and store extracted data'''
    (mmdd, hh) = check_args(args)
    month = int(mmdd/100)
    day = mmdd - 100*month
    year_list = get_year(month)     # list of int, 4 digit
    capt = str(month) + '月' + str(day) + '日 ' + str(hh) + '時'
    ext_data = [['琵琶湖水位B.S.L.', 'm'], ['年', capt]]    # output data w/header
    print('extract Biwako surface level data of {}/{}:'.format(month, day))
    for year in year_list:
        try:
            # check calendar date for small month confirmation
            dt = datetime(year, month, day)
            str_ymd = dt.strftime('%Y/%m/%d')   # YYYY/MM/DD
            print('{} '.format(year), end='', flush=True)
            year_dat = ext_bl(str_ymd, hh)
            if year_dat == Blank:
                year_dat = ''
            ext_data.append([year, year_dat])
        except ValueError:
            mes = ('[{}/{}/{} is out of range'.format(year, month, day))
            print(mes + ', skip] ', end='', flush=True)
    # make data frame
    df = pd.DataFrame(ext_data)
    # store csv file
    fname = 'ebl' + str(mmdd).zfill(4) + str(hh).zfill(2) + '.csv'
    df.to_csv(fname, index=False, header=False)
    print('\nfinished')
    return


if __name__ == '__main__':
    '''main routine as usual'''
    args = sys.argv
    # args[0] : name of script, len(args) : number of args for OS
    ebl_body(args)
