## 라이브러리 설정 로딩
from wecolib.wecolib_configs_and_tools import *

###########################################################################
##                         거래일 얻기
###########################################################################

def get_past_working_day(country, asset_type, start_date, end_date):
    key = '%s-%s' % (country, asset_type)
    price_dbtable_dict = {'KOR-Index': "SELECT DISTINCT Date_ FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Date_ BETWEEN '%s' AND '%s' ORDER BY Date_" % (start_date, end_date),
                          'KOR-Stock': "SELECT DISTINCT Date_ FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX WHERE Market IN ('KOSPI','KOSDAQ') AND Date_ BETWEEN '%s' AND '%s' ORDER BY Date_" % (start_date, end_date),
                          'KOR-ETF': "SELECT DISTINCT Date_ FROM KOR_Price_Data.dbo.KOR_ETFPriceDataFromNF WHERE Date_ BETWEEN '%s' AND '%s' ORDER BY Date_" % (start_date, end_date),
                          'GLOB-Index': "SELECT DISTINCT Date_ FROM GLOB_Price_Data.dbo.GLOB_IndexPriceDataFromIV WHERE Date_ BETWEEN '%s' AND '%s' ORDER BY Date_" % (start_date, end_date),
                          'GLOB-IndexFutures': "SELECT DISTINCT Date_ FROM GLOB_Price_Data.dbo.GLOB_IndexFuturesPriceDataFromIV WHERE Date_ BETWEEN '%s' AND '%s' ORDER BY Date_" % (start_date, end_date),
                          'GLOB-FxFutures': "SELECT DISTINCT Date_ FROM GLOB_Price_Data.dbo.GLOB_FxFuturesPriceDataFromIV WHERE Date_ BETWEEN '%s' AND '%s' ORDER BY Date_" % (start_date, end_date),
                          'GLOB-FxRate': "SELECT DISTINCT Date_ FROM GLOB_Price_Data.dbo.GLOB_FxRateDataFromIV WHERE Date_ BETWEEN '%s' AND '%s' ORDER BY Date_" % (start_date, end_date),
                          'GLOB-Commodities': "SELECT DISTINCT Date_ FROM GLOB_Price_Data.dbo.GLOB_CommoditiesPriceDataFromIV WHERE Date_ BETWEEN '%s' AND '%s' ORDER BY Date_" % (start_date, end_date),
                          'KOR-MajorIndex': "SELECT DISTINCT Date_ FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Date_ BETWEEN '%s' AND '%s' ORDER BY Date_" % (start_date, end_date),
                          'KOR-KOSPI': "SELECT DISTINCT Date_ FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Ticker = 'KOSPI' AND Date_ BETWEEN '%s' AND '%s' ORDER BY Date_" % (start_date, end_date),
                          'KOR-KOSDAQ': "SELECT DISTINCT Date_ FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Ticker = 'KOSDAQ지수' Date_ BETWEEN '%s' AND '%s' ORDER BY Date_" % (start_date, end_date),
                          'KOR-KSStock': "SELECT DISTINCT Date_ FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX WHERE Market = 'KOSPI' AND Date_ BETWEEN '%s' AND '%s' ORDER BY Date_" % (start_date, end_date),
                          'KOR-KQStock': "SELECT DISTINCT Date_ FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX WHERE Market = 'KOSDAQ' AND Date_ BETWEEN '%s' AND '%s' ORDER BY Date_" % (start_date, end_date)
                          }

    working_day_df = read_sql_table(sql=price_dbtable_dict[key])

    return working_day_df


###########################################################################
##                         티커데이터 로딩 관련
###########################################################################

