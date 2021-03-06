import cbpro
import os
import time
import traceback
import threading
from decimal import Decimal, ROUND_DOWN, ROUND_UP
from datetime import datetime, timedelta

API_URL = "https://api.pro.coinbase.com"
API_KEY = 'APIKey'
API_SECRET = 'APISecret'
API_PASSPHRASE = 'APIPassphrase'
DATA_FILENAME = 'data.cfg'
SETTINGS_FILENAME = 'settings.cfg'
ENGINE_RUN_DURATION = "ENGINE_RUN_DURATION"
AUTO_RESTART = "AUTO_RESTART"
IGNORE_EXISTING_FILLS = "IGNORE_EXISTING_FILLS"
KEEP_SELL_ORDER_OPEN = "KEEP_SELL_ORDER_OPEN"
AUTO_CANCEL = "AUTO_CANCEL"
MAX_BUY_AMOUNT = "MAX_BUY_AMOUNT"
BUY_PRICE_FACTOR = "BUY_PRICE_FACTOR"
SELL_PRICE_FACTOR = "SELL_PRICE_FACTOR"
BUY_PRICE_FACTOR = "BUY_PRICE_FACTOR"
SELL_PRICE_FACTOR = "SELL_PRICE_FACTOR"
BUY_AMOUNT_FACTOR = "BUY_AMOUNT_FACTOR"
SELL_AMOUNT_FACTOR = "SELL_AMOUNT_FACTOR"
ORDER_TIME_DURATION = "ORDER_TIME_DURATION"
ORDER_TIME_INTERVAL = "ORDER_TIME_INTERVAL"
BASE_CURRENCY = "BASE_CURRENCY"
CRYPTO_CURRENCY = "CRYPTO_CURRENCY"
TAKER_FEE_RATE = "taker_fee_rate"
MAKER_FEE_RATE = "maker_fee_rate"
MIN_SIZE = "base_min_size"
MAX_SIZE = "base_max_size"
SIZE_INCREMENT = "base_increment"
PRICE_INCREMENT = "quote_increment"
ORDER_SIDE_BUY = "buy"
ORDER_SIDE_SELL = "sell"
TIME_INTERVAL_DAY = 86400
TIME_INTERVAL_MONTH = TIME_INTERVAL_DAY * 30
TIME_INTERVAL_QUARTER = TIME_INTERVAL_MONTH * 3
TIME_INTERVAL_3QUARTER = TIME_INTERVAL_QUARTER * 3
RATIO_9M = Decimal(0.6)
RATIO_3M = Decimal(0.3)
RATIO_M = Decimal(0.1)
PRODUCT_MIN_VALUE = "product_min_value"
PRODUCT_MAX_VALUE = "product_max_value"

DEFAULT_ENGINE_RUN_DURATION = 300
DEFAULT_AUTO_RESTART = 0

DEFAULT_IGNORE_EXISTING_FILLS = 1
DEFAULT_KEEP_SELL_ORDER_OPEN = 1
DEFAULT_AUTO_CANCEL = 1

DEFAULT_MAX_BUY_AMOUNT = Decimal('Inf')

DEFAULT_BUY_PRICE_FACTOR = 0.5
DEFAULT_SELL_PRICE_FACTOR = 1.5

DEFAULT_BUY_AMOUNT_FACTOR = 0.5
DEFAULT_SELL_AMOUNT_FACTOR = 0.5

DEFAULT_ORDER_TIME_DURATION = 10
DEFAULT_ORDER_TIME_INTERVAL = 3

DEFAULT_BASE_CURRENCY = "EUR"
DEFAULT_CRYPTO_CURRENCY = "XLM"

TRADING_ENGINE_ACTIVE = 0
LAST_ORDERS = ""

def getConfiguration(fileName):
    """Retrieve the configuration file."""
    directory = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    )
    conf = {}
    filePath = os.path.join(directory, fileName)
    with open(filePath, 'r') as f:
        for line in f:
            if (line[0] != "#") and len(line) > 0:
                line = line[:len(line)-1]
                pair = line.split(":")
                if len(pair) == 2:
                    conf[pair[0]] = pair[1]
    return conf

