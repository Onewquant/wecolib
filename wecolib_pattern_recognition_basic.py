## 지표생성 및 데이터 편집
from wecolib.wecolib_indicators_and_editing_data import *

###########################################################################
##              Pattern Screening Basic Tools
###########################################################################



def local_limit_pattern_table_upg(ds, pivot, loclim_type):
    loclim_dict = {'min': True, 'max': False}

    if loclim_type == 'min':
        target_ds = ds * (ds < pivot)
    elif loclim_type == 'max':
        target_ds = ds * (ds >= pivot)
    last_target_ds = target_ds.shift(1).fillna(0)
    next_target_ds = target_ds.shift(-1).fillna(0)

    uc_index = target_ds[(last_target_ds == 0) & (target_ds != 0)].index
    ud_index = target_ds[(next_target_ds == 0) & (target_ds != 0)].index
    group_index_tuple_list = list(zip(uc_index, ud_index))

    ds_patterm_list = list()
    for group in range(len(group_index_tuple_list)):

        lmd_1 = None
        lmv_1 = np.nan
        lmd_2 = None
        lmv_2 = np.nan

        group_frag_series = target_ds.loc[group_index_tuple_list[group][0]:group_index_tuple_list[group][1]]
        if len(group_frag_series) >= 2:
            group_frag_series = group_frag_series.sort_values(ascending=loclim_dict[loclim_type])
            lmd_1 = group_frag_series.index[0]
            lmv_1 = group_frag_series.iloc[0]
            lmd_2 = group_frag_series.index[1]
            lmv_2 = group_frag_series.iloc[1]
        else:
            lmd_1 = group_frag_series.index[0]
            lmv_1 = group_frag_series.iloc[0]

        group_pattern_frag = [lmd_1, lmv_1, lmd_2, lmv_2]
        ds_patterm_list.append(group_pattern_frag)

    if loclim_type == 'min':
        ds_patterm_df = pd.DataFrame(ds_patterm_list,columns=['LocMinDate1', 'LocMinValue1', 'LocMinDate2', 'LocMinValue2'])
    elif loclim_type == 'max':
        ds_patterm_df = pd.DataFrame(ds_patterm_list,columns=['LocMaxDate1', 'LocMaxValue1', 'LocMaxDate2', 'LocMaxValue2'])

    return ds_patterm_df

def local_limit_pattern_table(ds, pivot, loclim_type):
    loclim_dict = {'min': True, 'max': False}

    if loclim_type == 'min':
        target_ds = ds * (ds < pivot)
    elif loclim_type == 'max':
        target_ds = ds * (ds >= pivot)
    last_target_ds = target_ds.shift(1).fillna(0)
    next_target_ds = target_ds.shift(-1).fillna(0)

    uc_index = target_ds[(last_target_ds == 0) & (target_ds != 0)].index
    ud_index = target_ds[(next_target_ds == 0) & (target_ds != 0)].index
    group_index_tuple_list = list(zip(uc_index, ud_index))

    ds_patterm_list = list()
    for group in range(len(group_index_tuple_list)):

        lmd_1 = None
        lmv_1 = np.nan
        lmd_2 = None
        lmv_2 = np.nan

        group_frag_series = target_ds.loc[group_index_tuple_list[group][0]:group_index_tuple_list[group][1]]
        if len(group_frag_series) >= 2:
            group_frag_series = group_frag_series.sort_values(ascending=loclim_dict[loclim_type])
            lmd_1 = group_frag_series.index[0]
            lmv_1 = group_frag_series.iloc[0]
            lmd_2 = group_frag_series.index[1]
            lmv_2 = group_frag_series.iloc[1]
        else:
            lmd_1 = group_frag_series.index[0]
            lmv_1 = group_frag_series.iloc[0]

        group_pattern_frag = [lmd_1, lmv_1, lmd_2, lmv_2]
        ds_patterm_list.append(group_pattern_frag)

    if loclim_type == 'min':
        ds_patterm_df = pd.DataFrame(ds_patterm_list,columns=['LocMinDate1', 'LocMinValue1', 'LocMinDate2', 'LocMinValue2'])
    elif loclim_type == 'max':
        ds_patterm_df = pd.DataFrame(ds_patterm_list,columns=['LocMaxDate1', 'LocMaxValue1', 'LocMaxDate2', 'LocMaxValue2'])

    return ds_patterm_df