def download_ticker_data(country = 'KOR', asset_type = 'Index', start_date = '2015-01-01', end_date = datetime.today().strftime('%Y-%m-%d')):

    key = '%s-%s'%(country,asset_type)
    sql_dict = {'KOR-Index':"SELECT DISTINCT Ticker FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Date_ BETWEEN '%s' AND '%s'"%(start_date,end_date)
        ,'KOR-Stock':"SELECT DISTINCT Ticker FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX WHERE Market IN ('KOSPI','KOSDAQ') AND Date_ BETWEEN '%s' AND '%s'"%(start_date,end_date)
        ,'KOR-ETF':"SELECT DISTINCT Ticker FROM KOR_Price_Data.dbo.KOR_ETFPriceDataFromNF WHERE Date_ BETWEEN '%s' AND '%s'"%(start_date,end_date)
        ,'GLOB-Index':"SELECT DISTINCT Ticker FROM GLOB_Price_Data.dbo.GLOB_IndexPriceDataFromIV WHERE Date_ BETWEEN '%s' AND '%s'"%(start_date,end_date)
        ,'GLOB-IndexFutures':"SELECT DISTINCT Ticker FROM GLOB_Price_Data.dbo.GLOB_IndexFuturesPriceDataFromIV WHERE Date_ BETWEEN '%s' AND '%s'"%(start_date,end_date)
        ,'GLOB-FxFutures':"SELECT DISTINCT Ticker FROM GLOB_Price_Data.dbo.GLOB_FxFuturesPriceDataFromIV WHERE Date_ BETWEEN '%s' AND '%s'"%(start_date,end_date)
        ,'GLOB-FxRate':"SELECT DISTINCT Ticker FROM GLOB_Price_Data.dbo.GLOB_FxRateDataFromIV WHERE Date_ BETWEEN '%s' AND '%s'"%(start_date,end_date)
        ,'GLOB-Commodities':"SELECT DISTINCT Ticker FROM GLOB_Price_Data.dbo.GLOB_CommoditiesPriceDataFromIV WHERE Date_ BETWEEN '%s' AND '%s'"%(start_date,end_date)
        ,'KOR-MajorIndex':"SELECT DISTINCT Ticker FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Ticker in ('KOSPI','KOSDAQ지수') AND Date_ BETWEEN '%s' AND '%s'"%(start_date,end_date)
        ,'KOR-KOSPI':"SELECT DISTINCT Ticker FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Ticker = 'KOSPI' AND Date_ BETWEEN '%s' AND '%s'"%(start_date,end_date)
        ,'KOR-KOSDAQ':"SELECT DISTINCT Ticker FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Ticker = 'KOSDAQ지수' AND Date_ BETWEEN '%s' AND '%s'"%(start_date,end_date)
        ,'KOR-KSStock': "SELECT DISTINCT Ticker FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX WHERE Market = 'KOSPI' AND Date_ BETWEEN '%s' AND '%s'" % (start_date, end_date)
        ,'KOR-KQStock': "SELECT DISTINCT Ticker FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX WHERE Market = 'KOSDAQ' AND Date_ BETWEEN '%s' AND '%s'" % (start_date, end_date)

   }

    ticker_df = read_sql_table(sql=sql_dict[key])
    ticker_df.columns = ['Ticker']
    ticker_df = ticker_df.sort_values(by=['Ticker'])
    ticker_df = ticker_df.reset_index(drop=True)

    return ticker_df

###########################################################################
##                         가격데이터 로딩 관련
###########################################################################

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

def prices_into_upper_time_scale_df(df, time_period='W'):
    price_other_time_period = pd.DataFrame(index=df.resample(time_period).max().index, columns=df.columns)

    if time_period == 'D':
        return df

    new_time_period_data_list = list()
    for i in range(len(price_other_time_period)):

        until_sunday_cond = (df.index < price_other_time_period.index[i])
        if i == 0:
            price_df_frag = df[until_sunday_cond]
        else:
            from_monday_cond = (df.index >= price_other_time_period.index[i - 1])
            price_df_frag = df[until_sunday_cond & from_monday_cond]

        if len(price_df_frag) != 0:
            frag_array = np.array(
                [price_df_frag['Open_'].iloc[0], price_df_frag['High'].max(), price_df_frag['Low'].min(),
                 price_df_frag['Close_'].iloc[-1], price_df_frag['Volume'].sum()])
        else:
            frag_array = np.array([np.nan, np.nan, np.nan, np.nan, np.nan])
        new_time_period_data_list.append(frag_array)

    ntp_df = pd.DataFrame(new_time_period_data_list, index=price_other_time_period.index,
                          columns=price_other_time_period.columns)
    ntp_df = ntp_df.dropna(subset=ntp_df.columns, axis=0)

    return ntp_df