def authenticateClient():
    config = getConfiguration(DATA_FILENAME)
    return cbpro.AuthenticatedClient(config[API_KEY], config[API_SECRET],
                                  config[API_PASSPHRASE], api_url=API_URL)

def updateSettings(client):
    """Retrieve settings stored on file."""
    settings = getConfiguration(SETTINGS_FILENAME)
    if settings:

        if settings[ENGINE_RUN_DURATION]:
            settings[ENGINE_RUN_DURATION] = int(settings[ENGINE_RUN_DURATION])
        else:
            settings[ENGINE_RUN_DURATION] = DEFAULT_ENGINE_RUN_DURATION

        if settings[AUTO_RESTART]:
            settings[AUTO_RESTART] = int(settings[AUTO_RESTART])
        else:
            settings[AUTO_RESTART] = DEFAULT_AUTO_RESTART

        if settings[IGNORE_EXISTING_FILLS]:
            settings[IGNORE_EXISTING_FILLS] = int(settings[IGNORE_EXISTING_FILLS])
        else:
            settings[IGNORE_EXISTING_FILLS] = DEFAULT_IGNORE_EXISTING_FILLS

        if settings[KEEP_SELL_ORDER_OPEN]:
            settings[KEEP_SELL_ORDER_OPEN] = int(settings[KEEP_SELL_ORDER_OPEN])
        else:
            settings[KEEP_SELL_ORDER_OPEN] = DEFAULT_KEEP_SELL_ORDER_OPEN

        if settings[AUTO_CANCEL]:
            settings[AUTO_CANCEL] = int(settings[AUTO_CANCEL])
        else:
            settings[AUTO_CANCEL] = DEFAULT_AUTO_CANCEL

        if settings[MAX_BUY_AMOUNT]:
            settings[MAX_BUY_AMOUNT] = Decimal(settings[MAX_BUY_AMOUNT])
        else:
            settings[MAX_BUY_AMOUNT] = DEFAULT_MAX_BUY_AMOUNT

        if settings[BUY_PRICE_FACTOR]:
            settings[BUY_PRICE_FACTOR] = Decimal(settings[BUY_PRICE_FACTOR])
        else:
            settings[BUY_PRICE_FACTOR] = DEFAULT_BUY_PRICE_FACTOR

        if settings[SELL_PRICE_FACTOR]:
            settings[SELL_PRICE_FACTOR] = Decimal(settings[SELL_PRICE_FACTOR])
        else:
            settings[SELL_PRICE_FACTOR] = DEFAULT_SELL_PRICE_FACTOR

        if settings[BUY_AMOUNT_FACTOR]:
            settings[BUY_AMOUNT_FACTOR] = Decimal(settings[BUY_AMOUNT_FACTOR])
        else:
            settings[BUY_AMOUNT_FACTOR] = DEFAULT_BUY_AMOUNT_FACTOR

        if settings[SELL_AMOUNT_FACTOR]:
            settings[SELL_AMOUNT_FACTOR] = Decimal(settings[SELL_AMOUNT_FACTOR])
        else:
            settings[SELL_AMOUNT_FACTOR] = DEFAULT_SELL_AMOUNT_FACTOR

        if settings[ORDER_TIME_DURATION]:
            settings[ORDER_TIME_DURATION] = int(settings[ORDER_TIME_DURATION])
        else:
            settings[ORDER_TIME_DURATION] = DEFAULT_ORDER_TIME_DURATION

        if settings[ORDER_TIME_INTERVAL]:
            settings[ORDER_TIME_INTERVAL] = int(settings[ORDER_TIME_INTERVAL])
        else:
            settings[ORDER_TIME_INTERVAL] = DEFAULT_ORDER_TIME_INTERVAL

        if settings[BASE_CURRENCY] is None:
            settings[BASE_CURRENCY] = DEFAULT_BASE_CURRENCY

        if settings[CRYPTO_CURRENCY] is None:
            settings[CRYPTO_CURRENCY] = DEFAULT_CRYPTO_CURRENCY

        product = getProduct(client, settings[BASE_CURRENCY], settings[CRYPTO_CURRENCY])
        settings[MIN_SIZE] = Decimal(product[MIN_SIZE])
        settings[MAX_SIZE] = Decimal(product[MAX_SIZE])
        settings[SIZE_INCREMENT] = product[SIZE_INCREMENT].rstrip("0")
        settings[PRICE_INCREMENT] = product[PRICE_INCREMENT].rstrip("0")
    return settings


