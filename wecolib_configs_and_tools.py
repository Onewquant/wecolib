###########################################
## System, File, Data Structure 관련 import
###########################################

import json
import xlsxwriter
import openpyxl
import os
import win32com.client

###########################################
## Multiprocessing 관련
###########################################

from multiprocessing import Pool, Queue, Process, Pipe, freeze_support

###########################################
## Asyncio 관련
###########################################
import concurrent.futures
import asyncio

###########################################
## urllib, request 관련 import
###########################################

import urllib
import urllib.parse
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import requests
from io import BytesIO

############################################# Pandas 관련 import
###########################################

import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
import math

###########################################
## mssql 관련 import
###########################################

import pyodbc
import sqlalchemy

###########################################
## 날짜관련 import
###########################################

import time
from datetime import datetime, timedelta
import calendar
from dateutil.relativedelta import relativedelta

###########################################
## Stats관련 import
###########################################

from scipy import stats, polyval

###########################################
## Matplotlib관련 import
###########################################

from matplotlib import font_manager, rc, pyplot as plt
import seaborn as sns

###########################################
## onew quantmod 관련 configurations
###########################################


## MSSQL 데이터베이스 접속 정보

mssql_ip_address = 'DataBase_IP_주소'
mssql_id = 'DB_id'
mssql_pw = 'DB_pw'

## 텔레그램 SNS 알람 정보

telegram_bot_api_token = '텔레그램_봇_토큰'
telegram_bot_chat_id_list = ["텔레그램_id_no",]



###########################################################################
##                          SQL-Connection
###########################################################################

# Transmit string to DataBase

def transmit_str_to_sql(sql) :

    """
    :param sql: str to transmit
    :return: None
    """

    con = pyodbc.connect("DRIVER={SQL Server};SERVER=%s;DATABASE=master;UID=%s;PWD=%s"%(mssql_ip_address,mssql_id,mssql_pw))
    cur = con.cursor()
    cur.execute(sql)
    con.commit()
    print("the str was transmitted successfully")

    con.close()
    return None


# Load Data from DataBase


def read_sql_table(sql) :

    """
    :param sql: Table to read
    :return: dataframe from the table

    """

    con = pyodbc.connect("DRIVER={SQL Server};SERVER=%s;DATABASE=master;UID=%s;PWD=%s"%(mssql_ip_address,mssql_id,mssql_pw))
    df = pd.read_sql(sql, con)

    con.commit()
    con.close()
    return df



# Insert Dataframe into Table of DataBase

def insert_data_into_sql_Table(df,TBL,DB_Name) :
    """
    :param df: Dataframe for insert
    :param TBL: Table that will be inserted into
    :return: None

    """

    params = urllib.parse.quote_plus("DRIVER={SQL Server};SERVER=%s;DATABASE=%s;UID=%s;PWD=%s" %(mssql_ip_address,DB_Name,mssql_id,mssql_pw))
    engine = sqlalchemy.create_engine("mssql+pyodbc:///?odbc_connect=%s" % params)

    try :
        df.to_sql(TBL, engine, if_exists='append', index=False)
        return 1
    except :
        return 0


###########################################################################
##            Telegram Alarm Chat Bot API Functions
###########################################################################


def telegram_get_new_user_chat_id():
    url = "https://api.telegram.org/bot%s/getUpdates" % telegram_bot_api_token
    r = requests.get(url)
    result = json.loads(r.text)
    new_user_chat_id = str(result['result'][0]['message']['from']['id'])
    return new_user_chat_id


def telegram_send_msg_to_user(chat_text="Text_Examples"):
    for chat_id in telegram_bot_chat_id_list:
        url = "https://api.telegram.org/bot%s/sendMessage?chat_id=%s&text=%s" % (
        telegram_bot_api_token, chat_id, chat_text)
        r = requests.get(url)
        result = json.loads(r.text)
        status = result['ok']

    return None

###########################################################################
##                          General Tools
###########################################################################


## 프로그램 작동 시간 측정 데코레이터
"""
opening_time = time.time()
closing_time = time.time()
print(closing_time-opening_time)
"""
# def runtime(f):
#     def wrapper(*args, **kwargs):
#         import time
#         start = time.time()
#         f
#         end = time.time()
#         print(end - start)
#         return f()
#     return wrapper

## 프로그램 프로파일 함수
"""
import cProfile
cProfile.run('Function Name')
"""

def df_column_setting(df,column_name,value):
    for inx, row in df.iterrows():
        df.at[inx, column_name] = value



## object 중 숫자인 것 골라내기

def distinguish_float_from_str(obj):
    try:
        result_element = int((obj >= 0) or (obj < 0))
    except:
        result_element = 0
    return result_element

