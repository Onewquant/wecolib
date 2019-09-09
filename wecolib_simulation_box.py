## 데이터 시각화
from wecolib.wecolib_visualization import *

###########################################################################
##                         Trading Experimental Box
###########################################################################

class trading_simulation_box():

    ## 매매 계획에 관한 Input Settings

    def input_settings_ent_plan(self,mode='Adaptive',var='Close_',coef=0.99,req=(None,None)):
        self.ent_plan_func_mode = mode
        self.ent_plan_func_price = var
        self.ent_plan_func_price_coef = coef
        self.ent_plan_func_req = req

    def input_settings_loss_cut_plan(self,mode='Adaptive',var='Lower_mBollinger',coef=1,req=(None,None), upside_only = False):
        self.lc_plan_func_mode = mode
        self.lc_plan_func_price = var
        self.lc_plan_func_price_coef = coef
        self.lc_plan_func_req = req
        self.lc_plan_func_upside_only = upside_only

    def input_settings_gain_cut_plan(self,mode='Adaptive',var='Upper_mBollinger',coef=1,req=(None,None)):
        self.gc_plan_func_mode = mode
        self.gc_plan_func_price = var
        self.gc_plan_func_price_coef = coef
        self.gc_plan_func_req = req

    def input_settings_confirmative_gain_cut_plan(self,mode='Off',var='Close_',days=1,comp_cond=(None,None)):
        self.cgc_plan_func_mode = mode
        self.cgc_plan_func_price = var
        self.cgc_plan_func_price_days = days
        self.cgc_plan_func_comp_cond = comp_cond

    def input_settings_confirmative_loss_cut_plan(self,mode='Off',var='Close_',days=1,comp_cond=(None,None)):
        self.clc_plan_func_mode = mode
        self.clc_plan_func_price = var
        self.clc_plan_func_price_days = days
        self.clc_plan_func_comp_cond = comp_cond

    def input_settings_force_cut_plan(self,mode='Off',var='Close_',req=(None,None)):
        self.fc_plan_func_mode = mode
        self.fc_plan_func_price = var
        self.fc_plan_func_req = req

    def input_settings_time_cut_plan(self, mode='SYET',ent_time_cut=1,trd_time_cut=3,trd_time_cut_var='Close_'):
        se_mode_dict = {'SYET' : 1, 'STET' : 0}
        self.se_mode = mode
        self.se_mode_switch = se_mode_dict[mode]
        self.se_mode_trd_day_complement = (self.se_mode_switch-1)**2

        if self.se_mode == 'STET':
            self.ent_time_cut = 1
        else:
            self.ent_time_cut = ent_time_cut


        self.trd_time_cut = trd_time_cut
        self.trd_time_cut_var = trd_time_cut_var
        self.max_time_cut = self.ent_time_cut + trd_time_cut
        self.date_ret_columns = ['Day%s_Ret' % n for n in range(self.trd_time_cut + 1)]

    def input_settings_position_size_plan(self,position_size_func, initial_risk_size):
        dict = {'CPR':self.set_position_size_cpr_model_func, 'FTV':self.set_position_size_ftv_model_func}
        self.position_size_func = dict[position_size_func]
        self.risk_size = initial_risk_size

    ## 포지션 사이즈 결정 전략들 (현재는 cpr 모델 하나)

    def set_position_size_cpr_model_func(self,days):
        try:
            self.units = int(self.risk_size / (self.planned_ent_price - self.planned_loss_cut + self.planned_ent_price * self.trd_fee_pct))
        except:
            self.units = np.nan
            self.trading_continue = 0

        self.r_value = self.risk_size

    def set_position_size_ftv_model_func(self,days):
        try:
            self.units = int(10 * self.risk_size / self.planned_ent_price)
        except:
            self.units = np.nan
            self.trading_continue = 0

        self.r_value = self.risk_size

    ## Working Variables 선언

    def set_fee(self, buy_fee, sell_fee, slippage):
        self.buy_fee_pct = buy_fee
        self.sell_fee_pct = sell_fee
        self.trd_fee_pct = buy_fee + sell_fee
        self.slippage_pct = slippage

    def set_report_format(self):

        ## Report Column 구성
        basic_columns = ['Date_', 'Market', 'Ticker', 'Name_', 'Units', 'Planned_Ent_Date_', 'Planned_Ent_Price','Planned_Loss_Cut', 'Planned_Gain_Cut']
        trading_columns = ['Ent_Date_', 'Real_Ent_Price', 'Ex_Date_', 'Ex_Price', 'Ex_Type', 'MDD', 'MDU', 'Ret', 'Net_Ret']
        date_ret_columns = self.date_ret_columns
        eval_columns = ['R_Value', 'R_Multiple', 'Ent_Score', 'Ex_Score', 'Trd_Score', 'Trd_Result']
        self.report_columns = basic_columns + trading_columns + date_ret_columns + eval_columns

        ## Report df 선언
        self.empty_dataframe = pd.DataFrame(columns=self.report_columns)
        self.report_df = self.empty_dataframe


    ## 트레이딩 시뮬레이션 플로우 함수

    def main_trading_experiment(self, country, asset_type, ticker, searching_date, position_size_input, ent_input, lc_input, gc_input, cgc_input, clc_input, fc_input, tc_input, fee_input):

        ## 입력 변수 세팅 및 가격 데이터 거래일 관련 완전성 확인
        self.set_fee(buy_fee=fee_input[0], sell_fee=fee_input[1], slippage=fee_input[2])
        self.input_settings_ent_plan(mode=ent_input[0],var=ent_input[1],coef=ent_input[2],req=ent_input[3])
        self.input_settings_loss_cut_plan(mode=lc_input[0],var=lc_input[1],coef=lc_input[2],req=lc_input[3],upside_only=lc_input[4])
        self.input_settings_gain_cut_plan(mode=gc_input[0],var=gc_input[1],coef=gc_input[2],req=gc_input[3])
        self.input_settings_confirmative_gain_cut_plan(mode=cgc_input[0],var=cgc_input[1],days=cgc_input[2],comp_cond=cgc_input[3])
        self.input_settings_confirmative_loss_cut_plan(mode=clc_input[0],var=clc_input[1],days=clc_input[2],comp_cond=clc_input[3])
        self.input_settings_force_cut_plan(mode=fc_input[0],var=fc_input[1],req=fc_input[2])
        self.input_settings_time_cut_plan(mode=tc_input[0],ent_time_cut=tc_input[1],trd_time_cut=tc_input[2],trd_time_cut_var=tc_input[3])
        self.input_settings_position_size_plan(position_size_func=position_size_input[0],initial_risk_size=position_size_input[1])
        self.set_report_format()

        setting_result = self.set_variables(country=country, asset_type=asset_type, ticker=ticker, searching_date=searching_date)
        if setting_result=='Price Data is not enough':
            return self.empty_dataframe

        ## 트레이딩 실행
        self.execute_trading()

        return self.report_df

    ## 변수 세팅 및 가격데이터 다운로드

    def set_variables(self, country, asset_type, ticker, searching_date):

        ## Variable
        self.country = country
        self.asset_type = asset_type
        self.ticker = ticker
        self.searching_date = searching_date

        ## Working Variables
        self.ticker_info_dict = get_current_name_of_ticker_data(country=country, asset_type=asset_type, ticker=ticker)
        self.market = self.ticker_info_dict['Market']
        self.name = self.ticker_info_dict['Name_']

        ## Prices Dataframe
        self.prices = self.download_prices_for_experiment(country=country, asset_type=asset_type, ticker=ticker, searching_date=searching_date, time_cut_period=self.max_time_cut)
        if len(self.prices) == 0:
            return 'Price Data is not enough'
        self.prices_index_list = list(self.prices.index)

        ## Date 관련 Variables
        self.searching_date_index = self.prices_index_list.index(datetime.strptime(searching_date, '%Y-%m-%d'))
        self.entry_date_index = self.searching_date_index + self.se_mode_switch
        self.entry_date = (self.prices_index_list[self.entry_date_index]).strftime('%Y-%m-%d')

        ## Trading 관련 Variables
        self.trading_result_dict = {'Ent_Date_': '-', 'Real_Ent_Price': np.nan, 'Ex_Date_': '-', 'Ex_Price': np.nan,'Ex_Type': '-', 'MDD': np.nan, 'MDU': np.nan, 'Ret': np.nan, 'Net_Ret': np.nan}
        self.date_ret_dict = {ret: np.nan for ret in self.date_ret_columns}
        self.date_high_ret_dict = {ret: np.nan for ret in self.date_ret_columns}
        self.date_low_ret_dict = {ret: np.nan for ret in self.date_ret_columns}

        ## Report 관련 Variables
        self.trading_report_dict = {'R_Value': np.nan, 'R_Multiple': np.nan, 'Ent_Score': np.nan, 'Ex_Score': np.nan,'Trd_Score': np.nan, 'Trd_Result': np.nan}

        ## Event 관련 Variables
        self.entry_process_occurred = 0
        self.trading_continue = 1

        ## Trading Evaluation Score
        self.ent_score = np.nan
        self.ex_score = np.nan
        self.trd_score = np.nan
        self.trd_result = np.nan

        return 'Setting is ok'

    ## 매매계획 전략

    def set_ent_plan_func(self,days):
        ## Plan 설정
        if self.ent_plan_func_mode == 'Fixed':
            days = 0
        elif self.ent_plan_func_mode == 'Adaptive':
            days = days
        self.planned_ent_price = (self.prices[self.ent_plan_func_price].iloc[self.searching_date_index+days])*self.ent_plan_func_price_coef

    def set_gain_cut_plan_func(self,days):
        ## Plan 설정
        if self.gc_plan_func_mode == 'Fixed':
            days = 0
        elif self.gc_plan_func_mode == 'Adaptive':
            days = days

        if self.gc_plan_func_price == 'Ent_Price':
            self.planned_gain_cut = self.planned_ent_price * self.gc_plan_func_price_coef
        else:
            self.planned_gain_cut = (self.prices[self.gc_plan_func_price].iloc[self.searching_date_index+days])*self.gc_plan_func_price_coef


    def set_loss_cut_plan_func(self,days):

        ## Plan 설정
        if self.lc_plan_func_mode == 'Fixed':
            days = 0
        elif self.lc_plan_func_mode == 'Adaptive':
            days = days

        if self.lc_plan_func_price == 'Ent_Price':
            self.planned_loss_cut = self.planned_ent_price*self.lc_plan_func_price_coef
        else:
            # print('lc_plan_func_price : %s / Searching_date : %s / days : %s '%(self.lc_plan_func_price,self.searching_date_index, days))
            # print(self.prices[self.lc_plan_func_price].iloc[0])
            # print(self.prices[self.lc_plan_func_price].iloc[-1])
            self.planned_loss_cut = (self.prices[self.lc_plan_func_price].iloc[self.searching_date_index+days])*self.lc_plan_func_price_coef

    def set_upside_only_loss_cut_plan_func(self,days):
        if (self.lc_plan_func_upside_only == True) == True:
            upside_cond = (self.prev_loss_cut <= self.planned_loss_cut)
            if upside_cond == False:
                self.planned_loss_cut = self.prev_loss_cut

    ## 가격 다운로드

    def download_prices_for_experiment(self, country, asset_type, ticker, searching_date, time_cut_period):

        start_date = (datetime.strptime(searching_date, '%Y-%m-%d') + timedelta(-250)).strftime('%Y-%m-%d')
        end_date = (datetime.strptime(searching_date, '%Y-%m-%d') + timedelta(time_cut_period*10)).strftime('%Y-%m-%d')
        prices = download_price_data(country=country, asset_type=asset_type, ticker=ticker, start_date=start_date,end_date=end_date, time_period='D')

        date_index_list = list(prices.index)
        time_cut_date_index = (date_index_list.index(datetime.strptime(searching_date, '%Y-%m-%d')) + 1) + time_cut_period

        after_entry_data_not_enough = (len(date_index_list) - 1) < time_cut_date_index
        if after_entry_data_not_enough:
            return pd.DataFrame()

        prices = prices[prices.index <= date_index_list[time_cut_date_index]]
        prices = add_on_technical_indicators(df=prices, window=20, price_type='Close_')

        return prices

    ## 트레이딩 시뮬레이션 시행 메인 함수

    def execute_trading(self):
        self.trading_continue = 1
        self.entry_process_occurred = 0

        ## 포지션 사이즈 설정 / 매매계획 설정 / 진입

        for ent_day in range(self.ent_time_cut):

            # Plan & Position Size Control
            self.set_ent_plan_func(days=ent_day)
            self.set_loss_cut_plan_func(days=ent_day)
            self.set_gain_cut_plan_func(days=ent_day)
            self.position_size_func(days=ent_day)

            # Entry
            self.execute_trading_entry_process(ent_day=ent_day)

            # Entry 진행 여부 확인
            if self.entry_process_occurred == 1:
                break

        ## 진입 이후 트레이딩

        for trd_day in range(self.trd_time_cut + 1):
            # Adaptive_mode_trd_day_control
            adaptive_trd_day = trd_day+ent_day-self.se_mode_trd_day_complement
            if adaptive_trd_day < 0:
                adaptive_trd_day = 0
            # Saving prev loss cut
            self.prev_loss_cut = self.planned_loss_cut
            # Adaptive Loss Cut plan setting
            self.set_loss_cut_plan_func(days=adaptive_trd_day)
            # Adaptive Loss Cut upside only condition setting
            self.set_upside_only_loss_cut_plan_func(days=(adaptive_trd_day))
            # Adaptive Gain Cut plan setting
            self.set_gain_cut_plan_func(days=adaptive_trd_day)

            # Checking plan logic
            self.check_plan_logic_and_data_quality_process(trd_day=trd_day)
            # Trading Opening Event
            self.execute_trading_gap_event_process(trd_day=trd_day)
            # Loss Cut
            self.execute_trading_planned_loss_cut_process(trd_day=trd_day)
            # Gain Cut
            self.execute_trading_planned_gain_cut_process(trd_day=trd_day)
            # Trading Closing Event
            self.execute_trading_day_close_process(trd_day=trd_day)
            # Trading 진행 여부 확인
            if self.trading_continue == 0:
                break

        # Report Statistics
        self.execute_trading_report_statistics()

        # Write Report
        self.write_report()

    ## 진입 이벤트 처리 함수

    def execute_trading_entry_process(self, ent_day):
        cond = (self.entry_process_occurred == 0) & (self.trading_continue == 1)

        if cond == True:

            ## 진입시 매매 계획 로직 혹은 가격데이터 퀄리티 확인 : 로직 및 데이터 부적절시 트레이딩 종료

            price_frag = self.prices.iloc[self.entry_date_index]
            self.ent_price_frag = price_frag
            price_data_cond = (price_frag['High'] >= price_frag['Low']) & (price_frag['High'] >= price_frag['Open_']) & (price_frag['High'] >= price_frag['Close_']) & (price_frag['Low'] <= price_frag['High']) & (price_frag['Low'] <= price_frag['Open_']) & (price_frag['Low'] <= price_frag['Close_'])
            logical_right_cond = (self.planned_ent_price > self.planned_loss_cut) & (self.planned_ent_price < self.planned_gain_cut) & (self.units > 0)
            if (price_data_cond==False):
                self.trading_result_dict['Ex_Type'] = 'ED'
                self.trading_continue = 0
                self.entry_process_occurred = 0
                return None
            if (logical_right_cond == False):
                self.trading_result_dict['Ex_Type'] = 'EL'
                self.trading_continue = 0
                self.entry_process_occurred = 0
                return None

            ## 데이터 적절성 및 매매 계획의 논리적 적절성 확보시 : 진입가격이 진입당일 레인지에 있는지 판별

            ent_cond_total = (self.planned_ent_price <= price_frag['High']) & (self.planned_ent_price >= price_frag['Low'])

            ## 진입에 특정한 제약조건 있는지 확인 : 제약 조건 만족 못하면 진입 안됨

            if (self.ent_plan_func_req[0]!=None)&(self.ent_plan_func_req[1]!=None):
                ent_cond_total = ent_cond_total & (price_frag[self.ent_plan_func_req[0]] == self.ent_plan_func_req[1])

            ## 진입조건에 만족할 때 : 진입

            if ent_cond_total == True:
                self.trading_result_dict['Ent_Date_'] = self.entry_date
                self.trading_result_dict['Real_Ent_Price'] = self.planned_ent_price * (1 + self.slippage_pct)
                self.ent_score = (price_frag['High'] - self.trading_result_dict['Real_Ent_Price']) * 100 / (price_frag['High'] - price_frag['Low'])
                self.trading_continue = 1
                self.entry_process_occurred = 1

            ## 진입조건에 만족하지 않을 때 : 진입하지 않음

            elif (ent_cond_total == False):

                ## 진입 허용 시간을 초과하지 않았을 때 : 지속적 진입 시도

                if (ent_day != self.ent_time_cut-1):
                    self.trading_continue = 1
                    self.entry_process_occurred = 0
                    self.entry_date_index = self.entry_date_index + 1
                    self.entry_date = (self.prices_index_list[self.entry_date_index]).strftime('%Y-%m-%d')

                ## 진입 허용 시간을 초과하였을 때 : 트레이딩 종료

                else:
                    self.trading_continue = 0
                    self.entry_process_occurred = 0

    ## 매매 계획 로직 및 가격데이터의 퀄리티 확인 처리 함수 : 부적절시 최악의 경우로 가정함

    def check_plan_logic_and_data_quality_process(self, trd_day):

        # 거래일 가격데이터 다운로드

        trd_date_index = self.entry_date_index + trd_day
        trd_date = (self.prices.index[trd_date_index]).strftime('%Y-%m-%d')
        price_frag = self.prices.iloc[trd_date_index]
        price_1da_frag = self.prices.iloc[trd_date_index-1]
        cur_price = price_frag['Low']

        # 매매 로직 적절성 확인 처리

        checking_logic = (self.planned_loss_cut < self.planned_gain_cut)
        if checking_logic == False:
            self.trading_result_dict['Ex_Date_'] = trd_date
            self.trading_result_dict['Ex_Price'] = cur_price * (1 - self.slippage_pct)
            self.trading_result_dict['Ex_Type'] = 'EL'
            self.trading_result_dict['Ret'] = (self.trading_result_dict['Ex_Price'] - self.trading_result_dict['Real_Ent_Price']) / self.trading_result_dict['Real_Ent_Price']
            self.trading_result_dict['Net_Ret'] = self.trading_result_dict['Ret'] - self.trd_fee_pct
            if (price_frag['High'] - price_frag['Low']) != 0:
                self.ex_score = (self.trading_result_dict['Ex_Price'] - price_frag['Low']) * 100 / (price_frag['High'] - price_frag['Low'])
            self.trading_continue = 0
        else:
            pass

        # 가격데이터 적절성 확인 처리

        high_price_data_cond = (price_frag['High'] >= price_frag['Low']) & (price_frag['High'] >= price_frag['Open_']) & (price_frag['High'] >= price_frag['Close_'])
        low_price_data_cond = (price_frag['Low'] <= price_frag['High']) & (price_frag['Low'] <= price_frag['Open_']) & (price_frag['Low'] <= price_frag['Close_'])
        if (price_1da_frag['Close_'] != 0):
            gap_change_data_cond = (((price_frag['Open_'] - price_1da_frag['Close_']) / price_1da_frag['Close_']) < 0.3) & (((price_frag['Open_'] - price_1da_frag['Close_']) / price_1da_frag['Close_']) > -0.3)
        else:
            gap_change_data_cond = False
        checking_data_quality = high_price_data_cond & low_price_data_cond & gap_change_data_cond
        if checking_data_quality == False:
            self.trading_result_dict['Ex_Date_'] = trd_date
            self.trading_result_dict['Ex_Price'] = cur_price * (1 - self.slippage_pct)
            self.trading_result_dict['Ex_Type'] = 'ED'
            self.trading_result_dict['Ret'] = (self.trading_result_dict['Ex_Price'] - self.trading_result_dict['Real_Ent_Price']) / self.trading_result_dict['Real_Ent_Price']
            self.trading_result_dict['Net_Ret'] = self.trading_result_dict['Ret'] - self.trd_fee_pct
            self.ex_score = np.nan
            self.trading_continue = 0
        else:
            pass

    ## 시가 갭 이벤트 처리 함수

    def execute_trading_gap_event_process(self, trd_day):
        cond = (self.entry_process_occurred == 1) & (self.trading_continue == 1) & (trd_day != 0)
        trd_date_index = self.entry_date_index + trd_day
        trd_date = (self.prices.index[trd_date_index]).strftime('%Y-%m-%d')
        price_frag = self.prices.iloc[trd_date_index]
        cur_price = price_frag['Open_']
        cur_net_ret = ((cur_price - self.planned_ent_price)/self.planned_ent_price)-self.trd_fee_pct

        if cond == True:

            ## 갭 변동 조건 설정

            gap_down_cond = (cur_price <= self.planned_loss_cut)
            gap_up_cond = (cur_price > self.planned_gain_cut)
            cofirmed_gap_down_execution_cond = (self.clc_plan_func_mode=='On') & (self.clc_plan_func_price != None) & (self.clc_plan_func_price in ['Both', 'Open_']) & (trd_day >= self.clc_plan_func_price_days) & (cur_net_ret < 0)
            cofirmed_gap_up_execution_cond = (self.cgc_plan_func_mode=='On') & (self.cgc_plan_func_price != None) & (self.cgc_plan_func_price in ['Both', 'Open_']) & (trd_day >= self.cgc_plan_func_price_days) & (trd_day > 0) & (cur_net_ret > 0)
            force_cut_cond = (self.fc_plan_func_mode=='On') & (self.fc_plan_func_price != None) & (self.fc_plan_func_price in ['Open_','Both']) & (trd_day > 0)
            time_cut_in_open_cond = (trd_day == self.trd_time_cut) & (self.trd_time_cut_var=='Open_')

            ## 진입첫날을 제외하고는 갭하락도 고려

            # 손실 확인 시가 청산 : 손실로 확인된 시가 청산 조건 존재시 비교대상에 비교 후 청산 실행
            if cofirmed_gap_down_execution_cond==True:
                clc_comp_cond = True
                if (self.clc_plan_func_comp_cond[0] == 'Ent_Var') & (self.clc_plan_func_comp_cond[1] != None):
                    clc_comp_cond = (((cur_price - self.ent_price_frag[self.clc_plan_func_comp_cond[1]])/self.ent_price_frag[self.clc_plan_func_comp_cond[1]] - self.trd_fee_pct) <= 0 )
                if (self.clc_plan_func_comp_cond[0] == 'Trd_Var') & (self.clc_plan_func_comp_cond[1] != None):
                    clc_comp_cond = (((cur_price - price_frag[self.clc_plan_func_comp_cond[1]])/price_frag[self.clc_plan_func_comp_cond[1]] - self.trd_fee_pct) <= 0 )

                if clc_comp_cond == True:
                    self.trading_result_dict['Ex_Date_'] = trd_date
                    self.trading_result_dict['Ex_Price'] = cur_price * (1 - self.slippage_pct)
                    self.trading_result_dict['Ex_Type'] = 'LC_C'
                    self.trading_result_dict['Ret'] = (self.trading_result_dict['Ex_Price'] - self.trading_result_dict['Real_Ent_Price']) / self.trading_result_dict['Real_Ent_Price']
                    self.trading_result_dict['Net_Ret'] = self.trading_result_dict['Ret'] - self.trd_fee_pct
                    if (price_frag['High'] - price_frag['Low']) != 0:
                        self.ex_score = (self.trading_result_dict['Ex_Price'] - price_frag['Low']) * 100 / (price_frag['High'] - price_frag['Low'])
                    self.trading_continue = 0


            # 시가의 손절 조건 만족 : 시가가 손절 조건에 만족할 경우 시가 청산됨
            if gap_down_cond == True:
                self.trading_result_dict['Ex_Date_'] = trd_date
                self.trading_result_dict['Ex_Price'] = cur_price * (1 - self.slippage_pct)
                self.trading_result_dict['Ex_Type'] = 'LC'
                self.trading_result_dict['Ret'] = (self.trading_result_dict['Ex_Price'] - self.trading_result_dict['Real_Ent_Price']) / self.trading_result_dict['Real_Ent_Price']
                self.trading_result_dict['Net_Ret'] = self.trading_result_dict['Ret'] - self.trd_fee_pct
                if (price_frag['High'] - price_frag['Low']) != 0:
                    self.ex_score = (self.trading_result_dict['Ex_Price'] - price_frag['Low']) * 100 / (price_frag['High'] - price_frag['Low'])
                self.trading_continue = 0


            ## 진입첫날을 제외하고는 갭상승도 고려

            # 이익 확인 시가 청산 : 이익으로 확인된 시가 청산 조건 존재시 청산 실행
            if cofirmed_gap_up_execution_cond==True:
                cgc_comp_cond = True
                if (self.cgc_plan_func_comp_cond[0] == 'Ent_Var') & (self.cgc_plan_func_comp_cond[1] != None):
                    cgc_comp_cond = (((cur_price - self.ent_price_frag[self.cgc_plan_func_comp_cond[1]])/self.ent_price_frag[self.cgc_plan_func_comp_cond[1]] - self.trd_fee_pct) >= 0)
                if (self.cgc_plan_func_comp_cond[0] == 'Trd_Var') & (self.cgc_plan_func_comp_cond[1] != None):
                    cgc_comp_cond = (((cur_price - price_frag[self.cgc_plan_func_comp_cond[1]])/price_frag[self.cgc_plan_func_comp_cond[1]] - self.trd_fee_pct) >= 0 )

                if cgc_comp_cond == True:
                    self.trading_result_dict['Ex_Date_'] = trd_date
                    self.trading_result_dict['Ex_Price'] = cur_price * (1 - self.slippage_pct)
                    self.trading_result_dict['Ex_Type'] = 'GC_C'
                    self.trading_result_dict['Ret'] = (self.trading_result_dict['Ex_Price'] - self.trading_result_dict['Real_Ent_Price']) / self.trading_result_dict['Real_Ent_Price']
                    self.trading_result_dict['Net_Ret'] = self.trading_result_dict['Ret'] - self.trd_fee_pct
                    if (price_frag['High'] - price_frag['Low']) != 0:
                        self.ex_score = (self.trading_result_dict['Ex_Price'] - price_frag['Low']) * 100 / (price_frag['High'] - price_frag['Low'])
                    self.trading_continue = 0

            # 시가의 익절 조건 만족 : 시가가 익절 조건에 만족할 경우 시가 청산됨
            if gap_up_cond == True:
                self.trading_result_dict['Ex_Date_'] = trd_date
                self.trading_result_dict['Ex_Price'] = cur_price * (1 - self.slippage_pct)
                self.trading_result_dict['Ex_Type'] = 'GC'
                self.trading_result_dict['Ret'] = (self.trading_result_dict['Ex_Price'] - self.trading_result_dict['Real_Ent_Price']) / self.trading_result_dict['Real_Ent_Price']
                self.trading_result_dict['Net_Ret'] = self.trading_result_dict['Ret'] - self.trd_fee_pct
                if (price_frag['High'] - price_frag['Low']) != 0:
                    self.ex_score = (self.trading_result_dict['Ex_Price'] - price_frag['Low']) * 100 / (price_frag['High'] - price_frag['Low'])
                self.trading_continue = 0

            ## 진입첫날을 제외하고는 강제청산 고려

            # 강제청산 조건 만족 : 강제청산 조건에 만족할 경우 시가 청산됨
            if force_cut_cond == True:
                force_cut_req_cond = (price_frag[self.fc_plan_func_req[0]] != None) & (price_frag[self.fc_plan_func_req[0]] == self.fc_plan_func_req[1])
                if force_cut_req_cond == True:
                    self.trading_result_dict['Ex_Date_'] = trd_date
                    self.trading_result_dict['Ex_Price'] = cur_price * (1 - self.slippage_pct)
                    self.trading_result_dict['Ret'] = (self.trading_result_dict['Ex_Price'] - self.trading_result_dict['Real_Ent_Price']) / self.trading_result_dict['Real_Ent_Price']
                    self.trading_result_dict['Net_Ret'] = self.trading_result_dict['Ret'] - self.trd_fee_pct
                    if self.trading_result_dict['Net_Ret'] >= 0:
                        self.trading_result_dict['Ex_Type'] = 'GC_F'
                    elif self.trading_result_dict['Net_Ret'] < 0:
                        self.trading_result_dict['Ex_Type'] = 'LC_F'
                    if (price_frag['High'] - price_frag['Low']) != 0:
                        self.ex_score = (self.trading_result_dict['Ex_Price'] - price_frag['Low']) * 100 / (price_frag['High'] - price_frag['Low'])
                    self.trading_continue = 0
            else:
                pass

            ## 시간 청산(시가설정) : 시간청산

            if time_cut_in_open_cond == True:
                self.trading_result_dict['Ex_Date_'] = trd_date
                self.trading_result_dict['Ex_Price'] = cur_price * (1 - self.slippage_pct)
                self.trading_result_dict['Ex_Type'] = 'TC'
                self.trading_result_dict['Ret'] = (self.trading_result_dict['Ex_Price'] - self.trading_result_dict['Real_Ent_Price']) / self.trading_result_dict['Real_Ent_Price']
                self.trading_result_dict['Net_Ret'] = self.trading_result_dict['Ret'] - self.trd_fee_pct
                if (price_frag['High'] - price_frag['Low']) != 0:
                    self.ex_score = (self.trading_result_dict['Ex_Price'] - price_frag['Low']) * 100 / (price_frag['High'] - price_frag['Low'])
                self.trading_continue = 0
            else:
                pass

    ## 손절 이벤트 처리 함수

    def execute_trading_planned_loss_cut_process(self, trd_day):
        cond = (self.entry_process_occurred == 1) & (self.trading_continue == 1)
        trd_date_index = self.entry_date_index + trd_day
        price_frag = self.prices.iloc[trd_date_index]

        if cond == True:
            cur_price = self.planned_loss_cut
            not_next_close_ent_in_syet_mode_cond = ~((trd_day==0) & (self.ent_plan_func_price=='Next_Close_') & (self.se_mode_switch==1))
            not_close_ent_in_stet_cond = ~((trd_day == 0) & (self.ent_plan_func_price == 'Close_') & (self.se_mode_switch == 0))
            loss_cut_cond = (self.planned_loss_cut >= price_frag['Low']) & (self.planned_loss_cut <= price_frag['High']) & not_next_close_ent_in_syet_mode_cond & not_close_ent_in_stet_cond

            ## 손절에 특정한 제약조건 있는지 확인 : 제약 조건 만족 못하면 손절 안 됨

            if (self.lc_plan_func_req[0] != None) & (self.lc_plan_func_req[1] != None):
                loss_cut_cond = loss_cut_cond & (price_frag[self.lc_plan_func_req[0]] == self.lc_plan_func_req[1])

            if loss_cut_cond == True:
                self.trading_result_dict['Ex_Date_'] = (self.prices.index[trd_date_index]).strftime('%Y-%m-%d')
                self.trading_result_dict['Ex_Price'] = cur_price * (1 - self.slippage_pct)
                self.trading_result_dict['Ex_Type'] = 'LC'
                self.trading_result_dict['Ret'] = (self.trading_result_dict['Ex_Price'] - self.trading_result_dict['Real_Ent_Price']) / self.trading_result_dict['Real_Ent_Price']
                self.trading_result_dict['Net_Ret'] = self.trading_result_dict['Ret'] - self.trd_fee_pct
                if (price_frag['High'] - price_frag['Low']) != 0:
                    self.ex_score = (self.trading_result_dict['Ex_Price'] - price_frag['Low']) * 100 / (price_frag['High'] - price_frag['Low'])
                self.trading_continue = 0
        else:
            pass

    ## 익절 이벤트 처리 함수

    def execute_trading_planned_gain_cut_process(self, trd_day):
        cond = (self.entry_process_occurred == 1) & (self.trading_continue == 1)
        trd_date_index = self.entry_date_index + trd_day
        trd_date = (self.prices.index[trd_date_index]).strftime('%Y-%m-%d')
        price_frag = self.prices.iloc[trd_date_index]

        if cond == True:
            cur_price = self.planned_gain_cut
            not_next_close_ent_in_syet_mode_cond = ~((trd_day==0) & (self.ent_plan_func_price=='Next_Close_') & (self.se_mode_switch==1))
            not_close_ent_in_stet_cond = ~((trd_day == 0) & (self.ent_plan_func_price == 'Close_') & (self.se_mode_switch==0))
            gain_cut_cond = (self.planned_gain_cut >= price_frag['Low']) & (self.planned_gain_cut <= price_frag['High']) & not_next_close_ent_in_syet_mode_cond & not_close_ent_in_stet_cond
            if trd_day == 0:
                gain_cut_cond = gain_cut_cond & (price_frag['Close_'] > price_frag['Open_'])


            ## 익절에 특정한 제약조건 있는지 확인 : 조건 만족해야지만 익절 실행

            if (self.gc_plan_func_req[0] != None) & (self.gc_plan_func_req[1] != None):
                gain_cut_cond = gain_cut_cond & (price_frag[self.gc_plan_func_req[0]] == self.gc_plan_func_req[1])

            if gain_cut_cond == True:
                self.trading_result_dict['Ex_Date_'] = trd_date
                self.trading_result_dict['Ex_Price'] = cur_price * (1 - self.slippage_pct)
                self.trading_result_dict['Ex_Type'] = 'GC'
                self.trading_result_dict['Ret'] = (self.trading_result_dict['Ex_Price'] - self.trading_result_dict['Real_Ent_Price']) / self.trading_result_dict['Real_Ent_Price']
                self.trading_result_dict['Net_Ret'] = self.trading_result_dict['Ret'] - self.trd_fee_pct
                if (price_frag['High'] - price_frag['Low']) != 0:
                    self.ex_score = (self.trading_result_dict['Ex_Price'] - price_frag['Low']) * 100 / (price_frag['High'] - price_frag['Low'])
                self.trading_continue = 0
        else:
            pass

    ## 거래일 정리 이벤트 처리 및 당일 변동폭 기록 함수

    def execute_trading_day_close_process(self, trd_day):
        trd_date_index = self.entry_date_index + trd_day
        trd_datetime = self.prices.index[trd_date_index]
        trd_date = trd_datetime.strftime('%Y-%m-%d')
        price_frag = self.prices.iloc[trd_date_index]
        cur_price = self.trading_result_dict['Real_Ent_Price']

        self.date_ret_dict['Day%s_Ret' % trd_day] = (price_frag['Close_'] - cur_price) / cur_price - self.trd_fee_pct
        self.date_high_ret_dict['Day%s_Ret' % trd_day] = (price_frag['High'] - cur_price) / cur_price - self.trd_fee_pct
        self.date_low_ret_dict['Day%s_Ret' % trd_day] = (price_frag['Low'] - cur_price) / cur_price - self.trd_fee_pct
        cur_price = price_frag['Close_']
        close_net_ret = ((cur_price - self.planned_ent_price)/self.planned_ent_price)-self.trd_fee_pct


        ## 종가 확인 이익 청산 : 이익 확인된 종가 청산 조건 존재시

        cond = (self.trading_continue == 1) & (self.cgc_plan_func_mode=='On') & (self.cgc_plan_func_price != None) & (self.cgc_plan_func_price in ['Both', 'Close_']) & (trd_day >= self.cgc_plan_func_price_days) & (close_net_ret > 0)

        if cond == True:
            cgc_comp_cond = True
            if (self.cgc_plan_func_comp_cond[0] == 'Ent_Var') & (self.cgc_plan_func_comp_cond[1] != None):
                cgc_comp_cond = (((cur_price - self.ent_price_frag[self.cgc_plan_func_comp_cond[1]]) /self.ent_price_frag[self.cgc_plan_func_comp_cond[1]] - self.trd_fee_pct) >= 0)
            if (self.cgc_plan_func_comp_cond[0] == 'Trd_Var') & (self.cgc_plan_func_comp_cond[1] != None):
                cgc_comp_cond = (((cur_price - price_frag[self.cgc_plan_func_comp_cond[1]]) / price_frag[self.cgc_plan_func_comp_cond[1]] - self.trd_fee_pct) >= 0)

            if cgc_comp_cond == True:
                self.trading_result_dict['Ex_Date_'] = trd_date
                self.trading_result_dict['Ex_Price'] = cur_price * (1 - self.slippage_pct)
                self.trading_result_dict['Ex_Type'] = 'GC_C'
                self.trading_result_dict['Ret'] = (self.trading_result_dict['Ex_Price'] - self.trading_result_dict['Real_Ent_Price']) / self.trading_result_dict['Real_Ent_Price']
                self.trading_result_dict['Net_Ret'] = self.trading_result_dict['Ret'] - self.trd_fee_pct
                if (price_frag['High'] - price_frag['Low']) != 0:
                    self.ex_score = (self.trading_result_dict['Ex_Price'] - price_frag['Low']) * 100 / (price_frag['High'] - price_frag['Low'])
                self.trading_continue = 0

        ## 종가 확인 손실 청산 : 손실 확인된 종가 청산 조건 존재시

        cond = (self.trading_continue == 1) & (self.clc_plan_func_mode=='On') & (self.clc_plan_func_price != None) & (self.clc_plan_func_price in ['Both', 'Close_']) & (trd_day >= self.clc_plan_func_price_days) & (close_net_ret < 0)

        if cond == True:
            clc_comp_cond = True
            if (self.clc_plan_func_comp_cond[0] == 'Ent_Var') & (self.clc_plan_func_comp_cond[1] != None):
                clc_comp_cond = (((cur_price - self.ent_price_frag[self.clc_plan_func_comp_cond[1]]) / self.ent_price_frag[self.clc_plan_func_comp_cond[1]] - self.trd_fee_pct) <= 0)
            if (self.clc_plan_func_comp_cond[0] == 'Trd_Var') & (self.clc_plan_func_comp_cond[1] != None):
                clc_comp_cond = (((cur_price - price_frag[self.clc_plan_func_comp_cond[1]]) / price_frag[self.clc_plan_func_comp_cond[1]] - self.trd_fee_pct) <= 0)

            if clc_comp_cond == True:
                self.trading_result_dict['Ex_Date_'] = trd_date
                self.trading_result_dict['Ex_Price'] = cur_price * (1 - self.slippage_pct)
                self.trading_result_dict['Ex_Type'] = 'LC_C'
                self.trading_result_dict['Ret'] = (self.trading_result_dict['Ex_Price'] - self.trading_result_dict['Real_Ent_Price']) / self.trading_result_dict['Real_Ent_Price']
                self.trading_result_dict['Net_Ret'] = self.trading_result_dict['Ret'] - self.trd_fee_pct
                if (price_frag['High'] - price_frag['Low']) != 0:
                    self.ex_score = (self.trading_result_dict['Ex_Price'] - price_frag['Low']) * 100 / (price_frag['High'] - price_frag['Low'])
                self.trading_continue = 0


        ## 강제 청산 확인 : 강제 청산 조건 존재시 청산 실행

        cond = (self.trading_continue == 1) & (self.fc_plan_func_mode=='On') & (self.fc_plan_func_price != None) & (self.fc_plan_func_price in ['Both', 'Close_'])

        if cond == True:

            force_cut_req_cond = (price_frag[self.fc_plan_func_req[0]] != None) & (price_frag[self.fc_plan_func_req[0]] == self.fc_plan_func_req[1])

            if force_cut_req_cond == True:
                self.trading_result_dict['Ex_Date_'] = trd_date
                self.trading_result_dict['Ex_Price'] = cur_price * (1 - self.slippage_pct)
                self.trading_result_dict['Ret'] = (self.trading_result_dict['Ex_Price'] - self.trading_result_dict['Real_Ent_Price']) / self.trading_result_dict['Real_Ent_Price']
                self.trading_result_dict['Net_Ret'] = self.trading_result_dict['Ret'] - self.trd_fee_pct
                if self.trading_result_dict['Net_Ret']>=0:
                    self.trading_result_dict['Ex_Type'] = 'GC_F'
                elif self.trading_result_dict['Net_Ret']<0:
                    self.trading_result_dict['Ex_Type'] = 'LC_F'
                if (price_frag['High'] - price_frag['Low']) != 0:
                    self.ex_score = (self.trading_result_dict['Ex_Price'] - price_frag['Low']) * 100 / (price_frag['High'] - price_frag['Low'])
                self.trading_continue = 0

            else:
                pass

        ## 시간 청산(종가설정) : 시간청산

        cond = (self.entry_process_occurred == 1) & (self.trading_continue == 1) & (trd_day == self.trd_time_cut) & (self.trd_time_cut_var=='Close_')

        if cond == True:
            self.trading_result_dict['Ex_Date_'] = trd_date
            self.trading_result_dict['Ex_Price'] = cur_price * (1 - self.slippage_pct)
            self.trading_result_dict['Ex_Type'] = 'TC'
            self.trading_result_dict['Ret'] = (self.trading_result_dict['Ex_Price'] - self.trading_result_dict['Real_Ent_Price']) / self.trading_result_dict['Real_Ent_Price']
            self.trading_result_dict['Net_Ret'] = self.trading_result_dict['Ret'] - self.trd_fee_pct
            if (price_frag['High'] - price_frag['Low']) != 0:
                self.ex_score = (self.trading_result_dict['Ex_Price'] - price_frag['Low']) * 100 / (price_frag['High'] - price_frag['Low'])
            self.trading_continue = 0
        else:
            pass

    ## 거래 통계값 생성

    def execute_trading_report_statistics(self):
        cond = (self.entry_process_occurred == 1) & (self.trading_continue == 0)
        if cond == True:
            initial_trd_amount = self.trading_result_dict['Real_Ent_Price'] * self.units

            self.trading_result_dict['MDD'] = min(list(self.date_low_ret_dict.values()))
            self.trading_result_dict['MDU'] = max(list(self.date_high_ret_dict.values()))
            self.trading_report_dict['R_Value'] = self.r_value
            self.trading_report_dict['R_Multiple'] = self.trading_result_dict['Net_Ret'] * initial_trd_amount / self.r_value
            self.trading_report_dict['Ent_Score'] = self.ent_score
            self.trading_report_dict['Ex_Score'] = self.ex_score
            self.trading_report_dict['Trd_Score'] = (self.trading_result_dict['Ex_Price'] - self.trading_result_dict['Real_Ent_Price']) * 100 / self.prices['Avg_Width_mBollinger'].loc[datetime.strptime(self.trading_result_dict['Ex_Date_'],'%Y-%m-%d')]

            if self.trading_result_dict['Net_Ret'] > 0:
                self.trading_report_dict['Trd_Result'] = 1
            elif self.trading_result_dict['Net_Ret'] == 0:
                self.trading_report_dict['Trd_Result'] = 0
            elif self.trading_result_dict['Net_Ret'] < 0:
                self.trading_report_dict['Trd_Result'] = -1
            elif np.isnan(self.trading_result_dict['Net_Ret']):
                self.trading_report_dict['Trd_Result'] = np.nan

    ## 거래 통계값 기록

    def write_report(self):
        basic_list = [self.searching_date, self.market, self.ticker, self.name, self.units, self.entry_date,self.planned_ent_price, self.planned_loss_cut, self.planned_gain_cut]
        trading_list = list(self.trading_result_dict.values())
        date_ret_list = list(self.date_ret_dict.values())
        eval_list = list(self.trading_report_dict.values())

        report_list = basic_list + trading_list + date_ret_list + eval_list

        report_df = pd.DataFrame(data=[report_list], columns=self.report_columns)
        self.report_df = report_df