def getCurrencyPair(baseCurrency, cryptoCurrency):
    """Returns the currency pair in the format expected in Coinbase Pro"""
    return cryptoCurrency + "-" + baseCurrency

def getWallets(client):
    """Retrieve the wallets of an account."""
    accounts = client.get_accounts()
    wallets = {}
    if accounts:
        for account in accounts:
            wallets[account["id"]] = account["balance"] +\
                                    " " + account["currency"]
    return wallets

def getProduct(client, baseCurrency, cryptoCurrency):
    """Returns the product specified in settings currencies"""
    products = client.get_products()
    currencyPair = getCurrencyPair(baseCurrency, cryptoCurrency)
    for product in products:
        if(product["id"]==currencyPair):
            return product
    return None

def getProductMinAndMaxValue(client, timeInterval, settings):
    GRANULARITY = 86400
    result = {}
    result[PRODUCT_MIN_VALUE] = Decimal('Inf')
    result[PRODUCT_MAX_VALUE] = Decimal('-Inf')
    actualTime = datetime.utcnow()
    startTime = actualTime - timedelta(seconds = timeInterval)
    endTime = actualTime
    product=getCurrencyPair(settings[BASE_CURRENCY], settings[CRYPTO_CURRENCY])
    historicRate = client.get_product_historic_rates(product, startTime, endTime, GRANULARITY)
    if historicRate:
        for candle in historicRate:
            if result[PRODUCT_MIN_VALUE] > candle[1]:
                result[PRODUCT_MIN_VALUE] = candle[1]
            if result[PRODUCT_MAX_VALUE] < candle[2]:
                result[PRODUCT_MAX_VALUE] = candle[2]
    return result

def getRatio(currentValue, minValue, maxValue):
    return Decimal(1 - ((Decimal(currentValue)-Decimal(minValue))/(Decimal(maxValue)-Decimal(minValue))))

def getOrderRatio(client, settings):
    monthMinMax = getProductMinAndMaxValue(client, TIME_INTERVAL_MONTH, settings)
    quarterMinMax = getProductMinAndMaxValue(client, TIME_INTERVAL_QUARTER, settings)
    threeQuarterMinMax = getProductMinAndMaxValue(client, TIME_INTERVAL_3QUARTER, settings)
    currentValue = Decimal(getCurrentPrice(client, settings[BASE_CURRENCY], settings[CRYPTO_CURRENCY]))
    ratio9M = RATIO_9M * getRatio(currentValue, threeQuarterMinMax[PRODUCT_MIN_VALUE], threeQuarterMinMax[PRODUCT_MAX_VALUE])
    ratio3M = RATIO_3M * getRatio(currentValue, quarterMinMax[PRODUCT_MIN_VALUE], quarterMinMax[PRODUCT_MAX_VALUE])
    ratioM = RATIO_M * getRatio(currentValue, monthMinMax[PRODUCT_MIN_VALUE], monthMinMax[PRODUCT_MAX_VALUE])
    return ratio9M + ratio3M + ratioM

def getWalletBalance(client, currency):
    """Returns the balance of the wallet in the given currency"""
    accounts = client.get_accounts()
    if accounts:
        for account in accounts:
            if account["currency"] == currency:
                return Decimal(account["balance"])

def getWalletHold(client, currency):
    """Returns the hold amount for the given currency"""
    accounts = client.get_accounts()
    if accounts:
        for account in accounts:
            if account["currency"] == currency:
                return Decimal(account["hold"])

def printWallets(client):
    """Print wallet content."""
    print ("\nHere's the list of your wallets:\n")
    print(getWalletsText(client))
    return

