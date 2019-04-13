## 트레이딩 스코어 계산
from wecolib.wecolib_score_evaluation import *

###########################################################################
##                         Drawing Graph
###########################################################################


def price_index_number_control_for_graph(prices,upscl=False):

    dataframe = prices

    ## 그래프를 위한 Index 개수 조정
    if upscl==False:
        for n in range(20):
            if (len(dataframe) % 4 == 0)|(len(dataframe) % 3 != 0):
                dataframe = dataframe.iloc[1:]
            else:
                break
    elif upscl==True:
        for n in range(10):
            if len(dataframe) % 2 == 1:
                dataframe = dataframe.iloc[1:]
            else:
                break

    return dataframe

def draw_candle_stick_chart(prices,axes,upscl=False):

    edited_prices = prices
    edited_prices = price_index_number_control_for_graph(prices=edited_prices,upscl=upscl)

    min_size_adj = edited_prices['Low'].min()*0.98
    max_size_adj = edited_prices['High'].max()*1.02
    downside = (edited_prices['Open_'] - edited_prices['Close_'] > 0)*1
    upside = (edited_prices['Open_'] - edited_prices['Close_'] < 0)*1
    equal = (edited_prices['Open_'] - edited_prices['Close_'] == 0)*1

    wide_width = 0.5
    short_width = 0.1

    (edited_prices['Open_']*downside).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='blue',width=wide_width,ylim=(min_size_adj,max_size_adj))
    (edited_prices['Close_']*downside).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='white',width=wide_width,ylim=(min_size_adj,max_size_adj))
    (edited_prices['Close_']*upside).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='red',width=wide_width,ylim=(min_size_adj,max_size_adj))
    (edited_prices['Open_']*upside).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='white',width=wide_width,ylim=(min_size_adj,max_size_adj))
    (edited_prices['Open_']*equal).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='black',width=wide_width,ylim=(min_size_adj,max_size_adj))
    ((edited_prices['Close_']*0.999)*equal).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='white',width=wide_width,ylim=(min_size_adj,max_size_adj))

    (edited_prices['High']*downside).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='blue',width=short_width,ylim=(min_size_adj,max_size_adj))
    (edited_prices['High']*upside).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='red',width=short_width,ylim=(min_size_adj,max_size_adj))
    (edited_prices['High']*equal).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='black',width=short_width,ylim=(min_size_adj,max_size_adj))
    (edited_prices['Low']).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='white',width=short_width,ylim=(min_size_adj,max_size_adj))




def draw_candle_stick_chart_short_version(prices,axes):

    edited_prices = prices

    min_size_adj = edited_prices['Low'].min()*0.98
    max_size_adj = edited_prices['High'].max()*1.02
    downside = (edited_prices['Open_'] - edited_prices['Close_'] > 0)*1
    upside = (edited_prices['Open_'] - edited_prices['Close_'] < 0)*1
    equal = (edited_prices['Open_'] - edited_prices['Close_'] == 0)*1

    wide_width = 0.5
    short_width = 0.1

    (edited_prices['Open_']*downside).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='blue',width=wide_width,ylim=(min_size_adj,max_size_adj))
    (edited_prices['Close_']*downside).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='white',width=wide_width,ylim=(min_size_adj,max_size_adj))
    (edited_prices['Close_']*upside).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='red',width=wide_width,ylim=(min_size_adj,max_size_adj))
    (edited_prices['Open_']*upside).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='white',width=wide_width,ylim=(min_size_adj,max_size_adj))
    (edited_prices['Open_']*equal).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='black',width=wide_width,ylim=(min_size_adj,max_size_adj))
    ((edited_prices['Close_']*0.999)*equal).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='white',width=wide_width,ylim=(min_size_adj,max_size_adj))

    (edited_prices['High']*downside).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='blue',width=short_width,ylim=(min_size_adj,max_size_adj))
    (edited_prices['High']*upside).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='red',width=short_width,ylim=(min_size_adj,max_size_adj))
    (edited_prices['High']*equal).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='black',width=short_width,ylim=(min_size_adj,max_size_adj))
    (edited_prices['Low']).plot(ax=axes,kind='bar',legend = None,alpha = 1,color='white',width=short_width,ylim=(min_size_adj,max_size_adj))




