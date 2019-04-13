## 트레이딩 실험박스
from wecolib.wecolib_simulation_box import *

## 새 진입 계획 작성

class real_trading_plan_new_entry():

    def set_variables(self, func, country, asset_type, searching_date, n_days_after=1):

        ## Variable

        self.inserting_db_name = 'Real_Trading'
        self.inserting_db_tbl = 'RealTrd_Trading_Plan'
        self.inserting_plan_columns = ['Trading_Date_', 'Country', 'Asset_Type', 'Market', 'Ticker', 'Name_',
                                       'Initial_Trd_Plan', 'Trading_Plan', 'Strategy', 'Searching_Date_','SE_Mode',
                                       'Ent_Days', 'Max_Ent_Days', 'Trd_Days', 'Max_Trd_Days', 'Trd_TC_Var', 'NumShrs',
                                       'Ent_Mode', 'Ent_Var', 'Ent_Coef','Planned_Ent_Price', 'Ent_Req', 'Ent_Req_Val',
                                       'LC_Mode', 'LC_Var', 'LC_Coef', 'Planned_LC_Price', 'Loss_Cut_Pct', 'LC_Req', 'LC_Req_Val', 'LC_Upside_Only',
                                       'GC_Mode', 'GC_Var', 'GC_Coef', 'Planned_GC_Price', 'Gain_Cut_Pct', 'GC_Req', 'GC_Req_Val',
                                       'CGC_Mode', 'CGC_Var', 'CGC_Days','CLC_Mode','CLC_Var','CLC_Days',
                                       'FC_Mode', 'FC_Var', 'FC_Req','FC_Req_Val','FC_Exec','Completion',
                                       'R_Value', 'R_Multiple','Ret','Net_Ret','Ent_Date_','Ent_Price',
                                       'Ex_Date_','Ex_Price','Ex_Type','Buy_Slippage','Sell_Slippage',
                                       'MDD','MDU','Ent_Score','Ex_Score','Trd_Score','Total_Score','Trd_Result']

        self.func = func
        self.country = country
        self.asset_type = asset_type

        self.searching_date = searching_date
        self.trading_date = (datetime.strptime(self.searching_date,'%Y-%m-%d') + timedelta(days=n_days_after)).strftime('%Y-%m-%d')


        self.pda_date_diff = 800
        self.pda_window = 20
        self.pda_price_type = 'Close_'
        self.pda_start_date = (datetime.strptime(self.searching_date,'%Y-%m-%d') + timedelta(days=self.pda_date_diff*(-1))).strftime('%Y-%m-%d')
        self.price_analysis_da1_date = (datetime.strptime(self.searching_date,'%Y-%m-%d') + timedelta(days=-1)).strftime('%Y-%m-%d')

    def input_settings(self,position_size_input, fee_input, tc_input, ent_input, lc_input, gc_input,cgc_input,clc_input,fc_input):

        ## position size input

        self.position_size_model = position_size_input[0]
        self.risk_size = position_size_input[1]

        ## fee input

        self.trd_fee_pct = fee_input[0] + fee_input[1]

        ## tc input

        self.ent_time_cut = tc_input[1]
        self.trd_time_cut = tc_input[2]
        self.se_mode = tc_input[0]
        if self.se_mode == 'STET':
            self.trading_date = self.searching_date
            self.ent_time_cut = 0

        self.max_time_cut = self.ent_time_cut + self.trd_time_cut
        self.trd_time_cut_var = tc_input[3]

        ## ent input

        self.ent_plan_func_mode = ent_input[0]
        self.ent_plan_func_var = ent_input[1]
        self.ent_plan_func_coef = ent_input[2]
        self.ent_plan_func_req = ent_input[3]

        ## lc input

        self.lc_plan_func_mode = lc_input[0]
        self.lc_plan_func_var = lc_input[1]
        self.lc_plan_func_coef = lc_input[2]
        self.lc_plan_func_req = lc_input[3]
        self.lc_plan_func_upside_only = lc_input[4]*1

        ## gc input

        self.gc_plan_func_mode = gc_input[0]
        self.gc_plan_func_var = gc_input[1]
        self.gc_plan_func_coef = gc_input[2]
        self.gc_plan_func_req = gc_input[3]

        ## cgc input

        self.cgc_plan_func_mode = cgc_input[0]
        self.cgc_plan_func_var = cgc_input[1]
        self.cgc_plan_func_days = cgc_input[2]

        ## clc input

        self.clc_plan_func_mode = clc_input[0]
        self.clc_plan_func_var = clc_input[1]
        self.clc_plan_func_days = clc_input[2]

        ## fc input

        self.fc_plan_func_mode = fc_input[0]
        self.fc_plan_func_var = fc_input[1]
        self.fc_plan_func_req = fc_input[2]


    ## 포지션 사이즈 , 매매계획 세팅 컨트롤 타워 함수

    def control_tower_of_position_size_functions(self):
        dict = {'CPR':self.set_position_size_cpr_model_func}
        self.position_size_func = dict[self.position_size_model]

    def set_position_size_cpr_model_func(self,risk_size,ent_price,lc_price):
        try:
            units = int(risk_size / (ent_price - lc_price + ent_price * self.trd_fee_pct))
        except:
            units = np.nan
        return units

    ###########################################################################
    ##                     SYET Mode (당일 검색, 익일 진입)
    ###########################################################################

    ## Searching Plan 불러오기

    def load_basic_plan(self):
        self.basic_plan_sql = "SELECT * FROM Real_Analysis.dbo.Plan_%s_%s_%s WHERE Date_ = '%s'" % (self.country, self.asset_type, self.func.__name__, self.searching_date)
        self.basic_plan = read_sql_table(self.basic_plan_sql)

    ## 가격 다운로드

    def download_prices_for_real_trading(self, ticker):

        prices = download_price_data(country=self.country, asset_type=self.asset_type, ticker=ticker, start_date=self.pda_start_date,end_date=self.searching_date, time_period='D')
        prices = add_on_technical_indicators(df=prices, window=self.pda_window, price_type=self.pda_price_type)

        return prices

    def generate_trading_plan_df_syet(self):
        result_list = list()
        for inx, row in self.basic_plan.iterrows():
            trading_date = self.trading_date
            country = self.country
            asset_type = self.asset_type

            ticker_info = get_current_name_of_ticker_data(country=country, asset_type=asset_type, ticker=row['Ticker'])

            market = ticker_info['Market']
            ticker = row['Ticker']
            name = ticker_info['Name_']

            initial_trading_plan = 'Entry'
            trading_plan = 'Entry'

            strategy = self.func.__name__

            searching_date = self.searching_date

            se_mode = self.se_mode
            ent_days = 1
            trd_days = 0
            max_ent_days = self.ent_time_cut
            max_trd_days = self.trd_time_cut
            trd_tc_var = self.trd_time_cut_var

            prices = self.download_prices_for_real_trading(ticker=row['Ticker'])
            last_date_of_prices = prices.index[-1].strftime('%Y-%m-%d')
            if last_date_of_prices != self.searching_date:
                print('%s / %s / %s / %s / No Price Data of Searching Date (%s) !' % (
                country, asset_type, ticker, name, searching_date))
                continue



            ent_mode = self.ent_plan_func_mode
            ent_var = self.ent_plan_func_var
            ent_coef = self.ent_plan_func_coef
            ent_req = self.ent_plan_func_req[0]
            ent_req_val =  self.ent_plan_func_req[1]

            lc_mode = self.lc_plan_func_mode
            lc_var = self.lc_plan_func_var
            lc_coef = self.lc_plan_func_coef
            lc_req = self.lc_plan_func_req[0]
            lc_req_val =  self.lc_plan_func_req[1]
            lc_upside_only = self.lc_plan_func_upside_only

            gc_mode = self.gc_plan_func_mode
            gc_var = self.gc_plan_func_var
            gc_coef = self.gc_plan_func_coef
            gc_req = self.gc_plan_func_req[0]
            gc_req_val = self.gc_plan_func_req[1]


            planned_ent_price = round((prices[ent_var].iloc[-1]) * ent_coef,0)
            planned_lc_price = round((prices[lc_var].iloc[-1]) * lc_coef,0)
            planned_gc_price = round((prices[gc_var].iloc[-1]) * gc_coef,0)

            if self.lc_plan_func_var == 'Ent_Price':
                planned_lc_price = round(planned_ent_price * self.lc_plan_func_coef, 0)
            if self.gc_plan_func_var == 'Ent_Price':
                planned_gc_price = round(planned_ent_price * self.gc_plan_func_coef, 0)


            numshrs = self.position_size_func(risk_size=self.risk_size, ent_price=planned_ent_price, lc_price=planned_lc_price)


            loss_cut_pct = round(((planned_lc_price - planned_ent_price) / planned_ent_price) - self.trd_fee_pct,2)
            gain_cut_pct = round(((planned_gc_price - planned_ent_price) / planned_ent_price) - self.trd_fee_pct,2)

            cgc_mode = self.cgc_plan_func_mode
            cgc_var = self.cgc_plan_func_var
            cgc_days = self.cgc_plan_func_days

            clc_mode = self.clc_plan_func_mode
            clc_var = self.clc_plan_func_var
            clc_days = self.clc_plan_func_days

            fc_mode = self.fc_plan_func_mode
            fc_var = self.fc_plan_func_var
            fc_req = self.fc_plan_func_req[0]
            fc_req_val = self.fc_plan_func_req[1]
            fc_exec = None



            completion = 'Ready'

            r_value = self.risk_size

            ## 실제 트레이딩 결과 관련

            r_multiple = np.nan
            ret = np.nan
            net_ret = np.nan

            ent_date = None
            ex_date = None

            ent_price = np.nan
            ex_price = np.nan

            ex_type = None

            buy_slippage = np.nan
            sell_slippage = np.nan
            mdd = np.nan
            mdu = np.nan
            ent_score = np.nan
            ex_score = np.nan
            trd_score = np.nan
            total_score = np.nan
            trd_result = np.nan

            result_frag = [trading_date, country, asset_type, market, ticker, name,
                           initial_trading_plan, trading_plan, strategy, searching_date, se_mode,
                           ent_days, max_ent_days, trd_days, max_trd_days, trd_tc_var, numshrs,
                           ent_mode, ent_var, ent_coef, planned_ent_price, ent_req, ent_req_val,
                           lc_mode, lc_var, lc_coef, planned_lc_price, loss_cut_pct, lc_req, lc_req_val, lc_upside_only,
                           gc_mode, gc_var, gc_coef, planned_gc_price, gain_cut_pct, gc_req, gc_req_val,
                           cgc_mode, cgc_var, cgc_days, clc_mode, clc_var, clc_days,
                           fc_mode, fc_var, fc_req, fc_req_val,fc_exec, completion,
                           r_value, r_multiple, ret, net_ret, ent_date, ent_price,
                           ex_date,ex_price, ex_type,buy_slippage,sell_slippage,
                           mdd,mdu, ent_score, ex_score, trd_score, total_score,trd_result]
            result_list.append(result_frag)

        if len(result_list)==0:
            self.plan_df = pd.DataFrame(columns=self.inserting_plan_columns)
        else:
            self.plan_df = pd.DataFrame(result_list)
            self.plan_df.columns = self.inserting_plan_columns

    ###########################################################################
    ##                     STET Mode (당일 검색, 당일 진입)
    ###########################################################################

    def load_basic_price_df_for_stet_mode(self):

        key = '%s-%s' % (self.country, self.asset_type)
        sql_dict = {
            'KOR-Index': "SELECT Date_, Ticker, Open_, High, Low, Close_, Volume FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Date_ BETWEEN '%s' AND '%s'" % (
            self.pda_start_date, self.price_analysis_da1_date),
            'KOR-Stock': "SELECT Date_, Ticker, Open_, High, Low, Close_, Volume FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX WHERE Date_ BETWEEN '%s' AND '%s'" % (
            self.pda_start_date, self.price_analysis_da1_date),
            'KOR-ETF': "SELECT Date_, Ticker, Open_, High, Low, Close_, Volume FROM KOR_Price_Data.dbo.KOR_ETFPriceDataFromNF WHERE Date_ BETWEEN '%s' AND '%s'" % (
            self.pda_start_date, self.price_analysis_da1_date),
            'GLOB-Index': "SELECT Date_, Ticker, Open_, High, Low, Close_, Volume FROM GLOB_Price_Data.dbo.GLOB_IndexPriceDataFromIV WHERE Date_ BETWEEN '%s' AND '%s'" % (
            self.pda_start_date, self.price_analysis_da1_date),
            'GLOB-IndexFutures': "SELECT Date_, Ticker, Open_, High, Low, Close_, Volume FROM GLOB_Price_Data.dbo.GLOB_IndexFuturesPriceDataFromIV WHERE Date_ BETWEEN '%s' AND '%s'" % (
            self.pda_start_date, self.price_analysis_da1_date),
            'GLOB-FxFutures': "SELECT Date_, Ticker, Open_, High, Low, Close_, Volume FROM GLOB_Price_Data.dbo.GLOB_FxFuturesPriceDataFromIV WHERE Date_ BETWEEN '%s' AND '%s'" % (
            self.pda_start_date, self.price_analysis_da1_date),
            'GLOB-FxRate': "SELECT Date_, Ticker, Open_, High, Low, Close_, Volume FROM GLOB_Price_Data.dbo.GLOB_FxRateDataFromIV WHERE Date_ BETWEEN '%s' AND '%s'" % (
            self.pda_start_date, self.price_analysis_da1_date),
            'GLOB-Commodities': "SELECT Date_, Ticker, Open_, High, Low, Close_, Volume FROM GLOB_Price_Data.dbo.GLOB_CommoditiesPriceDataFromIV WHERE Date_ BETWEEN '%s' AND '%s'" % (
            self.pda_start_date, self.price_analysis_da1_date),
            'KOR-MajorIndex': "SELECT Date_, Ticker, Open_, High, Low, Close_, Volume FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Date_ BETWEEN '%s' AND '%s'" % (
            self.pda_start_date, self.price_analysis_da1_date),
            'KOR-KOSPI': "SELECT Date_, Ticker, Open_, High, Low, Close_, Volume FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Date_ BETWEEN '%s' AND '%s'" % (
            self.pda_start_date, self.price_analysis_da1_date),
            'KOR-KOSDAQ': "SELECT Date_, Ticker, Open_, High, Low, Close_, Volume FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Date_ BETWEEN '%s' AND '%s'" % (
            self.pda_start_date, self.price_analysis_da1_date),
            'KOR-KSStock': "SELECT Date_, Ticker, Open_, High, Low, Close_, Volume FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX WHERE Date_ BETWEEN '%s' AND '%s'" % (
            self.pda_start_date, self.price_analysis_da1_date),
            'KOR-KQStock': "SELECT Date_, Ticker, Open_, High, Low, Close_, Volume FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX WHERE Date_ BETWEEN '%s' AND '%s'" % (
            self.pda_start_date, self.price_analysis_da1_date),
        }

        self.basic_price_df = read_sql_table(sql=sql_dict[key])
        # self.basic_price_df = self.basic_price_df.set_index(keys=['Date_'], drop=True)
        # self.basic_price_df.index = pd.to_datetime(self.basic_price_df.index)
        self.basic_price_df = self.basic_price_df.sort_values(by=['Ticker','Date_']).reset_index(drop=True)

    def generate_trading_plan_df_stet(self):

        self.basic_price_columns = ['Open_','High','Low','Close_','Volume']
        self.empty_result_df = pd.DataFrame(columns=self.inserting_plan_columns)
        self.recent_ticker_start_date = (datetime.strptime(self.searching_date,'%Y-%m-%d') + timedelta(days=-10)).strftime('%Y-%m-%d')
        self.multiprocessing_cores = os.cpu_count()-1


        self.tickers = download_ticker_data(self.country, self.asset_type, self.recent_ticker_start_date, self.searching_date)
        ticker_list = np.array_split(self.tickers, self.multiprocessing_cores)

        self.result_queue = Queue()
        procs = list()

        for mc in range(self.multiprocessing_cores):
            if len(ticker_list[mc]) == 0:
                continue
            proc = Process(target=self.quantitative_search_async_loop_function, args=(ticker_list[mc],self.result_queue))
            procs.append(proc)
            proc.start()

        self.result_list = [self.result_queue.get() for p in range(len(procs))]

        for proc in procs:
            proc.join()
            proc.terminate()

        self.result_queue.close()
        self.result_queue.join_thread()

        self.plan_df = self.empty_result_df
        for result_frag in self.result_list:
            self.plan_df = self.plan_df.append(result_frag)

        self.plan_df = self.plan_df.reset_index(drop=True)

        print('All Works done')

    def quantitative_search_async_loop_function(self,tickers,result_queue):
        print('Process : {}'.format(os.getpid(),))
        loop = asyncio.get_event_loop()
        result_df = loop.run_until_complete(self.saving_tickers_plan_collection(tickers,))
        result_queue.put(result_df)
        loop.close()

    async def saving_tickers_plan_collection(self,tickers):

        futures = [asyncio.ensure_future(self.exec_investigation_for_single_ticker(ticker)) for ticker in tickers['Ticker']]
        result_df = self.empty_result_df
        for f in asyncio.as_completed(futures):
            result_frag = (await f)
            result_df = result_df.append(result_frag)

        return result_df


    async def exec_investigation_for_single_ticker(self,ticker):
        try:
            ticker_cur_price_df = get_current_price_state_of_ticker(ticker = ticker).set_index(keys=['Date_'], drop=True)[self.basic_price_columns]
        except:
            return self.empty_result_df

        ticker_price_df = self.basic_price_df[self.basic_price_df['Ticker']==ticker].set_index(keys=['Date_'], drop=True)[self.basic_price_columns]

        ticker_price_df = ticker_price_df.append(ticker_cur_price_df)
        ticker_price_df = add_on_technical_indicators(df=ticker_price_df)
        pattern_existancy = self.func(df=ticker_price_df,recent=True)
        if len(pattern_existancy) > 0:
            single_ticker_plan_df = self.single_ticker_plan_data(ticker=ticker,price_df=ticker_price_df)
            return single_ticker_plan_df
        else:
            return self.empty_result_df

    def single_ticker_plan_data(self,ticker,price_df):
        trading_date = self.trading_date
        country = self.country
        asset_type = self.asset_type

        ticker_info = get_current_name_of_ticker_data(country=country, asset_type=asset_type, ticker=ticker)

        market = ticker_info['Market']
        name = ticker_info['Name_']

        initial_trading_plan = 'Entry'
        trading_plan = 'Entry'

        strategy = self.func.__name__

        searching_date = self.searching_date

        se_mode = self.se_mode
        ent_days = 0
        trd_days = 0
        max_ent_days = self.ent_time_cut
        max_trd_days = self.trd_time_cut
        trd_tc_var = self.trd_time_cut_var

        ent_mode = self.ent_plan_func_mode
        ent_var = self.ent_plan_func_var
        ent_coef = self.ent_plan_func_coef
        ent_req = self.ent_plan_func_req[0]
        ent_req_val = self.ent_plan_func_req[1]

        lc_mode = self.lc_plan_func_mode
        lc_var = self.lc_plan_func_var
        lc_coef = self.lc_plan_func_coef
        lc_req = self.lc_plan_func_req[0]
        lc_req_val = self.lc_plan_func_req[1]
        lc_upside_only = self.lc_plan_func_upside_only

        gc_mode = self.gc_plan_func_mode
        gc_var = self.gc_plan_func_var
        gc_coef = self.gc_plan_func_coef
        gc_req = self.gc_plan_func_req[0]
        gc_req_val = self.gc_plan_func_req[1]

        planned_ent_price = round((price_df[ent_var].iloc[-1]) * ent_coef, 0)
        planned_lc_price = round((price_df[lc_var].iloc[-1]) * lc_coef, 0)
        planned_gc_price = round((price_df[gc_var].iloc[-1]) * gc_coef, 0)

        if self.lc_plan_func_var == 'Ent_Price':
            planned_lc_price = round(planned_ent_price * self.lc_plan_func_coef, 0)
        if self.gc_plan_func_var == 'Ent_Price':
            planned_gc_price = round(planned_ent_price * self.gc_plan_func_coef, 0)

        numshrs = self.position_size_func(risk_size=self.risk_size, ent_price=planned_ent_price,
                                          lc_price=planned_lc_price)

        loss_cut_pct = round(((planned_lc_price - planned_ent_price) / planned_ent_price) - self.trd_fee_pct, 2)
        gain_cut_pct = round(((planned_gc_price - planned_ent_price) / planned_ent_price) - self.trd_fee_pct, 2)

        cgc_mode = self.cgc_plan_func_mode
        cgc_var = self.cgc_plan_func_var
        cgc_days = self.cgc_plan_func_days

        clc_mode = self.clc_plan_func_mode
        clc_var = self.clc_plan_func_var
        clc_days = self.clc_plan_func_days

        fc_mode = self.fc_plan_func_mode
        fc_var = self.fc_plan_func_var
        fc_req = self.fc_plan_func_req[0]
        fc_req_val = self.fc_plan_func_req[1]
        fc_exec = None

        completion = 'Ready'

        r_value = self.risk_size

        ## 실제 트레이딩 결과 관련

        r_multiple = np.nan
        ret = np.nan
        net_ret = np.nan

        ent_date = None
        ex_date = None

        ent_price = np.nan
        ex_price = np.nan

        ex_type = None

        buy_slippage = np.nan
        sell_slippage = np.nan
        mdd = np.nan
        mdu = np.nan
        ent_score = np.nan
        ex_score = np.nan
        trd_score = np.nan
        total_score = np.nan
        trd_result = np.nan

        result_frag = [trading_date, country, asset_type, market, ticker, name,
                       initial_trading_plan, trading_plan, strategy, searching_date, se_mode,
                       ent_days, max_ent_days, trd_days, max_trd_days, trd_tc_var, numshrs,
                       ent_mode, ent_var, ent_coef, planned_ent_price, ent_req, ent_req_val,
                       lc_mode, lc_var, lc_coef, planned_lc_price, loss_cut_pct, lc_req, lc_req_val, lc_upside_only,
                       gc_mode, gc_var, gc_coef, planned_gc_price, gain_cut_pct, gc_req, gc_req_val,
                       cgc_mode, cgc_var, cgc_days, clc_mode, clc_var, clc_days,
                       fc_mode, fc_var, fc_req, fc_req_val, fc_exec, completion,
                       r_value, r_multiple, ret, net_ret, ent_date, ent_price,
                       ex_date, ex_price, ex_type, buy_slippage, sell_slippage,
                       mdd, mdu, ent_score, ex_score, trd_score, total_score, trd_result]

        return pd.DataFrame(data=[result_frag],columns=self.inserting_plan_columns)


    ###########################################################################
    ##                     Plan Generation & Insertion
    ###########################################################################

    def plan_generation(self):

        self.control_tower_of_position_size_functions()

        if self.se_mode == 'SYET':
            self.load_basic_plan()
            self.generate_trading_plan_df_syet()
        elif self.se_mode == 'STET':
            self.load_basic_price_df_for_stet_mode()
            self.generate_trading_plan_df_stet()


    def plan_insertion(self):
        insert_data_into_sql_Table(df=self.plan_df,TBL=self.inserting_db_tbl,DB_Name=self.inserting_db_name)

    ###########################################################################
    ##                     Plan Screening
    ###########################################################################

    def plan_screening_for_var_percentile(self,pct_var='Close_',percentile=(None, None)):

        ## 검색된 플랜과 실제 플랜 조인

        real_trd_plan_data_for_report = self.plan_df

        plan_sql = "SELECT Date_ AS Searching_Date_,* FROM Real_Analysis.dbo.Plan_%s_%s_%s WHERE Date_ = '%s'" % (self.country, self.asset_type, self.func.__name__, self.searching_date)
        plan_data_for_report = read_sql_table(sql=plan_sql)

        working_df1 = real_trd_plan_data_for_report.set_index(['Searching_Date_', 'Ticker', 'Name_'])
        working_df2 = plan_data_for_report.set_index(['Searching_Date_', 'Ticker', 'Name_'])
        working_df = pd.concat([working_df1, working_df2], axis=1, join_axes=[working_df1.index])
        working_df.reset_index(inplace=True)

        ## Percentile 기준가 Table 생성

        min_pct = percentile[0]
        max_pct = percentile[1]

        if percentile[0] == None:
            min_pct = 0
        if percentile[1] == None:
            max_pct = 1

        key = '%s-%s' % (self.country, self.asset_type)
        sql_for_pct_dict = {
            'KOR-Index': "SELECT DISTINCT Date_ ,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Date_ = '%s') A" % (
            min_pct, pct_var, max_pct, pct_var, self.searching_date),
            'KOR-Stock': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX WHERE Date_ = '%s') A" % (
            min_pct, pct_var, max_pct, pct_var, self.searching_date),
            'KOR-ETF': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM KOR_Price_Data.dbo.KOR_ETFPriceDataFromNF WHERE Date_ = '%s') A" % (
            min_pct, pct_var, max_pct, pct_var, self.searching_date),
            'GLOB-Index': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM GLOB_Price_Data.dbo.GLOB_IndexPriceDataFromIV WHERE Date_ = '%s') A" % (
            min_pct, pct_var, max_pct, pct_var, self.searching_date),
            'GLOB-IndexFutures': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM GLOB_Price_Data.dbo.GLOB_IndexFuturesPriceDataFromIV WHERE Date_ = '%s') A" % (
            min_pct, pct_var, max_pct, pct_var, self.searching_date),
            'GLOB-FxFutures': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM GLOB_Price_Data.dbo.GLOB_FxFuturesPriceDataFromIV WHERE Date_ = '%s') A" % (
            min_pct, pct_var, max_pct, pct_var, self.searching_date),
            'GLOB-FxRate': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM GLOB_Price_Data.dbo.GLOB_FxRateDataFromIV WHERE Date_ = '%s') A" % (
            min_pct, pct_var, max_pct, pct_var, self.searching_date),
            'GLOB-Commodities': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM GLOB_Price_Data.dbo.GLOB_CommoditiesPriceDataFromIV WHERE Date_ = '%s') A" % (
            min_pct, pct_var, max_pct, pct_var, self.searching_date),
            'KOR-MajorIndex': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM (SELECT * FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Ticker IN ('KOSPI','KOSDAQ지수'))B WHERE Date_ = '%s') A" % (
            min_pct, pct_var, max_pct, pct_var, self.searching_date),
            'KOR-KOSPI': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM (SELECT * FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Ticker = 'KOSPI')B WHERE Date_ = '%s') A" % (
            min_pct, pct_var, max_pct, pct_var, self.searching_date),
            'KOR-KOSDAQ': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM (SELECT * FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Ticker = 'KOSDAQ지수')B WHERE Date_ = '%s') A" % (
            min_pct, pct_var, max_pct, pct_var, self.searching_date)
        }

        pct_tbl = read_sql_table(sql_for_pct_dict[key])
        pct_tbl.columns = ['Searching_Date_','Min_Pct','Max_Pct']


        ## Percentile 기준가 Table 과 Working df 결합
        working_df = working_df.set_index(['Searching_Date_'])
        pct_tbl = pct_tbl.set_index(['Searching_Date_'])
        working_df = pd.concat([working_df, pct_tbl], axis=1, join_axes=[working_df.index])
        working_df.reset_index(inplace=True)


        ## Percentile 기준가로 가격 스크리닝

        working_df = working_df[(working_df[pct_var] >= working_df['Min_Pct']) & (working_df[pct_var] <= working_df['Max_Pct'])]
        working_df = working_df[self.plan_df.columns].reset_index(drop=True)
        working_df.columns = real_trd_plan_data_for_report.columns
        self.plan_df = working_df

        return None

    def plan_screening_for_var_range(self,range_var='Close_',range_min_max=(None,None)):


        ## 검색된 플랜과 실제 플랜 조인

        real_trd_plan_report = self.plan_df

        plan_sql = "SELECT Date_ AS Searching_Date_,* FROM Real_Analysis.dbo.Plan_%s_%s_%s WHERE Date_ = '%s'" % (self.country, self.asset_type, self.func.__name__,self.searching_date )
        plan_data_for_report = read_sql_table(sql=plan_sql)


        working_df1 = real_trd_plan_report.set_index(['Searching_Date_', 'Ticker', 'Name_'])
        working_df2 = plan_data_for_report.set_index(['Searching_Date_', 'Ticker', 'Name_'])
        working_df = pd.concat([working_df1, working_df2], axis=1, join_axes=[working_df1.index])
        working_df.reset_index(inplace=True)

        ## 가격 스크리닝

        min_var = range_min_max[0]
        max_var = range_min_max[1]

        if range_min_max[0] == None:
            min_var = 0
        if range_min_max[1] == None:
            max_var = working_df[range_var].max() * 10000

        working_df = working_df[(working_df[range_var] >= min_var) & (working_df[range_var] <= max_var)]
        working_df = working_df[self.plan_df.columns].reset_index(drop=True)

        self.plan_df = working_df

        return None

    def plan_screening_for_impulse_system(self, time_period):

        real_trd_plan_report = self.plan_df

        ultimate_start_date = (datetime.strptime(self.searching_date, '%Y-%m-%d') + timedelta(-2000)).strftime('%Y-%m-%d')
        tickers = real_trd_plan_report['Ticker'].drop_duplicates(keep='first').reset_index(drop=True)

        result_list = list()
        for ticker in tickers:
            ticker_trd_report = real_trd_plan_report[real_trd_plan_report['Ticker'] == ticker]
            ticker_prices = download_price_data(country=self.country, asset_type=self.asset_type, ticker=ticker,
                                                start_date=ultimate_start_date, end_date=self.searching_date,
                                                time_period=time_period)
            ticker_prices = add_on_technical_indicators(df=ticker_prices)

            ticker_ema_trend = ((ticker_prices['EMA_Trend1']).iloc[-1] < 0)
            ticker_macd_hist_trend = ((ticker_prices['MACD_Histogram_Trend']).iloc[-1] < 0)
            ticker_impulse_system = ~(ticker_ema_trend & ticker_macd_hist_trend)

            if ticker_impulse_system == True:
                result_list.append(ticker_trd_report)
            else:
                continue

        result_df = pd.concat(result_list)
        result_df = result_df.reset_index(drop=True)
        self.plan_df = result_df

        return None