def getWalletsText(client):
    """Print wallet content."""
    result = ""
    wallets = getWallets(client)
    for account in wallets:
        if Decimal(wallets[account][:-4]) > 0:
            result = result + account + ", " + wallets[account]
    return result

def printValue(client, settings):
    """Print currency value"""
    settings = updateSettings(client)
    currencyPair = getCurrencyPair(settings[BASE_CURRENCY], settings[CRYPTO_CURRENCY])
    ticker = client.get_product_ticker(product_id=currencyPair)
    print ("Current %s price is: %s %s" % (settings[CRYPTO_CURRENCY], ticker["price"],
                                              settings[BASE_CURRENCY]))

def getCurrentPrice(client, baseCurrency, cryptoCurrency):
    """Returns the current price of a crypto currency expressed in base currency"""
    currencyPair = getCurrencyPair(baseCurrency, cryptoCurrency)
    ticker = client.get_product_ticker(product_id=currencyPair)
    if ticker:
        return ticker["price"]
    else:
        return ""

def getFills(client, baseCurrency, cryptoCurrency):
    """Returns the list of fills for the product identified by the given pair of currencies"""
    return list(client.get_fills(product_id=getCurrencyPair(baseCurrency, cryptoCurrency)))

def cancelObsoleteOrders(client, settings):
    currencyPair = getCurrencyPair(settings[BASE_CURRENCY], settings[CRYPTO_CURRENCY])
    orders = list(client.get_orders())
    for order in orders:
        if order["product_id"] == currencyPair and (order["side"] == ORDER_SIDE_BUY or not settings[KEEP_SELL_ORDER_OPEN]):
            placedAt = datetime.strptime(order["created_at"],'%Y-%m-%dT%H:%M:%S.%fZ')
            limitTime = placedAt + timedelta(seconds = settings[ORDER_TIME_DURATION])
            actualTime = datetime.utcnow()
            if actualTime > limitTime:
                client.cancel_order(order["id"])
                print ("Canceled " + order["side"] + " order " + order["id"] + " of size " + order["size"] + " and price " + order["price"] + " placed at " + str(placedAt))
    return

def calculateOrderPrice(client, orderSide, settings):
    """Returns the order price based on the settings and the side of the order (buy vs sell)"""
    #Get the price factor from the settings and choose a rounding: down in case of buy (means buying at a lower price) and up in case of sell (the opposite)
    orderFactor = settings[BUY_PRICE_FACTOR]
    roundingStrategy = ROUND_DOWN
    if orderSide == ORDER_SIDE_SELL:
        orderFactor = settings[SELL_PRICE_FACTOR]
        roundingStrategy = ROUND_UP
    #Get the current currency price
    currentCurrencyPrice = Decimal(getCurrentPrice(client, settings[BASE_CURRENCY], settings[CRYPTO_CURRENCY]))
    #The order price is built as currentPrice * orderFactor, and then rounded down or up with a precision of the minimum price increment possible
    orderPrice = Decimal(currentCurrencyPrice) * Decimal(orderFactor)
    orderPrice = orderPrice.quantize(Decimal(settings[PRICE_INCREMENT]), rounding = roundingStrategy)
    return orderPrice

def calculateBuySize(euroAvailable, buyPrice, client, settings):
    """Returns the size of currency to buy based on the settings and the buy price, rounded with a precision of the smallest quantity that can be bought"""
    buySize = Decimal(euroAvailable)* Decimal(settings[BUY_AMOUNT_FACTOR]) / Decimal(buyPrice)
    buySize = buySize * getOrderRatio(client, settings)
    buySize = buySize.quantize(Decimal(settings[SIZE_INCREMENT]))
    return buySize

def getFeeRate(client):
    return Decimal(client._send_message('get', '/fees')[MAKER_FEE_RATE])

