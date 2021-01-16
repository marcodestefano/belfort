# belfort
A python tool to trade cryptocurrencies on Coinbase Pro

## How to use belfort:

### Before starting

#### Install dependencies
- cbpro (pip install cbpro)
- python-telegram-bot (pip install python-telegram-bot)

#### Configure the tool with your Coinbase Pro API Key
1. You need to rename the file data.cfg.bak into data.cfg and put your own Coinbase Pro APIKey, APISecret and Passphrase. To know how to create an API key, please follow the official guide here: https://help.coinbase.com/en/pro/other-topics/api/how-do-i-create-an-api-key-for-coinbase-pro
2. (Optional) You can also activate and control belfort via a telegram bot. To do that, you need to rename the telegram.cfg.bak into telegram.cfg and put your own TelegramBotToken after the / character. To know how to define a bot, please follow the official guide here: https://core.telegram.org/bots#6-botfather
3. (Optional, but recommended if you are using the telegram bot) To limit users that can access the otherwise publicly available bot, you need to rename users.cfg.bak into users.cfg and list your authorized telegram usernames, one on each line. 

#### Understand settings.cfg file

File settings.cfg contains settings used in running the engine, that can be customized. The following are the parameters that can be changed to customize belfort trading engine behavior:

- ENGINE_RUN_DURATION: Trading Engine execution duration, expressed in seconds
- AUTO_RESTART: Auto restarts the trading engine in case of failure (e.g. connection lost). If restarted, the engine will run again for ENGINE_RUN_DURATION seconds
- IGNORE_EXISTING_FILLS: The trading engine ignores the existing fills during the order placing calculation. For more details on how fills are calculated, please have a look at Fills section below
- BASE_CURRENCY: the base currency to use as fiat
- CRYPTO_CURRENCY: the crypto currency to trade
- ORDER_TIME_DURATION: Validity in seconds of open orders. After this time, the orders are canceled
- ORDER_TIME_INTERVAL: Time interval in seconds between two new orders
IF YES, ORDERS ARE CANCELED AFTER ONE MINUTE AND ORDER_TIME_DURATION IS IGNORED)
- AUTO_CANCEL: Use Coinbase Pro order auto canceling. If this setting is used, the open orders are canceled after one minute, and ORDER_TIME_DURATION is ignored
- KEEP_SELL_ORDER_OPEN: Keep sell orders open indefinitely, regardless of ORDER_TIME_DURATION or AUTO_CANCEL setting
- MAX_BUY_AMOUNT: Max amount of base currency to use in buy orders
- BUY_PRICE_FACTOR: Price ratio used in placing buying order, compared to current price at the moment order is placed
- SELL_PRICE_FACTOR: Price ratio used in placing selling order, compared to buying price
- BUY_AMOUNT_FACTOR: Ratio of the available base currency to use when placing buying orders
- SELL_AMOUNT_FACTOR: Ratio of the available crypto currency (bought at a price lower than the selling one multiplied by the SELL_PRICE_FACTOR) to use when placing selling orders

### Running the trading engine

There are two main ways to run the trading engine: running the belfort.py script or the belfortgram.py one. The former is intended for usage and control on a normal terminal window, the latter for usage via telegram bot. In any case, to start the program use one of these two options:
1. python belfort.py
2. python belfortgram.py

#### Features

If you are using the belfort.py script, you'll be prompted with these options:

```
Welcome to Belfort!

What's next?
Press 1 to display your wallets
Press 2 to display your open orders
Press 3 to print your current balance
Press 4 to print the active fills
Press 5 to start the trading engine
Press 6 to stop the trading engine
Press 7 to sell the active fills
Press e (or ctrl+c at any time) to exit the program
Select your choice: 
```

Similar options are shown if you use the /help command with the telegram bot.
These features behave as follows:
1. Display wallet: belfort shows the available amount of fiat and crypto in the Coinbase Pro portfolio linked to your API Key
2. Display orders: belfort shows the currently open orders on your portfolio
3. Print balance: belfort shows the difference, in the chosen fiat currency, between the amount you had when defining the portfolio and the current portfolio value
4. Print active fills: belfort shows the active fills on your portfolio. For more details on how fills are calculated, please have a look at Fills section below
5. Start trading engine: belfort starts the trading engine with the parameters defined in settings.cfg file
6. Stop trading engine: belfort stops the trading engine
7. Sell active fills: belfort places sell orders to sell all your active fills that can be sold, at a price depending on the SELL_PRICE_FACTOR parameter

#### Fills

Fills are calculated during execution of belfort as the real price paid (i.e. including the Coinbase Pro fees) for a given orders. The belfort algo calculates these fills with the related crypto amount, and automatically subtracts the amount sold at a price higher than the buying one. You can consider the *active fills* at any point in time as the guide to identify the maximum amount of crypto that can be sold at a given price.