## 기존 Plan에 대한 Adaptive Renewal

class real_trading_plan_adaptive_renewal():

    def __init__(self):
        self.inserting_db_name = 'Real_Trading'
        self.inserting_db_tbl = 'RealTrd_Trading_Plan'
        self.inserting_plan_columns = ['Trading_Date_', 'Country', 'Asset_Type', 'Market', 'Ticker', 'Name_',
                                       'Initial_Trd_Plan', 'Trading_Plan', 'Strategy', 'Searching_Date_','SE_Mode',
                                       'Ent_Days', 'Max_Ent_Days', 'Trd_Days', 'Max_Trd_Days', 'Trd_TC_Var', 'NumShrs',
                                       'Ent_Mode', 'Ent_Var', 'Ent_Coef','Planned_Ent_Price', 'Ent_Req', 'Ent_Req_Val',
                                       'LC_Mode', 'LC_Var', 'LC_Coef', 'Planned_LC_Price', 'Loss_Cut_Pct', 'LC_Req', 'LC_Req_Val', 'LC_Upside_Only',
                                       'GC_Mode', 'GC_Var', 'GC_Coef', 'Planned_GC_Price', 'Gain_Cut_Pct', 'GC_Req', 'GC_Req_Val',
                                       'CGC_Mode', 'CGC_Var', 'CGC_Days','CLC_Mode','CLC_Var','CLC_Days',
                                       'FC_Mode', 'FC_Var', 'FC_Req','FC_Req_Val','FC_Exec','Completion',
                                       'R_Value', 'R_Multiple','Ret','Net_Ret','Ent_Date_','Ent_Price',
                                       'Ex_Date_','Ex_Price','Ex_Type','Buy_Slippage','Sell_Slippage',
                                       'MDD','MDU','Ent_Score','Ex_Score','Trd_Score','Total_Score','Trd_Result']

        self.working_day = today_is_kor_stock_trading_day()


    def set_variables(self, func, country, asset_type, searching_date, n_days_after):
        self.func = func
        self.country = country
        self.asset_type = asset_type


        self.searching_date = searching_date
        self.trading_date = (datetime.strptime(self.searching_date, '%Y-%m-%d') + timedelta(days=n_days_after)).strftime('%Y-%m-%d')

        self.pda_date_diff = 800
        self.pda_window = 20
        self.pda_price_type = 'Close_'
        self.pda_start_date = (datetime.strptime(self.searching_date,'%Y-%m-%d') + timedelta(days=self.pda_date_diff*(-1))).strftime('%Y-%m-%d')

    def input_settings(self, position_size_input, fee_input, tc_input, ent_input, lc_input, gc_input, cgc_input, clc_input, fc_input):
        ## position size input

        self.position_size_model = position_size_input[0]
        self.risk_size = position_size_input[1]

        ## fee input

        self.trd_fee_pct = fee_input[0] + fee_input[1]

        ## tc input

        self.se_mode = tc_input[0]
        self.ent_time_cut = tc_input[1]
        self.trd_time_cut = tc_input[2]
        self.max_time_cut = self.ent_time_cut + self.trd_time_cut
        self.trd_time_cut_var = tc_input[3]

        ## ent input

        self.ent_plan_func_mode = ent_input[0]
        self.ent_plan_func_var = ent_input[1]
        self.ent_plan_func_coef = ent_input[2]
        self.ent_plan_func_req = ent_input[3]

        ## lc input

        self.lc_plan_func_mode = lc_input[0]
        self.lc_plan_func_var = lc_input[1]
        self.lc_plan_func_coef = lc_input[2]
        self.lc_plan_func_req = lc_input[3]
        self.lc_plan_func_upside_only = lc_input[4] * 1

        ## gc input

        self.gc_plan_func_mode = gc_input[0]
        self.gc_plan_func_var = gc_input[1]
        self.gc_plan_func_coef = gc_input[2]
        self.gc_plan_func_req = gc_input[3]

        ## cgc input

        self.cgc_plan_func_mode = cgc_input[0]
        self.cgc_plan_func_var = cgc_input[1]
        self.cgc_plan_func_days = cgc_input[2]

        ## clc input

        self.clc_plan_func_mode = clc_input[0]
        self.clc_plan_func_var = clc_input[1]
        self.clc_plan_func_days = clc_input[2]

        ## fc input

        self.fc_plan_func_mode = fc_input[0]
        self.fc_plan_func_var = fc_input[1]
        self.fc_plan_func_req = fc_input[2]

    ## 가격 다운로드

    def download_prices_for_real_trading(self, ticker):

        prices = download_price_data(country=self.country, asset_type=self.asset_type, ticker=ticker, start_date=self.pda_start_date,end_date=self.searching_date, time_period='D')
        prices = add_on_technical_indicators(df=prices, window=self.pda_window, price_type=self.pda_price_type)

        return prices

    def plan_generation(self):
        self.holding_plan_generation()
        self.entry_plan_generation()
        self.plan_df = pd.concat([self.holding_plan_df, self.entry_plan_df]).reset_index(drop=True)

    def plan_insertion(self):
        ## 기존 홀딩 계획 삭제
        sql = "DELETE FROM %s.dbo.%s WHERE Country = '%s' AND Asset_Type = '%s' AND Trading_Date_ = '%s' AND Initial_Trd_Plan = 'Holding' AND Strategy='%s'" % (
        self.inserting_db_name, self.inserting_db_tbl,self.country,self.asset_type, self.trading_date, self.func.__name__)
        transmit_str_to_sql(sql=sql)
        print('Delete existing Holding Plan / Success !')

        ## 기존 진입 계획 삭제
        sql = "DELETE FROM %s.dbo.%s WHERE Country = '%s' AND Asset_Type = '%s' AND Trading_Date_ = '%s' AND Initial_Trd_Plan = 'Entry' AND Strategy='%s' AND Ent_Days >= 2" % (
        self.inserting_db_name, self.inserting_db_tbl,self.country,self.asset_type, self.trading_date, self.func.__name__)
        transmit_str_to_sql(sql=sql)
        print('Delete existing Entry Plan / Success !')

        ## 새 진입계획 삽입
        insert_data_into_sql_Table(df=self.plan_df, TBL=self.inserting_db_tbl, DB_Name=self.inserting_db_name)

    def holding_plan_generation(self):

        sql = "SELECT * FROM %s.dbo.%s WHERE Country = '%s' AND Asset_Type = '%s' AND Trading_Date_ = '%s' AND Initial_Trd_Plan = 'Holding' AND Strategy='%s' " % (
        self.inserting_db_name, self.inserting_db_tbl,self.country,self.asset_type, self.trading_date, self.func.__name__)
        self.basic_holding_plan = read_sql_table(sql=sql)

        if len(self.basic_holding_plan)==0:
            self.holding_plan_df = pd.DataFrame(columns=self.inserting_plan_columns)

            return None

        for inx, row in self.basic_holding_plan.iterrows():
            ## 티커 가격데이터 불러오기
            ticker = row['Ticker']
            ent_price = row['Ent_Price']
            self.working_price = self.download_prices_for_real_trading(ticker=ticker)

            ## 손절라인 교정

            adaptive_lc_cond = (row['LC_Mode'] == 'Adaptive')
            pre_lc_price = row['Planned_LC_Price']
            lc_upside_only = (row['LC_Upside_Only'] == 1)
            self.holding_adaptive_loss_cut_func(ticker=ticker, adaptive_lc_cond=adaptive_lc_cond,
                                                lc_upside_only=lc_upside_only, pre_lc_price=pre_lc_price,ent_price=ent_price)

            ## 익절라인 교정
            adaptive_gc_cond = (row['GC_Mode'] == 'Adaptive')
            pre_gc_price = row['Planned_GC_Price']
            self.holding_adaptive_gain_cut_func(ticker=ticker, adaptive_gc_cond=adaptive_gc_cond,
                                                pre_gc_price=pre_gc_price,ent_price=ent_price)

        self.holding_plan_df = self.basic_holding_plan

    def entry_plan_generation(self):
        sql = "SELECT * FROM %s.dbo.%s WHERE Country = '%s' AND Asset_Type = '%s' AND Trading_Date_ = '%s' AND Initial_Trd_Plan = 'Entry' AND Strategy='%s' AND Ent_Days >= 2" % (
        self.inserting_db_name, self.inserting_db_tbl, self.country,self.asset_type, self.trading_date, self.func.__name__)
        self.basic_entry_plan = read_sql_table(sql=sql)

        if len(self.basic_entry_plan)==0:
            self.entry_plan_df = pd.DataFrame(columns=self.inserting_plan_columns)

        for inx, row in self.basic_entry_plan.iterrows():
            ## 티커 가격데이터 불러오기
            ticker = row['Ticker']
            self.working_price = self.download_prices_for_real_trading(ticker=ticker)

            ## 진입라인 교정
            adaptive_ent_cond = (row['Ent_Mode'] == 'Adaptive')
            pre_ent_price = row['Planned_Ent_Price']
            self.entry_adaptive_ent_func(ticker=ticker, adaptive_ent_cond=adaptive_ent_cond,
                                         pre_ent_price=pre_ent_price)

            ## 손절라인 교정

            adaptive_lc_cond = (row['LC_Mode'] == 'Adaptive')
            pre_lc_price = row['Planned_LC_Price']
            lc_upside_only = (row['LC_Upside_Only'] == 1)
            self.entry_adaptive_loss_cut_func(ticker=ticker, adaptive_lc_cond=adaptive_lc_cond,
                                              lc_upside_only=lc_upside_only,
                                              pre_lc_price=pre_lc_price)

            ## 익절라인 교정
            adaptive_gc_cond = (row['GC_Mode'] == 'Adaptive')
            pre_gc_price = row['Planned_GC_Price']
            self.entry_adaptive_gain_cut_func(ticker=ticker, adaptive_gc_cond=adaptive_gc_cond,
                                              pre_gc_price=pre_gc_price)

            ## 투자주식 수 교정

            self.entry_adaptive_unit_func(ticker=ticker, adaptive_unit_cond=adaptive_lc_cond)

        self.entry_plan_df = self.basic_entry_plan

    def holding_adaptive_loss_cut_func(self, ticker, adaptive_lc_cond, lc_upside_only, pre_lc_price,ent_price):
        if adaptive_lc_cond:
            if self.lc_plan_func_var=='Ent_Price':
                self.adaptive_lc_price = ent_price * self.lc_plan_func_coef
            else:
                self.adaptive_lc_price = self.working_price[self.lc_plan_func_var][-1] * self.lc_plan_func_coef
            if lc_upside_only:
                self.adaptive_lc_price = max([self.adaptive_lc_price, pre_lc_price])
        else:
            self.adaptive_lc_price = pre_lc_price

        ## basic_plan에 기록
        ticker_index = self.basic_holding_plan[self.basic_holding_plan['Ticker'] == ticker].index[0]
        ret = (self.adaptive_lc_price - self.basic_holding_plan.loc[ticker_index, 'Ent_Price']) / self.basic_holding_plan.loc[ticker_index, 'Ent_Price']
        net_ret = ret - self.trading_fee
        self.basic_holding_plan.at[ticker_index, 'Planned_LC_Price'] = round(self.adaptive_lc_price, 0)
        self.basic_holding_plan.at[ticker_index, 'Loss_Cut_Pct'] = round(net_ret, 2)

    def holding_adaptive_gain_cut_func(self, ticker, adaptive_gc_cond, pre_gc_price,ent_price):
        if adaptive_gc_cond:
            if self.gc_plan_func_var=='Ent_Price':
                self.adaptive_gc_price = ent_price * self.gc_plan_func_coef
            else:
                self.adaptive_gc_price = self.working_price[self.gc_plan_func_var][-1] * self.gc_plan_func_coef
        else:
            self.adaptive_gc_price = pre_gc_price

        ## basic_plan에 기록
        ticker_index = self.basic_holding_plan[self.basic_holding_plan['Ticker'] == ticker].index[0]
        ret = (self.adaptive_gc_price - self.basic_holding_plan.loc[ticker_index, 'Ent_Price']) / self.basic_holding_plan.loc[ticker_index, 'Ent_Price']
        net_ret = ret - self.trading_fee
        self.basic_holding_plan.at[ticker_index, 'Planned_GC_Price'] = round(self.adaptive_gc_price, 0)
        self.basic_holding_plan.at[ticker_index, 'Gain_Cut_Pct'] = round(net_ret, 2)

    def entry_adaptive_ent_func(self, ticker, adaptive_ent_cond, pre_ent_price):
        if adaptive_ent_cond:
            self.adaptive_ent_price = self.working_price[self.ent_plan_func_var][-1] * self.ent_plan_func_coef
        else:
            self.adaptive_ent_price = pre_ent_price

        ## basic_plan에 기록
        ticker_index = self.basic_entry_plan[self.basic_entry_plan['Ticker'] == ticker].index[0]
        self.basic_entry_plan.at[ticker_index, 'Planned_Ent_Price'] = round(self.adaptive_ent_price, 0)

    def entry_adaptive_loss_cut_func(self, ticker, adaptive_lc_cond, lc_upside_only, pre_lc_price):
        if adaptive_lc_cond:
            if self.lc_plan_func_var=='Ent_Price':
                self.adaptive_lc_price = self.adaptive_ent_price * self.lc_plan_func_coef
            else:
                self.adaptive_lc_price = self.working_price[self.lc_plan_func_var][-1] * self.lc_plan_func_coef
            if lc_upside_only:
                self.adaptive_lc_price = max([self.adaptive_lc_price, pre_lc_price])
        else:
            self.adaptive_lc_price = pre_lc_price

        ## basic_plan에 기록
        ticker_index = self.basic_entry_plan[self.basic_entry_plan['Ticker'] == ticker].index[0]
        ret = (self.adaptive_lc_price - self.basic_entry_plan.loc[ticker_index, 'Ent_Price']) / \
              self.basic_entry_plan.loc[ticker_index, 'Ent_Price']
        net_ret = ret - self.trading_fee
        self.basic_entry_plan.at[ticker_index, 'Planned_LC_Price'] = round(self.adaptive_lc_price, 0)
        self.basic_entry_plan.at[ticker_index, 'Loss_Cut_Pct'] = round(net_ret, 2)

    def entry_adaptive_gain_cut_func(self, ticker, adaptive_gc_cond, pre_gc_price):
        if adaptive_gc_cond:
            if self.gc_plan_func_var=='Ent_Price':
                self.adaptive_gc_price = self.adaptive_ent_price * self.gc_plan_func_coef
            else:
                self.adaptive_gc_price = self.working_price[self.gc_plan_func_var][-1] * self.gc_plan_func_coef
        else:
            self.adaptive_gc_price = pre_gc_price

        ## basic_plan에 기록
        ticker_index = self.basic_entry_plan[self.basic_entry_plan['Ticker'] == ticker].index[0]
        ret = (self.adaptive_gc_price - self.basic_entry_plan.loc[ticker_index, 'Ent_Price']) / \
              self.basic_entry_plan.loc[ticker_index, 'Ent_Price']
        net_ret = ret - self.trading_fee
        self.basic_entry_plan.at[ticker_index, 'Planned_GC_Price'] = round(self.adaptive_gc_price, 0)
        self.basic_entry_plan.at[ticker_index, 'Gain_Cut_Pct'] = round(net_ret, 2)

    def entry_adaptive_unit_func(self, ticker, adaptive_unit_cond):
        if adaptive_unit_cond:
            lc_price = self.basic_entry_plan[self.basic_entry_plan['Ticker'] == ticker].iloc[0]['Planned_LC_Price']
            ent_price = self.basic_entry_plan[self.basic_entry_plan['Ticker'] == ticker].iloc[0]['Planned_Ent_Price']
            risk_size = self.basic_entry_plan[self.basic_entry_plan['Ticker'] == ticker].iloc[0]['R_Value']
            new_units = risk_size / (ent_price-lc_price)
        else:
            new_units = self.basic_entry_plan[self.basic_entry_plan['Ticker'] == ticker].iloc[0]['NumShrs']

        ## basic_plan에 기록
        ticker_index = self.basic_entry_plan[self.basic_entry_plan['Ticker'] == ticker].index[0]
        self.basic_entry_plan.at[ticker_index, 'NumShrs'] = int(round(new_units, 0))


    def plan_on_not_working_day(self):

        if self.working_day == 1:
            print(111)
            return None
        elif self.working_day==0:
            sql = "SELECT * FROM %s.dbo.%s WHERE Trading_Date_ = '%s' AND Strategy='%s' " % (self.inserting_db_name, self.inserting_db_tbl, self.searching_date, self.func.__name__)
            self.ready_plan = read_sql_table(sql=sql)
            self.ready_plan['Trading_Date_'] = self.trading_date
            insert_data_into_sql_Table(df=self.ready_plan, TBL=self.inserting_db_tbl, DB_Name=self.inserting_db_name)