def calculateActiveFills(client, settings):
    fills = getFills(client, settings[BASE_CURRENCY], settings[CRYPTO_CURRENCY])
    feeRate = getFeeRate(client)
    buyFills = {}
    sellFills = {}
    for fill in fills:
        if fill["side"] == ORDER_SIDE_BUY:
            realFillPrice = (Decimal(fill["price"])+Decimal(fill["fee"])/Decimal(fill["size"]))*(1+feeRate)
            if realFillPrice not in buyFills:
                buyFills[realFillPrice] = Decimal(0)
            buyFills[realFillPrice] = buyFills[realFillPrice] + Decimal(fill["size"])
        else:
            realFillPrice = (Decimal(fill["price"])-Decimal(fill["fee"])/Decimal(fill["size"]))*(1+feeRate)
            if realFillPrice not in sellFills:
                sellFills[realFillPrice] = Decimal(0)
            sellFills[realFillPrice] = sellFills[realFillPrice] + Decimal(fill["size"])
    orderedBuyPrices = list(buyFills.keys())
    orderedSellPrices = list(sellFills.keys())
    orderedBuyPrices.sort(reverse = True)
    orderedSellPrices.sort(reverse = True)
    for sellPriceItem in orderedSellPrices:
        for buyPriceItem in orderedBuyPrices:
            quantitySell = sellFills[sellPriceItem]
            if quantitySell > 0:
                if buyPriceItem < sellPriceItem:
                    quantityBuy = buyFills[buyPriceItem]
                    if quantityBuy > 0:
                        if quantitySell < quantityBuy:
                            sellFills[sellPriceItem] = 0
                            buyFills[buyPriceItem] = buyFills[buyPriceItem] - quantitySell
                        else:
                            sellFills[sellPriceItem] = sellFills[sellPriceItem] - quantityBuy
                            buyFills[buyPriceItem] = 0
    return buyFills

def calculateSellSize(client, cryptoAvailable, sellPrice, activeFillsToRemove, settings):
    buyFills = calculateActiveFills(client, settings)
    #if there are fills to ignore, the related quantities are removed from the active fills count
    for fill in activeFillsToRemove:
        if fill in buyFills:
            buyFills[fill] = buyFills[fill] - min(buyFills[fill],activeFillsToRemove[fill])
    openOrders = list(client.get_orders(product_id = getCurrencyPair(settings[BASE_CURRENCY], settings[CRYPTO_CURRENCY])))
    sellOrders = {}
    for order in openOrders:
        if order["side"] == ORDER_SIDE_SELL:
            if Decimal(order["price"]) not in sellOrders:
                sellOrders[Decimal(order["price"])] = Decimal(0)
            sellOrders[Decimal(order["price"])] = sellOrders[Decimal(order["price"])] + Decimal(order["size"]) - Decimal(order["filled_size"]) 
    orderedOrderPrices = list(sellOrders.keys())
    orderedBuyPrices = list(buyFills.keys())
    orderedOrderPrices.sort(reverse = True)
    orderedBuyPrices.sort(reverse = True)
    for orderPriceItem in orderedOrderPrices:
        for buyPriceItem in orderedBuyPrices:
            quantityOrder = sellOrders[orderPriceItem]
            if quantityOrder > 0:
                #if buyPriceItem < orderPriceItem*Decimal(1-ORDER_FEE):
                if buyPriceItem < orderPriceItem:
                    quantityBuy = buyFills[buyPriceItem]
                    if quantityBuy > 0:
                        if quantityOrder < quantityBuy:
                            sellOrders[orderPriceItem] = 0
                            buyFills[buyPriceItem] = buyFills[buyPriceItem] - quantityOrder
                        else:
                            sellOrders[orderPriceItem] = sellOrders[orderPriceItem] - quantityBuy
                            buyFills[buyPriceItem] = 0
    amountToSell = 0
    for buyPriceItem in buyFills:
        #if buyPriceItem < sellPrice*Decimal(1-ORDER_FEE):
        if buyPriceItem < sellPrice:
            amountToSell = amountToSell + buyFills[buyPriceItem]

    cryptoAvailable = min(Decimal(cryptoAvailable), Decimal(amountToSell))
    sellSize = Decimal(cryptoAvailable)* Decimal(settings[SELL_AMOUNT_FACTOR])
    sellSize = sellSize.quantize(Decimal(settings[SIZE_INCREMENT]))
    return sellSize

