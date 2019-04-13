## 로우 데이터 로딩
from wecolib.wecolib_get_raw_data import *

###########################################################################
##                        기술적 지표
###########################################################################

## 가격 관련

def price_derivatives_dataframe(df):
    dataframe = df

    ## Trend
    dataframe['Open_Trend'] = dataframe['Open_'] - dataframe['Open_'].shift(1)
    dataframe['High_Trend'] = dataframe['High'] - dataframe['High'].shift(1)
    dataframe['Low_Trend'] = dataframe['Low'] - dataframe['Low'].shift(1)
    dataframe['Close_Trend'] = dataframe['Close_'] - dataframe['Close_'].shift(1)



    ## Next Price
    dataframe['Next_Open_'] = dataframe['Open_'].shift(-1)
    dataframe['Next_High'] = dataframe['High'].shift(-1)
    dataframe['Next_Low'] = dataframe['Low'].shift(-1)
    dataframe['Next_Close_'] = dataframe['Close_'].shift(-1)

    ## Past Price
    dataframe['DA1_Open_'] = dataframe['Open_'].shift(1)
    dataframe['DA1_High'] = dataframe['High'].shift(1)
    dataframe['DA1_Low'] = dataframe['Low'].shift(1)
    dataframe['DA1_Close_'] = dataframe['Close_'].shift(1)
    dataframe['DA2_Open_'] = dataframe['Open_'].shift(2)
    dataframe['DA2_High'] = dataframe['High'].shift(2)
    dataframe['DA2_Low'] = dataframe['Low'].shift(2)
    dataframe['DA2_Close_'] = dataframe['Close_'].shift(2)

    ## Others
    dataframe['Higher_High'] = ((dataframe['DA1_High'] <= dataframe['High'])&(dataframe['DA1_High'] >= dataframe['Low']))*1
    dataframe['Lower_Low'] = ((dataframe['High'] > dataframe['DA1_Low'])&(dataframe['Low'] < dataframe['DA1_Low']))*1
    dataframe['Lower_DA1_Close_'] = (dataframe['DA2_High'] > dataframe['DA1_Close_'])*1
    dataframe['Higher_Open_'] = (dataframe['Open_'] > dataframe['DA1_Low'])*1
    dataframe['20D_High'] = dataframe['High'].rolling(center=False, window=20).max()
    dataframe['2D_High'] = dataframe['High'].rolling(center=False,window=2).max()
    dataframe['10D_Low'] = dataframe['Low'].rolling(center=False, window=10).min()

    d2_open_max = dataframe['Open_'].rolling(center=False, window=2).max()
    d2_close_max = dataframe['Close_'].rolling(center=False, window=2).max()
    max_discriminant = ((d2_close_max - d2_open_max) >= 0)
    dataframe['2D_TR_Max'] = d2_close_max * (max_discriminant*1) + d2_open_max * (~max_discriminant*1)

    ## Gap
    dataframe['Opening_Gap'] = (dataframe['Open_'] - dataframe['DA1_Close_'])/dataframe['DA1_Close_']
    dataframe['Opening_Gap_Cond'] = (dataframe['Opening_Gap'] > -0.01)*1

    return dataframe




## 거래량, 거래금액 관련

def trd_volume_dataframe(df,column='Close_'):
    dataframe = df
    volume = df['Volume']
    price = df[column]

    volume_trend = volume - volume.shift(1)
    trd_amount = price * volume
    trd_amount_trend = trd_amount - trd_amount.shift(1)

    window_list = [3,5,20]
    for w in window_list:
        dataframe['Volume_MA%s'%w] = volume.rolling(center=False, window=w).mean()

    dataframe['Volume_Trend'] = volume_trend
    dataframe['Trd_Amount'] = trd_amount
    dataframe['Trd_Amount_Trend'] = trd_amount_trend

    return dataframe

## 누적 수익률

def cum_rets_dataframe(df,column='Close_'):
    dataframe = df
    close_price = df[column]
    cumrets_series = (1 + ((close_price - close_price.shift(1)) / close_price).fillna(0)).cumprod()
    dataframe['Cum_Rets'] = cumrets_series
    return dataframe

## 단순 이동평균선

def moving_average_dataframe(df,column='Close_',window_list=[5,20,50,100]):
    dataframe = df
    for window in window_list:
        dataframe['MA%s'%window] = dataframe[column].rolling(center=False, window=window).mean()
    return dataframe

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