###########################################################################
##                         Trading Simulation Control Box
###########################################################################

class trading_simulation_control_box():

    def input_control_settings(self,mpcores,country,asset_type,plan,position_size_input,ent_input,lc_input,gc_input,cgc_input,clc_input,fc_input,tc_input,fee_input):
        self.mpcores = mpcores
        if os.cpu_count() < mpcores:
            self.mpcores = os.cpu_count()

        self.country = country
        self.asset_type = asset_type
        self.plan = plan
        self.position_size_input = position_size_input
        self.ent_input = ent_input
        self.lc_input = lc_input
        self.gc_input = gc_input
        self.cgc_input = cgc_input
        self.clc_input = clc_input
        self.fc_input = fc_input
        self.tc_input = tc_input
        self.fee_input = fee_input

    def exec_trading_simulation_box_main(self):
        print('Main Process : {}'.format(os.getpid(), ))
        if len(self.plan)==0:
            print('No plan for simulation. Please recheck !')
            return None

        plan_list = np.array_split(self.plan, self.mpcores)


        self.result_queue = Queue()
        procs = list()

        for mc in range(self.mpcores):
            if len(plan_list[mc]) == 0:
                continue
            proc = Process(target=self.exec_running_loop, args=(plan_list[mc],self.result_queue))
            procs.append(proc)
            proc.start()

        self.result_list = [self.result_queue.get() for p in range(len(procs))]

        for p in range(len(procs)):
            procs[p].join()
            procs[p].terminate()

        self.result_queue.close()
        self.result_queue.join_thread()

        if len(self.result_list) > 1:
            self.trd_report = pd.concat(self.result_list).sort_values(by=['Date_', 'Ticker'],ascending=True).reset_index(drop=True)
        else:
            self.trd_report = self.result_list[0]

        ## Trd Report 최종 편집

        self.trd_report = self.trd_report.copy()
        trd_report_columns = self.trd_report.columns
        int_columns_list = list(trd_report_columns[6:9]) + [trd_report_columns[10],trd_report_columns[12]] + list(trd_report_columns[-4:-1])
        float_columns_list = list(trd_report_columns[14:-4])
        self.trd_report[int_columns_list] = self.trd_report[int_columns_list].applymap(lambda x:round(x*10,0)/10)
        self.trd_report[float_columns_list] = self.trd_report[float_columns_list].applymap(lambda x:round(x*10000,0)/10000)

        print('Works done !')

    def exec_running_loop(self, plan, result_queue):
        print('Process : {}'.format(os.getpid(),))
        loop = asyncio.get_event_loop()
        result_df = loop.run_until_complete(self.trading_simulation_result_collector(plan))
        result_queue.put(result_df)
        loop.close()

    async def trading_simulation_result_collector(self,plan):

        futures = list()
        result_frag_list = list()
        for inx, row in plan.iterrows():
            futures.append(asyncio.ensure_future(self.exec_single_trading_simulation(row['Date_'],row['Ticker'])))

        for f in asyncio.as_completed(futures):
            result_frag_list.append(await f)

        result_df = pd.concat(result_frag_list).sort_values(by=['Date_', 'Ticker'],ascending=True).reset_index(drop=True)
        return result_df

    async def exec_single_trading_simulation(self,searching_date,ticker):
        single_box = trading_simulation_box()
        single_result_df = single_box.main_trading_experiment(country=self.country, asset_type=self.asset_type, ticker=ticker,searching_date=searching_date, position_size_input=self.position_size_input,ent_input=self.ent_input, lc_input=self.lc_input, gc_input=self.gc_input, cgc_input=self.cgc_input,clc_input=self.clc_input, fc_input=self.fc_input, tc_input=self.tc_input, fee_input=self.fee_input)
        return single_result_df