## 사이문자열 찾기

def find_between( s, first, last ):
    try:
        start = s.rfind( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        print('Error for finding letters')
        return ''

## Date list generator

def generate_day_list(start_date,end_date=None):

    start_date = datetime.strptime(start_date,'%Y-%m-%d')

    if end_date == None :
        end_date = datetime.today()
    else :
        end_date = datetime.strptime(end_date,'%Y-%m-%d')

    delta = end_date - start_date
    date_list = []

    for i in range(delta.days + 1):
        d = start_date + timedelta(days=i)
        date_list = date_list + [d.strftime("%Y-%m-%d")]

    return date_list

def generate_day_index_df(start_date,end_date=None):

    start_date = datetime.strptime(start_date,'%Y-%m-%d')

    if end_date == None :
        end_date = datetime.today()
    else :
        end_date = datetime.strptime(end_date,'%Y-%m-%d')

    delta = end_date - start_date
    date_list = []

    for i in range(delta.days + 1):
        d = start_date + timedelta(days=i)
        date_list = date_list + [d.strftime("%Y-%m-%d")]

    df = pd.DataFrame(index=date_list)
    df.index = pd.to_datetime(df.index)

    return df

## 가장 가까운 날짜 찾기 (datetime)

def datetime_nearest(item_list, pivot):
    datetime_nearest =  min(item_list, key=lambda x: abs(pivot - x ))
    return datetime_nearest

## 아직 지나가지 않은 가장 가까운 날짜 찾기 (datetime)

def datetime_nearest_not_passed(item_list, pivot):
    working_list = list()
    not_yet_list = [x < pivot for x in item_list]
    for i in range(len(not_yet_list)):
        if not_yet_list[i]==True:
            working_list.append(item_list[i])

    datetime_nearest = min(working_list, key=lambda x: abs(pivot - x))
    return datetime_nearest


## 범위에 있는 특정 window를 가진 period 조각들을 반환

def date_period_fragments(start, end, months_window):
    start_datetime = datetime.strptime(start, '%Y-%m-%d')
    end_datetime = datetime.strptime(end, '%Y-%m-%d')

    if start_datetime.year == end_datetime.year:
        years = np.array([start_datetime.year])
        months = np.arange(start=start_datetime.month + 1, stop=end_datetime.month + 1, step=1)

        sim_period_list = list()
        for y in years:
            for m in months:
                last_day_tuple = calendar.monthrange(year=y, month=m)
                last_date_frag = '%s-%s-%s' % (y, m, last_day_tuple[1])

                start_date_frag = (datetime.strptime(last_date_frag, '%Y-%m-%d') - relativedelta(
                    months=months_window) + timedelta(days=1)).strftime('%Y-%m-%d')
                sim_period_list.append((start_date_frag, last_date_frag))

    elif (start_datetime.year < end_datetime.year):
        execute_list = [[start_datetime.year, start_datetime.year + 1, start_datetime.month, 13],
                        [start_datetime.year + 1, end_datetime.year, 1, 13],
                        [end_datetime.year, end_datetime.year + 1, 1, end_datetime.month + 1]]
        sim_period_list = list()
        for ex in execute_list:
            years = np.arange(start=ex[0], stop=ex[1], step=1)
            months = np.arange(start=ex[2], stop=ex[3], step=1)
            for y in years:
                for m in months:
                    last_day_tuple = calendar.monthrange(year=y, month=m)

                    last_date_frag = datetime(year=y, month=m, day=last_day_tuple[1]).strftime('%Y-%m-%d')
                    start_date_frag = (datetime.strptime(last_date_frag, '%Y-%m-%d') - relativedelta(
                        months=months_window) + timedelta(days=1)).strftime('%Y-%m-%d')

                    sim_period_list.append((start_date_frag, last_date_frag))

    else:
        print('start와 end를 올바르게 입력하세요.')

    return sim_period_list

## Ticker의 현재 가격 상태를 df으로 돌려주는 함수

def get_current_price_state_of_ticker(ticker):
    url = 'http://finance.naver.com/item/main.nhn?code=%s' % (ticker)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    span_list = soup.find('div', attrs={'class': 'rate_info'}).findAll('span', attrs={'class': 'blind'})
    info_list = list()
    for span in span_list:
        info_list += [float(span.text.replace(',', ''))]
    array_frag = np.array([info_list[7], info_list[4], info_list[8], info_list[0], (info_list[7] - info_list[3]), info_list[6]])
    df_frag = pd.DataFrame(data= array_frag.reshape(1,len(array_frag)),columns=['Open_', 'High', 'Low', 'Close_', 'Change', 'Volume'])
    df_frag['Date_'] = datetime.today().strftime('%Y-%m-%d')
    df_frag['Ticker'] = ticker
    df_frag = df_frag[['Date_','Ticker','Open_', 'High', 'Low', 'Close_', 'Change', 'Volume']]

    return df_frag

## 전종목 시세 테이블

def get_current_price_table():
    total_result_df = pd.DataFrame(columns=['Date_','Time_','Code','Ticker','Name_','Close_','Volume','Trd_Amount','Market_Cap','Foreign_Ratio'])
    for m in ['KOSPI','KOSDAQ']:
        down_url = 'http://finance.daum.net/api/quotes/sectors'
        down_data = {
            'market': m,
        }

        headers = {'Referer': 'http://finance.daum.net/domestic/all_quotes','User-Agent': 'Mozilla/5.0'}
        r = requests.get(url=down_url, data=down_data, headers=headers)
        jl = json.loads(r.text)
        jn_df = json_normalize(jl,'data')
        result_df = pd.DataFrame(columns=pd.DataFrame(jn_df['includedStocks'].iloc[0]).columns)
        for j in range(len(jn_df)):
            result_df = result_df.append(pd.DataFrame(jn_df['includedStocks'].iloc[j]))

        result_df = result_df.reset_index(drop=True)
        result_df['Date_'] = datetime.now().strftime('%Y-%m-%d')
        result_df['Time_'] = datetime.now().strftime('%H:%M:%S')
        result_df.columns = ['Trd_Amount', 'Volume', 'Direction', 'Change_', 'Change_Pct', 'Code', 'Foreign_Ratio', 'Market_Cap','Name_', 'Ticker', 'Close_','Date_','Time_']
        result_df = result_df[['Date_','Time_','Code','Ticker','Name_','Close_','Volume','Trd_Amount','Market_Cap','Foreign_Ratio']]
        total_result_df = total_result_df.append(result_df)

    total_result_df = total_result_df.drop_duplicates(subset=['Ticker'],keep='first').sort_values(by=['Ticker']).reset_index(drop=True)

    return total_result_df

def get_current_price_table_several_trials():
    try:
        table = get_current_price_table()
    except:
        print('현재시세 다운로드 다시 시도')
        time.sleep(1)
        try:
            table = get_current_price_table()
        except:
            print('현재시세 다운로드 다시 시도')
            time.sleep(1)
            try:
                table = get_current_price_table()
            except:
                print('현재시세 다운로드 다시 시도')
                time.sleep(1)
    return table

## Dataframe의 i번째 행을 특정 Series 값으로 치환

def replace_row_with_series(df_frag, row_num, series_frag):
    array_frag = np.array(series_frag)
    if len(array_frag) == len(df_frag.columns):
        for c in range(0, len(array_frag)):
            df_frag.iat[row_num, c] = array_frag[c]
        return df_frag
    else:
        print('Series 개수와 Column 개수 안 맞음')
        return None


## Series에서 Rolling Cumret 계산

def rolling_cumret(ds, window):
    ret_for_cum = ((ds - ds.shift(1)) / ds.shift(1)).fillna(0) + 1
    result_series = pd.Series()
    for k in range(len(ret_for_cum)):
        starting_inx = -(len(ret_for_cum) - k) - window + 1
        ending_inx = -(len(ret_for_cum) - k) + 1
        if ending_inx == 0:
            cumprod_value = ret_for_cum.iloc[starting_inx:].prod()
        else:
            if starting_inx < -len(ret_for_cum):
                cumprod_value = np.nan
            else:
                cumprod_value = ret_for_cum.iloc[starting_inx:ending_inx].prod()

        result_series = result_series.append(pd.Series(data=[cumprod_value], index=[ret_for_cum.index[k]]))
    return result_series



###########################################################################
##            Real Trading 관련
###########################################################################

## 거래일 여부 확인

def today_is_kor_stock_trading_day():

    today = datetime.today().strftime('%Y-%m-%d')

    url = 'https://finance.naver.com/sise/sise_index.nhn?code=KOSPI'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    span = soup.find('div', attrs={'class': 'ly_realtime'}).find('span', attrs={'id': 'time'})
    trd_date = span.text.split()[0].replace('.','-')

    result = (trd_date == today)*1
    return result

## 최근접 상위 호가 정보

def kor_queue_price_more_than(market,price):
    be_price = int(math.ceil(price))
    if price < 1000:
        pass
    elif (price >= 1000)&(price < 5000):
        be_price_units = be_price%10
        if (be_price_units==0)|(be_price_units==5):
            pass
        elif (be_price_units!=0)&(be_price_units < 5):
            be_price += (5 - be_price_units)
        else:
            be_price += (10 - be_price_units)
    elif (price >= 5000)&(price < 10000):
        be_price = math.ceil(be_price/10)*10
    elif (price >= 10000)&(price < 50000):
        be_price_units = be_price%100
        if (be_price_units==0)|(be_price_units==50):
            pass
        elif (be_price_units!=0)&(be_price_units < 50):
            be_price += (50 - be_price_units)
        else:
            be_price += (100 - be_price_units)

    elif (price >= 50000):
        if market == 'KOSPI':
            if (price>= 50000)&(price < 100000):
                be_price = math.ceil(be_price / 100) * 100
            elif (price>= 100000)&(price < 500000):
                be_price_units = be_price % 1000
                if (be_price_units == 0) | (be_price_units == 500):
                    pass
                elif (be_price_units != 0) & (be_price_units < 500):
                    be_price += (500 - be_price_units)
                else:
                    be_price += (1000 - be_price_units)
            elif (price>= 500000):
                be_price = math.ceil(be_price / 1000) * 1000

        elif market == 'KOSDAQ':
            be_price = math.ceil(be_price / 100) * 100

    return be_price

## 최근접 하위 호가 정보

def kor_queue_price_less_than(market,price):
    be_price = int(math.ceil(price))
    if price < 1000:
        pass
    elif (price >= 1000)&(price < 5000):
        be_price_units = be_price%10
        if (be_price_units==0)|(be_price_units==5):
            pass
        elif (be_price_units!=0)&(be_price_units < 5):
            be_price -= be_price_units
        else:
            be_price -= be_price_units
    elif (price >= 5000)&(price < 10000):
        be_price = int(be_price/10)*10
    elif (price >= 10000)&(price < 50000):
        be_price_units = be_price%100
        if (be_price_units==0)|(be_price_units==50):
            pass
        elif (be_price_units!=0)&(be_price_units < 50):
            be_price -= be_price_units
        else:
            be_price -= be_price_units

    elif (price >= 50000):
        if market == 'KOSPI':
            if (price>= 50000)&(price < 100000):
                be_price = int(be_price / 100) * 100
            elif (price>= 100000)&(price < 500000):
                be_price_units = be_price % 1000
                if (be_price_units == 0) | (be_price_units == 500):
                    pass
                elif (be_price_units != 0) & (be_price_units < 500):
                    be_price -= be_price_units
                else:
                    be_price -= be_price_units
            elif (price>= 500000):
                be_price = int(be_price / 1000) * 1000

        elif market == 'KOSDAQ':
            be_price = int(be_price / 100) * 100

    return be_price

## N호가 변동 가격

def kor_queue_price_n_units_changed(market,price,n):

    be_price = int(math.ceil(price))
    if price < 1000:
        be_price += n
    elif (price >= 1000)&(price < 5000):
        be_price_units = be_price%10
        if (be_price_units==0)|(be_price_units==5):
            be_price += 5*n
        elif (be_price_units!=0)&(be_price_units < 5):
            be_price += (5 - be_price_units + 5*n)
        else:
            be_price += (10 - be_price_units + 5*n)
    elif (price >= 5000)&(price < 10000):
        be_price = math.ceil(be_price/10)*10 + 10*n
    elif (price >= 10000)&(price < 50000):
        be_price_units = be_price%100
        if (be_price_units==0)|(be_price_units==50):
            be_price += 50 * n
        elif (be_price_units!=0)&(be_price_units < 50):
            be_price += (50 - be_price_units) + 50*n
        else:
            be_price += (100 - be_price_units) + 50*n

    elif (price >= 50000):
        if market == 'KOSPI':
            if (price>= 50000)&(price < 100000):
                be_price = math.ceil(be_price / 100) * 100 + 100*n
            elif (price>= 100000)&(price < 500000):
                be_price_units = be_price % 1000
                if (be_price_units == 0) | (be_price_units == 500):
                    be_price += 500*n
                elif (be_price_units != 0) & (be_price_units < 500):
                    be_price += (500 - be_price_units) + 500*n
                else:
                    be_price += (1000 - be_price_units) + 500*n
            elif (price>= 500000):
                be_price = math.ceil(be_price / 1000) * 1000 + 1000*n

        elif market == 'KOSDAQ':
            be_price = math.ceil(be_price / 100) * 100 + 100*n

    return be_price

def kor_queue_price_n_units_changed_delicate_version(market,price,n):
    first_return = kor_queue_price_n_units_changed(market=market,price=price,n=n)
    final_return = kor_queue_price_more_than(market=market,price=first_return)
    return final_return

## 로우 데이터 로딩
## from wecolib.Curvelib_get_raw_data import *