## 기존 Plan에 대한 Adaptive Renewal

class real_trading_plan_executeing_simulation():

    def __init__(self):
        self.inserting_db_name = 'Real_Trading'
        self.inserting_db_tbl = 'RealTrd_Trading_Plan'
        self.inserting_plan_columns = ['Trading_Date_', 'Country', 'Asset_Type', 'Market', 'Ticker', 'Name_',
                                       'Initial_Trd_Plan', 'Trading_Plan', 'Strategy', 'Searching_Date_','SE_Mode',
                                       'Ent_Days', 'Max_Ent_Days', 'Trd_Days', 'Max_Trd_Days', 'Trd_TC_Var', 'NumShrs',
                                       'Ent_Mode', 'Ent_Var', 'Ent_Coef','Planned_Ent_Price', 'Ent_Req', 'Ent_Req_Val',
                                       'LC_Mode', 'LC_Var', 'LC_Coef', 'Planned_LC_Price', 'Loss_Cut_Pct', 'LC_Req', 'LC_Req_Val', 'LC_Upside_Only',
                                       'GC_Mode', 'GC_Var', 'GC_Coef', 'Planned_GC_Price', 'Gain_Cut_Pct', 'GC_Req', 'GC_Req_Val',
                                       'CGC_Mode', 'CGC_Var', 'CGC_Days','CLC_Mode','CLC_Var','CLC_Days',
                                       'FC_Mode', 'FC_Var', 'FC_Req','FC_Req_Val','FC_Exec','Completion',
                                       'R_Value', 'R_Multiple','Ret','Net_Ret','Ent_Date_','Ent_Price',
                                       'Ex_Date_','Ex_Price','Ex_Type','Buy_Slippage','Sell_Slippage',
                                       'MDD','MDU','Ent_Score','Ex_Score','Trd_Score','Total_Score','Trd_Result']


        self.working_day = today_is_kor_stock_trading_day()

        self.trd_result_db_name = 'Real_Trading'
        self.trd_result_db_tbl = 'RealTrd_Trading_Result'

        self.trading_fee = 0.0033

        self.vacant_df = pd.DataFrame(columns=self.inserting_plan_columns)
        self.entry_entry_info_list = list()
        self.entry_holding_info_list = list()
        self.holding_holding_info_list = list()
        self.exit_info_list = list()

    def input_trading_info_list(self,ee_info_list=list(),eh_info_list=list(),hh_info_list=list(),exit_info_list=list()):
        self.entry_entry_info_list = ee_info_list
        self.entry_holding_info_list = eh_info_list
        self.holding_holding_info_list = hh_info_list
        self.exit_info_list = exit_info_list

    def set_variables(self, func, country, asset_type, searching_date, n_days_after):
        self.func = func
        self.country = country
        self.asset_type = asset_type

        self.searching_date = searching_date
        self.trading_date = (datetime.strptime(self.searching_date, '%Y-%m-%d') + timedelta(days=n_days_after)).strftime('%Y-%m-%d')

        self.pda_date_diff = 800
        self.pda_window = 20
        self.pda_price_type = 'Close_'


    def input_settings(self, position_size_input, fee_input, tc_input, ent_input, lc_input, gc_input, cgc_input, clc_input, fc_input):

        ## position size input

        self.position_size_model = position_size_input[0]
        self.risk_size = position_size_input[1]

        ## fee input

        self.trd_fee_pct = fee_input[0] + fee_input[1]

        ## tc input

        self.se_mode = tc_input[0]
        self.ent_time_cut = tc_input[1]
        self.trd_time_cut = tc_input[2]
        self.max_time_cut = self.ent_time_cut + self.trd_time_cut
        self.trd_time_cut_var = tc_input[3]

        ## ent input

        self.ent_plan_func_mode = ent_input[0]
        self.ent_plan_func_var = ent_input[1]
        self.ent_plan_func_coef = ent_input[2]
        self.ent_plan_func_req = ent_input[3]

        ## lc input

        self.lc_plan_func_mode = lc_input[0]
        self.lc_plan_func_var = lc_input[1]
        self.lc_plan_func_coef = lc_input[2]
        self.lc_plan_func_req = lc_input[3]
        self.lc_plan_func_upside_only = lc_input[4] * 1

        ## gc input

        self.gc_plan_func_mode = gc_input[0]
        self.gc_plan_func_var = gc_input[1]
        self.gc_plan_func_coef = gc_input[2]
        self.gc_plan_func_req = gc_input[3]

        ## cgc input

        self.cgc_plan_func_mode = cgc_input[0]
        self.cgc_plan_func_var = cgc_input[1]
        self.cgc_plan_func_days = cgc_input[2]

        ## clc input

        self.clc_plan_func_mode = clc_input[0]
        self.clc_plan_func_var = clc_input[1]
        self.clc_plan_func_days = clc_input[2]

        ## fc input

        self.fc_plan_func_mode = fc_input[0]
        self.fc_plan_func_var = fc_input[1]
        self.fc_plan_func_req = fc_input[2]

    ## 가격 다운로드

    def download_prices_for_executing_simulation(self, ticker, ent_date, ex_date):

        start_date = (datetime.strptime(ent_date, '%Y-%m-%d') + timedelta(self.pda_date_diff * (-1))).strftime('%Y-%m-%d')
        end_date = (datetime.strptime(ex_date, '%Y-%m-%d')).strftime('%Y-%m-%d')
        prices = download_price_data(country=self.country, asset_type=self.asset_type, ticker=ticker,start_date=start_date,end_date=end_date, time_period='D')

        prices = add_on_technical_indicators(df=prices, window=self.pda_window, price_type=self.pda_price_type)

        return prices

    def plan_generation(self):

        if len(self.entry_entry_info_list)==0:
            self.entry_entry_result = self.vacant_df
        else:
            self.entry_entry_result = self.manual_control_from_entry_to_entry()

        if len(self.entry_holding_info_list)==0:
            self.entry_holding_result = self.vacant_df
        else:
            self.entry_holding_result = self.manual_control_from_entry_to_holding()

        if len(self.holding_holding_info_list)==0:
            self.holding_holding_result = self.vacant_df
        else:
            self.holding_holding_result = self.manual_control_from_holding_to_holding()

        if len(self.exit_info_list)==0:
            self.exit_result = self.vacant_df
        else:
            self.exit_result = self.manual_control_for_exit()
        pass


        self.plan_df = pd.concat([self.entry_entry_result,self.entry_holding_result,self.holding_holding_result]).reset_index(drop=True)
        self.result_occurred = self.exit_result
        self.result_not_occurred = self.manual_control_for_no_exit()
        self.result_df = pd.concat([self.result_occurred,self.result_not_occurred]).reset_index(drop=True)


    def plan_insertion(self):

        plan_insertion = insert_data_into_sql_Table(df=self.plan_df,TBL=self.inserting_db_tbl,DB_Name=self.inserting_db_name)
        result_insertion = insert_data_into_sql_Table(df=self.result_df,TBL=self.trd_result_db_tbl,DB_Name=self.trd_result_db_name)
        if plan_insertion == 1:
            print('%s / Insertion of Plans from trading / Completed !'%self.searching_date)
        elif plan_insertion == 0:
            print('%s / Insertion of Plans from trading / Failed. Please Recheck !' % self.searching_date)
        if result_insertion == 1:
            print('%s / Insertion of Results from trading / Completed !'%self.searching_date)
        elif result_insertion == 0:
            print('%s / Insertion of Results from trading / Failed. Please Recheck !' % self.searching_date)

    def manual_control_from_entry_to_entry(self):

        ticker_list = [eil[0] for eil in self.entry_entry_info_list]
        ticker_list_str = ''
        for x in ticker_list:
            ticker_list_str += ',%s' % x
        ticker_list_str = ticker_list_str[1:]

        trd_plan_sql = "SELECT * FROM %s.dbo.%s WHERE Trading_Date_ = '%s' AND Ticker in (%s) AND Initial_Trd_Plan = 'Entry' AND Trading_Plan = 'Entry'" % (self.inserting_db_name, self.inserting_db_tbl, self.searching_date, ticker_list_str)

        working_df = read_sql_table(sql=trd_plan_sql)

        if len(working_df)==0:
            return self.vacant_df

        result_list = list()
        for eil in self.entry_entry_info_list:

            ticker = eil[0]

            working_df_frag = working_df[working_df['Ticker'] == ticker].reset_index(drop=True)
            working_df_frag.at[0, 'Trading_Date_'] = (datetime.strptime(self.searching_date, '%Y-%m-%d') + timedelta(1)).strftime('%Y-%m-%d')
            working_df_frag.at[0, 'Ent_Days'] = working_df_frag.loc[0,'Ent_Days'] + 1
            if working_df_frag['Ent_Days'] >  working_df_frag.loc[0,'Max_Ent_Days']:
                continue
            elif working_df_frag['Ent_Days'] <=  working_df_frag.loc[0,'Max_Ent_Days']:
                result_list.append(working_df_frag)

        if len(result_list) == 0:
            return self.vacant_df

        result_df = pd.concat(result_list).reset_index(drop=True)
        return result_df

    def manual_control_from_entry_to_holding(self):

        ticker_list = [eil[0] for eil in self.entry_holding_info_list]
        ticker_list_str = ''
        for x in ticker_list:
            ticker_list_str += ',%s' % x
        ticker_list_str = ticker_list_str[1:]

        trd_plan_sql = "SELECT * FROM %s.dbo.%s WHERE Trading_Date_ = '%s' AND Ticker in (%s) AND Initial_Trd_Plan = 'Entry' AND Trading_Plan = 'Entry'" % (self.inserting_db_name, self.inserting_db_tbl, self.searching_date, ticker_list_str)

        working_df = read_sql_table(sql=trd_plan_sql)

        if len(working_df)==0:
            return self.vacant_df

        result_list = list()
        for eil in self.entry_holding_info_list:
            ticker = eil[0]

            working_df_frag = working_df[working_df['Ticker'] == ticker].reset_index(drop=True)
            working_df_frag.at[0, 'Trading_Date_'] = (datetime.strptime(self.searching_date, '%Y-%m-%d') + timedelta(1)).strftime('%Y-%m-%d')
            working_df_frag.at[0, 'Ent_Date_'] = self.searching_date
            try:
                working_df_frag.at[0, 'Ent_Price'] = eil[1]
            except:
                working_df_frag.at[0, 'Ent_Price'] = working_df_frag.loc[0,'Planned_Ent_Price']
            working_df_frag.at[0, 'Initial_Trd_Plan'] = 'Holding'
            working_df_frag.at[0, 'Trading_Plan'] = 'Holding'
            working_df_frag.at[0, 'Trd_Days'] = working_df_frag.loc[0,'Trd_Days'] + 1

            result_list.append(working_df_frag)

        if len(result_list)==0:
            return self.vacant_df

        result_df = pd.concat(result_list).reset_index(drop=True)
        return result_df


    def manual_control_from_holding_to_holding(self):

        ticker_list = [eil[0] for eil in self.holding_holding_info_list]
        ticker_list_str = ''
        for x in ticker_list:
            ticker_list_str += ',%s' % x
        ticker_list_str = ticker_list_str[1:]

        trd_plan_sql = "SELECT * FROM %s.dbo.%s WHERE Trading_Date_ = '%s' AND Ticker in (%s) AND Initial_Trd_Plan = 'Holding' AND Trading_Plan = 'Holding'" % (
        self.inserting_db_name, self.inserting_db_tbl, self.searching_date, ticker_list_str)

        working_df = read_sql_table(sql=trd_plan_sql)

        if len(working_df)==0:
            return self.vacant_df

        result_list = list()
        for eil in self.holding_holding_info_list:
            ticker = eil[0]
            working_df_frag = working_df[working_df['Ticker'] == ticker].reset_index(drop=True)
            working_df_frag.at[0, 'Trading_Date_'] = (datetime.strptime(self.searching_date, '%Y-%m-%d') + timedelta(1)).strftime('%Y-%m-%d')
            working_df_frag.at[0, 'Trd_Days'] = working_df_frag.loc[0,'Trd_Days'] + 1

            result_list.append(working_df_frag)

        if len(result_list) == 0:
            return self.vacant_df

        result_df = pd.concat(result_list).reset_index(drop=True)
        return result_df


    def manual_control_for_exit(self):

        ticker_list = [eil[0] for eil in self.exit_info_list]
        ticker_list_str = ''
        for x in ticker_list:
            ticker_list_str += ",'%s'" % x
        ticker_list_str = ticker_list_str[1:]

        trd_plan_sql = "SELECT * FROM %s.dbo.%s WHERE Trading_Date_ = '%s' AND Ticker in (%s)" % (self.inserting_db_name, self.inserting_db_tbl, self.searching_date, ticker_list_str)

        working_df = read_sql_table(sql=trd_plan_sql)

        if len(working_df)==0:
            return self.vacant_df

        result_list = list()
        for eil in self.exit_info_list:

            ticker = eil[0]
            ex_type = eil[1]
            ex_price = eil[2]

            working_df_frag = working_df[working_df['Ticker'] == ticker].reset_index(drop=True)
            if len(working_df_frag)==0:
                continue

            ent_date = working_df_frag.loc[0,'Ent_Date_']
            if (ent_date==None):
                ent_date=self.searching_date
                working_df_frag.at[0, 'Ent_Date_'] = ent_date
            ex_date = self.searching_date
            entry_datetime = datetime.strptime(ent_date,'%Y-%m-%d')
            exit_datetime = datetime.strptime(ex_date,'%Y-%m-%d')

            ticker_price_df = self.download_prices_for_executing_simulation(ticker=ticker,ent_date=ent_date,ex_date=ex_date)
            exit_low_price = ticker_price_df.loc[exit_datetime,'Low']
            exit_high_price = ticker_price_df.loc[exit_datetime,'High']

            planned_ent_price = working_df_frag.loc[0,'Planned_Ent_Price']
            ent_price = working_df_frag.loc[0,'Ent_Price']
            if (ent_price == None):
                ent_price = np.nan
            if (np.isnan(ent_price)):
                ent_price = planned_ent_price
                working_df_frag.at[0, 'Ent_Price'] = ent_price

            ex_price_in_range_cond = (ex_price >= exit_low_price) & (ex_price <= exit_high_price)
            lc_exec_cond = ex_price_in_range_cond & (ex_type == 'LC')
            gc_exec_cond = ex_price_in_range_cond & (ex_type == 'GC')
            cgc_exec_cond = (working_df_frag.loc[0, 'CGC_Mode']=='On') & (ex_type == 'CGC')
            clc_exec_cond = (working_df_frag.loc[0, 'CLC_Mode']=='On') & (ex_type == 'CLC')
            fc_exec_cond = (working_df_frag.loc[0, 'FC_Mode']=='On') & (ex_type == 'FC')
            tc_exec_cond = (working_df_frag.loc[0, 'Trd_Days']>=working_df_frag.loc[0, 'Max_Trd_Days']) & (ex_type == 'TC')
            intu_exec_cond = (ex_type=='INTU')

            if lc_exec_cond :
                planned_ex_price = working_df_frag.loc[0, 'Planned_LC_Price']
            elif gc_exec_cond :
                planned_ex_price = working_df_frag.loc[0, 'Planned_GC_Price']
            elif cgc_exec_cond:
                cgc_var = working_df_frag.loc[0, 'CGC_Var']
                if cgc_var=='Both':
                    planned_ex_price = ticker_price_df.loc[exit_datetime, 'Open_']
                else:
                    planned_ex_price = ticker_price_df.loc[exit_datetime,cgc_var]
            elif clc_exec_cond:
                clc_var = working_df_frag.loc[0, 'CLC_Var']
                if clc_var=='Both':
                    planned_ex_price = ticker_price_df.loc[exit_datetime, 'Open_']
                else:
                    planned_ex_price = ticker_price_df.loc[exit_datetime,clc_var]
            elif fc_exec_cond:
                fc_var = working_df_frag.loc[0, 'FC_Var']
                working_df_frag.at[0, 'FC_Exec'] = 1
                planned_ex_price = ticker_price_df.loc[exit_datetime,fc_var]
            elif tc_exec_cond:
                tc_var = working_df_frag.loc[0, 'Trd_TC_Var']
                planned_ex_price = ticker_price_df.loc[exit_datetime,tc_var]
            elif intu_exec_cond:
                planned_ex_price = np.nan
            else:
                print('Ex_Date : %s / %s / Please Recheck Ex_Type or Ex_Price !'%(ex_date,ticker))
                planned_ex_price = np.nan

            units = working_df_frag.loc[0,'NumShrs']
            ret = (ex_price - ent_price)/ent_price
            net_ret = ret-self.trading_fee
            r_value = working_df_frag.loc[0,'R_Value']
            r_multiple = (net_ret*ent_price*units)/r_value
            buy_slippage = (ent_price - planned_ent_price)/planned_ent_price
            sell_slippage = (ent_price - planned_ex_price)/planned_ex_price

            mdd = (ticker_price_df.loc[entry_datetime:exit_datetime])['Low'].min()
            mdu = (ticker_price_df.loc[entry_datetime:exit_datetime])['High'].max()
            mdd = (mdd - ent_price) / ent_price
            mdu = (mdu - ent_price) / ent_price


            ent_date_price_frag = (ticker_price_df.loc[entry_datetime])
            ex_date_price_frag = (ticker_price_df.loc[exit_datetime])
            ent_score = (ent_date_price_frag['High'] - ent_price)*100/(ent_date_price_frag['High']-ent_date_price_frag['Low'])
            ex_score = (ex_price - ex_date_price_frag['Low'])*100/(ex_date_price_frag['High']-ex_date_price_frag['Low'])
            trd_score = ((ex_price-ent_price)*100/ex_date_price_frag['Avg_Width_mBollinger'])*(10/3)
            total_score = ent_score*0.25 + ex_score*0.25 + trd_score * 0.5

            score_list = [ent_score,ex_score,trd_score,total_score]
            for i in range(len(score_list)):
                if ~np.isnan(score_list[i]):
                    score_list[i] = int(score_list[i])


            trd_result = (net_ret >= 0)*1+(net_ret < 0)*(-1)

            completion = 1

            ## 기록
            working_df_frag.at[0, 'Trading_Plan'] = 'Off'
            working_df_frag.at[0, 'Completion'] = completion
            working_df_frag.at[0, 'Ret'] = round(ret*100,2)
            working_df_frag.at[0, 'Net_Ret'] = round(net_ret*100,2)
            working_df_frag.at[0, 'R_Multiple'] = round(r_multiple,2)
            working_df_frag.at[0, 'Ex_Date_'] = ex_date
            working_df_frag.at[0, 'Ex_Price'] = ex_price
            working_df_frag.at[0, 'Ex_Type'] = ex_type
            working_df_frag.at[0, 'Buy_Slippage'] = round(buy_slippage*100,2)
            working_df_frag.at[0, 'Sell_Slippage'] = round(sell_slippage*100,2)
            working_df_frag.at[0, 'MDD'] = round(mdd*100,2)
            working_df_frag.at[0, 'MDU'] = round(mdu*100,2)
            working_df_frag.at[0, 'Ent_Score'] = score_list[0]
            working_df_frag.at[0, 'Ex_Score'] = score_list[1]
            working_df_frag.at[0, 'Trd_Score'] = score_list[2]
            working_df_frag.at[0, 'Total_Score'] = score_list[3]
            working_df_frag.at[0, 'Trd_Result'] = int(trd_result)

            result_list.append(working_df_frag)

        if len(result_list) == 0:
            return self.vacant_df

        result_df = pd.concat(result_list).reset_index(drop=True)
        return result_df

    def manual_control_for_no_exit(self):
        trd_plan_sql = "SELECT * FROM %s.dbo.%s WHERE Trading_Date_ = '%s'" % (self.inserting_db_name, self.inserting_db_tbl, self.searching_date)

        working_df = read_sql_table(sql=trd_plan_sql)

        if len(working_df)==0:
            return self.vacant_df

        unique_ticker_list = list(set(list(self.plan_df['Ticker']) + list(self.result_occurred['Ticker'])))
        result_df = working_df[~working_df['Ticker'].isin(unique_ticker_list)]

        if len(result_df) == 0:
            return self.vacant_df

        df_column_setting(df=result_df,column_name='Completion',value=-1)

        return result_df

## wecolib 총괄
## from wecolib.wecolib import *