## 패턴인식 기본
from wecolib.wecolib_pattern_recognition_basic import *

###########################################################################
##                     Executable Recipe
###########################################################################

## 패턴 예시

def example_pattern_recipe(df, recent=True):

    """
    검색할 패턴 함수 :
    조건 (1) 검색당일 종가가 전일고가보다 높음
    조건 (2) 검색 당일 종가가 당일 시가보다 높은 양봉패턴
    조건 (3) 검색 당일 거래량이 전일 하루 거래량의 3배 이상
    """

    # 패턴에 필요한 팩터들 따로 정의하기 (따로 정의하지 않고 조건 설정시 직접 df['~~']로 써서 사용해도 됨)

    high = df['High']
    low = df['Low']
    close = df['Close_']
    open = df['Open_']

    # 수정주가 데이터가 아니므로 급격한 이벤트 발생하여 의미없는 데이터가 저장되어 있을 경우 (감자, 증자, 거래정지기간 등) 종목 검색에서 아예 제외하는 조건

    normal_data_cond = (df['High'] != 0) & (df['DA1_High'] != 0) & (df['Next_High'] != 0)

    # 원하는 패턴 조건을 설정

    cond1 = (df['DA1_High'] < close)
    cond2 = (open < close)
    cond3 = (2*df['Volume'].shift(1) <= df['Volume'])

    # 조건 통합 : 최종 검색 패턴 완성

    searching_cond = normal_data_cond & cond1 & cond2 & cond3

    #==================== 아래는 Library에서 사용하는 형식이니 Copy & Paste =========================

    result_df = df[searching_cond]

    if len(result_df) == 0:
        final_result = pd.DataFrame(columns=result_df.columns)
    else:
        final_result = result_df
        if recent == True:
            recent_date = df.index[-1]
            final_result = result_df[result_df.index == recent_date]

    return final_result


## 패턴의 퀀트적 검색
## from wecolib.Curvelib_quantitative_search import *