## 지수 이동평균선의 추세 지표

def ema_trend_series(df,window=5):

    ds = df['EMA']

    ds_tangent = ds - ds.shift(window)
    ds_increase_cond = (ds_tangent >= 0)
    ds_decrease_cond = (ds_tangent < 0)

    ema_trend_series = (ds_increase_cond*1 + ds_decrease_cond*(-1))

    return ema_trend_series

def ema_trend_dataframe(df,window=5):
    dataframe = df
    dataframe['EMA_Trend'] = ema_trend_series(df=dataframe,window=window)
    dataframe['EMA_Trend1'] = ema_trend_series(df=dataframe, window=1)
    dataframe['EMA_Trend2'] = ema_trend_series(df=dataframe,window=2)
    dataframe['EMA_Trend3'] = ema_trend_series(df=dataframe,window=3)
    dataframe['EMA_Trend5'] = ema_trend_series(df=dataframe,window=5)
    dataframe['EMA_Trend20'] = ema_trend_series(df=dataframe,window=20)
    dataframe['EMA_Trend50'] = ema_trend_series(df=dataframe,window=50)
    dataframe['EMA_Trend100'] = ema_trend_series(df=dataframe, window=100)

    return dataframe

## 평균 이동평균선 스코어 (단순 이평선 이용)

def average_moving_average_score_dataframe(df,column = 'Close_',window_list = [5,20,60,100]):
    dataframe = df
    cum_ma_series = pd.Series(index=df.index).fillna(0)
    for w in window_list:
        cum_ma_series+=(df[column] > df[column].rolling(center=False,window=w).mean())
    ama_series = cum_ma_series/len(window_list)
    dataframe['AMA_Score'] = ama_series
    return dataframe

## Envelop 채널지표 (지수 이동평균선이 중심선)

def channel_dataframe(df,window=20,coefficient=0.05):
    dataframe = df
    column = 'Close_'
    ema = exponential_moving_average_series(df=df,column=column,window=window)
    upper = (1+coefficient)*ema
    lower = (1-coefficient)*ema

    dataframe['Upper_Channel'] = upper
    dataframe['Lower_Channel'] = lower
    return dataframe

## 볼린저밴드 채널지표 (20일 단순이동평균선이 중심선)

def bollinger_band_dataframe(df,window=20):
    dataframe = df
    column = 'Close_'
    std_series = df[column].rolling(center=False,window=window).std()
    ma_series = df[column].rolling(center=False,window=window).mean()
    upper = ma_series - 2*std_series
    lower = ma_series + 2*std_series

    dataframe['Upper_Bollinger'] = upper
    dataframe['Lower_Bollinger'] = lower
    return dataframe

## 변형 볼린저밴드 채널 지표 (지수이동평균선을 중심선으로 함)

def modified_bollinger_band_dataframe(df,window=20):
    dataframe = df
    column = 'Close_'
    std_series = df[column].rolling(center=False,window=window).std()
    ema_series = exponential_moving_average_series(df=df,column=column,window=window)
    upper = ema_series + 2*std_series
    lower = ema_series - 2*std_series

    dataframe['Upper_mBollinger'] = upper
    dataframe['Lower_mBollinger'] = lower

    dataframe['Avg_Width_mBollinger'] = (dataframe['Upper_mBollinger'] - dataframe['Lower_mBollinger']).rolling(center=False, window=window).mean()
    return dataframe


## MACD 지표

def macd_series(df,column='Close_'):
    ema12 = exponential_moving_average_series(df=df,column=column,window=12)
    ema26 = exponential_moving_average_series(df=df, column=column, window=26)

    fast_macd = ema12 - ema26
    slow_macd = exponential_moving_average_series(df=pd.DataFrame(data = fast_macd), column=0, window=9)
    histogram = fast_macd - slow_macd

    histogram_trend = histogram - histogram.shift(1)

    result = {'Fast':fast_macd,'Slow':slow_macd,'Histogram':histogram,'Histogram_Trend':histogram_trend}
    return result

def macd_dataframe(df,column='Close_'):
    dataframe = df
    macd_dict = macd_series(df=df,column=column)
    dataframe['MACD_Fast'] = macd_dict['Fast']
    dataframe['MACD_Slow'] = macd_dict['Slow']
    dataframe['MACD_Histogram'] = macd_dict['Histogram']
    dataframe['MACD_Histogram_Trend']=macd_dict['Histogram_Trend']

    return dataframe