def upper_time_scale_trading_graph(upscl_df_dict,axes,ax_column):

    edited_target_df = upscl_df_dict['Prices_For_Chart']
    edited_target_df = price_index_number_control_for_graph(prices=edited_target_df,upscl=True)
    edited_target_zeroline = upscl_df_dict['Zero_Line']
    edited_target_zeroline = price_index_number_control_for_graph(prices=edited_target_zeroline,upscl=True)

    upscl_prices_for_csc = edited_target_df
    upscl_prices_min_size_adj = upscl_prices_for_csc['Low'].min() * 0.9
    upscl_prices_max_size_adj = upscl_prices_for_csc['High'].max() * 1.1

    if upscl_prices_for_csc.index.name != None:
        del upscl_prices_for_csc.index.name

    axes[0,ax_column].set_title('Weekly Chart - Prices')
    draw_candle_stick_chart(prices=upscl_prices_for_csc,axes=axes[0,ax_column])
    upscl_prices_for_csc['EMA'].plot(ax=axes[0,ax_column],legend = 'best',alpha = 0.7,color='black',ylim=(upscl_prices_min_size_adj,upscl_prices_max_size_adj))
    upscl_prices_for_csc['Upper_mBollinger'].plot(ax=axes[0,ax_column],legend = 'best',alpha = 0.5,color='orange',ylim=(upscl_prices_min_size_adj,upscl_prices_max_size_adj))
    upscl_prices_for_csc['Lower_mBollinger'].plot(ax=axes[0,ax_column],legend = 'best',alpha = 0.5,color='green',ylim=(upscl_prices_min_size_adj,upscl_prices_max_size_adj))
    edited_target_zeroline['Zero_Line'].plot(ax=axes[0,ax_column],kind='bar',legend=None, alpha=1, color='black',lw=1)

    axes[1,ax_column].set_title('Weekly Chart - Volume')
    upscl_prices_for_csc['Volume'].plot(kind='bar', ax=axes[1,ax_column], legend='best', alpha=0.5, color='black')

    axes[2,ax_column].set_title('Weekly Chart - MACD')
    upscl_prices_for_csc['MACD_Fast'].plot(ax=axes[2,ax_column], legend=None, alpha=0.3, color='red')
    upscl_prices_for_csc['MACD_Slow'].plot(ax=axes[2,ax_column], legend=None, alpha=0.3, color='blue')
    ((upscl_prices_for_csc['MACD_Wall']*int(upscl_prices_for_csc['MACD_Histogram'].max()*2))).plot(ax=axes[2,ax_column], kind='bar', legend=None, alpha=0.2, color='black')
    upscl_prices_for_csc['MACD_Histogram'].plot(ax=axes[2,ax_column], kind='bar', legend=None, alpha=0.6, color='black')
    edited_target_zeroline['Zero_Line'].plot(ax=axes[2,ax_column], legend=None, alpha=1, color='black',lw=1)

    axes[3,ax_column].set_title('Weekly Chart - Force Index Ratio')
    upscl_prices_for_csc['Force_Index_Ratio'].plot(kind='bar', ax=axes[3,ax_column], legend='best', alpha=0.5, color='purple')

    for axn in range(len(axes)):

        axes[axn,ax_column].xaxis.set_major_locator(plt.MaxNLocator(int(len(upscl_prices_for_csc)/2)))
        axes[axn,ax_column].grid(color='black', linestyle='dashed', linewidth=0.3, alpha=0.2)
        axes[axn,ax_column].set_xticklabels([])
        if axn == (len(axes)-1):
            axes[axn,ax_column].set_xticklabels(list(upscl_prices_for_csc.index[0::2]), rotation=30,fontsize=6)

    return None