def placeOrder(client, orderSide, orderSize, orderPrice, settings):
    """Places an order on Coinbase Pro of the given size, price, side (buy or sell) based on the available settings"""
    #If order size is bigger than the maximum allowed size for transaction, the order is capped at max size
    textResult = ""
    if orderSize >= settings[MAX_SIZE]:
        orderSize = settings[MAX_SIZE]
        textResult = "Warning in placing " + orderSide + " order of size : " + str(orderSize)  + ". Reducing to maximum size " + str(settings[MAX_SIZE]) + " " + settings[CRYPTO_CURRENCY]
        print (textResult)
    #If order is bigger than the minimum allowed size, it is placed
    if orderSize >= settings[MIN_SIZE]:
        print ("Placing a " + orderSide + " order of " + str(orderSize) + " " + settings[CRYPTO_CURRENCY] + " at price of " + str(orderPrice) + " " + settings[BASE_CURRENCY])
        textResult = textResult + "\n" + "Placing a " + orderSide + " order of " + str(orderSize) + " " + settings[CRYPTO_CURRENCY] + " at price of " + str(orderPrice) + " " + settings[BASE_CURRENCY]
        timeInForce = None
        cancelAfter = None
        if settings[AUTO_CANCEL] and (orderSide == ORDER_SIDE_BUY or not settings[KEEP_SELL_ORDER_OPEN]):
            timeInForce = "GTT"
            cancelAfter = "min"
        result = client.place_limit_order(product_id=getCurrencyPair(settings[BASE_CURRENCY], settings[CRYPTO_CURRENCY]), 
                  side=orderSide, 
                  price=str(orderPrice), 
                  size=str(orderSize), post_only = True, time_in_force = timeInForce, cancel_after = cancelAfter)
        try:
            #If order is correctly placed, it will have a unique ID
            print (orderSide + " order placed with ID " + result["id"])
            textResult = textResult + "\n" + orderSide + " order placed with ID " + result["id"]
        except Exception:
            #If there was an error in placing the order, the error message will be displayed
            print ("Error in placing " + orderSide + " order: " + result["message"])
            textResult = textResult + "\n" + "Error in placing " + orderSide + " order: " + result["message"]
    else:
        #If order size is smaller than minimum allowed size, it can't be placed
        print ("Impossible to place " + orderSide + " order: " + "Minimum size is " + str(settings[MIN_SIZE]) + " " + settings[CRYPTO_CURRENCY] + " and you're trying to " + orderSide + " " + str(orderSize) + " " + settings[CRYPTO_CURRENCY])
        textResult = textResult + "\n" + "Impossible to place " + orderSide + " order: " + "Minimum size is " + str(settings[MIN_SIZE]) + " " + settings[CRYPTO_CURRENCY] + " and you're trying to " + orderSide + " " + str(orderSize) + " " + settings[CRYPTO_CURRENCY]
    return textResult

def placeBuyOrder(client, settings):
    """Place a buy order based on current settings"""
    #Get the amount available to place a buy order
    textResult = ""
    baseCurrencyInOpenOrders = getWalletHold(client, settings[BASE_CURRENCY])
    baseCurrencyAvailable = min(getWalletBalance(client, settings[BASE_CURRENCY])- baseCurrencyInOpenOrders, settings[MAX_BUY_AMOUNT])
    print (settings[BASE_CURRENCY] + " available: " + str(float(baseCurrencyAvailable)))
    #If there's an amount available, price and size are calculated based on the settings
    if baseCurrencyAvailable > 0:
        buyPrice = calculateOrderPrice(client, ORDER_SIDE_BUY, settings)
        buySize = calculateBuySize(baseCurrencyAvailable, buyPrice, client, settings)
        textResult = placeOrder(client, ORDER_SIDE_BUY, buySize, buyPrice, settings)
    else:
        print ("You have no available " + settings[BASE_CURRENCY] + " to place a " + ORDER_SIDE_BUY + " order")
    return textResult