## Force Index (강도지수) 지표

def force_index_dataframe(df,column='Close_',window=2):
    dataframe = df

    force_index_series = (df[column] - df[column].shift(1)) * df['Volume']
    force_index_mean_rolling_series = force_index_series.rolling(center=False,window=250).mean()
    force_index_std_rolling_series = force_index_series.rolling(center=False,window=250).std()
    force_index_ratio = force_index_series / force_index_mean_rolling_series
    force_index_norm = (force_index_series-force_index_mean_rolling_series)/force_index_std_rolling_series

    force_index_fear_rolling_standard = ((((force_index_norm < -2.5) * 1).rolling(center=False,window=3).sum())>0) * 1
    force_index_greed_rolling_standard = ((((force_index_norm >= 2.5) * 1).rolling(center=False, window=3).sum()) > 0) * 1

    dataframe['Force_Index_Fear'] = force_index_fear_rolling_standard
    dataframe['Force_Index_Greed'] = force_index_greed_rolling_standard

    dataframe['Force_Index_Norm'] = force_index_norm
    dataframe['Force_Index_Ratio'] = force_index_ratio

    dataframe['Force_Index_DDM'] = ((force_index_norm < force_index_norm.shift(1))&(force_index_norm < 0))*1
    dataframe['Force_Index_DUM'] = ((force_index_norm > force_index_norm.shift(1))&(force_index_norm > 0))*1

    return dataframe

## Elder Ray 지표

def elder_ray_dataframe(df,column='Close_',window=20):
    dataframe = df
    ema_series = exponential_moving_average_series(df=df,column=column,window=window)
    buy_force_index = df['High'] - ema_series
    sell_force_index = df['Low'] - ema_series

    dataframe['Buy_Elder_Ray'] = buy_force_index
    dataframe['Sell_Elder_Ray'] = sell_force_index
    return dataframe

## Williams %R 지표

def williams_r_dataframe(df,column='Close_',window=7):
    dataframe = df
    rolling_high = df['High'].rolling(center=False,window=window).max()
    rolling_low = df['Low'].rolling(center=False,window=window).min()
    close = df['Close_']
    williamsR = (rolling_high-close)*(-100)/(rolling_high-rolling_low)
    dataframe['Williams_R'] = williamsR
    dataframe['Williams_R_Signal'] = exponential_moving_average_series(df=pd.DataFrame(dataframe['Williams_R'],columns=['WRS']),column='WRS',window=5)
    return dataframe

## ATR(Average True Range) 지표


def average_true_range_dataframe(df,window=20):

    dataframe = df
    atr_df = pd.DataFrame(index=df.index)
    atr_df['atr0'] = abs(df['High']-df['Low'])
    atr_df['atr1'] = abs(df['High']-df['Close_'].shift(1))
    atr_df['atr2'] = abs(df['Low']-df['Close_'].shift(1))

    true_range = pd.DataFrame(atr_df.max(axis=1),columns=['TR'])
    dataframe['TR'] = true_range['TR']
    dataframe['ATR3'] = exponential_moving_average_series(df=true_range, column='TR', window = 3)
    dataframe['ATR5'] = exponential_moving_average_series(df=true_range,column='TR',window = 5)
    dataframe['ATR'] = exponential_moving_average_series(df=true_range, column='TR', window=window)
    dataframe['ATR1_Pct'] = 100*true_range['TR']/(df['Close_'].shift(1))
    dataframe['ATR3_Pct'] = 100*dataframe['ATR3']/(df['Close_'].shift(1))
    dataframe['ATR5_Pct'] = 100*dataframe['ATR5']/(df['Close_'].shift(1))
    dataframe['ATR20_Pct'] = 100*dataframe['ATR']/(df['Close_'].shift(1))

    return dataframe

# def greatest_swing_value_dataframe(df):
#
#     dataframe = df
#     making_gsv_df0 = (dataframe['Open_']-dataframe['Low'])*((dataframe['Open_'] < dataframe['Close_'])&(dataframe['Open_']!=0)*1)
#     making_gsv_df1 = (dataframe['High']-dataframe['Open_'])*((dataframe['Open_'] > dataframe['Close_'])*1)
#     making_gsv_df2 = min((dataframe['High']-dataframe['Open_']),(dataframe['Open_']-dataframe['Low']))*((dataframe['Open_'] == dataframe['Close_'])*1)
#     dataframe['GSV'] = making_gsv_df0 + making_gsv_df1 + making_gsv_df2
#     dataframe['GSV3'] = exponential_moving_average_series(df=dataframe['GSV'], column='GSV', window = 3)
#     dataframe['GSV5'] = exponential_moving_average_series(df=dataframe['GSV'],column='GSV',window = 5)
#     dataframe['Next_GSV_Price'] = dataframe['Next_Open_'] + 1.8 * dataframe['GSV3']
#
#     return dataframe