###########################################################################
##                         Simulation Statistics
###########################################################################

## 개별 통계 함수

def statistical_analysis_of_trading_simulation(report,drop_duplicates=True,drop_data_errors=True,printing_show=True,graph_show=True,result_return=False):

    df = report
    dup_count = len(df)

    ## Result Columns

    result_short_cut_basic_columns_list = ['Start_Date_', 'End_Date_', 'Period_', 'Trd_Count']
    result_short_cut_wr_columns_list = ['Winning_Ratio', 'GGC_Pct', 'GLC_Pct', 'CGC_Pct', 'CLC_Pct', 'FC_Pct','FGC_Pct', 'FLC_Pct', 'GC_Pct', 'LC_Pct', 'TC_Pct']
    result_short_cut_wlr_columns_list = ['Loss_Gain_Ratio', 'Avg_Gain_Size', 'Avg_Loss_Size', 'Trd_MDD', 'Trd_MDU','Net_Ret_MV']
    result_short_cut_score_columns_list = ['Ent_Score_MV', 'Ex_Score_MV', 'Trd_Score_MV']
    result_short_cut_ev_columns_list = ['Trd_Expected_Value', 'Total_Expected_Value_Weekly','Total_Expected_Value_Monthly', 'Total_Expected_Value_Annually']
    result_short_cut_system_columns_list = ['Sharpe_Ratio', 'SQN']
    result_short_cut_holding_columns_list = ['Avg_Position_Holding_Days', 'TC_Holding_Period', 'Avg_Gain_Trd_Days','Avg_Loss_Trd_Days']
    result_short_cut_cont_columns_list = ['Max_Cont_Gain_Count', 'Max_Cont_Loss_Count']
    result_short_cut_error_columns_list = ['RMV_Error_Data', 'RMV_Dup_Trd']
    result_short_cut_columns_list = result_short_cut_basic_columns_list + result_short_cut_wr_columns_list + result_short_cut_wlr_columns_list + result_short_cut_score_columns_list + result_short_cut_ev_columns_list + result_short_cut_system_columns_list + result_short_cut_holding_columns_list + result_short_cut_cont_columns_list + result_short_cut_error_columns_list

    ## Report가 Vacant df 일경우

    if dup_count==0:
        if result_return==True:
            return pd.DataFrame(columns=result_short_cut_columns_list)
        else :
            return None

    ## 에러데이터 처리

    if drop_duplicates == True:
        df = df.drop_duplicates(subset=list(df.columns[1:]), keep='first')
        dup_count -= len(df)
        df = df.reset_index(drop=True)
    if drop_data_errors == True:
        error_count = len(df[df['Ex_Type'] == 'ED'])
        df = df[df['Ex_Type'] != 'ED']
        df = df.reset_index(drop=True)

    ## Variables for Statistics

    # 기간 (검색 시점 기준)
    searching_start_date = df['Date_'].min()
    searching_end_date = df['Date_'].max()
    searching_date_diff = (datetime.strptime(searching_end_date, '%Y-%m-%d') - datetime.strptime(searching_start_date,'%Y-%m-%d')).days

    # 승률 관련
    total_entered_trds = (df['Trd_Result'][~pd.isna(df['Trd_Result'])]).map(lambda x:int(x)).reset_index(drop=True)
    gain_trds = total_entered_trds[(total_entered_trds > 0)]
    if len(total_entered_trds) == 0:
        winning_ratio = np.nan
    else:
        winning_ratio = len(gain_trds) * 100 / len(total_entered_trds)

    # 연속 손실 및 이익 관련

    df_for_cont_gain = pd.DataFrame((total_entered_trds > 0) * 1)
    df_for_cont_loss = pd.DataFrame((total_entered_trds < 0) * 1)

    cont_count_list = list()
    for profit_df in [df_for_cont_gain, df_for_cont_loss]:
        pivot_pointing_df = profit_df[((profit_df + profit_df.shift(1).fillna(0))['Trd_Result'] == 1)]
        pivot_point_inx_df = pd.DataFrame(pivot_pointing_df.index)
        pre_result = pivot_point_inx_df - pivot_point_inx_df.shift(1).fillna(0)
        result = pre_result[pre_result.index % 2 == 1]
        result_count = result[0].max()
        cont_count_list.append(result_count)

    cont_gain_count = cont_count_list[0]
    cont_loss_count = cont_count_list[1]

    # 신호발생
    if searching_date_diff == 0:
        searching_date_diff = 1
    trd_freq_weekly = len(total_entered_trds) * 7 / searching_date_diff
    trd_freq_monthly = len(total_entered_trds) * 30 / searching_date_diff
    trd_freq_annually = len(total_entered_trds) * 365 / searching_date_diff

    # 기대값 관련
    r_multiple = df['R_Multiple']
    real_expected_value = r_multiple.mean()
    real_expected_value_stdev = r_multiple.std()
    system_quality_number = real_expected_value / real_expected_value_stdev
    real_expected_value_week = trd_freq_weekly * real_expected_value
    real_expected_value_month = trd_freq_monthly * real_expected_value
    real_expected_value_year = trd_freq_annually * real_expected_value
    gain_r_multiple = r_multiple[r_multiple > 0]
    loss_r_multiple = r_multiple[r_multiple < 0]
    win_loss_ratio = abs(gain_r_multiple.mean() / loss_r_multiple.mean())

    avg_gain_r_multiple = gain_r_multiple.mean()
    avg_loss_r_multiple = loss_r_multiple.mean()

    # 수익률 관련
    net_ret = df['Net_Ret']
    net_ret_mean_value = net_ret.mean()
    net_ret_stdev = net_ret.std()
    sharpe_ratio = net_ret_mean_value / net_ret_stdev

    # 손익요인 분석
    cause = df['Ex_Type']
    ggc_cause = (cause == 'GC') * 1
    cgc_cause = (cause == 'GC_C') * 1
    fgc_cause = (cause == 'GC_F') * 1
    glc_cause = (cause == 'LC') * 1
    clc_cause = (cause == 'LC_C') * 1
    flc_cause = (cause == 'LC_F') * 1
    fc_cause = fgc_cause + flc_cause
    gc_cause = ggc_cause + cgc_cause + fgc_cause
    lc_cause = glc_cause + clc_cause + flc_cause
    tc_cause = (cause == 'TC') * 1
    cause_total = len(cause[cause != '-'])
    if cause_total == 0:
        ggc_cause_pct = np.nan
        glc_cause_pct = np.nan
        tc_cause_pct = np.nan
        cgc_cause_pct = np.nan
        clc_cause_pct = np.nan
        fgc_cause_pct = np.nan
        flc_cause_pct = np.nan
        fc_cause_pct = np.nan
        gc_cause_pct = np.nan
        lc_cause_pct = np.nan
    else:
        ggc_cause_pct = ggc_cause.sum() * 100 / cause_total
        glc_cause_pct = glc_cause.sum() * 100 / cause_total
        tc_cause_pct = tc_cause.sum() * 100 / cause_total
        cgc_cause_pct = cgc_cause.sum() * 100 / cause_total
        clc_cause_pct = clc_cause.sum() * 100 / cause_total
        fgc_cause_pct = fgc_cause.sum() * 100 / cause_total
        flc_cause_pct = flc_cause.sum() * 100 / cause_total
        fc_cause_pct = fc_cause.sum() * 100 / cause_total
        gc_cause_pct = gc_cause.sum() * 100 / cause_total
        lc_cause_pct = lc_cause.sum() * 100 / cause_total

    # 트레이딩 스코어 관련
    ent_score = df['Ent_Score']
    ex_score = df['Ex_Score']
    trd_score = df['Trd_Score']
    ent_score_mean_value = ent_score.mean()
    ex_score_mean_value = ex_score.mean()
    trd_score_mean_value = trd_score.mean()

    # 포지션 보유일수
    daily_ret_columns = df.columns[18:-6]
    total_position_holding = (df[daily_ret_columns].dropna(axis=0, how='all'))
    avg_days_position_holding = total_position_holding.count(axis=1).mean()

    minimum_trd_mdd = total_position_holding.min().min()
    maximum_trd_mdu = total_position_holding.max().max()

    avg_gain_trading_days = (total_position_holding > 0).sum(axis=1).mean()
    avg_loss_trading_days = (total_position_holding < 0).sum(axis=1).mean()

    ## Statistics Report

    if printing_show == True:
        print('--------------------------------------------------------')
        print('                    Statistics Report           ')
        print('--------------------------------------------------------')
        print(' 종목 검색 기간 : %s ~ %s (총 %s 일간)' % (searching_start_date, searching_end_date, searching_date_diff))
        print(' 총 트레이딩 횟수 : %s 회' % (len(total_entered_trds)))
        print('')
        print(' 승률 : %s %%' % (round(winning_ratio, 2)))
        print(' General Gain Cut Pct : %s %%' % (round(ggc_cause_pct, 2)))
        print(' General Loss Cut Pct : %s %%' % (round(glc_cause_pct, 2)))
        print(' Confirmative Gain Cut Pct : %s %%' % (round(cgc_cause_pct, 2)))
        print(' Confirmative Loss Cut Pct : %s %%' % (round(clc_cause_pct, 2)))
        print(' Force Cut Pct (Total) : %s %%' % (round(fc_cause_pct, 2)))
        print(' Force Cut Pct (Gain): %s %%' % (round(fgc_cause_pct, 2)))
        print(' Force Cut Pct (Loss) : %s %%' % (round(flc_cause_pct, 2)))
        print('')
        print(' Gain Cut Pct : %s %%' % (round(gc_cause_pct, 2)))
        print(' Loss Cut Pct : %s %%' % (round(lc_cause_pct, 2)))
        print(' Time Cut Pct : %s %%' % (round(tc_cause_pct, 2)))
        print('')
        print(' 손익비 : 1 / %s (L/G)' % (round(win_loss_ratio, 2)))
        print(' 평균 이익거래 크기 : %s R' % (round(avg_gain_r_multiple, 2)))
        print(' 평균 손실거래 크기 : %s R' % (round(avg_loss_r_multiple, 2)))
        print(' 1회 트레이딩 중 최대 손실 : %s %%' % (round(minimum_trd_mdd, 2)))
        print(' 1회 트레이딩 중 최대 이익 : %s %%' % (round(maximum_trd_mdu, 2)))
        print(' 1회 트레이딩 중 평균 순 이익 : %s %%' % (round(net_ret_mean_value, 2)))
        print('')
        print(' 평균 진입점수(Ent Score) : %s' % (round(ent_score_mean_value, 2)))
        print(' 평균 청산점수(Ex Score) : %s' % (round(ex_score_mean_value, 2)))
        print(' 평균 거래점수(Trd Score) : %s' % (round(trd_score_mean_value, 2)))
        print('')
        print(' 기대값(1거래당) : %s R' % (round(real_expected_value, 2)))
        print(' 종합기대값(주간) : %s R' % (round(real_expected_value_week, 2)))
        print(' 종합기대값(월간) : %s R' % (round(real_expected_value_month, 2)))
        print(' 종합기대값(연간) : %s R' % (round(real_expected_value_year, 2)))
        print('')
        print(' 샤프지수(Sharpe Index) : %s' % (round(sharpe_ratio, 2)))
        print(' 시스템 평가 스코어(SQN) : %s' % (round(system_quality_number, 2)))
        print('')
        print(' 평균 포지션 보유 일수 : %s 일 (시간청산 최대보유일 : %s 일)' % (round(avg_days_position_holding, 2), len(daily_ret_columns)))
        print(' 평균 이익 포지션 보유 일수 : %s 일' % (round(avg_gain_trading_days, 2)))
        print(' 평균 손실 포지션 보유 일수 : %s 일' % (round(avg_loss_trading_days, 2)))
        print('')
        print(' 최대 연속 이익 거래 수 : %s 회' % (round(cont_gain_count, 2)))
        print(' 최대 연속 손실 거래 수 : %s 회' % (round(cont_loss_count, 2)))
        print('')
        print(' 에러 데이터 제거 : %s 개' % (error_count))
        print(' 중복 거래 제거 : %s 개' % (dup_count))

    ## Statistics Graph

    if graph_show == True:
        # 예측치 배수의 히스토그램
        r_multiple.hist(grid=True, histtype='bar', rwidth=0.8, alpha=0.8, color='red', bins=50)
        plt.show()

    if result_return == True:
        result_short_cut_basic_list = [searching_start_date, searching_end_date, searching_date_diff,
                                       len(total_entered_trds)]
        result_short_cut_wr_list = [round(winning_ratio, 2), round(ggc_cause_pct, 2), round(glc_cause_pct, 2),
                                    round(cgc_cause_pct, 2), round(clc_cause_pct, 2), round(fc_cause_pct, 2),
                                    round(fgc_cause_pct, 2), round(flc_cause_pct, 2), round(gc_cause_pct, 2),
                                    round(lc_cause_pct, 2), round(tc_cause_pct, 2)]
        result_short_cut_wlr_list = [round(win_loss_ratio, 2), round(avg_gain_r_multiple, 2),
                                     round(avg_loss_r_multiple, 2), round(minimum_trd_mdd, 2),
                                     round(maximum_trd_mdu, 2), round(net_ret_mean_value, 2)]
        result_short_cut_score_list = [round(ent_score_mean_value, 2), round(ex_score_mean_value, 2),
                                       round(trd_score_mean_value, 2)]
        result_short_cut_ev_list = [round(real_expected_value, 2), round(real_expected_value_week, 2),
                                    round(real_expected_value_month, 2), round(real_expected_value_year, 2)]
        result_short_cut_system_list = [round(sharpe_ratio, 2), round(system_quality_number, 2)]
        result_short_cut_holding_list = [round(avg_days_position_holding, 2), len(daily_ret_columns),
                                         round(avg_gain_trading_days, 2), round(avg_loss_trading_days, 2)]
        result_short_cut_cont_list = [round(cont_gain_count, 2), round(cont_loss_count, 2)]
        result_short_cut_error_list = [error_count, dup_count]

        result_short_cut_list = result_short_cut_basic_list + result_short_cut_wr_list + result_short_cut_wlr_list + result_short_cut_score_list + result_short_cut_ev_list + result_short_cut_system_list + result_short_cut_holding_list + result_short_cut_cont_list + result_short_cut_error_list

        result_short_cut = pd.DataFrame([result_short_cut_list])
        result_short_cut.columns = result_short_cut_columns_list
        return result_short_cut