def get_current_name_of_ticker_data(country, asset_type, ticker):
    if asset_type in ['Index', 'IndexFutures','Commodities','FxFutures','FxRate','KOSPI','KOSDAQ','MajorIndex']:
        return {'Market': ticker, 'Name_': ticker}

    key = '%s-%s' % (country, asset_type)

    name_dbtable_dict = {'KOR-Stock': "SELECT TOP 1 * FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX WHERE Ticker = '%s' ORDER BY Date_ DESC" % (ticker),
                         'KOR-ETF': "SELECT TOP 1 * FROM Universe_Master.dbo.KOR_ETFTickers WHERE Ticker = '%s' ORDER BY Date_ DESC" % (ticker),
                         'KOR-KSStock': "SELECT TOP 1 * FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX WHERE Market = 'KOSPI' AND Ticker = '%s' ORDER BY Date_ DESC" % (ticker),
                         'KOR-KQStock': "SELECT TOP 1 * FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX WHERE Market = 'KOSDAQ' AND Ticker = '%s' ORDER BY Date_ DESC" % (ticker)
                         }

    market_result_key_dict = {'KOR-Stock': 'Market',
                              'KOR-ETF': 'Underlying_Asset',
                              'KOR-KSStock': 'Market',
                              'KOR-KQStock': 'Market',
                              }

    ticker_info = read_sql_table(name_dbtable_dict[key])

    if len(ticker_info) == 0:
        return {'Market': '-', 'Name_': '-'}
    else:
        return {'Market': ticker_info.loc[0, market_result_key_dict[key]],
                'Name_': ticker_info.loc[0, 'Name_']}



def download_price_data(country = 'KOR', asset_type = 'Index', ticker = 'KOSDAQ지수', start_date = '2015-01-01', end_date = datetime.today().strftime('%Y-%m-%d'),time_period = 'D'):

    key = '%s-%s'%(country,asset_type)
    sql_dict = {
        'KOR-Index': "SELECT Date_, Open_, High, Low, Close_, Volume FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Ticker='%s' AND Date_ BETWEEN '%s' AND '%s'" % (ticker,start_date, end_date),
        'KOR-Stock': "SELECT Date_, Open_, High, Low, Close_, Volume FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX WHERE Ticker='%s' AND Date_ BETWEEN '%s' AND '%s'" % (ticker,start_date, end_date),
        'KOR-ETF': "SELECT Date_, Open_, High, Low, Close_, Volume FROM KOR_Price_Data.dbo.KOR_ETFPriceDataFromNF WHERE Ticker='%s' AND Date_ BETWEEN '%s' AND '%s'" % (ticker,start_date, end_date),
        'GLOB-Index': "SELECT Date_, Open_, High, Low, Close_, Volume FROM GLOB_Price_Data.dbo.GLOB_IndexPriceDataFromIV WHERE Ticker='%s' AND Date_ BETWEEN '%s' AND '%s'" % (ticker,start_date, end_date),
        'GLOB-IndexFutures': "SELECT Date_, Open_, High, Low, Close_, Volume FROM GLOB_Price_Data.dbo.GLOB_IndexFuturesPriceDataFromIV WHERE Ticker='%s' AND Date_ BETWEEN '%s' AND '%s'" % (ticker,start_date, end_date),
        'GLOB-FxFutures': "SELECT Date_, Open_, High, Low, Close_, Volume FROM GLOB_Price_Data.dbo.GLOB_FxFuturesPriceDataFromIV WHERE Ticker='%s' AND Date_ BETWEEN '%s' AND '%s'" % (ticker,start_date, end_date),
        'GLOB-FxRate': "SELECT Date_, Open_, High, Low, Close_, Volume FROM GLOB_Price_Data.dbo.GLOB_FxRateDataFromIV WHERE Ticker='%s' AND Date_ BETWEEN '%s' AND '%s'" % (ticker,start_date, end_date),
        'GLOB-Commodities': "SELECT Date_, Open_, High, Low, Close_, Volume FROM GLOB_Price_Data.dbo.GLOB_CommoditiesPriceDataFromIV WHERE Ticker='%s' AND Date_ BETWEEN '%s' AND '%s'" % (ticker,start_date, end_date),
        'KOR-MajorIndex': "SELECT Date_, Open_, High, Low, Close_, Volume FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Ticker='%s' AND Date_ BETWEEN '%s' AND '%s'" % (ticker,start_date, end_date),
        'KOR-KOSPI': "SELECT Date_, Open_, High, Low, Close_, Volume FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Ticker='%s' AND Date_ BETWEEN '%s' AND '%s'" % (ticker,start_date, end_date),
        'KOR-KOSDAQ': "SELECT Date_, Open_, High, Low, Close_, Volume FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Ticker='%s' AND Date_ BETWEEN '%s' AND '%s'" % (ticker,start_date, end_date),
        'KOR-KSStock': "SELECT Date_, Open_, High, Low, Close_, Volume FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX WHERE Ticker='%s' AND Date_ BETWEEN '%s' AND '%s'" % (ticker, start_date, end_date),
        'KOR-KQStock': "SELECT Date_, Open_, High, Low, Close_, Volume FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX WHERE Ticker='%s' AND Date_ BETWEEN '%s' AND '%s'" % (ticker, start_date, end_date),
        }

    price_df = read_sql_table(sql=sql_dict[key])
    price_df = price_df.set_index(keys=['Date_'], drop=True)
    price_df.index = pd.to_datetime(price_df.index)


    ntp_df = prices_into_upper_time_scale_df(df=price_df,time_period=time_period)

    return ntp_df