def placeSellOrder(client, activeFillsToRemove, settings):
    """Place a sell order based on current settings"""
    #Get the amount available to place a buy order
    textResult = ""
    cryptoInOpenOrders = getWalletHold(client, settings[CRYPTO_CURRENCY])
    cryptoAvailable = getWalletBalance(client, settings[CRYPTO_CURRENCY]) - cryptoInOpenOrders
    print (settings[CRYPTO_CURRENCY] + " available: " + str(float(cryptoAvailable)))
    #If there's an amount available, price and size are calculated based on the settings
    if cryptoAvailable > 0:
        sellPrice = calculateOrderPrice(client, ORDER_SIDE_SELL, settings)
        sellSize = calculateSellSize(client, cryptoAvailable, sellPrice, activeFillsToRemove, settings)
        if sellSize > 0:
            textResult = placeOrder(client, ORDER_SIDE_SELL, sellSize, sellPrice, settings)
        else:
            print ("You have no available " + settings[CRYPTO_CURRENCY] + " to place a " + ORDER_SIDE_SELL + " order at " + str(sellPrice))
    else:
        print ("You have no available " + settings[CRYPTO_CURRENCY] + " to place a " + ORDER_SIDE_SELL + " order")
    return textResult

def executeTradingEngine(client, settings, duration):
    """Execute the trading engine for the given duration"""
    try:
        global LAST_ORDERS
        global TRADING_ENGINE_ACTIVE
        activeFillsToRemove = {}
        if settings[IGNORE_EXISTING_FILLS]:
            activeFillsToRemove = calculateActiveFills(client, settings)
        actualTime = datetime.utcnow()
        limitTime = actualTime + timedelta(seconds = duration)
        output = "Engine executed correctly from " + str(actualTime)
        while (actualTime < limitTime) and TRADING_ENGINE_ACTIVE:
            LAST_ORDERS = ""
            if not settings[AUTO_CANCEL]:
                cancelObsoleteOrders(client, settings)
            LAST_ORDERS = placeBuyOrder(client, settings)
            time.sleep(settings[ORDER_TIME_INTERVAL]/2)
            LAST_ORDERS = LAST_ORDERS + "\n" + placeSellOrder(client, activeFillsToRemove, settings)
            time.sleep(settings[ORDER_TIME_INTERVAL]/2)
            actualTime = datetime.utcnow()
        if not settings[AUTO_CANCEL]:
            time.sleep(settings[ORDER_TIME_DURATION] - settings[ORDER_TIME_INTERVAL]/2)
            cancelObsoleteOrders(client, settings)
        output = output + " to " + str(actualTime)
        print(output)
        LAST_ORDERS = ""
    except Exception:
        print("Error in the execution of the engine: " + str(traceback.print_exc()))
        TRADING_ENGINE_ACTIVE = 0
        if(settings[AUTO_RESTART]):
                startTradingEngine(client, settings)
    return

def startTradingEngine(client, settings):
    global TRADING_ENGINE_ACTIVE
    if not TRADING_ENGINE_ACTIVE:
        settings = updateSettings(client)
        result = ""
        duration = settings[ENGINE_RUN_DURATION]
        if duration >= 0:
            result = "Engine is going to run for " + str(duration) + " seconds"
        else:
            result = "Engine duration is set to a negative number. Please correct its value in settings.cfg"
        TRADING_ENGINE_ACTIVE = 1
        tradingEngineThread = threading.Thread(target = executeTradingEngine, args = [client, settings, settings[ENGINE_RUN_DURATION]])
        tradingEngineThread.start()
    else:
        result =  "Trading engine is already running."
    return result

def stopTradingEngine():
    result = ""
    global TRADING_ENGINE_ACTIVE
    if TRADING_ENGINE_ACTIVE:
        TRADING_ENGINE_ACTIVE = 0
        result = "Trading engine stopped."
    else:
        result = "Trading engine already stopped."
    return result

def getTradingEngineStatusText():
    result = ""
    global TRADING_ENGINE_ACTIVE
    global LAST_ORDERS
    if TRADING_ENGINE_ACTIVE:
        result = "Trading engine is running.\nLast orders were:\n" + LAST_ORDERS
    else:
        result = "Trading engine is not running"
    return result