###########################################################################
##                         Parameter Tuning
###########################################################################

class parameter_tuning_box():

    def set_basic_info_variables(self,mpcores,func,country,asset_type, plan, sv_db_name, sv_db_tbl):
        self.mpcores = mpcores
        self.func = func
        self.country = country
        self.asset_type = asset_type
        self.plan = plan
        self.sv_db_name = sv_db_name
        self.sv_db_tbl = sv_db_tbl

        ## Saving Column 관련
        self.strategy_id_columns=['Country','Asset_Type','Func_Name_','Pos_Size_Mode','Initial_Risk','Buy_Fee','Sell_Fee','Slippage','SE_Mode','Ent_TC','Trd_TC','Trd_TC_Var','Ent_Mode','Ent_Var','Ent_Coef','Ent_Req','Ent_Req_Val','LC_Mode','LC_Var','LC_Coef','LC_Req','LC_Req_Val','LC_Upside_Only','GC_Mode','GC_Var','GC_Coef','GC_Req','GC_Req_Val','CGC_Mode','CGC_Var','CGC_Days','CGC_Comp_Lv_Mode','CGC_Comp_Lv_Var','CLC_Mode','CLC_Var','CLC_Days','CLC_Comp_Lv_Mode','CLC_Comp_Lv_Var','FC_Mode','FC_Var','FC_Req','FC_Req_Val']
        self.strategy_id_columns_str = ''
        for s in self.strategy_id_columns:
            self.strategy_id_columns_str + ', {}'.format(s)

    def set_parameter_variables(self,position_size_params,fee_params,se_mode_params,ent_tc_params,trd_tc_params,trd_tc_var_params,ent_mode_params,ent_var_params,ent_coef_params,ent_req_params,lc_mode_params,lc_var_params,lc_coef_params,lc_req_params,lc_upside_only_params,gc_mode_params,gc_var_params,gc_coef_params,gc_req_params,cgc_mode_params,cgc_var_params,cgc_days_params,cgc_comp_level_params,clc_mode_params,clc_var_params,clc_days_params,clc_comp_level_params,fc_mode_params,fc_var_params,fc_req_params):
        self.position_size_params = position_size_params
        self.fee_params = fee_params

        self.se_mode_params = se_mode_params
        self.ent_tc_params = ent_tc_params
        self.trd_tc_params = trd_tc_params
        self.trd_tc_var_params = trd_tc_var_params

        self.ent_mode_params = ent_mode_params
        self.ent_var_params = ent_var_params
        self.ent_coef_params = ent_coef_params
        self.ent_req_params = ent_req_params

        self.lc_mode_params = lc_mode_params
        self.lc_var_params = lc_var_params
        self.lc_coef_params = lc_coef_params
        self.lc_req_params = lc_req_params
        self.lc_upside_only_params = lc_upside_only_params

        self.gc_mode_params = gc_mode_params
        self.gc_var_params = gc_var_params
        self.gc_coef_params = gc_coef_params
        self.gc_req_params = gc_req_params

        self.cgc_mode_params = cgc_mode_params
        self.cgc_var_params = cgc_var_params
        self.cgc_days_params = cgc_days_params
        self.cgc_comp_level_params = cgc_comp_level_params

        self.clc_mode_params = clc_mode_params
        self.clc_var_params = clc_var_params
        self.clc_days_params = clc_days_params
        self.clc_comp_level_params = clc_comp_level_params

        self.fc_mode_params = fc_mode_params
        self.fc_var_params = fc_var_params
        self.fc_req_params = fc_req_params


    def parameter_tuning_combination_generator(self):

        position_size_input_list = list()
        for a in self.position_size_params:
            position_size_input_list.append(a)

        tc_input_comb_list = list()
        for a in self.se_mode_params:
            for b in self.ent_tc_params:
                for c in self.trd_tc_params:
                    for d in self.trd_tc_var_params:
                        tc_input_comb_list.append((a,b,c,d))

        ent_input_comb_list = list()
        for a in self.ent_mode_params:
            for b in self.ent_var_params:
                for c in self.ent_coef_params:
                    for d in self.ent_req_params:
                        ent_input_comb_list.append((a,b,c,d))

        lc_input_comb_list = list()
        for a in self.lc_mode_params:
            for b in self.lc_var_params:
                for c in self.lc_coef_params:
                    for d in self.lc_req_params:
                        for e in self.lc_upside_only_params:
                            lc_input_comb_list.append((a,b,c,d,e))

        gc_input_comb_list = list()
        for a in self.gc_mode_params:
            for b in self.gc_var_params:
                for c in self.gc_coef_params:
                    for d in self.gc_req_params:
                        gc_input_comb_list.append((a,b,c,d))

        cgc_input_comb_list = list()
        for a in self.cgc_mode_params:
            for b in self.cgc_var_params:
                for c in self.cgc_days_params:
                    for d in self.cgc_comp_level_params:
                        cgc_input_comb_list.append((a,b,c,d))

        clc_input_comb_list = list()
        for a in self.clc_mode_params:
            for b in self.clc_var_params:
                for c in self.clc_days_params:
                    for d in self.clc_comp_level_params:
                        clc_input_comb_list.append((a,b,c,d))

        fc_input_comb_list = list()
        for a in self.fc_mode_params:
            for b in self.fc_var_params:
                for c in self.fc_req_params:
                    fc_input_comb_list.append((a, b, c))

        fee_input_list = list()
        for a in self.fee_params:
            fee_input_list.append(a)

        self.params_comb_list = list()
        for a in position_size_input_list:
            for b in fee_input_list:
                for c in tc_input_comb_list:
                    for d in ent_input_comb_list:
                        for e in lc_input_comb_list:
                            for f in gc_input_comb_list:
                                for g in cgc_input_comb_list:
                                    for h in clc_input_comb_list:
                                        for i in fc_input_comb_list:
                                            self.params_comb_list.append([a,b,c,d,e,f,g,h,i])


        ## Total Combination 중 논리적 조건에 맞지 않는 조합 제거

        ## GC var과 LC var이 같을 경우 GC coef > LC coef를 만족해야함

        ## Fixed 이면서 Ent var이 GC var나 LC var와 같을 경우 Ent coef < GC coef 및 Ent coef > LC coef을 만족해야함

        ## GC var이 Ent_Price 일경우 GC_coef > 0을 만족해야함

        ## LC var이 Ent_Price 일경우 LC_coef < 0을 만족해야함

        print('Total Combinations : %s' % len(self.params_comb_list))


    def parameter_tuning_executor(self):

        ## 기존테이블 존재확인 및 중복 값 제거를 위한 데이터 로드

        try:
            existing_id_df = read_sql_table("SELECT %s FROM %s.dbo.%s" % (self.strategy_id_columns_str, self.sv_db_name, self.sv_db_tbl))
        except:
            existing_id_df = pd.DataFrame(columns=self.strategy_id_columns)
            print('DB에 새로운 테이블을 생성합니다')

        ## Parameter Tuning 실행
        inx = 1
        for pc in self.params_comb_list:

            ## 중복여부 검사

            param_comb_frag = [self.country, self.asset_type, self.func.__name__ ]
            for i in range(len(pc)):
                for j in range(len(pc[i])):
                    if ((i >= 3) & (i < 8) & (j == 3)) | ((i==8) & (j==2)):
                        param_comb_frag.append(pc[i][j][0])
                        param_comb_frag.append(pc[i][j][1])
                    else:
                        param_comb_frag.append(pc[i][j])

            param_comb_frag_df = pd.DataFrame([param_comb_frag],columns=self.strategy_id_columns)
            duplication_check = pd.concat([param_comb_frag_df,existing_id_df,existing_id_df]).drop_duplicates()
            if len(duplication_check) == 0:
                inx +=1
                continue

            ## 트레이딩 시뮬레이션 객체 생성

            exp_box = trading_simulation_control_box()
            exp_box.input_control_settings(mpcores=self.mpcores, country=self.country, asset_type=self.asset_type, plan=self.plan,position_size_input=pc[0], ent_input=pc[3], lc_input=pc[4], gc_input=pc[5],cgc_input=pc[6], clc_input=pc[7], fc_input=pc[8], tc_input=pc[2], fee_input=pc[1])

            ## 시뮬레이션 실행

            exp_box.exec_trading_simulation_box_main()

            ## 트레이딩 결과 리포트에 대한 통계분석 출력

            statistical_result = statistical_analysis_of_trading_simulation(report=exp_box.trd_report, drop_duplicates=True, drop_data_errors=True,printing_show=False,graph_show=False, result_return=True)

            total_result_column_list = list(self.strategy_id_columns) + list(statistical_result.columns)
            total_result_list = param_comb_frag + list(statistical_result.iloc[0])
            total_result = pd.DataFrame([total_result_list],columns=total_result_column_list)
            insert_data_into_sql_Table(df=total_result,TBL=self.sv_db_tbl,DB_Name=self.sv_db_name)
            print('Strategy %s / 분석 완료 !'%inx)
            inx += 1


###########################################################################
##                        Plan, Report 스크리너
###########################################################################

## 검색 기간에 따른 스크리닝

def screener_for_period(df, start_date, end_date):

    total_dates_series = pd.Series(generate_day_index_df(start_date=start_date, end_date=end_date).index)
    screened_date_series = total_dates_series.map(lambda x: x.strftime('%Y-%m-%d')).reset_index(drop=True)
    screened_df = df[df['Date_'].isin(screened_date_series)].reset_index(drop=True)
    return screened_df

## 요일에 따른 스크리닝

def screener_for_tdw(df, weekday_list):
    start_date = df['Date_'].min()
    end_date = df['Date_'].max()

    week_day_dict = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6}

    week_day_num_list = [week_day_dict[i] for i in weekday_list]

    total_dates_series = pd.Series(generate_day_index_df(start_date=start_date, end_date=end_date).index)
    specific_weekday_cond = (total_dates_series.map(lambda x: (x.weekday() in week_day_num_list)))
    screened_date_series = total_dates_series[specific_weekday_cond].map(lambda x: x.strftime('%Y-%m-%d')).reset_index(drop=True)

    screened_df = df[df['Date_'].isin(screened_date_series)].reset_index(drop=True)
    return screened_df

## 월별 스크리닝

def screener_for_trading_month(df, month_list):

    start_date = df['Date_'].min()
    end_date = df['Date_'].max()

    total_dates_series = pd.Series(generate_day_index_df(start_date=start_date, end_date=end_date).index)
    screened_date_series = total_dates_series.map(lambda x: x.strftime('%Y-%m-%d'))
    screened_date_series = screened_date_series[screened_date_series.map(lambda x:x[5:7]).isin(month_list)].reset_index(drop=True)

    screened_df = df[df['Date_'].isin(screened_date_series)].reset_index(drop=True)
    return screened_df


## Market Trend에 따른 스크리닝

def screener_for_asset_trend(df, country, asset_type, ticker, mode='Dual',trend_days=3):

    """
    mode : Trend / Beta / Dual
    """

    start_date = datetime.strptime(df['Date_'].min(),'%Y-%m-%d')+timedelta(days=-30)
    end_date = df['Date_'].max()
    asset_price = download_price_data(country=country,asset_type=asset_type,ticker=ticker,start_date=start_date,end_date=end_date,time_period='D')
    asset_price = add_on_technical_indicators(df=asset_price,window=20,price_type='Close_')

    trend_cond = (asset_price['EMA_Trend%s'%trend_days] >= 0)
    beta_cond = (asset_price['EMA'] <= asset_price['Close_'])

    if mode == 'Trend':
        total_cond = trend_cond
    elif mode == 'Beta':
        total_cond = beta_cond
    elif mode == 'Dual':
        total_cond = trend_cond & beta_cond

    screened_date_series = pd.Series(asset_price.index[total_cond]).map(lambda x:x.strftime('%Y-%m-%d'))
    screened_df = df[df['Date_'].isin(screened_date_series)].reset_index(drop=True)

    return screened_df


## 주가, 거래량 범위 스크리닝 결과 통계값

def screener_for_var_range(country,asset_type,func,trd_report,range_var='Close_', range_min_max=(None,None)):

    max_date = trd_report['Date_'].max()
    min_date = trd_report['Date_'].min()

    ## 한국 주식의 경우 시가총액 데이터도 붙여서 불러옴

    if (country == 'KOR') & (asset_type == 'Stock'):
        plan_sql = "SELECT * FROM Real_Analysis.dbo.Plan_%s_%s_%s JOIN (SELECT Date_ AS MC_Date_, Ticker AS MC_Ticker,  Market_Cap FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX) A ON Date_ = MC_Date_ AND Ticker = MC_Ticker WHERE Date_ BETWEEN '%s' AND '%s'" % (country, asset_type, func.__name__, min_date, max_date)
    else:
        plan_sql = "SELECT * FROM Real_Analysis.dbo.Plan_%s_%s_%s WHERE Date_ BETWEEN '%s' AND '%s'"%(country,asset_type,func.__name__,min_date,max_date)
    plan_data_for_report = read_sql_table(sql=plan_sql)

    working_df1 = trd_report.set_index(['Date_','Ticker','Name_'])
    working_df2 = plan_data_for_report.set_index(['Date_','Ticker','Name_'])
    working_df = pd.concat([working_df1,working_df2],axis=1, join_axes=[working_df1.index])
    working_df.reset_index(inplace=True)

    ## 가격 스크리닝

    min_var = range_min_max[0]
    max_var = range_min_max[1]

    if range_min_max[0]==None:
        min_var = 0
    if range_min_max[1]==None:
        max_var = working_df[range_var].max()*10000

    working_df = working_df[(working_df[range_var]>=min_var)&(working_df[range_var]<max_var)]
    working_df = working_df[trd_report.columns].reset_index(drop=True)


    return working_df


## 주가, 거래량, 시가총액 Percentile 스크리닝 결과 통계값

def screener_for_var_percentile(country, asset_type, func, trd_report, pct_var = 'Close_', percentile=(None, None)):

    min_date = trd_report['Date_'].min()
    max_date = trd_report['Date_'].max()

    ## 한국 주식의 경우 시가총액 데이터도 붙여서 불러옴

    if (country == 'KOR') & (asset_type == 'Stock'):
        plan_sql = "SELECT * FROM Real_Analysis.dbo.Plan_%s_%s_%s JOIN (SELECT Date_ AS MC_Date_, Ticker AS MC_Ticker,  Market_Cap FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX) A ON Date_ = MC_Date_ AND Ticker = MC_Ticker WHERE Date_ BETWEEN '%s' AND '%s'" % (country, asset_type, func.__name__, min_date, max_date)
    else:
        plan_sql = "SELECT * FROM Real_Analysis.dbo.Plan_%s_%s_%s WHERE Date_ BETWEEN '%s' AND '%s'"%(country,asset_type,func.__name__,min_date,max_date)
    plan_data_for_report = read_sql_table(sql=plan_sql)

    ## Working df 생성

    working_df1 = trd_report.set_index(['Date_', 'Ticker', 'Name_'])
    working_df2 = plan_data_for_report.set_index(['Date_', 'Ticker', 'Name_'])
    working_df = pd.concat([working_df1, working_df2], axis=1, join_axes=[working_df1.index])

    working_df.reset_index(inplace=True)

    ## Percentile 기준가 Table 생성

    min_pct = percentile[0]
    max_pct = percentile[1]

    if percentile[0] == None:
        min_pct = 0
    if percentile[1] == None:
        max_pct = 1

    key = '%s-%s'%(country,asset_type)
    sql_for_pct_dict = {
        'KOR-Index': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Date_ BETWEEN '%s' AND '%s') A ORDER BY Date_" % (min_pct,pct_var,max_pct,pct_var,min_date, max_date),
        'KOR-Stock': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount, Market_Cap FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX WHERE Market IN ('KOSPI','KOSDAQ') AND Date_ BETWEEN '%s' AND '%s') A ORDER BY Date_" % (min_pct,pct_var,max_pct,pct_var,min_date, max_date),
        'KOR-ETF': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM KOR_Price_Data.dbo.KOR_ETFPriceDataFromNF WHERE Date_ BETWEEN '%s' AND '%s') A ORDER BY Date_" % (min_pct,pct_var,max_pct,pct_var,min_date, max_date),
        'GLOB-Index': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM GLOB_Price_Data.dbo.GLOB_IndexPriceDataFromIV WHERE Date_ BETWEEN '%s' AND '%s') A ORDER BY Date_" % (min_pct,pct_var,max_pct,pct_var,min_date, max_date),
        'GLOB-IndexFutures': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM GLOB_Price_Data.dbo.GLOB_IndexFuturesPriceDataFromIV WHERE Date_ BETWEEN '%s' AND '%s') A ORDER BY Date_" % (min_pct,pct_var,max_pct,pct_var,min_date, max_date),
        'GLOB-FxFutures': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM GLOB_Price_Data.dbo.GLOB_FxFuturesPriceDataFromIV WHERE Date_ BETWEEN '%s' AND '%s') A ORDER BY Date_" % (min_pct,pct_var,max_pct,pct_var,min_date, max_date),
        'GLOB-FxRate': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM GLOB_Price_Data.dbo.GLOB_FxRateDataFromIV WHERE Date_ BETWEEN '%s' AND '%s') A ORDER BY Date_" % (min_pct,pct_var,max_pct,pct_var,min_date, max_date),
        'GLOB-Commodities': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM GLOB_Price_Data.dbo.GLOB_CommoditiesPriceDataFromIV WHERE Date_ BETWEEN '%s' AND '%s') A ORDER BY Date_" % (min_pct,pct_var,max_pct,pct_var,min_date, max_date),
        'KOR-MajorIndex': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM (SELECT * FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Ticker IN ('KOSPI','KOSDAQ지수'))B WHERE Date_ BETWEEN '%s' AND '%s') A ORDER BY Date_" % (min_pct,pct_var,max_pct,pct_var,min_date, max_date),
        'KOR-KOSPI': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM (SELECT * FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Ticker = 'KOSPI')B WHERE Date_ BETWEEN '%s' AND '%s') A ORDER BY Date_" % (min_pct,pct_var,max_pct,pct_var,min_date, max_date),
        'KOR-KOSDAQ': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount FROM (SELECT * FROM KOR_Price_Data.dbo.KOR_IndexPriceDataFromKRX WHERE Ticker = 'KOSDAQ지수')B WHERE Date_ BETWEEN '%s' AND '%s') A ORDER BY Date_" % (min_pct,pct_var,max_pct,pct_var,min_date, max_date),
        'KOR-KSStock': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount, Market_Cap FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX WHERE Market = 'KOSPI' AND Date_ BETWEEN '%s' AND '%s') A ORDER BY Date_" % (min_pct, pct_var, max_pct, pct_var, min_date, max_date),
        'KOR-KQStock': "SELECT DISTINCT Date_,Min_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_),Max_Pct = PERCENTILE_DISC(%s) WITHIN GROUP (ORDER BY %s) OVER (PARTITION BY Date_) FROM (SELECT Date_, Ticker, Open_, High, Low, Close_, Volume, Close_*Volume AS Trd_Amount, Market_Cap FROM KOR_Price_Data.dbo.KOR_StockPriceDataFromKRX WHERE Market = 'KOSDAQ' AND Date_ BETWEEN '%s' AND '%s') A ORDER BY Date_" % (min_pct, pct_var, max_pct, pct_var, min_date, max_date),

        }

    pct_tbl = read_sql_table(sql_for_pct_dict[key])

    ## Percentile 기준가 Table 과 Working df 결합

    working_df = working_df.set_index(['Date_'])
    pct_tbl = pct_tbl.set_index(['Date_'])
    working_df = pd.concat([working_df, pct_tbl], axis=1, join_axes=[working_df.index])
    working_df.reset_index(inplace=True)

    ## Percentile 기준가로 가격 스크리닝


    working_df = working_df[(working_df[pct_var] >= working_df['Min_Pct']) & (working_df[pct_var] < working_df['Max_Pct'])]
    working_df = working_df[trd_report.columns].reset_index(drop=True)

    return working_df