def major_time_scale_trading_graph_long_period(major_df_dict,axes,ax_column):

    edited_target_df = major_df_dict['Prices_For_Chart']
    edited_target_df = price_index_number_control_for_graph(prices=edited_target_df,upscl=False)
    edited_target_zeroline = major_df_dict['Zero_Line']
    edited_target_zeroline = price_index_number_control_for_graph(prices=edited_target_zeroline,upscl=False)


    prices_for_csc = edited_target_df
    prices_min_size_adj = prices_for_csc['Low'].min() * 0.9
    prices_max_size_adj = prices_for_csc['High'].max() * 1.1

    if prices_for_csc.index.name != None:
        del prices_for_csc.index.name

    axes[0,ax_column].set_title('Daily Chart - Prices')
    draw_candle_stick_chart(prices=prices_for_csc,axes=axes[0,ax_column])
    prices_for_csc['EMA'].plot(ax=axes[0,ax_column],legend = 'best',alpha = 0.7,color='black',ylim=(prices_min_size_adj,prices_max_size_adj))
    prices_for_csc['Upper_mBollinger'].plot(ax=axes[0,ax_column],legend = 'best',alpha = 0.5,color='orange',ylim=(prices_min_size_adj,prices_max_size_adj))
    prices_for_csc['Lower_mBollinger'].plot(ax=axes[0,ax_column],legend = 'best',alpha = 0.5,color='green',ylim=(prices_min_size_adj,prices_max_size_adj))
    edited_target_zeroline['Zero_Line'].plot(ax=axes[0, ax_column], kind='bar', legend=None, alpha=1, color='black',lw=1)

    axes[1,ax_column].set_title('Daily Chart - Volume')
    prices_for_csc['Volume'].plot(kind='bar', ax=axes[1,ax_column], legend='best', alpha=0.5, color='black')

    axes[2,ax_column].set_title('Daily Chart - MACD')
    prices_for_csc['MACD_Fast'].plot(ax=axes[2,ax_column], legend=None, alpha=0.3, color='red')
    prices_for_csc['MACD_Slow'].plot(ax=axes[2,ax_column], legend=None, alpha=0.3, color='blue')
    ((prices_for_csc['MACD_Wall']*int(prices_for_csc['MACD_Histogram'].max()*2))).plot(ax=axes[2,ax_column], kind='bar', legend=None, alpha=0.2, color='black')
    prices_for_csc['MACD_Histogram'].plot(ax=axes[2,ax_column], kind='bar', legend=None, alpha=0.6, color='black')
    edited_target_zeroline['Zero_Line'].plot(ax=axes[2,ax_column], legend=None, alpha=1, color='black',lw=1)

    axes[3,ax_column].set_title('Daily Chart - Force Index Ratio')
    prices_for_csc['Force_Index_Ratio'].plot(kind='bar', ax=axes[3,ax_column], legend='best', alpha=0.5, color='purple')


    for axn in range(len(axes)):

        axes[axn,ax_column].xaxis.set_major_locator(plt.MaxNLocator(int(len(prices_for_csc)/3)))
        axes[axn,ax_column].grid(color='black', linestyle='dashed', linewidth=0.3, alpha=0.2)
        axes[axn,ax_column].set_xticklabels([])
        if axn == (len(axes)-1):
            axes[axn,ax_column].set_xticklabels(list(prices_for_csc.index[::3]), rotation=30,fontsize=6)

    return None


def major_time_scale_trading_graph_short_period_1st(major_df_dict, axes, ax_column, short_period):
    ## Graph 1 (mBollinger Band, Volume, MACD, Williams%R)

    prices_for_csc_sp = major_df_dict['Prices_For_Chart'].iloc[-short_period:]
    prices_sp_min_size_adj = prices_for_csc_sp['Low'].min() * 0.9
    prices_sp_max_size_adj = prices_for_csc_sp['High'].max() * 1.1

    if prices_for_csc_sp.index.name != None:
        del prices_for_csc_sp.index.name

    zero_line_sp = pd.DataFrame(data=np.zeros(prices_for_csc_sp.shape[0]), index=list(prices_for_csc_sp.index),columns=['Zero_Line'])


    axes[0, ax_column].set_title('Daily Chart1 (Short Period) - Prices')
    draw_candle_stick_chart_short_version(prices=prices_for_csc_sp, axes=axes[0, ax_column])
    prices_for_csc_sp['EMA'].plot(ax=axes[0, ax_column], legend=None, alpha=0.7, color='black',ylim=(prices_sp_min_size_adj, prices_sp_max_size_adj))
    prices_for_csc_sp['Upper_mBollinger'].plot(ax=axes[0, ax_column], legend=None, alpha=0.5, color='orange',ylim=(prices_sp_min_size_adj, prices_sp_max_size_adj))
    prices_for_csc_sp['Lower_mBollinger'].plot(ax=axes[0, ax_column], legend=None, alpha=0.5, color='green',ylim=(prices_sp_min_size_adj, prices_sp_max_size_adj))
    zero_line_sp['Zero_Line'].plot(ax=axes[0, ax_column], kind='bar',legend=None, alpha=1, color='black', lw=0.5)

    axes[1, ax_column].set_title('Daily Chart1 (Short Period) - Volume')
    prices_for_csc_sp['Volume'].plot(kind='bar', ax=axes[1, 0], legend=None, alpha=0.5, color='black')

    axes[2, ax_column].set_title('Daily Chart1 (Short Period) - MACD')
    prices_for_csc_sp['MACD_Fast'].plot(ax=axes[2, ax_column], legend=None, alpha=0.3, color='red')
    prices_for_csc_sp['MACD_Slow'].plot(ax=axes[2, ax_column], legend=None, alpha=0.3, color='blue')
    ((prices_for_csc_sp['MACD_Wall'] * int(prices_for_csc_sp['MACD_Histogram'].max() * 2))).plot(ax=axes[2, ax_column],kind='bar',legend=None,alpha=0.2,color='black')
    prices_for_csc_sp['MACD_Histogram'].plot(ax=axes[2, ax_column], kind='bar', legend=None, alpha=0.6, color='black')
    zero_line_sp['Zero_Line'].plot(ax=axes[2, ax_column], legend=None, alpha=1, color='black', lw=1)

    axes[3, ax_column].set_title('Daily Chart1 (Short Period) - Williams%R')
    prices_for_csc_sp['Williams_R'].plot(ax=axes[3, ax_column], legend=None, alpha=1, color='pink')
    (zero_line_sp['Zero_Line'] - 90).plot(ax=axes[3, ax_column], legend=None, alpha=1, color='black', lw=1)
    (zero_line_sp['Zero_Line'] - 10).plot(ax=axes[3, ax_column], legend=None, alpha=1, color='black', lw=1)
    (zero_line_sp['Zero_Line']).plot(ax=axes[3, ax_column], kind='bar', legend=None, alpha=1, color='black', lw=1)

    for axn in range(len(axes)):

        axes[axn, ax_column].xaxis.set_major_locator(plt.MaxNLocator(int(len(prices_for_csc_sp))))
        axes[axn, ax_column].grid(color='black', linestyle='dashed', linewidth=0.3, alpha=0.2)
        axes[axn, ax_column].set_xticklabels([])
        if axn == (len(axes) - 1):
            axes[axn, ax_column].set_xticklabels(list(prices_for_csc_sp.index[::1]), rotation=30, fontsize=6)

    return None