###########################################################################
##                         수급데이터 로딩 관련
###########################################################################

def download_supply_data(country = 'KOR', asset_type = 'Stock', ticker = '000030', start_date = '2015-01-01', end_date = datetime.today().strftime('%Y-%m-%d'),time_period = 'D'):


    key = '%s-%s'%(country,asset_type)
    supply_dbtable_dict = {'KOR-Index':'',
                          'KOR-Stock':'KOR_SD_Data.dbo.KOR_SDVolumeDataFromKRX',
                          'KOR-ETF':'',
                          'GLOB-Index':'',
                          'GLOB-IndexFutures':'',
                           'GLOB-FxFutures': '',
                           'GLOB-FxRate': '',
                          'GLOB-Commodities': '',
                           'KOR-MajorIndex': '',
                           'KOR-KOSPI': '',
                           'KOR-KOSDAQ': '',
                           'KOR-KSStock': 'KOR_SD_Data.dbo.KOR_SDVolumeDataFromKRX',
                           'KOR-KQStock': 'KOR_SD_Data.dbo.KOR_SDVolumeDataFromKRX',
                          }


    sql = "SELECT * FROM %s WHERE Ticker = '%s' AND Date_ BETWEEN '%s' AND '%s' ORDER BY Date_"%(supply_dbtable_dict[key],ticker,start_date,end_date)
    supply_df = read_sql_table(sql=sql)
    supply_df = supply_df[['Date_','개인','외국인','기관','연기금','투신','사모','금융투자','은행','보험','국가지자체','기타금융','기타법인','기타외국인']]
    supply_df = supply_df.set_index(keys=['Date_'], drop=True)
    supply_df.index = pd.to_datetime(supply_df.index)


    ntp_df = supply_into_upper_time_scale_df(df=supply_df,time_period=time_period)

    return ntp_df

def supply_into_upper_time_scale_df(df, time_period='W'):
    supply_other_time_period = pd.DataFrame(index=df.resample(time_period).max().index, columns=df.columns)

    if time_period == 'D':
        return df

    new_time_period_data_list = list()
    for i in range(len(supply_other_time_period)):

        until_sunday_cond = (df.index < supply_other_time_period.index[i])
        if i == 0:
            supply_df_frag = df[until_sunday_cond]
        else:
            from_monday_cond = (df.index >= supply_other_time_period.index[i - 1])
            supply_df_frag = df[until_sunday_cond & from_monday_cond]

        if len(supply_df_frag) != 0:
            frag_array = np.array([supply_df_frag[c].sum() for c in list(supply_df_frag.columns)[0:]])
        else:
            frag_array = np.array([np.nan for c in list(supply_df_frag.columns)[0:]])
        new_time_period_data_list.append(frag_array)

    ntp_df = pd.DataFrame(new_time_period_data_list, index=supply_other_time_period.index,
                          columns=supply_other_time_period.columns)
    ntp_df = ntp_df.dropna(subset=ntp_df.columns, axis=0)

    return ntp_df

###########################################################################
##                         재무데이터 로딩 관련
###########################################################################


def download_fs_data(country = 'KOR', asset_type = 'Stock', ticker = '000030', start_date = '2015-01-01', end_date = datetime.today().strftime('%Y-%m-%d'),time_period = 'Q'):

    try:
        key = '%s-%s' % (country, asset_type)
        supply_dbtable_dict = {
                                'KOR-Stock': 'KOR_FS_Data.dbo.KOR_StockFSDataFromCG_%s'%time_period,
                                'KOR-KSStock': 'KOR_FS_Data.dbo.KOR_StockFSDataFromCG_%s' % time_period,
                                'KOR-KQStock': 'KOR_FS_Data.dbo.KOR_StockFSDataFromCG_%s' % time_period
                               }


        sql = "SELECT * FROM %s WHERE Ticker = '%s' AND Date_ BETWEEN '%s' AND '%s'"%(supply_dbtable_dict[key],ticker,start_date,end_date)
        fs_df = read_sql_table(sql=sql)
        fs_df = fs_df[['Date_','Item','Value_']]
        fs_df = fs_df.pivot(index='Date_',columns='Item',values='Value_')
        fs_df.index = pd.to_datetime(fs_df.index)
    except:
        fs_df = pd.DataFrame()

    return fs_df


## 지표생성 및 데이터 편집
## from wecolib.Curvelib_indicators_and_editing_data import *