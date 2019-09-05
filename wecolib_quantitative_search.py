## 패턴인식 스크리너
from wecolib.wecolib_pattern_recognition_recipe import *

class quantitative_search():

    def set_variables(self,mpcores, mode, country, asset_type, func, start_date, end_date):
        self.multiprocessing_cores = mpcores
        self.mode = mode
        self.func = func
        self.country = country
        self.asset_type = asset_type
        self.start_date = start_date
        self.end_date = end_date

        if self.mode == 'Longi':
            self.ultimate_start_date = '1990-01-01'
            self.recent = False
        elif self.mode == 'Cross':
            self.ultimate_start_date = datetime.strptime(self.end_date,'%Y-%m-%d') + relativedelta(years=-3)
            self.recent = True
        else:
            print('모드를 올바르게 입력하세요.')


        if os.cpu_count() < mpcores:
            self.multiprocessing_cores = os.cpu_count()

        ## Working Variables

        self.saving_tbl_name = 'Plan_%s_%s_%s' % (self.country, self.asset_type, self.func.__name__)
        self.saving_db_name = 'Real_Analysis'
        self.sv_data_columns = ['Open_', 'High', 'Low', 'Close_', 'Volume', 'DA1_Open_', 'DA1_High', 'DA1_Low',
                                'DA1_Close_', 'Next_Open_', 'Next_High', 'Next_Low', 'Next_Close_', 'Volume_Trend',
                                'Volume_MA3', 'Volume_MA5', 'Volume_MA20', 'Trd_Amount', 'Trd_Amount_Trend',
                                'EMA','EMA_Trend1','EMA_Trend2', 'EMA_Trend5', 'EMA_Trend10', 'EMA_Trend20', 'EMA_Trend60', 'EMA_Trend120',
                                'Upper_Bollinger', 'Lower_Bollinger', 'Avg_Width_Bollinger',
                                'Upper_mBollinger', 'Lower_mBollinger', 'Avg_Width_mBollinger',
                                'MACD_Fast', 'MACD_Slow', 'MACD_Histogram', 'MACD_Histogram_Trend']

        self.for_sql_columns = ['Open_', 'High', 'Low', 'Close_', 'Volume']
        self.create_tbl_sql_columns = ''
        for str_frag in [', ' + x + ' float' for x in self.sv_data_columns]:
            self.create_tbl_sql_columns += str_frag
        self.empty_result_df = pd.DataFrame(columns=['Date_', 'Ticker', 'Name_'] + self.sv_data_columns)


    ###########################################################################
    ##                      전 종목 Tickers Recipe 검색
    ###########################################################################

    def quantitative_search_main(self):

        print('Main Process : {}'.format(os.getpid(),))

        try:
            existing_max_date = read_sql_table("SELECT TOP 1 Date_ FROM {}.dbo.{} ORDER BY Date_ DESC".format(self.saving_db_name,self.saving_tbl_name)).iloc[0, 0]
            self.start_date = (datetime.strptime(existing_max_date,'%Y-%m-%d') + timedelta(1)).strftime('%Y-%m-%d')
            if self.start_date > self.end_date:
                print('All the works were inserted.')
                return self.empty_result_df
        except:
            try:
                transmit_str_to_sql('CREATE TABLE {}.dbo.{} (Date_ date, Ticker varchar(30),Name_ varchar(30){})'.format(self.saving_db_name,self.saving_tbl_name,self.create_tbl_sql_columns))
            except:
                pass

        self.tickers = download_ticker_data(self.country, self.asset_type, self.start_date, self.end_date)
        ticker_list = np.array_split(self.tickers, self.multiprocessing_cores)

        procs = list()

        for mc in range(self.multiprocessing_cores):
            if len(ticker_list[mc]) == 0:
                continue
            proc = Process(target=self.quantitative_search_async_loop_function, args=(ticker_list[mc],))
            procs.append(proc)
            proc.start()

        for proc in procs:
            proc.join()
            proc.terminate()

        print('All Works done')

        return None

    ###########################################################################
    ##                      전 종목 Tickers Recipe 검색
    ###########################################################################

    def quantitative_search_async_loop_function(self,tickers,):
        print('Process : {}'.format(os.getpid(),))
        loop = asyncio.get_event_loop()
        result_df = loop.run_until_complete(self.saving_tickers_plan_collection(tickers,))
        insert_data_into_sql_Table(df=result_df, TBL=self.saving_tbl_name, DB_Name=self.saving_db_name)
        loop.close()


    async def saving_tickers_plan_collection(self,tickers):

        futures = [asyncio.ensure_future(self.quantitative_search_with_longitudinal_section(ticker)) for ticker in tickers['Ticker']]
        result_df = self.empty_result_df
        for f in asyncio.as_completed(futures):
            result_frag = (await f)
            result_df = result_df.append(result_frag)

        if len(result_df)==0:
            return result_df
        else :
            if ((result_df['Date_'].max()).strftime('%Y-%m-%d') >= self.start_date):
                return result_df[result_df['Date_'] >= datetime.strptime(self.start_date,'%Y-%m-%d')].sort_values(by=['Date_', 'Ticker'],ascending=True).reset_index(drop=True)
            else:
                return self.empty_result_df

    ##===========================================================================
    ##                      Quantitative Search Basic
    ##===========================================================================

    async def quantitative_search_with_longitudinal_section(self, ticker):

        ## Variable 설정

        prices = download_price_data(self.country, self.asset_type, ticker,self.ultimate_start_date, self.end_date)
        if len(prices) == 0:
            return self.empty_result_df
        prices = add_on_technical_indicators(df=prices, window=20, price_type='Close_')

        ## 패턴 확인

        recipe_pattern_existance = self.func(df=prices, recent=self.recent)
        if len(recipe_pattern_existance) > 0:
            recipe_pattern_existance = recipe_pattern_existance.copy()
            recipe_pattern_existance['Ticker'] = ticker
            ticker_info_frag = get_current_name_of_ticker_data(country=self.country, asset_type=self.asset_type,ticker=ticker)
            recipe_pattern_existance['Name_'] = ticker_info_frag['Name_']
            recipe_pattern_existance.reset_index(inplace=True)
            recipe_pattern_existance = recipe_pattern_existance[['Date_', 'Ticker', 'Name_'] + self.sv_data_columns]
            return recipe_pattern_existance
        else:
            return self.empty_result_df




## 트레이딩 스코어 계산
## from wecolib.Curvelib_score_evaluation import *