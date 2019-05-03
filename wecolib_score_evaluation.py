## 패턴의 퀀트적 검색
from wecolib.wecolib_quantitative_search import *

###########################################################################
##                         거래 평가 점수
###########################################################################

## 트레이딩 점수

def trading_result_trading_evaluation_score(ent_price,ex_price,df):
    avg_mboll_width = average_width_of_modified_bollinger_band_series(df=df,window=20)
    trd_eval_score = (ex_price-ent_price)*100/(avg_mboll_width.iloc[-1])
    return trd_eval_score

def trading_evaluation_score(prices, trd_eval_dict):
    trd_eval_score = trading_result_trading_evaluation_score(ent_price=trd_eval_dict['Ent_Price'],
                                                             ex_price=trd_eval_dict['Ex_Price'], df=prices)
    trd_eval_score = round(trd_eval_score, 2)
    return trd_eval_score


## 청산 가격 점수

def trading_result_exit_price_level_score(trd_price,trd_date,df):

    if len(df[df.index==trd_date])!=0:
        trd_index = trd_date
    elif len(df[df.index==datetime.strptime(trd_date, '%Y-%m-%d')])!=0:
        trd_index = datetime.strptime(trd_date, '%Y-%m-%d')
    else :
        print('Trading Result / Entering_Score / No Matched Index. Please recheck !')
        return None

    low_price = df['Low'].loc[trd_index]
    price_range = (df['High']-df['Low']).loc[trd_index]
    trd_level = trd_price - low_price
    trd_score = round((trd_level/price_range)*100,2)

    return trd_score

def trading_evaluation_exit_score(prices,ex_trading_dict):

    score_df = pd.DataFrame(ex_trading_dict['Date_List'],columns=['Date_'])
    score_df['Numshrs'] = pd.Series(ex_trading_dict['Numshrs_List'])
    score_df['Prices'] = pd.Series(ex_trading_dict['Price_List'])


    score_df = score_df.set_index(keys=['Date_'],drop=True)
    score_list = list()
    for i in range(len(score_df)):
        score_frag = trading_result_exit_price_level_score(trd_price=score_df['Prices'].iloc[i],trd_date=score_df.index[i],df=prices)
        score_list.append(score_frag)

    score_df['Score'] = pd.Series(data = score_list, index=list(score_df.index))
    average_score = 0
    for i in range(len(score_df)):
        average_score+= score_df['Score'].iloc[i]*score_df['Numshrs'].iloc[i]
    average_score /= score_df['Numshrs'].sum()
    average_score = round(average_score,2)
    return average_score

## 진입가격 점수

def trading_result_entering_price_level_score(trd_price,trd_date,df):

    if len(df[df.index==trd_date])!=0:
        trd_index = trd_date
    elif len(df[df.index==datetime.strptime(trd_date, '%Y-%m-%d')])!=0:
        trd_index = datetime.strptime(trd_date, '%Y-%m-%d')
    else :
        print('Trading Result / Entering_Score / No Matched Index. Please recheck !')
        return None

    low_price = df['Low'].loc[trd_index]
    price_range = (df['High']-df['Low']).loc[trd_index]
    trd_level = trd_price - low_price
    trd_score = round((1-trd_level/price_range)*100,2)

    return trd_score


def trading_evaluation_entry_score(prices,ent_trading_dict):

    score_df = pd.DataFrame(ent_trading_dict['Date_List'],columns=['Date_'])
    score_df['Numshrs'] = pd.Series(ent_trading_dict['Numshrs_List'])
    score_df['Prices'] = pd.Series(ent_trading_dict['Price_List'])

    score_df = score_df.set_index(keys=['Date_'],drop=True)
    score_list = list()
    for i in range(len(score_df)):
        score_frag = trading_result_entering_price_level_score(trd_price=score_df['Prices'].iloc[i],trd_date=score_df.index[i],df=prices)
        score_list.append(score_frag)

    score_df['Score'] = pd.Series(data = score_list, index=list(score_df.index))
    average_score = 0
    for i in range(len(score_df)):
        average_score+= score_df['Score'].iloc[i]*score_df['Numshrs'].iloc[i]
    average_score /= score_df['Numshrs'].sum()
    average_score = round(average_score, 2)
    return average_score

###########################################################################
##                거래 평가 점수 계산에 필요한 기본함수들
###########################################################################

## 지수 이동평균선

def exponential_moving_average_series(df,column='Close_',window=20):
    weight = float(2)/(window+1) # 지수이동평균가중치
    result = list()
    for inx,row in df.iterrows():
        value = row[column]
        if not result: # price_df.iloc[0]은 계산하지 않음
            result.append(value)
        else:
            result.append((value*weight)+(result[-1]*(1-weight)))

    result = pd.Series(data=result,index=list(df.index))
    return result

def exponential_moving_average_dataframe(df,column='Close_',window=20):
    dataframe = df
    ema_series = exponential_moving_average_series(df=df,column=column,window=window)
    dataframe['EMA'] = ema_series
    return dataframe

## 변형 볼린저밴드 채널 지표 (지수이동평균선을 중심선으로 함)

def modified_bollinger_band_series(df,window=20):
    column = 'Close_'
    std_series = df[column].rolling(center=False,window=window).std()
    ema_series = exponential_moving_average_series(df=df,column=column,window=window)
    upper = ema_series + 2*std_series
    lower = ema_series - 2*std_series
    result = {'Upper':upper,'Lower':lower}
    return result

def modified_bollinger_band_dataframe(df,window=20):
    dataframe = df
    bollinger_dict = modified_bollinger_band_series(df=df,window=window)
    dataframe['Upper_mBollinger'] = bollinger_dict['Upper']
    dataframe['Lower_mBollinger'] = bollinger_dict['Lower']
    return dataframe

## 변형 볼린저밴드 채널의 평균폭 지표 (지수이동평균선을 중심선으로 함)

def average_width_of_modified_bollinger_band_series(df,window=20):
    result = (df['Upper_mBollinger'] - df['Lower_mBollinger']).rolling(center=False,window=window).mean()
    return result

def average_width_of_modified_bollinger_band_dataframe(df,window=20):
    dataframe = df
    dataframe['Avg_Width_mBollinger'] = average_width_of_modified_bollinger_band_series(df=dataframe,window=window)
    return dataframe

## 데이터 시각화
## from wecolib.Curvelib_visualization import *