def local_limit_change_screener(ds, lim_type='min', ascending=True):
    last_tangent = ds - ds.shift(1)
    next_tangent = ds.shift(-1) - ds
    local_maximum_cond = (last_tangent > 0) & (next_tangent < 0)
    local_minimum_cond = (last_tangent < 0) & (next_tangent > 0)
    local_minimum_tangent = (ds[local_minimum_cond] - ds[local_minimum_cond].shift(1))
    local_maximum_tangent = (ds[local_maximum_cond] - ds[local_maximum_cond].shift(1))
    locmin_increase_cond = local_minimum_tangent > 0
    locmin_decrease_cond = local_minimum_tangent < 0
    locmax_increase_cond = local_maximum_tangent > 0
    locmax_decrease_cond = local_maximum_tangent < 0

    locmin_inc = local_minimum_tangent[locmin_increase_cond]
    locmin_dec = local_minimum_tangent[locmin_decrease_cond]
    locmax_inc = local_maximum_tangent[locmax_increase_cond]
    locmax_dec = local_maximum_tangent[locmax_decrease_cond]

    if (lim_type == 'min') & (ascending == True):
        result = locmin_inc
    elif (lim_type == 'min') & (ascending == False):
        result = locmin_dec
    elif (lim_type == 'max') & (ascending == True):
        result = locmax_inc
    elif (lim_type == 'max') & (ascending == False):
        result = locmax_dec

    return result


def trend_screener(ds, window, direction):

    trend_standard = window * 0.6

    ds_tangent = ds - ds.shift(window)
    ds_increase_cond = ds_tangent > 0
    ds_decrease_cond = ds_tangent < 0

    change_freq_bull_cond = (ds_increase_cond.rolling(center=False, window=window).sum() >= trend_standard)
    change_freq_bear_cond = (ds_decrease_cond.rolling(center=False, window=window).sum() >= trend_standard)

    bull_cond = ds_increase_cond & change_freq_bull_cond
    bear_cond = ds_decrease_cond & change_freq_bear_cond

    if direction == 'bull':
        total_cond = bull_cond
    elif direction == 'bear':
        total_cond = bear_cond
    elif direction == 'box':
        total_cond = (~bull_cond) & (~bear_cond)

    return ds[total_cond]


def get_sufficient_df_comparing_ent_and_pre_dataframes(ent_df, pre_df, date_diff):
    """
    ## 진입포인트를 스크린한 Dataframe이 존재할때
    ## 다른 선행 조건을 스크린한 Dataframe에서
    ## 일정 날짜 차이내에 선행관계를 만족하는 포인트가 있는지를 구함
    ## 선행관계를 만족하는 조건이 존재하는 ent_df의 row 반환
    """

    if len(ent_df) == 0:
        # print('Entry Point가 존재하지 않습니다.')
        result_df = pd.DataFrame(columns=ent_df.columns)
        return result_df
    if len(pre_df) == 0:
        # print('Pre Event Point가 존재하지 않습니다')
        result_df = pd.DataFrame(columns=ent_df.columns)
        return result_df

    ent_index_list = ent_df.index
    pre_index_list = pre_df.index

    result_index = list()
    for ent in ent_index_list:
        date_diff_series = (ent - pd.Series(pre_df.index))
        date_diff_series = date_diff_series.map(lambda x: x.days)
        pre_existing_cond = (date_diff_series >= 0)
        existance_frag = pd.Series(pre_df.index)[pre_existing_cond]
        no_pre_existing_event_cond = (len(existance_frag) == 0)
        date_diff_is_long_cond = (((pre_existing_cond * 1).iloc[-1]) > date_diff)
        if (no_pre_existing_event_cond | date_diff_is_long_cond):
            continue
        else:
            result_index.append(ent)

    result_df = ent_df[ent_df.index.isin(result_index)]
    return result_df


def get_screened_ent_ds_comparing_ent_value_to_last_pre_value(ent_ds, pre_ds,ascending=True):

    if len(ent_ds) == 0:
        # print('Entry Point가 존재하지 않습니다.')
        result_ds = pd.Series()
        return result_ds
    if len(pre_ds) == 0:
        # print('Pre Event Point가 존재하지 않습니다')
        result_ds = pd.Series()
        return result_ds

    ent_df = pd.DataFrame(ent_ds)
    pre_df = pd.DataFrame(pre_ds)
    ent_df.columns = ['Ent']
    pre_df.columns = ['Pre']

    if ascending==True:
        result_index_list = list()
        for inx, row in ent_df.iterrows():
            pre_occurred = pre_df[pre_df.index < inx]
            if len(pre_occurred) == 0:
                continue
            last_value = pre_occurred.iloc[-1]['Pre']
            cur_value = row['Ent']
            value_diff = cur_value - last_value
            if value_diff > 0:
                result_index_list.append(inx)

    elif ascending==False:
        result_index_list = list()
        for inx, row in ent_df.iterrows():
            pre_occurred = pre_df[pre_df.index < inx]
            if len(pre_occurred) == 0:
                continue
            last_value = pre_occurred.iloc[-1]['Pre']
            cur_value = row['Ent']
            value_diff = cur_value - last_value
            if value_diff < 0:
                result_index_list.append(inx)

    result = ent_ds[ent_df.index.isin(result_index_list)]
    return result