## 임펄스시스템 스크리닝

class screener_for_impulse_system():

    def set_variables(self, mpcores, trd_report, country, asset_type, time_period):

        self.mpcores = mpcores
        if self.mpcores < 1:
            self.mpcores = 1
        self.trd_report = trd_report
        self.trd_report_columns = self.trd_report.columns
        self.empty_df = pd.DataFrame(columns=self.trd_report_columns)
        self.country = country
        self.asset_type = asset_type
        self.time_period = time_period
        self.ultimate_start_date = (datetime.strptime(self.trd_report['Date_'].min(),'%Y-%m-%d')+timedelta(-2000)).strftime('%Y-%m-%d')


    def insert_into_db(self,pre_sv_name, pre_sv_tbl):
        self.sv_db_name = pre_sv_name
        self.sv_db_tbl = "{}_Impulse_System".format(pre_sv_tbl)

        insertion_result = insert_data_into_sql_Table(df=self.screened_trd_report, TBL=self.sv_db_tbl,DB_Name=self.sv_db_name)
        if insertion_result == 1:
            print('Impulse System Screened Data / Insertion / Completed !')
        else:
            print('Impulse System Screened Data / Insertion / Failed. Please recheck !')

    def impulse_system_screener_main(self):

        print('Main Process : {}'.format(os.getpid(),))

        tickers = self.trd_report['Ticker'].drop_duplicates(keep='first').reset_index(drop=True)
        ticker_list = np.array_split(tickers, self.mpcores)

        procs = list()
        self.result_queue = Queue()

        for mc in range(self.mpcores):
            if len(ticker_list[mc]) == 0:
                continue
            proc = Process(target=self.impulse_system_screener_running_loop_exec, args = (ticker_list[mc], self.result_queue))
            procs.append(proc)
            proc.start()

        self.result_list = [self.result_queue.get() for p in range(len(procs))]


        for proc in procs:
            proc.join()
            proc.terminate()

        self.result_queue.close()
        self.result_queue.join_thread()

        self.screened_trd_report = pd.concat(self.result_list).sort_values(by=['Date_', 'Ticker'],ascending=True).reset_index(drop=True)

        print('All Works done')

    def impulse_system_screener_running_loop_exec(self,tickers,result_queue):
        print('Process : {}'.format(os.getpid(),))
        loop = asyncio.get_event_loop()
        result_df = loop.run_until_complete(self.screener_for_impulse_system(tickers))
        result_queue.put(result_df)
        loop.close()

    async def screener_for_impulse_system(self,tickers):

        futures = [asyncio.ensure_future(self.impulse_system_screener_for_single_ticker(self.trd_report[self.trd_report['Ticker']==tk])) for tk in tickers]
        result_df = self.empty_df
        for f in asyncio.as_completed(futures):
            screened_frag = await f
            result_df = result_df.append(screened_frag)

        if len(result_df)==0:
            return result_df
        else:
            return result_df.sort_values(by=['Date_', 'Ticker'],ascending=True).reset_index(drop=True)


    async def impulse_system_screener_for_single_ticker(self, ticker_trd_report):
        ticker = ticker_trd_report['Ticker'].iloc[0]
        ticker_prices = download_price_data(country=self.country, asset_type=self.asset_type, ticker=ticker,start_date=self.ultimate_start_date, end_date=ticker_trd_report['Date_'].max(), time_period='D')
        uts_ticker_prices = prices_into_upper_time_scale_df(ticker_prices, time_period=self.time_period)
        ticker_result_df = self.empty_df
        for inx, row in ticker_trd_report.iterrows():
            searching_date = row['Date_']
            prior_part = uts_ticker_prices[(uts_ticker_prices.index < searching_date)]
            if len(prior_part) == 0:
                continue
            later_part_start_date = (prior_part.index[-1] + timedelta(1)).strftime('%Y-%m-%d')
            later_part_lts = ticker_prices[(ticker_prices.index >= later_part_start_date) & (ticker_prices.index <= searching_date)]
            later_part = prices_into_upper_time_scale_df(later_part_lts)
            later_part.index = [datetime.strptime(searching_date, '%Y-%m-%d')]
            uts_prices = pd.concat([prior_part, later_part])
            uts_prices = add_on_technical_indicators(uts_prices)

            uts_ema_trend = ((uts_prices['EMA_Trend1']).iloc[-1] < 0)
            uts_macd_hist_trend = ((uts_prices['MACD_Histogram_Trend']).iloc[-1] < 0)

            uts_impulse_system = ~(uts_ema_trend & uts_macd_hist_trend)

            if uts_impulse_system == True:
                ticker_result_df = ticker_result_df.append(pd.DataFrame([row]))
            else:
                continue

        return ticker_result_df

## 스크리닝 컨트롤 타워

class screening_control_tower():

    def __init__(self):
        self.input_settings_price_screening()
        self.input_settings_volume_screening()
        self.input_settings_trd_amount_screening()
        self.input_settings_market_cap_screening()
        self.input_settings_volatility_screening()
        self.input_settings_impulse_system_screening()


    def screening_main(self):

        self.screened_report = self.trd_report

        ## 가격 스크리닝

        if self.price_mode=='Off':
            pass
        elif self.price_mode=='Pct':
            self.screened_report = screener_for_var_percentile(country=self.country, asset_type=self.asset_type, func=self.func, trd_report=self.screened_report, pct_var='Close_', percentile=self.price_pct_cond)
        elif self.price_mode=='Range':
            self.screened_report = screener_for_var_range(country=self.country, asset_type=self.asset_type,func=self.func, trd_report=self.screened_report, range_var='Close_',range_min_max=self.price_range_cond)

        ## 거래량 스크리닝

        if self.volume_mode == 'Off':
            pass
        elif self.volume_mode == 'Pct':
            self.screened_report = screener_for_var_percentile(country=self.country, asset_type=self.asset_type,func=self.func, trd_report=self.screened_report,pct_var='Volume', percentile=self.volume_pct_cond)
        elif self.volume_mode == 'Range':
            self.screened_report = screener_for_var_range(country=self.country, asset_type=self.asset_type,func=self.func, trd_report=self.screened_report,range_var='Volume',range_min_max=self.volume_range_cond)

        ## 거래대금 스크리닝

        if self.trd_amount_mode == 'Off':
            pass
        elif self.trd_amount_mode == 'Pct':
            self.screened_report = screener_for_var_percentile(country=self.country, asset_type=self.asset_type,func=self.func, trd_report=self.screened_report,pct_var='Trd_Amount', percentile=self.trd_amount_pct_cond)
        elif self.trd_amount_mode == 'Range':
            self.screened_report = screener_for_var_range(country=self.country, asset_type=self.asset_type,func=self.func, trd_report=self.screened_report,range_var='Trd_Amount',range_min_max=self.trd_amount_range_cond)

        ## 시가총액 스크리닝
        if (self.market_cap_mode == 'Off'):
            pass
        else:
            if (self.asset_type =='Stock')&(self.country=='KOR'):
                if self.market_cap_mode == 'Pct':
                    self.screened_report = screener_for_var_percentile(country=self.country, asset_type=self.asset_type,func=self.func, trd_report=self.screened_report,pct_var='Market_Cap',percentile=self.market_cap_pct_cond)
                elif self.market_cap_mode == 'Range':
                    self.screened_report = screener_for_var_range(country=self.country, asset_type=self.asset_type,func=self.func, trd_report=self.screened_report,range_var='Market_Cap',range_min_max=self.market_cap_range_cond)

        ## 변동성 스크리닝

        if self.volatility_mode == 'Off':
            pass
        elif self.volatility_mode == 'Pct':
            print('변동성 스크리닝은 Pct 모드를 지원하지 않습니다')
        elif self.volatility_mode == 'Range':
            self.screened_report = screener_for_var_range(country=self.country, asset_type=self.asset_type,func=self.func, trd_report=self.screened_report,range_var='ATR%s'%self.volatility_window,range_min_max=self.volatility_range_cond)


        ## Impulse System 스크리닝
        if self.impulse_system_mode == 'Off':
            pass
        elif self.impulse_system_mode == 'On':
            try:
                impulse_sql = "SELECT * FROM %s" % self.impulse_system_db_tbl
                temp_report = self.screened_report.set_index(keys=['Date_','Ticker'])
                impulse_system_report = read_sql_table(sql=impulse_sql)
                impulse_system_report = impulse_system_report.set_index(keys=['Date_','Ticker'])
                temp_report = temp_report[temp_report.index.isin(impulse_system_report.index)]
                temp_report.reset_index(inplace=True)
                self.screened_report = temp_report
            except:
                print('No Screened Data By Impulse System. Please Recheck !')
                pass

        return self.screened_report

    def input_settings_basic_report_info(self,country, asset_type, func, trd_report):
        self.country = country
        self.asset_type = asset_type
        self.func = func
        self.trd_report = trd_report
        self.impulse_system_db_tbl = 'Real_Analysis.dbo.SimResult_%s_%s_%s_Impulse_System'%(country,asset_type,func.__name__)

    def input_settings_price_screening(self,mode='Off',pct_cond=(None,None),range_cond=(None,None)):
        self.price_mode = mode
        self.price_pct_cond = pct_cond
        self.price_range_cond = range_cond

    def input_settings_volume_screening(self,mode='Off',pct_cond=(None,None),range_cond=(None,None)):
        self.volume_mode = mode
        self.volume_pct_cond = pct_cond
        self.volume_range_cond = range_cond

    def input_settings_trd_amount_screening(self,mode='Off',pct_cond=(None,None),range_cond=(None,None)):
        self.trd_amount_mode = mode
        self.trd_amount_pct_cond = pct_cond
        self.trd_amount_range_cond = range_cond

    def input_settings_market_cap_screening(self, mode='Off', pct_cond=(None, None), range_cond=(None, None)):
        self.market_cap_mode = mode
        self.market_cap_pct_cond = pct_cond
        self.market_cap_range_cond = range_cond

    def input_settings_volatility_screening(self, mode='Off', range_cond=(None, None), window=1):
        self.volatility_mode = mode
        self.volatility_range_cond = range_cond
        self.volatility_window = window

    def input_settings_impulse_system_screening(self,mode='Off'):
        self.impulse_system_mode = mode

###########################################################################
##                        스크리닝 결과 분석
###########################################################################

## 그래프에서 적절한 xlabel 개수 및 간격 찾기

def find_proper_label_interval_for_graph(df):
    num_of_labels = 5
    step = 0.1
    result = list()
    while (step != int(step)) & (num_of_labels <= 50):
        step = (len(df) - 1) / num_of_labels
        num_of_labels += 1
        if (step == int(step)):
            result.append((num_of_labels,int(step)))

    if len(result)==0:
        result.append((len(df) - 1,1))

    optimized_result = result[-1]

    return optimized_result

## 분석 결과

def analysis_for_market_trend_screening(trd_report, market_country, market_asset_type, ticker_list, trend_days=5, graph_show=True):
    mode_list = ['Trend', 'Beta', 'Dual']
    var_list = ['Ticker', 'Mode', 'Winning_Ratio', 'Loss_Gain_Ratio', 'Total_Expected_Value_Annually', 'SQN',
                'Sharpe_Ratio', 'Net_Ret_MV', 'Trd_Expected_Value', 'Ent_Score_MV', 'Ex_Score_MV', 'Trd_Score_MV',
                'Trd_Count']
    result_list = list()
    for ticker in ticker_list:
        for mode in mode_list:
            screening_by_mt = screener_for_asset_trend(df=trd_report, country=market_country,asset_type=market_asset_type, ticker=ticker, mode=mode,trend_days=trend_days)
            market_trend_analysis = statistical_analysis_of_trading_simulation(report=screening_by_mt,
                                                                                        drop_duplicates=True,
                                                                                        drop_data_errors=True,
                                                                                        printing_show=False,
                                                                                        graph_show=False,
                                                                                        result_return=True)
            market_trend_analysis['Ticker'] = ticker
            market_trend_analysis['Mode'] = mode
            market_trend_analysis = market_trend_analysis[var_list]
            result_list.append(market_trend_analysis)

    result_df = pd.concat(result_list).reset_index(drop=True)

    if graph_show == True:
        pass

    return result_df


## Trading Day Of Week (요일별 트레이딩 결과)

def analysis_for_tdw_screening(trd_report,graph_show):

    week_dict = {0:'Mon',1:'Tue',2:'Wed',3:'Thu',4:'Fri',5:'Sat',6:'Sun'}

    week_collection = list()
    week_collection_list = list()
    week_ds = trd_report['Date_'].map(lambda x:datetime.strptime(x,'%Y-%m-%d').weekday()).drop_duplicates(keep='first').sort_values().reset_index(drop=True)
    for w in week_ds:
        week_collection.append([week_dict[w]])
        week_collection_list.append(week_dict[w])

    weekday_stats = list()
    for wc in week_collection:
        weekday_list = wc
        screened_trd_report = screener_for_tdw(df=trd_report, weekday_list=weekday_list)
        statistical_result_frag = statistical_analysis_of_trading_simulation(report=screened_trd_report,drop_duplicates=True,drop_data_errors=True, printing_show=False,graph_show=False, result_return=True)
        statistical_result_frag['TDW']=wc[0]
        weekday_stats.append(statistical_result_frag)

    weekday_stats_df = pd.concat(weekday_stats).reset_index(drop=True)
    result_columns = [weekday_stats_df.columns[-1]] + list(weekday_stats_df.columns[0:-1])
    weekday_stats_df = weekday_stats_df[result_columns]


    ## TDW 그래프를 위한 전처리
    weekday_stats_df_for_graph = weekday_stats_df
    weekday_stats_df_for_graph['Zero_Line'] = pd.DataFrame(data=np.zeros(weekday_stats_df_for_graph.shape[0]),
                                                           index=list(weekday_stats_df_for_graph.index),
                                                           columns=['Zero_Line'])
    if graph_show==True:

        ## 요일에 따른 통계값 그래프 그리기
        row_num = 3
        col_num = 2
        fig, axes = plt.subplots(row_num, col_num, figsize=(13, 12))

        ## 승률
        wr_max = 110
        wr_min = 0

        axes[0,0].set_title('Winning Ratio - TDW')
        weekday_stats_df_for_graph['Winning_Ratio'].plot(ax=axes[0,0], kind='bar',legend=None, alpha=0.5, color='red', ylim=(0, wr_max))
        weekday_stats_df_for_graph['Zero_Line'].plot(ax=axes[0,0], kind='bar', legend=None, alpha=0.5, color='black',ylim=(0, wr_max))

        ## 손익비
        lgr_max = weekday_stats_df_for_graph['Loss_Gain_Ratio'].max() + 0.5
        lgr_min = weekday_stats_df_for_graph['Loss_Gain_Ratio'].min() - 0.5
        if weekday_stats_df_for_graph['Loss_Gain_Ratio'].min() >= 0:
            lgr_min = 0

        axes[0,1].set_title('Loss-Gain Ratio - TDW')
        weekday_stats_df_for_graph['Loss_Gain_Ratio'].plot(ax=axes[0,1], kind='bar',legend=None, alpha=0.5, color='darkorange',ylim=(0, lgr_max))
        weekday_stats_df_for_graph['Zero_Line'].plot(ax=axes[0,1], kind='bar', legend=None, alpha=0.5, color='black',ylim=(0, lgr_max))

        ## 거래당 기대값
        ev_max = weekday_stats_df_for_graph['Trd_Expected_Value'].max() + 0.1
        ev_min = weekday_stats_df_for_graph['Trd_Expected_Value'].min() - 0.1
        if weekday_stats_df_for_graph['Trd_Expected_Value'].min() >= 0:
            ev_min = 0

        axes[1,0].set_title('Expected Value Per Trading - TDW')
        weekday_stats_df_for_graph['Trd_Expected_Value'].plot(ax=axes[1,0], kind='bar', legend=None, alpha=0.4,color='darkgreen', ylim=(ev_min, ev_max))
        weekday_stats_df_for_graph['Zero_Line'].plot(ax=axes[1,0], kind='bar', legend=None, alpha=0.5, color='black',ylim=(ev_min, ev_max))

        ## 연간 기대값
        eva_max = weekday_stats_df_for_graph['Total_Expected_Value_Annually'].max() + 2
        eva_min = weekday_stats_df_for_graph['Total_Expected_Value_Annually'].min() - 2
        if weekday_stats_df_for_graph['Total_Expected_Value_Annually'].min() >= 0:
            eva_min = 0

        axes[1,1].set_title('Expected Value Annually - TDW')
        weekday_stats_df_for_graph['Total_Expected_Value_Annually'].plot(ax=axes[1, 1], kind='bar', legend=None, alpha=0.5,color='darkgreen', ylim=(eva_min, eva_max))
        weekday_stats_df_for_graph['Zero_Line'].plot(ax=axes[1, 1], kind='bar', legend=None, alpha=0.5, color='black',ylim=(eva_min, eva_max))

        ## Sharpe Ratio
        sr_max = weekday_stats_df_for_graph['Sharpe_Ratio'].max() + 0.03
        sr_min = weekday_stats_df_for_graph['Sharpe_Ratio'].min() - 0.03
        if weekday_stats_df_for_graph['Sharpe_Ratio'].min() >= 0:
            sr_min = 0

        axes[2, 0].set_title('Sharpe Ratio - TDW')
        weekday_stats_df_for_graph['Sharpe_Ratio'].plot(ax=axes[2, 0], kind='bar', legend=None, alpha=0.4,color='navy', ylim=(sr_min, sr_max))
        weekday_stats_df_for_graph['Zero_Line'].plot(ax=axes[2, 0], kind='bar', legend=None, alpha=0.5, color='black',ylim=(sr_min, sr_max))

        ## SQN
        sq_max = weekday_stats_df_for_graph['SQN'].max() + 0.03
        sq_min = weekday_stats_df_for_graph['SQN'].min() - 0.03
        if weekday_stats_df_for_graph['SQN'].min() >= 0:
            sq_min = 0

        axes[2, 1].set_title('SQN - TDW')
        weekday_stats_df_for_graph['SQN'].plot(ax=axes[2, 1], kind='bar', legend=None, alpha=0.5,color='navy', ylim=(sq_min, sq_max))
        weekday_stats_df_for_graph['Zero_Line'].plot(ax=axes[2, 1], kind='bar', legend=None, alpha=0.5, color='black',ylim=(sq_min, sq_max))

        ## 그래프 정리
        for c in range(col_num):
            for r in range(row_num):
                axes[r,c].xaxis.set_major_locator(plt.MaxNLocator(int(len(weekday_stats_df_for_graph))))
                axes[r,c].grid(color='black', linestyle='dashed', linewidth=0.3, alpha=0.2)
                axes[r,c].set_xticklabels([])
                if r == (row_num - 1):
                    axes[r,c].set_xticklabels(['Mon']+week_collection_list, rotation=0, fontsize=9)

    return weekday_stats_df_for_graph