def trading_temperature_dataframe(df,coef=3,window=20):
    dataframe = df

    positive_invasion = (dataframe['High'] - dataframe['High'].shift(1))
    negative_invasion = (dataframe['Low'].shift(1)-dataframe['Low'])
    from_high_cond = ((positive_invasion - negative_invasion) >= 0)*1
    from_low_cond = (from_high_cond-1)*(-1)
    raw_temp = (positive_invasion * from_high_cond + negative_invasion * from_low_cond)
    trading_temp = raw_temp.map(lambda x:abs(x))

    dataframe['Trd_Temp'] = trading_temp.fillna(0)
    dataframe['Trd_Temp_EMA'] = exponential_moving_average_series(df=dataframe,column='Trd_Temp',window=window)
    dataframe['Trd_Temp_Gain_Cut'] = dataframe['High'] + coef*dataframe['Trd_Temp_EMA']
    dataframe['Trd_Temp_Loss_Cut'] = dataframe['Low'] - coef*dataframe['Trd_Temp_EMA']
    return dataframe


def chandelier_exit_dataframe(df,coef=3,window=20):
    dataframe = df

    rolling_high = dataframe['High'].rolling(center=False,window=window).max()
    atr = dataframe['ATR']
    chandelier_exit = rolling_high-coef*atr

    dataframe['Chandelier_Exit'] = chandelier_exit

    return dataframe

def sss_red_and_black_indicators_dataframe(df):
    dataframe = df
    vol = (3*(df['Volume'].rolling(center=False,window=20).mean()) <= df['Volume'])*1
    std_series = df['Close_'].rolling(center=False,window=10).std()
    ma20_series = df['Close_'].rolling(center=False,window=20).mean()
    ma40_series = df['Close_'].rolling(center=False,window=40).mean()
    black = ma40_series + 2*std_series
    red = ma20_series + 2*std_series
    dataframe['SSS_Red'] = red
    dataframe['SSS_Black'] = black
    dataframe['SSS_Volume'] = vol
    return dataframe

def larry_williams_volatility_explosion_indicators_dataframe(df):
    dataframe = df
    range = df['High'] - df['Close_']
    ent_price = df['Next_Open_'] + range
    lc_price = df['Next_Open_'] - 0.5*range

    dataframe['LWVE_Cond'] = (range > range.shift(1))&(range/df['Close_'] > 0.005)*1
    dataframe['LWVE_Ent_Price'] = ent_price
    dataframe['LWVE_LC_Price'] = lc_price

    return dataframe


###########################################################################
##                    자금관리, 매매 계획 관련 지표
###########################################################################



def avg_price_between_lower_bollinger_and_ema_dataframe(df):
    dataframe = df
    avg_price_level = (df['Lower_mBollinger'] + df['EMA'])/2
    dataframe['Avg_LB_EMA'] = avg_price_level
    return dataframe


def recent_low_price_dataframe(df,window=5):
    dataframe = df
    recent_low = df['Low'].rolling(center=False,window=window).mean()
    dataframe['Recent_Low'] = recent_low
    return dataframe