###########################################################################
##                       Pattern Screener
###########################################################################

# def macd_histogram_double_bottoms_screener(df):
#
#     searching_date_df = df[(df['MACD_Histogram'] < 0) & (df['MACD_Histogram_Trend'] < 0)]
#     bottoms_date_df = df[(df['MACD_Histogram'] < 0) & (df['MACD_Histogram_Trend'] < 0) & (df['MACD_Histogram'].shift(-1) - df['MACD_Histogram'] > 0)].sort_index(ascending=False)
#
#     scr_df = pd.DataFrame(columns=list(searching_date_df.columns))
#     for sd_inx, sd_row in searching_date_df.iterrows():
#         bottoms_date_df_frag = bottoms_date_df[bottoms_date_df.index < sd_inx]
#         if len(bottoms_date_df_frag) ==0 :
#             continue
#         b_row = bottoms_date_df_frag.iloc[0]
#         true_lower_price = min(sd_row['Close_'],sd_row['Open_'])
#         price_range_margin = (sd_row['EMA']-sd_row['Lower_mBollinger'])/5
#
#         macd_hist_uptrend_cond = (sd_row['MACD_Histogram'] > b_row['MACD_Histogram'])
#         true_lower_price_position_cond = (true_lower_price <= (sd_row['Lower_mBollinger']+price_range_margin))
#         upper_range_of_pre_true_lower_price_cond = min(b_row['Close_'],b_row['Open_']) <= true_lower_price + 2 * price_range_margin
#         lower_range_of_pre_true_lower_price_cond = min(b_row['Close_'],b_row['Open_']) >= true_lower_price - 2 * price_range_margin
#         total_cond = macd_hist_uptrend_cond & true_lower_price_position_cond & upper_range_of_pre_true_lower_price_cond & lower_range_of_pre_true_lower_price_cond
#         if total_cond:
#             scr_df = scr_df.append(sd_row)
#
#     return scr_df

def macd_histogram_max_velocity_point_screener(df,recent=True):

    """
    ## MACD Histogram이 음수에서 양수로 변화되는 조건
    ## MACD Histogram이 포인트 직전에 저점을 높인 이벤트 존재 조건
    ## 위의 두 조건을 모두 만족하는 포인트
    """

    histogram = df['MACD_Histogram']
    histogram_pattern_tbl = local_limit_pattern_table(ds=histogram, pivot=0, loclim_type='min')
    histogram_acceleration_table = histogram_pattern_tbl[(histogram_pattern_tbl['LocMinValue1']-histogram_pattern_tbl['LocMinValue1'].shift(1))>0]

    ## 필요조건
    cur_histogram_positive_cond = (histogram>=0)
    last_histogram_negative_cond = (histogram.shift(1)<0)
    histogram_increase_cond = (histogram - histogram.shift(1)>0)
    mid_total_cond = ((cur_histogram_positive_cond)&(last_histogram_negative_cond)&(histogram_increase_cond))
    mid_total_cond_shift =  mid_total_cond.shift(-7)
    mid_total_index = histogram[mid_total_cond==True].index
    mid_total_shift_index = histogram[mid_total_cond_shift==True].index
    index_num_diff = len(mid_total_index)-len(mid_total_shift_index)
    if index_num_diff > 0:
        mid_total_index = mid_total_index[index_num_diff:]
    comparing_date_range_list = list(zip(mid_total_shift_index,mid_total_index))

    index_result_list = list()
    for tup in comparing_date_range_list:

        comparing_tbl_frag = histogram_acceleration_table[(histogram_acceleration_table['LocMinDate1'] < tup[1])&(histogram_acceleration_table['LocMinDate1'] > tup[0])]
        if len(comparing_tbl_frag)==0:
            continue
        else:
            index_result_list.append(tup[1])


    result_df = df[df.index.isin(index_result_list)]
    if recent==True:
        result_df = result_df[result_df.index == result_df.index[-1]]

    return result_df