def sellActiveFills(client, settings):
    try:
        settings = updateSettings(client)
        activeFills = calculateActiveFills(client, settings)
        orderedBuyPrices = list(activeFills.keys())
        orderedBuyPrices.sort(reverse = True)
        for orderedPriceItem in orderedBuyPrices:
            if activeFills[orderedPriceItem] != 0:
                cryptoInOpenOrders = getWalletHold(client, settings[CRYPTO_CURRENCY])
                cryptoAvailable = getWalletBalance(client, settings[CRYPTO_CURRENCY]) - cryptoInOpenOrders
                if cryptoAvailable > 0:
                    sellPrice = Decimal(orderedPriceItem * settings[SELL_PRICE_FACTOR])
                    sellPrice = sellPrice.quantize(Decimal(settings[PRICE_INCREMENT]), rounding = ROUND_UP)
                    sellSize = min(activeFills[orderedPriceItem], cryptoAvailable)
                    sellSize = sellSize.quantize(Decimal(settings[SIZE_INCREMENT]))
                    placeOrder(client, ORDER_SIDE_SELL, sellSize, sellPrice, settings)
    except Exception:
        print("Error in the execution of the engine: " + str(traceback.print_exc()))
    return

def sellActiveFillsText(client, settings):
    result = "Selling following active fills:\n"
    result = result + getFillsText(client, settings)
    sellActiveFills(client, settings)
    return result

def printSellActiveFills(client, settings):
    print(sellActiveFillsText(client, settings))

def printOpenOrders(client):
    print ("\n")
    print(getOpenOrdersText(client))
    return

def getOpenOrdersText(client):
    result = ""
    orders = list(client.get_orders())
    if not orders:
        result = "There are no open orders on your wallet account."
    for order in orders:
        result = result + "ID: " + order["id"] + "\n" + "Type: " + order["side"] + "\n" + "Price: " + order["price"] + "\n" + "Size: " + order["size"] + "\n" + "Product ID: " + order["product_id"] + "\n"
    return result

def printBalance(client, settings):
    print(getBalanceText(client, settings))

def getBalanceText(client, settings):
    result = ""
    fills = getFills(client, settings[BASE_CURRENCY], settings[CRYPTO_CURRENCY])
    balance = Decimal(0.0)
    last24hBalance = Decimal(0.0)
    last24hSize = Decimal(0.0)
    limitTime = datetime.utcnow() - timedelta(hours = 24)
    for fill in fills:
        size = Decimal(fill["size"])
        amount = Decimal(fill["price"]) * size
        fee = Decimal(fill["fee"])
        if fill["side"] == ORDER_SIDE_BUY:
            balance = balance - amount
        else:
            balance = balance + amount
        balance = balance - fee
        fillTime = datetime.strptime(fill["created_at"],'%Y-%m-%dT%H:%M:%S.%fZ')
        if fillTime > limitTime:
            if fill["side"] == ORDER_SIDE_BUY:
                last24hBalance = last24hBalance - amount
                last24hSize = last24hSize + size
            else:
                last24hBalance = last24hBalance + amount
                last24hSize = last24hSize - size
            last24hBalance = last24hBalance - fee
    result = result + "Current overall gain is " + str(float(balance)) + " " + settings[BASE_CURRENCY] + "\n"
    result = result + "Last 24 hours gain is "+ str(float(last24hBalance)) + " " + settings[BASE_CURRENCY] + " and " + str(float(last24hSize)) + " " + settings[CRYPTO_CURRENCY] + " bought"
    return result

def printActiveFills(client, settings):
    print(getFillsText(client, settings))

def getFillsText(client, settings):
    result = ""
    activeFills = calculateActiveFills(client, settings)
    orderedBuyPrices = list(activeFills.keys())
    orderedBuyPrices.sort(reverse = True)
    for orderedPriceItem in orderedBuyPrices:
        if activeFills[orderedPriceItem] != 0:
            result = result + "Buy price: " + str(float(orderedPriceItem)) + " Remaining quantity: " + str(float(activeFills[orderedPriceItem])) + "\n"
    if not result:
        result = "There are no active fills to sell."
    return result