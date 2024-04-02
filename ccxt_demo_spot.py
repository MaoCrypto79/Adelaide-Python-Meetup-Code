#%%
import ccxt
import json 
import pandas as pd 
import numpy as np

#%%
# Set your exchange Using the CCXT Declaration
my_exchange = ccxt.bybit({
    'enableRateLimit': True, 
    'apiKey': '',
    'secret': '',
    'options':{"defaultType":"spot"} 
    })
# %%

#%%
##### MAKE SURE YOU SELECT THE SYMBOL AND PAIR IN THE FOLLOWING FORMAT
symbol = 'ZIL/USDT'
## THE AMOUNT OF USDT YOU WAN TO INVEST/BUY OF THE PARTICULAR COIN
usdt_buy = 15

# %%
#SEND ORDER TO EXCHANGE
order_market = my_exchange.createMarketBuyOrderWithCost(symbol =symbol,
                                                        cost = usdt_buy )
order_market


# %%
# Get all the information about the specific trade
order_info = my_exchange.fetchClosedOrders(symbol = symbol )
order_info



#%%
# It retunrs a list of all the orders of this symbol
# Filter for the last specific order link id 
for order in order_info:
    if order.get('info').get('orderLinkId') == order_market.get('info').get('orderLinkId'):
        order_id = order.get('info').get('orderId')
        buy_price = order.get('average')
        cost = order.get('cost')
        amount_filled = order.get('filled')

# %%
### Get Trade specifics including Fees
        
order_details = my_exchange.fetchMyTrades(symbol = symbol )

for order in order_details:
    if order_id == order.get('info').get('orderId'):
        trade_fee_in_coin = order.get('fee').get('cost')
#%%

amount_coin = amount_filled - trade_fee_in_coin
# %%
print(f'buy_price = {buy_price}')
print(f'Cost = {cost}')
print(f'Holding Coins = {amount_coin}')
# %%
#################################################
### AM I IN PROFIT OR LOSS LOOP 
### YOU CAN RUN THIS INS A LOOP EVERY SECOND OR MINUTE UNTIL YOU HAVE A LOGIC TO CLOSE THE POSITION 


bars = my_exchange.fetch_ohlcv(symbol, timeframe="1m", \
                                limit=3)
new_df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', \
                        'close', 'volume'])
new_df['timestamp'] = pd.to_datetime(
new_df['timestamp'], unit='ms')
print(new_df)

current_price = new_df[-1:].close.values[0]
profit = current_price - buy_price
profit_pct = (profit / buy_price) * 100
print(f'Profit USDT : {profit}')
print(f'Profit % : {profit_pct}')


######################################################

# %%
############################################################
### Other Metodology using Order books instead of the OHLCV data
order_book = my_exchange.fetch_order_book(symbol)
bid = order_book['bids'][0][0]
ask = order_book['asks'][0][0]
print(f'for {symbol} the current bid: {bid} ask: {ask}')
obook_current_price = order_book['asks'][0][0]
obook_current_profit = obook_current_price - buy_price
obook_profit_pct = (obook_current_profit /buy_price ) * 100
print(f'OrderBook_Profit USDT : {obook_current_profit}')
print(f'OrderBook_Profit % : {obook_profit_pct}')
#######################################################
# %%




#%%
#### CLOSING POSITION OR SELLING THE ASSET  ###
## You end up with a small remaining that then you can convert in the exchange 
order_sell_market = my_exchange.create_order(symbol= symbol,
                                             type= 'market',
                                             side= 'sell',
                                             amount = amount_coin
                                             )

# %%