def macd_histogram_min_velocity_point_screener(df,recent=True):

    """
    ## MACD Histogram이 양수에서 음수로 변화되는 조건
    ## MACD Histogram이 포인트 직전에 고점을 낮춘 이벤트 존재 조건
    ## 위의 두 조건을 모두 만족하는 포인트
    """

    histogram = df['MACD_Histogram']
    histogram_pattern_tbl = local_limit_pattern_table(ds=histogram, pivot=0, loclim_type='max')
    histogram_acceleration_table = histogram_pattern_tbl[(histogram_pattern_tbl['LocMaxValue1']-histogram_pattern_tbl['LocMaxValue1'].shift(1))<0]

    ## 필요조건
    cur_histogram_negative_cond = (histogram<=0)
    last_histogram_positive_cond = (histogram.shift(1)>0)
    histogram_decrease_cond = (histogram - histogram.shift(1)<0)
    mid_total_cond = ((cur_histogram_negative_cond)&(last_histogram_positive_cond)&(histogram_decrease_cond))
    mid_total_cond_shift =  mid_total_cond.shift(-7)
    mid_total_index = histogram[mid_total_cond==True].index
    mid_total_shift_index = histogram[mid_total_cond_shift==True].index
    index_num_diff = len(mid_total_index)-len(mid_total_shift_index)
    if index_num_diff > 0:
        mid_total_index = mid_total_index[index_num_diff:]
    comparing_date_range_list = list(zip(mid_total_shift_index,mid_total_index))

    index_result_list = list()
    for tup in comparing_date_range_list:

        comparing_tbl_frag = histogram_acceleration_table[(histogram_acceleration_table['LocMaxDate1'] < tup[1])&(histogram_acceleration_table['LocMaxDate1'] > tup[0])]
        if len(comparing_tbl_frag)==0:
            continue
        else:
            index_result_list.append(tup[1])


    result_df = df[df.index.isin(index_result_list)]
    if recent==True:
        result_df = result_df[result_df.index == result_df.index[-1]]

    return result_df



def macd_acceleration_point_screener(df,recent=True):

    """
    ## MACD Slow 가 저점을 높인 이벤트 존재 조건
    ## 위의 조건을 만족하는 포인트
    """
    screened_ds = local_limit_change_screener(ds=df['MACD_Slow'], lim_type='min', ascending=True)
    index_result_list = screened_ds.index

    result_df = df[df.index.isin(index_result_list)]
    if recent==True:
        result_df = result_df[result_df.index == result_df.index[-1]]

    return result_df

def macd_deceleration_point_screener(df,recent=True):

    """
    ## MACD Slow 가 고점을 낮춘 이벤트 존재 조건
    ## 위의 조건을 만족하는 포인트
    """
    screened_ds = local_limit_change_screener(ds=df['MACD_Slow'], lim_type='max', ascending=False)
    index_result_list = screened_ds.index

    result_df = df[df.index.isin(index_result_list)]
    if recent==True:
        result_df = result_df[result_df.index == result_df.index[-1]]

    return result_df

def ema_bull_screener(df,window,recent=True):
    """
    ## 지수이평선 window 기간 기준 상승 조건
    ## 위의 조건을 만족하는 포인트
    """

    screened_ds = trend_screener(ds=df['EMA'],window=window,direction='bull')
    index_result_list = screened_ds.index

    result_df = df[df.index.isin(index_result_list)]
    if recent==True:
        result_df = result_df[result_df.index == result_df.index[-1]]

    return result_df


def ema_bear_screener(df, window, recent=True):
    """
    ## 지수이평선 window 기간 기준 하락 조건
    ## 위의 조건을 만족하는 포인트
    """

    screened_ds = trend_screener(ds=df['EMA'], window=window, direction='bear')
    index_result_list = screened_ds.index

    result_df = df[df.index.isin(index_result_list)]
    if recent == True:
        result_df = result_df[result_df.index == result_df.index[-1]]

    return result_df


def ema_box_screener(df, window, recent=True):
    """
    ## 지수이평선 window 기간 기준 하락 조건
    ## 위의 조건을 만족하는 포인트
    """

    screened_ds = trend_screener(ds=df['EMA'], window=window, direction='box')
    index_result_list = screened_ds.index

    result_df = df[df.index.isin(index_result_list)]
    if recent == True:
        result_df = result_df[result_df.index == result_df.index[-1]]

    return result_df

## 패턴인식 스크리너
## from wecolib.Curvelib_pattern_recognition_recipe import *