## Trading Day Of Month (월간 거래일별 트레이딩 결과)

def analysis_for_trading_month_screening(trd_report,graph_show):

    month_dict = {'01': 'Jan', '02': 'Feb', '03': 'Mar', '04': 'Apr', '05': 'May', '06': 'Jun', '07': 'Jul',
                  '08': 'Aug', '09': 'Sep', '10': 'Oct', '11': 'Nov', '12': 'Dec'}
    month_collection = list()
    month_collection_list = list()
    month_ds = trd_report['Date_'].map(lambda x: x[5:7]).drop_duplicates(keep='first').sort_values(ascending=True).reset_index(drop=True)
    for m in month_ds:
        month_collection.append([m])
        month_collection_list.append(month_dict[m])

    monthly_stats = list()
    for mc in month_collection:
        month_list = mc
        screened_trd_report = screener_for_trading_month(df=trd_report, month_list=month_list)
        statistical_result_frag = statistical_analysis_of_trading_simulation(report=screened_trd_report,drop_duplicates=True,drop_data_errors=True, printing_show=False,graph_show=False, result_return=True)
        monthly_stats.append(statistical_result_frag)

    monthly_stats_df =pd.concat(monthly_stats).reset_index(drop=True)
    monthly_stats_df.index = list(month_ds.map(lambda x:int(x)))

    ## TM Statistics 그래프를 위한 전처리
    month_stats_df_for_graph = monthly_stats_df
    month_stats_df_for_graph['Zero_Line'] = pd.DataFrame(data=np.zeros(month_stats_df_for_graph.shape[0]),
                                                           index=list(month_stats_df_for_graph.index),
                                                           columns=['Zero_Line'])
    if graph_show==True:

        ## 달에 따른 통계값 그래프 그리기
        row_num = 3
        col_num = 2
        fig, axes = plt.subplots(row_num, col_num, figsize=(13, 12))

        ## 승률
        wr_max = 110
        wr_min = 0

        axes[0,0].set_title('Winning Ratio - TM')
        month_stats_df_for_graph['Winning_Ratio'].plot(ax=axes[0,0], kind='bar',legend=None, alpha=0.5, color='red', ylim=(0, wr_max))
        month_stats_df_for_graph['Zero_Line'].plot(ax=axes[0,0], kind='bar', legend=None, alpha=0.5, color='black',ylim=(0, wr_max))

        ## 손익비
        lgr_max = month_stats_df_for_graph['Loss_Gain_Ratio'].max() + 0.5
        lgr_min = month_stats_df_for_graph['Loss_Gain_Ratio'].min() - 0.5
        if month_stats_df_for_graph['Loss_Gain_Ratio'].min() >= 0:
            lgr_min = 0

        axes[0,1].set_title('Loss-Gain Ratio - TM')
        month_stats_df_for_graph['Loss_Gain_Ratio'].plot(ax=axes[0,1], kind='bar',legend=None, alpha=0.5, color='darkorange',ylim=(0, lgr_max))
        month_stats_df_for_graph['Zero_Line'].plot(ax=axes[0,1], kind='bar', legend=None, alpha=0.5, color='black',ylim=(0, lgr_max))

        ## 거래당 기대값
        ev_max = month_stats_df_for_graph['Trd_Expected_Value'].max() + 0.1
        ev_min = month_stats_df_for_graph['Trd_Expected_Value'].min() - 0.1
        if month_stats_df_for_graph['Trd_Expected_Value'].min() >= 0:
            ev_min = 0

        axes[1,0].set_title('Expected Value Per Trading - TM')
        month_stats_df_for_graph['Trd_Expected_Value'].plot(ax=axes[1,0], kind='bar', legend=None, alpha=0.4,color='darkgreen', ylim=(ev_min, ev_max))
        month_stats_df_for_graph['Zero_Line'].plot(ax=axes[1,0], kind='bar', legend=None, alpha=0.5, color='black',ylim=(ev_min, ev_max))

        ## 연간 기대값
        eva_max = month_stats_df_for_graph['Total_Expected_Value_Annually'].max() + 2
        eva_min = month_stats_df_for_graph['Total_Expected_Value_Annually'].min() - 2
        if month_stats_df_for_graph['Total_Expected_Value_Annually'].min() >= 0:
            eva_min = 0

        axes[1,1].set_title('Expected Value Annually - TM')
        month_stats_df_for_graph['Total_Expected_Value_Annually'].plot(ax=axes[1, 1], kind='bar', legend=None, alpha=0.5,color='darkgreen', ylim=(eva_min, eva_max))
        month_stats_df_for_graph['Zero_Line'].plot(ax=axes[1, 1], kind='bar', legend=None, alpha=0.5, color='black',ylim=(eva_min, eva_max))

        ## Sharpe Ratio
        sr_max = month_stats_df_for_graph['Sharpe_Ratio'].max() + 0.03
        sr_min = month_stats_df_for_graph['Sharpe_Ratio'].min() - 0.03
        if month_stats_df_for_graph['Sharpe_Ratio'].min() >= 0:
            sr_min = 0

        axes[2,0].set_title('Sharpe Ratio - TM')
        month_stats_df_for_graph['Sharpe_Ratio'].plot(ax=axes[2,0], kind='bar', legend=None, alpha=0.4,color='navy', ylim=(sr_min, sr_max))
        month_stats_df_for_graph['Zero_Line'].plot(ax=axes[2,0], kind='bar', legend=None, alpha=0.5, color='black',ylim=(sr_min, sr_max))

        ## SQN
        sq_max = month_stats_df_for_graph['SQN'].max() + 0.03
        sq_min = month_stats_df_for_graph['SQN'].min() - 0.03
        if month_stats_df_for_graph['SQN'].min() >= 0:
            sq_min = 0

        axes[2,1].set_title('SQN - TM')
        month_stats_df_for_graph['SQN'].plot(ax=axes[2,1], kind='bar', legend=None, alpha=0.5,color='navy', ylim=(sq_min, sq_max))
        month_stats_df_for_graph['Zero_Line'].plot(ax=axes[2,1], kind='bar', legend=None, alpha=0.5, color='black',ylim=(sq_min, sq_max))

        ## 그래프 정리
        for c in range(col_num):
            for r in range(row_num):
                axes[r,c].xaxis.set_major_locator(plt.MaxNLocator(int(len(month_stats_df_for_graph))))
                axes[r,c].grid(color='black', linestyle='dashed', linewidth=0.3, alpha=0.2)
                axes[r,c].set_xticklabels([])
                if r == (row_num - 1):
                    axes[r,c].set_xticklabels(['Mon']+month_collection_list, rotation=0, fontsize=9)

    return month_stats_df_for_graph

## N개월 Rolling (Rolling 통계값)

def analysis_for_rolling_screening(trd_report,months_window,graph_show):

    end_date = trd_report['Date_'].max()
    start_date = trd_report['Date_'].min()

    rolling_end_date = (datetime.strptime(end_date,'%Y-%m-%d')).strftime('%Y-%m-%d')
    rolling_start_date = (datetime.strptime(start_date,'%Y-%m-%d') + relativedelta(months=1)).strftime('%Y-%m-%d')

    rolling_date_frags = date_period_fragments(start=rolling_start_date, end=rolling_end_date, months_window=months_window)

    rolling_stats_result_list = list()
    for rdf in rolling_date_frags:
        screened_trd_report_frag = screener_for_period(df=trd_report, start_date=rdf[0], end_date=rdf[1])
        rolling_stats_result_frag = statistical_analysis_of_trading_simulation(report=screened_trd_report_frag,drop_duplicates=True,drop_data_errors=True,printing_show=False,graph_show=False, result_return=True)
        rolling_stats_result_list.append(rolling_stats_result_frag)

    rolling_stats_df = pd.concat(rolling_stats_result_list).reset_index(drop=True)


    ## rolling 통계값들에 대한 통계분석
    var_list = ['Winning_Ratio', 'Loss_Gain_Ratio','Trd_Expected_Value','Total_Expected_Value_Annually', 'Sharpe_Ratio','SQN',
                'Net_Ret_MV', 'Ent_Score_MV', 'Ex_Score_MV', 'Trd_Score_MV', 'Trd_Count']
    result_tbl = list()
    for var in var_list:
        max_v = rolling_stats_df[var].max()
        min_v = rolling_stats_df[var].min()
        m = rolling_stats_df[var].mean()
        s = rolling_stats_df[var].std()
        cv = s / m
        result_tbl.append(['%sM'%months_window,var, min_v, max_v, m, s, cv])

    result_tbl_df = pd.DataFrame(result_tbl)
    result_tbl_df.columns = ['Rolling_Period','Variable','Min_Value', 'Max_Value', 'Mean_Value', 'Stdev', 'Coef_Of_Var']


    ## Rolling Statistics 그래프를 위한 전처리
    x_labels_list = list(rolling_stats_df['End_Date_'])
    rolling_stats_df_for_graph = rolling_stats_df
    rolling_stats_df_for_graph['Zero_Line'] = pd.DataFrame(data=np.zeros(rolling_stats_df_for_graph.shape[0]),index=list(rolling_stats_df_for_graph.index),columns=['Zero_Line'])


    if graph_show == True:

        ## Rolling 에 따른 통계값 그래프 그리기
        row_num = 3
        col_num = 2
        fig, axes = plt.subplots(row_num, col_num, figsize=(13, 12))

        ## 승률
        wr_max = 110
        wr_min = 0

        axes[0,0].set_title('Winning Ratio - Rolling %s Months '%months_window)
        rolling_stats_df_for_graph['Winning_Ratio'].plot(ax=axes[0,0], kind='bar',legend=None, alpha=0.5, color='red', ylim=(0, wr_max))
        rolling_stats_df_for_graph['Zero_Line'].plot(ax=axes[0,0], kind='bar', legend=None, alpha=0.5, color='black',ylim=(0, wr_max))

        ## 손익비
        lgr_max = rolling_stats_df_for_graph['Loss_Gain_Ratio'].max() + 0.5
        lgr_min = rolling_stats_df_for_graph['Loss_Gain_Ratio'].min() - 0.5
        if rolling_stats_df_for_graph['Loss_Gain_Ratio'].min() >= 0:
            lgr_min = 0

        axes[0,1].set_title('Loss-Gain Ratio - Rolling %s Months '%months_window)
        rolling_stats_df_for_graph['Loss_Gain_Ratio'].plot(ax=axes[0,1], kind='bar',legend=None, alpha=0.5, color='darkorange',ylim=(0, lgr_max))
        rolling_stats_df_for_graph['Zero_Line'].plot(ax=axes[0,1], kind='bar', legend=None, alpha=0.5, color='black',ylim=(0, lgr_max))

        ## 거래당 기대값
        ev_max = rolling_stats_df_for_graph['Trd_Expected_Value'].max() + 0.1
        ev_min = rolling_stats_df_for_graph['Trd_Expected_Value'].min() - 0.1
        if rolling_stats_df_for_graph['Trd_Expected_Value'].min() >= 0:
            ev_min = 0

        axes[1,0].set_title('Expected Value Per Trading - Rolling %s Months '%months_window)
        rolling_stats_df_for_graph['Trd_Expected_Value'].plot(ax=axes[1,0], kind='bar', legend=None, alpha=0.4,color='darkgreen', ylim=(ev_min, ev_max))
        rolling_stats_df_for_graph['Zero_Line'].plot(ax=axes[1,0], kind='bar', legend=None, alpha=0.5, color='black',ylim=(ev_min, ev_max))

        ## 연간 기대값
        eva_max = rolling_stats_df_for_graph['Total_Expected_Value_Annually'].max() + 2
        eva_min = rolling_stats_df_for_graph['Total_Expected_Value_Annually'].min() - 2
        if rolling_stats_df_for_graph['Total_Expected_Value_Annually'].min() >= 0:
            eva_min = 0

        axes[1,1].set_title('Expected Value Annually - Rolling %s Months '%months_window)
        rolling_stats_df_for_graph['Total_Expected_Value_Annually'].plot(ax=axes[1, 1], kind='bar', legend=None, alpha=0.5,color='darkgreen', ylim=(eva_min, eva_max))
        rolling_stats_df_for_graph['Zero_Line'].plot(ax=axes[1, 1], kind='bar', legend=None, alpha=0.5, color='black',ylim=(eva_min, eva_max))

        ## Sharpe Ratio
        sr_max = rolling_stats_df_for_graph['Sharpe_Ratio'].max() + 0.03
        sr_min = rolling_stats_df_for_graph['Sharpe_Ratio'].min() - 0.03
        if rolling_stats_df_for_graph['Sharpe_Ratio'].min() >= 0:
            sr_min = 0

        axes[2, 0].set_title('Sharpe Ratio - Rolling %s Months '%months_window)
        rolling_stats_df_for_graph['Sharpe_Ratio'].plot(ax=axes[2, 0], kind='bar', legend=None, alpha=0.4,color='navy', ylim=(sr_min, sr_max))
        rolling_stats_df_for_graph['Zero_Line'].plot(ax=axes[2, 0], kind='bar', legend=None, alpha=0.5, color='black',ylim=(sr_min, sr_max))

        ## SQN
        sq_max = rolling_stats_df_for_graph['SQN'].max() + 0.03
        sq_min = rolling_stats_df_for_graph['SQN'].min() - 0.03
        if rolling_stats_df_for_graph['SQN'].min() >= 0:
            sq_min = 0

        axes[2, 1].set_title('SQN - Rolling %s Months '%months_window)
        rolling_stats_df_for_graph['SQN'].plot(ax=axes[2, 1], kind='bar', legend=None, alpha=0.5,color='navy', ylim=(sq_min, sq_max))
        rolling_stats_df_for_graph['Zero_Line'].plot(ax=axes[2, 1], kind='bar', legend=None, alpha=0.5, color='black',ylim=(sq_min, sq_max))

        ## 그래프 정리

        xlabel_conf = find_proper_label_interval_for_graph(df=rolling_stats_df_for_graph)

        for c in range(col_num):
            for r in range(row_num):
                axes[r,c].xaxis.set_major_locator(plt.MultipleLocator(xlabel_conf[1]))
                axes[r,c].grid(color='black', linestyle='dashed', linewidth=0.3, alpha=0.2)
                axes[r,c].set_xticklabels([])
                if (r == (row_num - 1))&(xlabel_conf[1]!=1):
                    axes[r,c].set_xticklabels([start_date]+x_labels_list[::xlabel_conf[1]], rotation=90, fontsize=6)


    return result_tbl_df

## 특정 기간별 결과 통계값

def analysis_for_specific_period_screening(trd_report, period_mode, printing_show,graph_show=False):
    end_date = trd_report['Date_'].max()

    ## 최근 성과

    if period_mode == 'Recent6m':
        screened_start_date = (datetime.strptime(end_date, '%Y-%m-%d') + relativedelta(months=-6)).strftime('%Y-%m-%d')
        screened_end_date = end_date

    elif period_mode == 'Recent1yr':
        screened_start_date = (datetime.strptime(end_date, '%Y-%m-%d') + relativedelta(years=-1)).strftime('%Y-%m-%d')
        screened_end_date = end_date

    elif period_mode == 'Recent2yr':
        screened_start_date = (datetime.strptime(end_date, '%Y-%m-%d') + relativedelta(years=-2)).strftime('%Y-%m-%d')
        screened_end_date = end_date

    elif period_mode == 'Recent3yr':
        screened_start_date = (datetime.strptime(end_date, '%Y-%m-%d') + relativedelta(years=-3)).strftime('%Y-%m-%d')
        screened_end_date = end_date

    ## 2008 금융위기 부근
    elif period_mode == 'FC_Whole':
        screened_start_date = '2007-11-15'
        screened_end_date = '2009-03-10'

    ## 2008 금융위기 절정
    elif period_mode == 'FC_Climax':
        screened_start_date = '2008-09-15'
        screened_end_date = '2008-10-30'

    screened_trd_report = screener_for_period(df=trd_report, start_date=screened_start_date, end_date=screened_end_date)
    result_df = statistical_analysis_of_trading_simulation(report=screened_trd_report, drop_duplicates=True,
                                                                    drop_data_errors=True, printing_show=printing_show,
                                                                    graph_show=False, result_return=True)

    if graph_show == True:
        pass

    return result_df


def analysis_for_specific_period_screening_batch(trd_report, graph_show=False):
    period_mode_list = ['Recent6m','Recent1yr','Recent2yr','Recent3yr', 'FC_Whole', 'FC_Climax']
    var_list = ['Period_Mode', 'Winning_Ratio', 'Loss_Gain_Ratio','Trd_Expected_Value', 'Total_Expected_Value_Annually', 'Sharpe_Ratio','SQN','Net_Ret_MV', 'Ent_Score_MV', 'Ex_Score_MV', 'Trd_Score_MV','Trd_Count']
    result_list = list()
    for pm in period_mode_list:
        sps_frag = analysis_for_specific_period_screening(trd_report=trd_report, period_mode=pm,printing_show=False,
                                                                 graph_show=False)
        sps_frag['Period_Mode'] = pm
        sps_frag = sps_frag[var_list]
        result_list.append(sps_frag)

    result_df = pd.concat(result_list).reset_index(drop=True)

    if graph_show == True:
        pass

    return result_df

## 가격, 거래량, 거래대금 스크리닝 분석