def major_time_scale_trading_graph_short_period_2nd(major_df_dict, axes, ax_column, short_period):
    ## Graph 2 (Loss/Gain Cut Level, Force Index, Elder-Ray)

    prices_for_csc_sp = major_df_dict['Prices_For_Chart'].iloc[-short_period:]
    prices_sp_min_size_adj = prices_for_csc_sp['Low'].min() * 0.9
    prices_sp_max_size_adj = prices_for_csc_sp['High'].max() * 1.1

    if prices_for_csc_sp.index.name != None:
        del prices_for_csc_sp.index.name

    zero_line_sp = pd.DataFrame(data=np.zeros(prices_for_csc_sp.shape[0]), index=list(prices_for_csc_sp.index),
                                columns=['Zero_Line'])

    axes[0, ax_column].set_title('Daily Chart2 (Short Period) - Prices')
    draw_candle_stick_chart_short_version(prices=prices_for_csc_sp, axes=axes[0, ax_column])
    prices_for_csc_sp['EMA'].plot(ax=axes[0, ax_column], legend=None, alpha=0.7, color='black',ylim=(prices_sp_min_size_adj, prices_sp_max_size_adj))
    prices_for_csc_sp['Upper_mBollinger'].plot(ax=axes[0, ax_column], legend=None, alpha=0.5, color='orange',ylim=(prices_sp_min_size_adj, prices_sp_max_size_adj))
    prices_for_csc_sp['Lower_mBollinger'].plot(ax=axes[0, ax_column], legend=None, alpha=0.5, color='green',ylim=(prices_sp_min_size_adj, prices_sp_max_size_adj))
    zero_line_sp['Zero_Line'].plot(ax=axes[0, ax_column], kind='bar', legend=None, alpha=1, color='black', lw=1)

    axes[1, ax_column].set_title('Daily Chart2 (Short Period) - Force Index')
    prices_for_csc_sp['Force_Index_Norm'].plot(kind='bar', ax=axes[1, ax_column], legend='best', alpha=0.5,color='black')
    zero_line_sp['Zero_Line'].plot(ax=axes[1, ax_column], legend='best', alpha=1, color='black', lw=1)

    axes[2, ax_column].set_title('Daily Chart2 (Short Period) - Elder-Ray-Buy')
    prices_for_csc_sp['Buy_Elder_Ray'].plot(ax=axes[2, ax_column], kind='bar', legend='best', alpha=0.5, color='red')
    zero_line_sp['Zero_Line'].plot(ax=axes[2, ax_column], legend=None, alpha=1, color='black', lw=1)

    axes[3, ax_column].set_title('Daily Chart2 (Short Period) - Elder-Ray-Sell')
    prices_for_csc_sp['Sell_Elder_Ray'].plot(ax=axes[3, ax_column], kind='bar', legend='best', alpha=0.5, color='Blue')
    zero_line_sp['Zero_Line'].plot(ax=axes[3, ax_column], legend=None, alpha=1, color='black', lw=1)

    for axn in range(len(axes)):

        axes[axn, ax_column].xaxis.set_major_locator(plt.MaxNLocator(int(len(prices_for_csc_sp))))
        axes[axn, ax_column].grid(color='black', linestyle='dashed', linewidth=0.3, alpha=0.2)
        axes[axn, ax_column].set_xticklabels([])
        if axn == (len(axes) - 1):
            axes[axn, ax_column].set_xticklabels(list(prices_for_csc_sp.index[::1]), rotation=30, fontsize=6)

    return None

## 트레이딩 실험박스
## from wecolib.Curvelib_simulation_box import *