# def turtle_trd_plan_dataframe(df,one_unit_loss,column='Close_',window=20):
#     dataframe = df
#     atr_series = average_true_range_series(df=df, column=column, window=window)
#     unit_series = (one_unit_loss/(atr_series*1.5))/(1.00315*1.015)
#
#     loss_cut_series = df[column].fillna(method = 'bfill') - 1.5*atr_series
#     one_day_ago_close_series = df[column].fillna(method='bfill')
#
#     result_column_min = (dataframe[column] == dataframe[column].rolling(center=False,window=window).min())
#     result_low = (dataframe['Low'] == dataframe['Low'].rolling(center=False, window=window).min())
#     result_min = result_column_min & result_low
#
#     result_column_max = (df[column] == df[column].rolling(center=False,window=5).max())
#     result_high = (df['High'] == df['High'].rolling(center=False,window=5).max())
#     result_max = result_column_max & result_high
#
#     dataframe['Turtle_Buying_Unit'] = unit_series
#
#     dataframe['Turtle_Recent_Max_Price'] = result_max
#     dataframe['Turtle_Recent_Min_Price'] = result_min
#
#     dataframe['Turtle_Loss_Cut'] = loss_cut_series
#
#     dataframe['Turtle_Pyramid_0'] = one_day_ago_close_series + 0.5 * atr_series
#     dataframe['Turtle_Pyramid_1'] = one_day_ago_close_series + 1.0 * atr_series
#     dataframe['Turtle_Pyramid_2'] = one_day_ago_close_series + 1.5 * atr_series
#     dataframe['Turtle_Pyramid_3'] = one_day_ago_close_series + 2.0 * atr_series
#
#     return dataframe



def average_invasion_length_dataframe(df, column='Low', window=20):
    dataframe = df
    invasion_length = dataframe[column] - dataframe[column].shift(1)
    invasion_length = (invasion_length - abs(invasion_length)) / 2
    invasion_length_sum = invasion_length.rolling(center=False, window=window).sum()
    invasion_count = (invasion_length / invasion_length).fillna(0).rolling(center=False, window=window).sum()
    average_invasion_length_series = (abs(invasion_length_sum) / invasion_count)
    dataframe['Avg_Invasion'] = average_invasion_length_series
    return dataframe


def avg_invasion_length_loss_cut_line_dataframe(df,coef=3,column='Low', window=20):
    dataframe = df
    invasion_length = dataframe[column] - dataframe[column].shift(1)


    invasion_length = (invasion_length - abs(invasion_length)) / 2
    invasion_length_sum = invasion_length.rolling(center=False, window=window).sum()
    invasion_count = (invasion_length / invasion_length).fillna(0).rolling(center=False, window=window).sum()
    average_invasion_length_series = (abs(invasion_length_sum) / invasion_count)
    ail_series = average_invasion_length_series
    ail_losc = (df['Low'] - coef*(ail_series))
    dataframe['Ail_Loss_Cut'] = ail_losc
    return dataframe



def average_skyrocket_length_dataframe(df, column='High', window=20):
    dataframe = df
    skyrocket_length = df[column] - df[column].shift(1)
    skyrocket_length = (skyrocket_length + abs(skyrocket_length)) / 2
    skyrocket_length_sum = skyrocket_length.rolling(center=False, window=window).sum()
    skyrocket_count = (skyrocket_length / skyrocket_length).fillna(0).rolling(center=False, window=window).sum()
    average_skyrocket_length_series = (abs(skyrocket_length_sum) / skyrocket_count)
    dataframe['Avg_Skyrocket'] = average_skyrocket_length_series
    return dataframe


def avg_skyrocket_length_gain_cut_line_dataframe(df,coef=3,column='High', window=20):
    dataframe = df
    skyrocket_length = df[column] - df[column].shift(1)
    skyrocket_length = (skyrocket_length + abs(skyrocket_length)) / 2
    skyrocket_length_sum = skyrocket_length.rolling(center=False, window=window).sum()
    skyrocket_count = (skyrocket_length / skyrocket_length).fillna(0).rolling(center=False, window=window).sum()
    average_skyrocket_length_series = (abs(skyrocket_length_sum) / skyrocket_count)
    asl_series = average_skyrocket_length_series
    asl_gainc = (df['High'] + coef*(asl_series))
    dataframe['Asl_Gain_Cut'] = asl_gainc
    return dataframe



## 시장과의 상관계수를 고려한 포지션 조절 함수