class analysis_for_screening_effect():

    def input_settings_screening_effect(self,trd_report, country, asset_type, func, mode, div_num, graph_show=False):
        self.trd_report = trd_report
        self.country = country
        self.asset_type = asset_type
        self.func = func
        self.mode = mode
        self.div_num = div_num
        self.graph_show = graph_show
        self.output_columns = ['Min_Pct', 'Max_Pct', 'Trd_Count', 'Winning_Ratio', 'Loss_Gain_Ratio', 'Trd_Expected_Value','Total_Expected_Value_Annually', 'Sharpe_Ratio', 'SQN']
        self.impulse_output_columns = ['Impulse_System_Mode', 'Trd_Count', 'Winning_Ratio', 'Loss_Gain_Ratio','Trd_Expected_Value', 'Total_Expected_Value_Annually', 'Sharpe_Ratio', 'SQN']
        self.step = round(1/div_num,4)

        self.original_result_df = statistical_analysis_of_trading_simulation(report=trd_report, drop_duplicates=True, drop_data_errors=True,printing_show=False, graph_show=False, result_return=True)
        self.original_result_df['Impulse_System_Mode'] = 'Off'

        self.price_result_df = pd.DataFrame(columns=self.output_columns)

    def screening_analysis_mode_controller(self,min_pct, max_pct, step):
        if self.mode == 'Min_Limit':
            min_pct += step
        elif self.mode == 'Max_Limit':
            max_pct -= step
        elif self.mode == 'Step_Limit':
            min_pct += step
            max_pct += step
        return round(min_pct,2), round(max_pct,2)

    ## Analysis

    def analysis_for_price_screening(self):

        trd_report = self.trd_report

        # Price
        min_pct = 0
        mode_dict = {'Min_Lim':1,'Max_Lim':1,'Step_Limit':min_pct+self.step}
        max_pct = mode_dict[self.mode]
        self.price_result_df = pd.DataFrame(columns=self.output_columns)
        for n in range(self.div_num):
            sc_ef = screening_control_tower()
            sc_ef.input_settings_basic_report_info(country=self.country,asset_type=self.asset_type,func=self.func,trd_report=trd_report)
            sc_ef.input_settings_price_screening(mode='Pct',pct_cond=(min_pct,max_pct),range_cond=(None,None))
            report_frag = sc_ef.screening_main()
            if len(report_frag)==0:
                min_pct, max_pct = self.screening_analysis_mode_controller(min_pct=min_pct, max_pct=max_pct,step=self.step)
                continue
            stats_result_frag = statistical_analysis_of_trading_simulation(report=report_frag, drop_duplicates=True,drop_data_errors=True, printing_show=False,graph_show=False, result_return=True)
            stats_result_frag['Min_Pct'] = min_pct
            stats_result_frag['Max_Pct'] = max_pct
            stats_result_frag = stats_result_frag[self.output_columns]

            self.price_result_df = self.price_result_df.append(stats_result_frag)
            min_pct,max_pct = self.screening_analysis_mode_controller(min_pct=min_pct, max_pct=max_pct, step=self.step)


    def analysis_for_volume_screening(self):

        trd_report = self.trd_report

        # Volume
        min_pct = 0
        mode_dict = {'Min_Lim':1,'Max_Lim':1,'Step_Limit':min_pct+self.step}
        max_pct = mode_dict[self.mode]

        self.volume_result_df = pd.DataFrame(columns=self.output_columns)
        for n in range(self.div_num):
            sc_ef = screening_control_tower()
            sc_ef.input_settings_basic_report_info(country=self.country,asset_type=self.asset_type,func=self.func,trd_report=trd_report)
            sc_ef.input_settings_volume_screening(mode='Pct',pct_cond=(min_pct,max_pct),range_cond=(None,None))
            report_frag = sc_ef.screening_main()
            print('Volume / Min : %s / Max : %s'%(min_pct,max_pct))
            print('Report Length : %s'%len(report_frag))
            if len(report_frag)==0:
                min_pct, max_pct = self.screening_analysis_mode_controller(min_pct=min_pct, max_pct=max_pct,step=self.step)
                continue
            stats_result_frag = statistical_analysis_of_trading_simulation(report=report_frag, drop_duplicates=True,drop_data_errors=True, printing_show=False,graph_show=False, result_return=True)
            stats_result_frag['Min_Pct'] = min_pct
            stats_result_frag['Max_Pct'] = max_pct
            stats_result_frag = stats_result_frag[self.output_columns]

            self.volume_result_df = self.volume_result_df.append(stats_result_frag)
            min_pct,max_pct = self.screening_analysis_mode_controller(min_pct=min_pct, max_pct=max_pct, step=self.step)


    def analysis_for_trd_amount_screening(self):

        trd_report = self.trd_report

        # Trd_Amount
        min_pct = 0
        mode_dict = {'Min_Lim':1,'Max_Lim':1,'Step_Limit':min_pct+self.step}
        max_pct = mode_dict[self.mode]

        self.trd_amount_result_df = pd.DataFrame(columns=self.output_columns)
        for n in range(self.div_num):
            sc_ef = screening_control_tower()
            sc_ef.input_settings_basic_report_info(country=self.country,asset_type=self.asset_type,func=self.func,trd_report=trd_report)
            sc_ef.input_settings_trd_amount_screening(mode='Pct',pct_cond=(min_pct,max_pct),range_cond=(None,None))
            report_frag = sc_ef.screening_main()
            print('Trd_Amount / Min : %s / Max : %s'%(min_pct,max_pct))
            print('Report Length : %s'%len(report_frag))
            if len(report_frag)==0:
                min_pct, max_pct = self.screening_analysis_mode_controller(min_pct=min_pct, max_pct=max_pct,step=self.step)
                continue
            stats_result_frag = statistical_analysis_of_trading_simulation(report=report_frag, drop_duplicates=True,drop_data_errors=True, printing_show=False,graph_show=False, result_return=True)
            stats_result_frag['Min_Pct'] = min_pct
            stats_result_frag['Max_Pct'] = max_pct
            stats_result_frag = stats_result_frag[self.output_columns]

            self.trd_amount_result_df = self.trd_amount_result_df.append(stats_result_frag)
            min_pct,max_pct = self.screening_analysis_mode_controller(min_pct=min_pct, max_pct=max_pct, step=self.step)


    def analysis_for_market_cap_screening(self):

        trd_report = self.trd_report

        # Trd_Amount
        min_pct = 0
        mode_dict = {'Min_Lim':1,'Max_Lim':1,'Step_Limit':min_pct+self.step}
        max_pct = mode_dict[self.mode]

        self.market_cap_result_df = pd.DataFrame(columns=self.output_columns)
        for n in range(self.div_num):
            sc_ef = screening_control_tower()
            sc_ef.input_settings_basic_report_info(country=self.country,asset_type=self.asset_type,func=self.func,trd_report=trd_report)
            sc_ef.input_settings_market_cap_screening(mode='Pct',pct_cond=(min_pct,max_pct),range_cond=(None,None))
            report_frag = sc_ef.screening_main()
            print('Market_Cap / Min : %s / Max : %s'%(min_pct,max_pct))
            print('Report Length : %s'%len(report_frag))
            if len(report_frag)==0:
                min_pct, max_pct = self.screening_analysis_mode_controller(min_pct=min_pct, max_pct=max_pct,step=self.step)
                continue
            stats_result_frag = statistical_analysis_of_trading_simulation(report=report_frag, drop_duplicates=True,drop_data_errors=True, printing_show=False,graph_show=False, result_return=True)
            stats_result_frag['Min_Pct'] = min_pct
            stats_result_frag['Max_Pct'] = max_pct
            stats_result_frag = stats_result_frag[self.output_columns]

            self.market_cap_result_df = self.market_cap_result_df.append(stats_result_frag)
            min_pct,max_pct = self.screening_analysis_mode_controller(min_pct=min_pct, max_pct=max_pct, step=self.step)


    def analysis_for_impulse_system_screening(self):

        trd_report = self.trd_report

        # Impulse_System
        impulse_system_result = list()
        impulse_system_result.append(self.original_result_df)

        sc_ef = screening_control_tower()
        sc_ef.input_settings_basic_report_info(country=self.country, asset_type=self.asset_type, func=self.func, trd_report=trd_report)
        sc_ef.input_settings_impulse_system_screening(mode='On')
        report_frag = sc_ef.screening_main()
        impulse_system_result_df = statistical_analysis_of_trading_simulation(report=report_frag, drop_duplicates=True,drop_data_errors=True, printing_show=False,graph_show=False, result_return=True)
        impulse_system_result_df['Impulse_System_Mode'] = 'On'
        impulse_system_result.append(impulse_system_result_df)

        self.impulse_system_result_df = pd.concat(impulse_system_result).reset_index(drop=True)
        self.impulse_system_result_df = self.impulse_system_result_df[self.impulse_output_columns]


    def analysis_for_screening_effect_main(self):

        self.analysis_for_price_screening()
        self.analysis_for_volume_screening()
        self.analysis_for_trd_amount_screening()
        self.analysis_for_impulse_system_screening()
        self.result_dict = {'Price':self.price_result_df,'Volume':self.volume_result_df,'Trd_Amount':self.trd_amount_result_df,'Market_Cap':pd.DataFrame(columns=self.output_columns),'Impulse_System':self.impulse_system_result_df}


        ## KOR Stock 에서는 시가총액을 이용한 스크리닝분석 시행

        if (self.country == 'KOR')&(self.asset_type == 'Stock'):
            self.analysis_for_market_cap_screening()
            self.result_dict['Market_Cap'] = self.market_cap_result_df

        ## 그래프 그리기

        if self.graph_show == True:
            for sc_var in self.result_dict.keys():

                if len(self.result_dict[sc_var])==0:
                    continue

                ## Rolling Statistics 그래프를 위한 전처리

                screening_stats_df_for_graph = self.result_dict[sc_var]
                screening_stats_df_for_graph['Zero_Line'] = pd.DataFrame(data=np.zeros(screening_stats_df_for_graph.shape[0]),index=list(screening_stats_df_for_graph.index),columns=['Zero_Line'])

                ## Rolling 에 따른 통계값 그래프 그리기
                row_num = 3
                col_num = 2
                fig, axes = plt.subplots(row_num, col_num, figsize=(13, 12))

                ## 승률
                wr_max = 110
                wr_min = 0

                axes[0, 0].set_title('Winning Ratio - %s Screening' % (sc_var))
                screening_stats_df_for_graph['Winning_Ratio'].plot(ax=axes[0, 0], kind='bar', legend=None, alpha=0.5,color='red',ylim=(0, wr_max))
                screening_stats_df_for_graph['Zero_Line'].plot(ax=axes[0, 0], kind='bar', legend=None, alpha=0.5,color='black',ylim=(0, wr_max))

                ## 손익비
                lgr_max = screening_stats_df_for_graph['Loss_Gain_Ratio'].max() + 0.5
                lgr_min = screening_stats_df_for_graph['Loss_Gain_Ratio'].min() - 0.5
                if screening_stats_df_for_graph['Loss_Gain_Ratio'].min() >= 0:
                    lgr_min = 0

                axes[0, 1].set_title('Loss-Gain Ratio - %s Screening' % (sc_var))
                screening_stats_df_for_graph['Loss_Gain_Ratio'].plot(ax=axes[0, 1], kind='bar', legend=None, alpha=0.5,
                                                                     color='darkorange', ylim=(0, lgr_max))
                screening_stats_df_for_graph['Zero_Line'].plot(ax=axes[0, 1], kind='bar', legend=None, alpha=0.5,
                                                               color='black',
                                                               ylim=(0, lgr_max))

                ## 거래당 기대값
                ev_max = screening_stats_df_for_graph['Trd_Expected_Value'].max() + 0.1
                ev_min = screening_stats_df_for_graph['Trd_Expected_Value'].min() - 0.1
                if screening_stats_df_for_graph['Trd_Expected_Value'].min() >= 0:
                    ev_min = 0

                axes[1, 0].set_title('Expected Value Per Trading - %s Screening' % (sc_var))
                screening_stats_df_for_graph['Trd_Expected_Value'].plot(ax=axes[1, 0], kind='bar', legend=None,
                                                                        alpha=0.4,
                                                                        color='darkgreen', ylim=(ev_min, ev_max))
                screening_stats_df_for_graph['Zero_Line'].plot(ax=axes[1, 0], kind='bar', legend=None, alpha=0.5,
                                                               color='black',
                                                               ylim=(ev_min, ev_max))

                ## 연간 기대값
                eva_max = screening_stats_df_for_graph['Total_Expected_Value_Annually'].max() + 2
                eva_min = screening_stats_df_for_graph['Total_Expected_Value_Annually'].min() - 2
                if screening_stats_df_for_graph['Total_Expected_Value_Annually'].min() >= 0:
                    eva_min = 0

                axes[1, 1].set_title('Expected Value Annually - %s Screening' % (sc_var))
                screening_stats_df_for_graph['Total_Expected_Value_Annually'].plot(ax=axes[1, 1], kind='bar',
                                                                                   legend=None, alpha=0.5,
                                                                                   color='darkgreen',
                                                                                   ylim=(eva_min, eva_max))
                screening_stats_df_for_graph['Zero_Line'].plot(ax=axes[1, 1], kind='bar', legend=None, alpha=0.5,
                                                               color='black',
                                                               ylim=(eva_min, eva_max))

                ## Sharpe Ratio
                sr_max = screening_stats_df_for_graph['Sharpe_Ratio'].max() + 0.03
                sr_min = screening_stats_df_for_graph['Sharpe_Ratio'].min() - 0.03
                if screening_stats_df_for_graph['Sharpe_Ratio'].min() >= 0:
                    sr_min = 0

                axes[2, 0].set_title('Sharpe Ratio - %s Screening' % (sc_var))
                screening_stats_df_for_graph['Sharpe_Ratio'].plot(ax=axes[2, 0], kind='bar', legend=None, alpha=0.4,
                                                                  color='navy',
                                                                  ylim=(sr_min, sr_max))
                screening_stats_df_for_graph['Zero_Line'].plot(ax=axes[2, 0], kind='bar', legend=None, alpha=0.5,
                                                               color='black',
                                                               ylim=(sr_min, sr_max))

                ## SQN
                sq_max = screening_stats_df_for_graph['SQN'].max() + 0.03
                sq_min = screening_stats_df_for_graph['SQN'].min() - 0.03
                if screening_stats_df_for_graph['SQN'].min() >= 0:
                    sq_min = 0

                axes[2, 1].set_title('SQN - %s Screening' % (sc_var))
                screening_stats_df_for_graph['SQN'].plot(ax=axes[2, 1], kind='bar', legend=None, alpha=0.5,
                                                         color='navy',
                                                         ylim=(sq_min, sq_max))
                screening_stats_df_for_graph['Zero_Line'].plot(ax=axes[2, 1], kind='bar', legend=None, alpha=0.5,
                                                               color='black',
                                                               ylim=(sq_min, sq_max))

                ## 그래프 정리
                x_ticks_labels_list = list()
                for inx, row in screening_stats_df_for_graph.iterrows():
                    if sc_var != 'Impulse_System':
                        x_tick_frag = '%s~%s %%' % (int(row['Min_Pct'] * 100), int(row['Max_Pct'] * 100))
                    elif sc_var == 'Impulse_System':
                        x_tick_frag = '%s' % (row['Impulse_System_Mode'])
                    x_ticks_labels_list.append(x_tick_frag)

                for c in range(col_num):
                    for r in range(row_num):
                        axes[r, c].xaxis.set_major_locator(plt.MaxNLocator(int(len(screening_stats_df_for_graph))))
                        axes[r, c].grid(color='black', linestyle='dashed', linewidth=0.3, alpha=0.2)
                        axes[r, c].set_xticklabels([])
                        axes[r, c].set_xticklabels([0] + x_ticks_labels_list, rotation=0, fontsize=6)

        return self.result_dict




## 엑셀파일 생성

def writing_excel_file_of_analysis_results(file_path, analysis_tuple_list):

    ## Excel File 생성 혹은 로딩

    try:
        wb = openpyxl.load_workbook(file_path)
    except:
        wb = openpyxl.Workbook()
        wb.save(file_path)

    ## Data Insertion

    for analysis in analysis_tuple_list:
        wb = openpyxl.load_workbook(file_path)
        wb.create_sheet(analysis[0])
        sheet = wb[analysis[0]]
        sheet.append(list(analysis[1].columns))
        for inx, row in analysis[1].iterrows():
            sheet.append(list(row))
        wb.save(file_path)

    ## 초기 Sheet 지우기

    del wb['Sheet']
    wb.save(file_path)

    print('Excel File 저장을 완료했습니다.')
    return None

###########################################################################
##                      포트폴리오 성과
###########################################################################

