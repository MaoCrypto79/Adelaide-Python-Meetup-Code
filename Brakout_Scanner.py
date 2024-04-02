import ccxt 
import pandas as pd 
import math
#import dontshare_config
import time, schedule

#import nice_funcs as n 
from datetime import date, datetime, timezone, tzinfo

schedule

### DO NOT NEED API INFO IF ONLY READING DATA AND NOT PLACING ORDER ####3
# bybit = ccxt.bybit({
#     'enableRateLimit': True, 
#     'apiKey': '',
#     'secret': '', 
#     })

bybit = ccxt.bybit({
    'enableRateLimit': True,  
    })


exchanges = [bybit]

def scanner():
    
    ## CCXT  Day = '1d' Hours = '4h' - '1h' minutes = '15m' - '5m' - '1m'
    timeframe = '1d'
    num_bars = 4

    # get all markets
    bybit_all_markets = bybit.load_markets()
    ###All coins and market available in Bybit
    all_coins_bybit_list = list(bybit_all_markets.keys())
    all_spot_usdt_bybit_list = [f for f in all_coins_bybit_list if ':USDT' not in f]
    ## Then get the ones that have '/USDT' so we know is spot and not FUTURES
    all_spot_usdt_bybit_list = [f for f in all_spot_usdt_bybit_list if '/USDT' in f]
    ## Filter the list to get Derivatives pairs 
    ### if the list contaiins ':USDT' then is a derivative 
    all_derivatives_usdt_bybit_list = [f for f in all_coins_bybit_list if ':USDT' in f]
    #%%
    all_spot_usdt_bybit_list
    
    
    exchanges = [bybit]

    for exchange in exchanges:
        df = pd.DataFrame(columns = ["timestamp" , "symbol", "exchange","vol_usdt_avg", "support", "resistance", "bid", "ask", "breakOUT", "breakDOWN"])

        for ticker in all_derivatives_usdt_bybit_list: 

            tickers = ticker
            #tickers = (f'{tickers}/USDT:USDT') # spot markets
            print(f'{ticker} on {exchange}')

            try:

                bars = exchange.fetch_ohlcv(tickers, timeframe=timeframe, \
                    limit=num_bars)
                new_df = pd.DataFrame(
                    bars, 
                    columns=['timestamp', 'open', 'high', 'low', \
                        'close', 'volume'])
                new_df['timestamp'] = pd.to_datetime(
                    new_df['timestamp'], unit='ms')
                tickerfound = True
                print('ticker found executed')

                # find support and resistance
                support = new_df['low'].min()
                resistance = new_df['high'].max()
                l2h = resistance - support 
                avg = (resistance+support)/2 
                vol_usdt_avg = new_df['high'].mean()
                print(f'support: {support}, high: {resistance}, l2h: {l2h}, avg: {avg}')

                order_book = exchange.fetch_order_book(tickers)
                bid = order_book['bids'][0][0]
                ask = order_book['asks'][0][0]
                print(f'for {tickers} the current bid: {bid} ask: {ask}')

                # DATA FRAME FOR SIGNALS
                signal_df = pd.DataFrame()
                signal_df['timestamp'] = new_df['timestamp']
                signal_df['symbol'] = tickers
                signal_df['exchange'] = exchange
                signal_df['vol_usdt_avg'] = vol_usdt_avg
                signal_df['support'] = support
                signal_df['resistance'] = resistance
                signal_df['bid'] = bid
                signal_df['ask'] = ask
                signal_df['breakOUT'] = False
                signal_df['breakDOWN'] = False 

                if bid > resistance:
                    print(f'**** we have a break OUT for {tickers}, bid is HIGHER than RESISTANCE')
                    breakout = True 
                    signal_df['breakOUT'] = breakout
                elif ask < support: 
                    print(f'**** we have a breaK DOWN for {tickers}, bid is LOWER than SUPPORT')
                    breakdown = True 
                    signal_df['breakDOWN'] = breakdown
                else:
                    print(f'no break out or break down for {tickers}... ')
                    
            except:
                print("#####SOMETHING IS GOING WRONG EXEPT IS BEING EXECUTED CHECK###")
                print(f'there is no symbol for {tickers}')
                ob = 'nothing'
                tickerfound = False 


            signal_df = signal_df[-1:]
            print(signal_df)
            
            #df = df.append(signal_df)
            # Change this as append seem not to be working
            df = pd.concat([df, signal_df], ignore_index= True) 
            print('')
            print('')
            print('-----')

        # count the number of breakouts or downs
        print(df.breakDOWN.value_counts())
        print(df.breakOUT.value_counts())
        print('the number of sumbols is:', len(df.index))

        # get symbol count in order to compare it
        symbol_count = len(df.index)

        breakout_num = df['breakOUT'].sum()
        print("####################################")
        print(f'ttotal number of breakouts are are TRUE: {breakout_num}')
        print("_____________________________________")

        breakdown_num = df['breakDOWN'].sum()
        print("####################################")
        print(f'ttotal number of breakdowns are are TRUE: {breakdown_num}')
        print("_____________________________________")
        print("_____________________________________")

        # bullish or bearish signal
        if breakdown_num > breakout_num:
            bullish = False 
            print("_____________________________________")
            print(f'there are more breakdowns thn breakouts bullish set to {bullish}')
            print("_____________________________________")
            print("_____________________________________")

        elif breakout_num > breakdown_num:

            bullish = True 
            print("_____________________________________")
            print(f'there are more breakOUTS thn breakdowns bullish set to {bullish}')
            print("_____________________________________")
            print("_____________________________________")

        else:
            print("_____________________________________")
            print('there are the same amout of breakouts and breakdowns.. ')
            print("_____________________________________")
            print("_____________________________________")


        print("####################################")
        print("BREAKOUTS")
        br_up_df = df.loc[(df['breakOUT'] == True)]
        print(df.loc[(df['breakOUT'] == True)] )
        print("_____________________________________")
        print("_____________________________________")
        print("####################################")
        print("BREAKDOWNS")
        br_down_df = df.loc[(df['breakDOWN'] == True) ]
        print(df.loc[(df['breakDOWN'] == True) ])
        print("_____________________________________")
        print("_____________________________________")
        #rowsw_true = df.loc[(df['breakOUT'] == True) | (df['breakDOWN'] ==True)]
        #print(rowsw_true)
        #rowsw_true.to_csv('signal_bo.csv', index=False)

        # if 7% or more of the symbol are breaking out or down, put emergency clsoe
        perc_07 = symbol_count * .07
        if breakdown_num > perc_07:
            print('**** EMERGENCY CLOSE ALL ** 7 percent+ symbols are breaking down.. ')
            perc_07_lows_close = True 
        elif breakout_num > perc_07:
            print('**** EMERGENCY CLOSE ALL ** 7 percent+ symbols are breaking down.. ')
            perc_07_his_close = True 
        else:
            print('.. no anomolies in breakouts or downs (measuring if 7%)')
        
        #######PRINT DF
        #print("########## LAST DF STATUS ########")
        ##print(df)
        file_name = file_name = str(datetime.now())
        br_up_df.to_csv ('/home/PYTHON PRESENTATION/ScannerOutput/' + 'BREAKOUTS' + file_name + ".csv")
        br_down_df.to_csv('/home/PYTHON PRESENTATION/ScannerOutput/' + 'BREAK-DOWNS' + file_name + ".csv")

        df.to_csv('/home/PYTHON PRESENTATION/ScannerOutput/' + file_name + ".csv")



schedule.every(120).seconds.do(scanner) 



while True:
    
    try:
        schedule.run_pending() 
    except:
        print('++++++++MAYBE AN INTERNET PROBLEM OR SOMETHING GOING TO SLEEP FOR 30 SECONDS AND TRY AGAIN, if keep happening its a bug++++++')
        time.sleep(30)