def get_position_size_control_ratio_considering_correlation_coefficient_with_market(price_dict, market_price_dict):
    ## Broad Market의 상승 하락 고려, 자금관리 (전체 시장의 추세 고려한 투자비율 조정)
    """
    추종하는 시장 혹은 종목이 속한 시장지수와 분석종목간의 상관계수 구함
    시장지수의 상승여부 구함
    - max( 상관계수 * 시장상승여부, 평균 이동평균선 스코어)  = 자금관리 비율 (0~1)
    - 위의 값이 0 보다 작을 경우는 평균 이동평균선 스코어 점수로 자금관리 비율 대체
    """
    ## 개별종목과 시장간의 상관계수 구하기

    stock_cumrets_series = price_dict['Prices']['Cum_Rets']
    market_cumrets_series = market_price_dict['Prices']['Cum_Rets']

    correlation_coef = market_cumrets_series.corr(stock_cumrets_series, method='pearson', min_periods=None)

    ## 시장 추세에 따른 자금관리 비율 결정

    market_trend = market_price_dict['Prices']['EMA_Trend']
    market_ama_score = market_price_dict['Prices']['AMA_Score']
    market_same = market_trend.iloc[-1] * correlation_coef
    market_opposite = market_ama_score.iloc[-1]
    if market_same > 0:
        market_control_ratio = max(market_same, market_opposite)
    else:
        market_control_ratio = max(0.2,market_opposite)

    result_dict = {'Market_Position_Control_Ratio':market_control_ratio,'Corr_Coef':correlation_coef,'Market_EMA_Trend':market_trend.iloc[-1],'Market_AMA_Score':market_ama_score.iloc[-1]}

    return result_dict

###########################################################################
##                        Row DataFrame 편집
###########################################################################

def add_on_technical_indicators(df,window=20,price_type='Close_'):
    pdf = df
    pdf = price_derivatives_dataframe(df=pdf)
    pdf = trd_volume_dataframe(df=pdf,column=price_type)
    pdf = cum_rets_dataframe(df=pdf,column=price_type)
    pdf = exponential_moving_average_dataframe(df=pdf,column=price_type,window=window)
    pdf = ema_trend_dataframe(df=pdf,window=10)
    pdf = average_moving_average_score_dataframe(df=pdf,column=price_type,window_list=[int(window/4),window,window*3,window*6])
    pdf = modified_bollinger_band_dataframe(df=pdf,window=window)
    pdf = average_true_range_dataframe(df=pdf,window=window)
    pdf = macd_dataframe(df=pdf,column=price_type)
    pdf = force_index_dataframe(df=pdf,column=price_type,window=2)
    pdf = avg_invasion_length_loss_cut_line_dataframe(df=pdf, coef=2, column='Low', window=window)
    pdf = avg_skyrocket_length_gain_cut_line_dataframe(df=pdf, coef=2, column='High', window=window)
    pdf = avg_price_between_lower_bollinger_and_ema_dataframe(df=pdf)
    pdf = recent_low_price_dataframe(df=pdf,window=5)
    # pdf = greatest_swing_value_dataframe(df=pdf)

    return pdf



def edit_prices_df_for_technical_analysis(df_list,window=20,price_type='Close_'):
    result_list = list()
    for pdf in df_list:
        pdf = price_derivatives_dataframe(df=pdf)
        pdf = trd_volume_dataframe(df=pdf, column=price_type)
        pdf = cum_rets_dataframe(df=pdf,column=price_type)
        pdf = exponential_moving_average_dataframe(df=pdf,column=price_type,window=window)
        pdf = ema_trend_dataframe(df=pdf,window=10)
        pdf = average_moving_average_score_dataframe(df=pdf,column=price_type,window_list=[int(window/4),window,window*3,window*6])
        pdf = modified_bollinger_band_dataframe(df=pdf,window=window)
        pdf = average_true_range_dataframe(df=pdf, window=window)
        pdf = macd_dataframe(df=pdf,column=price_type)
        pdf = force_index_dataframe(df=pdf,column=price_type,window=2)
        pdf = avg_invasion_length_loss_cut_line_dataframe(df=pdf,coef=2,column='Low',window=window)
        pdf = avg_skyrocket_length_gain_cut_line_dataframe(df=pdf,coef=2,column='High',window=window)
        pdf = avg_price_between_lower_bollinger_and_ema_dataframe(df=pdf)
        pdf = recent_low_price_dataframe(df=pdf, window=5)
        # pdf = greatest_swing_value_dataframe(df=pdf)

        ## 기술분석을 위한 dataframe 새로 선언 및 그래프의 Zero line Data 설정

        pdf_for_csc = pdf.set_index(pdf.index.map(lambda x:x.strftime('%Y-%m-%d')))
        zero_line = pd.DataFrame(data=np.zeros(pdf.shape[0]),index=list(pdf_for_csc.index),columns=['Zero_Line'])

        result_dict = {'Prices':pdf,'Prices_For_Chart':pdf_for_csc,'Zero_Line':zero_line}
        result_list.append(result_dict)
    return result_list

## 패턴인식 기본
## from wecolib.Curvelib_pattern_recognition_basic import *