class trading_portfolio():

    def __init__(self):
        self.bm_country = None
        self.bm_asset_type = None
        self.bm_ticker = None
        self.graph_legend = ['Portfolio']

    def settings_for_risk_management(self,initial_risk_rate, risk_management = (None,None,None,None)):

        self.risk_mng_mode = risk_management[0]
        self.risk_mng_monitoring_period = risk_management[1]
        self.risk_mng_frag_period = risk_management[2]
        self.risk_mng_eq_dec_pct = risk_management[3]

        self.risk_mng_func_dict = {None:self.risk_mng_none,'AMS':self.risk_mng_ams,'MAS':self.risk_mng_mas, 'EDP':self.risk_mng_edp}
        self.risk_mng_func = self.risk_mng_func_dict[self.risk_mng_mode]

        self.initial_risk_rate = initial_risk_rate
        if initial_risk_rate > 1:
            self.initial_risk_rate = 1

    def settings_for_fee(self,buy_fee, sell_fee, ann_risk_free_rate):
        self.buy_fee = buy_fee
        self.sell_fee = sell_fee
        self.trd_fee = self.buy_fee + self.sell_fee
        self.ann_risk_free_rate = ann_risk_free_rate
        self.daily_risk_free_rate = (1+self.ann_risk_free_rate) ** (1 / 365) - 1

    def settings_for_config(self,country, asset_type, trd_report, ticker_number_limit, sorting_ticker_ascending):

        self.country = country
        self.asset_type = asset_type
        self.ticker_number_limit = ticker_number_limit
        self.sorting_ticker_ascending = sorting_ticker_ascending

        ## 데이터에러 및 진입 안된 Row 제거

        self.trd_report = trd_report[((trd_report['Ex_Type'] != 'ED'))&(~trd_report['Real_Ent_Price'].isna())].reset_index(drop=True)
        self.initial_balance = self.trd_report['R_Value'].iloc[0] / self.initial_risk_rate

        ## 계산에 필요한 Data만 남도록 편집

        self.working_ret_columns = list(set(trd_report.columns) - set(list(trd_report.columns[-6:]) + list(trd_report.columns[:18])))
        self.working_ret_columns.sort()

        self.working_other_columns = ['Date_', 'Ticker', 'Ent_Date_', 'Ex_Date_', 'Units', 'Real_Ent_Price', 'Ex_Price', 'Ret', 'Net_Ret', 'R_Value', 'R_Multiple']
        self.working_columns = self.working_other_columns + self.working_ret_columns

    def set_benchmark_market(self,bm_country, bm_asset_type, bm_ticker):
        self.bm_country = bm_country
        self.bm_asset_type = bm_asset_type
        self.bm_ticker = bm_ticker

    def generate_working_df(self):

        ## Working Dataframe 구성 (기본 working columns + ent_position_size + 각 날의 balance 값)

        self.working_report = self.trd_report[self.working_columns].copy()
        self.working_report['Ent_Position_Size'] = self.working_report['Units'] * self.working_report['Real_Ent_Price']
        net_balance_report = self.working_report['Ent_Position_Size'] * (1 + self.working_report['Net_Ret'])
        daily_balance_report = (1 + self.working_report[self.working_ret_columns])

        for i in range(len(self.working_ret_columns)):
            if i == (len(self.working_ret_columns) - 1):
                trd_tc_cond = ~daily_balance_report[self.working_ret_columns[i]].isna()
                daily_balance_report[self.working_ret_columns[i]] = net_balance_report * (trd_tc_cond * 1) + daily_balance_report[self.working_ret_columns[i]] * (~trd_tc_cond * 1)
            else:
                daily_balance_report[self.working_ret_columns[i]] *= self.working_report['Ent_Position_Size']
                trd_end_cond = daily_balance_report[self.working_ret_columns[i + 1]].isna()
                daily_balance_report[self.working_ret_columns[i]] = daily_balance_report[self.working_ret_columns[i]] * (~trd_end_cond * 1) + net_balance_report * (trd_end_cond * 1)

            self.working_report['Day%s_Balance' % i] = daily_balance_report[self.working_ret_columns[i]]



    ## System Stop Functions

    def risk_mng_none(self,new_balacne, date):

        ## None Stop
        self.risk_management_coef = 1
        self.system_continue = 1
        return None

    def risk_mng_ams(self,new_balacne, date):

        ## Average Momentum Score (평균모멘텀스코어)

        self.system_monitoring_balance = self.system_monitoring_balance.append(pd.DataFrame(data=[new_balacne],index=[date], columns=['Monitoring_Balance']))

        if len(self.system_monitoring_balance) < self.risk_mng_monitoring_period:
            pass
        else:
            self.risk_management_coef = self.average_momentum_score_lite(ds=self.system_monitoring_balance['Monitoring_Balance'],date=date,monitoring_days=self.risk_mng_monitoring_period,frag_days=self.risk_mng_frag_period)
            if self.risk_management_coef == 0:
                self.system_continue = 0
            else:
                self.system_continue = 1

        # print('%s / %s / sys_con : %s / risk_coef %s'%(date,new_balacne,self.system_continue,self.risk_management_coef))

    def risk_mng_mas(self,new_balacne, date):

        ma_list = [int(self.risk_mng_monitoring_period/r) for r in [24,12,6,2,1]]

        ## Moving Average Score (이평선스코어)

        self.system_monitoring_balance = self.system_monitoring_balance.append(pd.DataFrame(data=[new_balacne],index=[date], columns=['Monitoring_Balance']))

        if len(self.system_monitoring_balance) < self.risk_mng_monitoring_period:
            pass
        else:
            self.risk_management_coef = self.moving_average_score_lite(ds=self.system_monitoring_balance['Monitoring_Balance'],date=date,ma_list=ma_list)
            if self.risk_management_coef == 0:
                self.system_continue = 0
            else:
                self.system_continue = 1

        # print('%s / %s / sys_con : %s / risk_coef %s'%(date,new_balacne,self.system_continue,self.risk_management_coef))

    def risk_mng_edp(self,new_balacne, date):

        ## Month change
        month_change = (self.system_monitoring_cur_month != date[5:7])

        ## Equity-Decreasing Percentage (자본감소 %에 따른 시스템 스탑)

        self.system_monitoring_balance = self.system_monitoring_balance.append(pd.DataFrame(data=[new_balacne],index=[date], columns=['Monitoring_Balance']))

        if (len(self.system_monitoring_balance) < self.risk_mng_monitoring_period):
            pass
        else:
            start_value = (self.system_monitoring_balance['Monitoring_Balance'].shift(self.risk_mng_monitoring_period-1)).loc[date]
            cur_value = (self.system_monitoring_balance['Monitoring_Balance']).loc[date]
            ret = (cur_value-start_value)/start_value

            self.risk_management_coef = 1

            ## 모니터링 기간 수익률이 기준 이하이면 강제중단

            if (ret < (-self.risk_mng_eq_dec_pct)):
                self.system_continue = 0

            ## 강제중단 스위치 On 상태인데, 달이 바뀌면 재시작

            if ((month_change) == True)&(self.system_continue==0):
                self.system_continue = 1

        self.system_monitoring_cur_month = date[5:7]

        # print('%s / %s / sys_con : %s / risk_coef %s'%(date,new_balacne,self.system_continue,self.risk_management_coef))

    ## Return Portfolio

    def return_portfolio(self):

        self.generate_working_df()

        ## 거래일 설정

        working_days_df = get_past_working_day(country=self.country, asset_type=self.asset_type,start_date=self.working_report['Date_'].min(),end_date=self.working_report['Ex_Date_'].max())

        ## System Monitoring 계좌 잔고

        self.system_monitoring_balance = pd.DataFrame(columns=['Monitoring_Balance'])
        self.system_monitoring_cur_month = self.trd_report['Date_'].iloc[0][5:7]
        self.risk_management_coef = 1
        self.system_continue = 1

        ## 포지션 계좌 잔고

        self.total_port_balance = pd.DataFrame(index=list(working_days_df['Date_']), columns=['Port', 'Cash', 'Total'])
        self.cur_port_balance = {'Port': 0, 'Cash': self.initial_balance, 'Total': self.initial_balance}
        self.cur_port = pd.DataFrame(columns=list(self.working_report.columns) + ['Max_Day_Counting', 'Cur_Day_Counting', 'Cur_Value', 'Risk_Management_Coef'])
        self.simulated_port = pd.DataFrame(columns=list(self.working_report.columns) + ['Max_Day_Counting', 'Cur_Day_Counting', 'Cur_Value', 'Risk_Management_Coef'])

        ## 포트폴리오 Return 계산

        for inx, row in working_days_df.iterrows():

            ## System Monitoring

            self.risk_mng_func(new_balacne=self.cur_port_balance['Total'],date=row['Date_'])

            ## Entry Event에 필요한 Var & Cond

            possible_ent_num = self.ticker_number_limit - len(self.cur_port)
            ent_possible_cond = (possible_ent_num > 0) & (self.system_continue > 0)

            ## Entry Event 시행

            if ent_possible_cond:
                possible_ent_report = self.working_report[self.working_report['Ent_Date_'] == row['Date_']].sort_index(ascending=self.sorting_ticker_ascending).reset_index(drop=True)
                limited_num_possible_ent_report = (possible_ent_report.iloc[0:min(possible_ent_num,len(possible_ent_report))])
                for pe_inx, pe_row in limited_num_possible_ent_report.iterrows():
                    pe_row = pe_row.copy()

                    ## Risk Management Coef 보정
                    pe_row['Units'] *= self.risk_management_coef
                    pe_row['Ent_Position_Size'] *= self.risk_management_coef
                    for d in range(len(self.working_ret_columns)):
                        pe_row['Day%s_Balance' % d] *= self.risk_management_coef

                    enough_cash_cond = ((self.cur_port_balance['Cash'] - (pe_row['Ent_Position_Size'])) > 0)
                    pe_row['Max_Day_Counting'] = (~pe_row[len(self.working_other_columns):len(self.working_columns)].isna() * 1).sum() - 1
                    pe_row['Cur_Day_Counting'] = 0
                    pe_row['Cur_Value'] = pe_row['Ent_Position_Size']
                    pe_row['Risk_Management_Coef'] = self.risk_management_coef
                    if enough_cash_cond & ent_possible_cond:
                        self.cur_port = self.cur_port.append(pd.DataFrame([pe_row]))
                        self.simulated_port = self.simulated_port.append(pd.DataFrame([pe_row]))
                        self.cur_port_balance['Cash'] -= pe_row['Ent_Position_Size']
                        self.cur_port_balance['Port'] += pe_row['Ent_Position_Size']
                        self.cur_port_balance['Total'] = self.cur_port_balance['Port'] + self.cur_port_balance['Cash']

                        possible_ent_num -= 1
                        ent_possible_cond = (possible_ent_num > 0)
                    else:
                        break

            self.cur_port = self.cur_port.reset_index(drop=True)

            ## Daily Change Event 시행

            self.cur_port_balance['Cash'] = self.cur_port_balance['Cash'] * (self.daily_risk_free_rate + 1)

            if (len(self.cur_port) > 0):

                ## Port Value Change 정산

                for ch_inx, ch_row in self.cur_port.iterrows():

                    max_count = ch_row['Max_Day_Counting']

                    before_value = ch_row['Cur_Value']
                    before_count = ch_row['Cur_Day_Counting']

                    after_value = self.cur_port.loc[ch_inx, 'Day%s_Balance' % before_count]
                    after_count = before_count + 1

                    changed_value = after_value - before_value
                    self.cur_port_balance['Port'] += changed_value

                    if after_count > max_count:
                        self.cur_port_balance['Port'] -= after_value
                        self.cur_port_balance['Cash'] += after_value

                    self.cur_port.at[ch_inx, 'Cur_Value'] = after_value
                    self.cur_port.at[ch_inx, 'Cur_Day_Counting'] = after_count

                ## 트레이딩 완료 종목 제거

                self.cur_port = self.cur_port[self.cur_port['Max_Day_Counting'] >= self.cur_port['Cur_Day_Counting']].reset_index(drop=True)

            ## Clear up & Recording

            self.cur_port_balance['Total'] = self.cur_port_balance['Port'] + self.cur_port_balance['Cash']

            self.total_port_balance.at[row['Date_'], 'Port'] = self.cur_port_balance['Port']
            self.total_port_balance.at[row['Date_'], 'Cash'] = self.cur_port_balance['Cash']
            self.total_port_balance.at[row['Date_'], 'Total'] = self.cur_port_balance['Total']



        port_value = self.total_port_balance['Total']
        port_rets = ((port_value - port_value.shift(1)) / port_value.shift(1)).fillna(0)

        port_cumret = self.portfolio_cumulative_return(R=port_rets)
        port_drawdown = self.portfolio_drawdown(R=port_rets)
        port_return_monthly = self.portfolio_monthly_return(R=port_rets)
        port_return_annually = self.portfolio_annual_return(R=port_rets)

        self.portfolio_result = {'values': port_value, 'net_rets': port_rets, 'cum_rets': port_cumret, 'drawdown': port_drawdown,
                       'mon_rets': port_return_monthly, 'ann_rets': port_return_annually}


    def statistics_of_portfolio(self):
        cum_rets = self.portfolio_result['cum_rets'] * 1
        drawdown = self.portfolio_result['drawdown'] * 1
        ann_rets = self.portfolio_result['ann_rets'] * 1

        for df in [cum_rets, ann_rets, drawdown]:
            df.columns = [0]

        portfolio_cum_return = round(cum_rets[0].iloc[-1] * 100, 2)
        portfolio_annual_return = round(np.average(ann_rets[0]) * 100, 2)
        portfolio_annual_std = round(np.std(ann_rets[0]) * 100, 2)
        annual_sharpe_ratio = round((portfolio_annual_return - self.ann_risk_free_rate) / portfolio_annual_std, 2)
        maximal_drawdown = round(drawdown[0].min() * 100, 2)

        self.stats_result = {'cum_rets': portfolio_cum_return, 'ann_rets_avg': portfolio_annual_return,
                  'ann_rets_std': portfolio_annual_std,
                  'sharpe_ratio': annual_sharpe_ratio, 'mdd': maximal_drawdown}

        return self.stats_result

    def plot_portfolio_return(self):

        ## 그래프를 위한 데이터 편집

        port_result = self.portfolio_result
        port_cumrets = port_result['cum_rets']
        port_mon_rets = port_result['mon_rets']
        port_ann_rets = port_result['ann_rets']
        port_result['Zero_Line'] = pd.DataFrame(data=np.zeros(port_cumrets.shape[0]), index=list(port_cumrets.index),columns=['Zero_Line'])
        port_result['One_Line'] = pd.DataFrame(data=np.ones(port_cumrets.shape[0]), index=list(port_cumrets.index),columns=['One_Line'])
        port_result['Zero_Line_Mon'] = pd.DataFrame(data=np.zeros(port_mon_rets.shape[0]), index=list(port_mon_rets.index),columns=['Zero_Line_Mon'])
        port_result['Zero_Line_Ann'] = pd.DataFrame(data=np.zeros(port_ann_rets.shape[0]), index=list(port_ann_rets.index),columns=['Zero_Line_Ann'])

        ## 벤치마크 설정

        if (self.bm_country != None) & (self.bm_asset_type != None) & (self.bm_ticker != None):
            portfolio_index = self.portfolio_result['cum_rets'].index
            bm_result_df = pd.DataFrame(index=portfolio_index)
            bm_start_date = portfolio_index[0]
            bm_end_date = portfolio_index[-1]
            bm_price = download_price_data(country=self.bm_country, asset_type=self.bm_asset_type, ticker=self.bm_ticker,
                                           start_date=bm_start_date, end_date=bm_end_date, time_period='D')['Close_']
            bm_price.index = [d.strftime('%Y-%m-%d') for d in bm_price.index]
            bm_ret = ((bm_price - bm_price.shift(1)) / bm_price.shift(1))
            pd.DataFrame(pd.Series([2,3,4,5]))
            bm_cum_ret = pd.DataFrame(self.portfolio_cumulative_return(R=bm_ret))
            bm_drawdown = pd.DataFrame(self.portfolio_drawdown(R=bm_ret))
            bm_mon_rets = pd.DataFrame(self.portfolio_monthly_return(R=bm_ret))
            bm_ann_rets = pd.DataFrame(self.portfolio_annual_return(R=bm_ret))

            bm_result_df = pd.concat([bm_result_df, bm_cum_ret,bm_drawdown], axis=1, join_axes=[portfolio_index])
            bm_result_df.columns = ['cum_rets','drawdown']

            bm_cum_ret = bm_result_df['cum_rets'].fillna(method='ffill')
            bm_drawdown = bm_result_df['drawdown'].fillna(method='ffill')

            self.graph_legend.append(self.bm_ticker)
            self.bm_result = {'cum_rets': bm_cum_ret, 'drawdown': bm_drawdown, 'mon_rets': bm_mon_rets, 'ann_rets': bm_ann_rets}


        ## 그래프 기본설정

        font_size = 6
        x_tick_rotation = 30
        linewidth = 1

        ## 그래프 그리기

        fig, axes = plt.subplots(2, 2, figsize=(24, 10))

        ## 포트폴리오 cumret 및 drqwdown 그래프

        axes[0, 0].set_title('Cumulative Return')
        port_result['cum_rets'].plot(ax=axes[0, 0], kind='line', linewidth = linewidth, legend=None, alpha=0.5, color='red')

        ## 벤치마크 그래프 추가

        if (self.bm_country != None) & (self.bm_asset_type != None) & (self.bm_ticker != None):
            bm_cum_ret.plot(ax=axes[0, 0], kind='line', linewidth = linewidth, legend=None, alpha=0.5, color='black')
            bm_drawdown.plot(ax=axes[1, 0], kind='line', linewidth = linewidth, legend=None, alpha=0.5, color='black')

        port_result['Zero_Line'].plot(ax=axes[0, 0], kind='bar', legend=None, alpha=0.5, color='black')
        port_result['One_Line'].plot(ax=axes[0, 0], kind='line', linestyle='dashed', legend=None, alpha=0.3, color='black')
        axes[0, 0].legend(self.graph_legend)


        axes[1, 0].set_title('Drawdown')
        port_result['drawdown'].plot(ax=axes[1, 0], kind='line', linewidth = linewidth, legend=None, alpha=0.5, color='red')
        port_result['Zero_Line'].plot(ax=axes[1, 0], kind='bar', legend=None, alpha=0.5, color='black')

        ## 포트폴리오 나머지 그래프

        axes[0, 1].set_title('Monthly Return')
        port_result['mon_rets'].plot(ax=axes[0, 1], kind='bar', legend=None, alpha=0.5, color='red')
        port_result['Zero_Line_Mon'].plot(ax=axes[0, 1], kind='bar', legend=None, alpha=0.5, color='black')

        axes[1, 1].set_title('Annual Return')
        port_result['ann_rets'].plot(ax=axes[1, 1], kind='bar', legend=None, alpha=0.5, color='red')
        port_result['Zero_Line_Ann'].plot(ax=axes[1, 1], kind='bar', legend=None, alpha=0.5, color='black')

        ## Figure 0,1 공통 설정

        x_ticks_num = 20
        x_ticks_step = int(len(port_cumrets) / (x_ticks_num - 1))
        remainder = len(port_cumrets) % (x_ticks_num - 1)
        if remainder != 0:
            tick_controller = 1
        else:
            tick_controller = 0
        x_ticks_labels = [port_cumrets.index[0]] + list(port_cumrets.index[tick_controller::x_ticks_step])[1:-1] + [
            port_cumrets.index[-1]]

        ## Figure 0 설정

        axes[0, 0].xaxis.set_major_locator(plt.LinearLocator(numticks=x_ticks_num))
        axes[0, 0].grid(color='black', linestyle='dashed', linewidth=0.3, alpha=0.2)
        axes[0, 0].set_xticklabels([])
        axes[0, 0].set_xticklabels(x_ticks_labels, rotation=x_tick_rotation, fontsize=font_size)

        ## Figure 1 설정

        axes[1, 0].xaxis.set_major_locator(plt.LinearLocator(numticks=x_ticks_num))
        axes[1, 0].grid(color='black', linestyle='dashed', linewidth=0.3, alpha=0.2)
        axes[1, 0].set_xticklabels([])
        axes[1, 0].set_xticklabels(x_ticks_labels, rotation=x_tick_rotation, fontsize=font_size)

        ## Figure 2 설정

        x_ticks_num = 20
        x_ticks_step = int(len(port_cumrets) / (x_ticks_num - 1))
        remainder = len(port_cumrets) % x_ticks_num
        if remainder != 0:
            tick_controller = 1
        else:
            tick_controller = 0
        month_list = [m[:7] for m in list(port_cumrets.index[tick_controller::x_ticks_step])[1:-1]]
        x_ticks_labels = [port_cumrets.index[0]] + month_list + [port_cumrets.index[-1]]

        axes[0, 1].xaxis.set_major_locator(plt.LinearLocator(numticks=x_ticks_num))
        axes[0, 1].grid(color='black', linestyle='dashed', linewidth=0.3, alpha=0.2)
        axes[0, 1].set_xticklabels(x_ticks_labels, rotation=x_tick_rotation, fontsize=font_size)

        ## Figure 2 설정

        x_ticks_step = 1
        x_ticks_labels = [y[:4] for y in list(port_ann_rets.index[::x_ticks_step])]

        axes[1, 1].grid(color='black', linestyle='dashed', linewidth=0.3, alpha=0.2)
        axes[1, 1].set_xticklabels(x_ticks_labels, rotation=x_tick_rotation, fontsize=font_size)

        print('Graph Completed')


    ## Cumulative return of portfolio

    @staticmethod
    def portfolio_cumulative_return(R):

        R = pd.DataFrame(R)

        R = R.fillna(0)

        temp = (1 + R).cumprod()
        # print("Total Return: ", round(temp.iloc[-1, :], 2))
        return (temp)

    ## Monthly return of portfolio

    @staticmethod
    def portfolio_monthly_return(R):

        R = pd.DataFrame(R)

        R.index = [datetime.strptime(x, '%Y-%m-%d') for x in R.index]

        s = pd.Series(np.arange(R.shape[0]), index=R.index)
        ep = s.resample("M").max()
        temp = pd.DataFrame(data=np.zeros(shape=(ep.shape[0], R.shape[1])), index=ep.index, columns=R.columns)

        for i in range(0, len(ep)):
            if (i == 0):
                sub_ret = R.iloc[0: ep[i] + 1, :]
            else:
                sub_ret = R.iloc[ep[i - 1] + 1: ep[i] + 1, :]
            replace_row_with_series(temp, i, (1 + sub_ret).prod() - 1)

        temp.index = [x.strftime('%Y-%m-%d') for x in ep.index]

        return (temp)

    ## Annual return of portfolio
    @staticmethod
    def portfolio_annual_return(R):

        R = pd.DataFrame(R)

        R.index = [datetime.strptime(x, '%Y-%m-%d') for x in R.index]

        s = pd.Series(np.arange(R.shape[0]), index=R.index)
        ep = s.resample("A").max()
        temp = pd.DataFrame(data=np.zeros(shape=(ep.shape[0], R.shape[1])), index=ep.index, columns=R.columns)

        for i in range(0, len(ep)):
            if (i == 0):
                sub_ret = R.iloc[0: ep[i] + 1, :]
            else:
                sub_ret = R.iloc[ep[i - 1] + 1: ep[i] + 1, :]
            replace_row_with_series(temp, i, (1 + sub_ret).prod() - 1)

        temp.index = [x.strftime('%Y-%m-%d') for x in ep.index]

        return (temp)

    ## Drawdown of portfolio
    @staticmethod
    def portfolio_drawdown(R):

        R = pd.DataFrame(R)

        dd = pd.DataFrame(data=np.zeros(shape=(R.shape[0], R.shape[1])), index=R.index, columns=R.columns)
        R[np.isnan(R)] = 0
        for j in range(0, R.shape[1]):

            if (R.iloc[0, j] > 0):
                dd.iloc[0, j] = 0
            else:
                dd.iloc[0, j] = R.iloc[0, j]

            for i in range(1, len(R)):
                temp_dd = (1 + dd.iloc[i - 1, j]) * (1 + R.iloc[i, j]) - 1
                if (temp_dd > 0):
                    dd.iloc[i, j] = 0
                else:
                    dd.iloc[i, j] = temp_dd

        return (dd)

    ## Moving Average Score 계산
    @staticmethod
    def moving_average_score(ds, ma_list):

        df = pd.DataFrame(data=ds, columns=['Value'])
        for m in ma_list:
            df['MA%s' % m] = (df['Value'] - ds.rolling(center=False, window=m).mean() >= 0) * 1
        result_series = (df[df.columns[1:]].sum(axis=1) / len(ma_list)).fillna(0)
        return result_series

    @staticmethod
    def moving_average_score_lite(ds, date, ma_list):
        ds = ds[ds.index <= date]
        mas_result = 0
        for m in ma_list:
            mas_result += ((ds.loc[date] - int((ds.rolling(center=False, window=m).mean()).loc[date])) >= 0) * 1

        return mas_result/len(ma_list)

    ## Average Momentum Score 계산
    @staticmethod
    def average_momentum_score(ds, monitoring_days, frag_days):
        n = int(monitoring_days / frag_days)
        df = pd.DataFrame(data=ds, columns=['Value'])
        for m in range(1, n + 1):
            df['CumRet%s' % m] = rolling_cumret(ds=ds, window=m * frag_days)

        result_series = ((df[df.columns[1:]].fillna(0) >= 0) * 1).mean(axis=1)
        return result_series

    @staticmethod
    def average_momentum_score_lite(ds, date, monitoring_days, frag_days):

        n = int(monitoring_days / frag_days)
        ams_result = 0
        for m in range(1, n + 1):
            start_value = ds.shift(m*frag_days-1).loc[date]
            cur_value = ds.loc[date]
            ret_frag = ((cur_value-start_value)/start_value)
            if ret_frag >= 0:
                ams_result+=1

        return ams_result/n

## 트레이딩 실제거래
## from wecolib.Curvelib_trading_on import *