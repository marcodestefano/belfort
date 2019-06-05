"""Main belfort file."""

import cbpro
import os
import time
import smtplib
from decimal import Decimal
from datetime import datetime
from datetime import timedelta

DATA_FILENAME = 'data.cfg'
SETTINGS_FILENAME = 'settings.cfg'
API_KEY = 'APIKey'
API_SECRET = 'APISecret'
API_PASSPHRASE = 'APIPassphrase'
# API_URL = "https://api-public.sandbox.pro.coinbase.com"
API_URL = "https://api.pro.coinbase.com"
EMAIL_ADDRESS = "EMAIL_ADDRESS"
ENGINE_RUN_DURATION = "ENGINE_RUN_DURATION"
AUTO_RESTART = "AUTO_RESTART"
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
ORDER_SIDE_BUY = "buy"
ORDER_SIDE_SELL = "sell"

DEFAULT_ENGINE_RUN_DURATION = 300
DEFAULT_AUTO_RESTART = 0

DEFAULT_BUY_PRICE_FACTOR = 0.5
DEFAULT_SELL_PRICE_FACTOR = 1.5

DEFAULT_BUY_AMOUNT_FACTOR = 0.5
DEFAULT_SELL_AMOUNT_FACTOR = 0.5

DEFAULT_ORDER_TIME_DURATION = 10
DEFAULT_ORDER_TIME_INTERVAL = 3

DEFAULT_BASE_CURRENCY = "EUR"
DEFAULT_CRYPTO_CURRENCY = "XLM"

ROUNDING_MINIMUM_ORDER = { "BTC": "0.001",
"BCH": "0.01",
"ETH": "0.01",
"MKR": "0.01",
"ZEC": "0.01",
"EOS": "0.1",
"ETC": "0.1",
"LTC": "0.1",
"REP": "0.1",
"BAT": "1",
"CVC": "1",
"DAI": "1",
"DNT": "1",
"GNT": "1",
"LOOM": "1",
"MANA":	"1",
"XLM": "1",
"XRP": "1",
"ZIL": "1",
"ZRX": "1"
}


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

def updateSettings():
	settings = getConfiguration(SETTINGS_FILENAME)
	if settings:

		if settings[ENGINE_RUN_DURATION]:
			settings[ENGINE_RUN_DURATION] = int(settings[ENGINE_RUN_DURATION])
		else:
			setting[ENGINE_RUN_DURATION] = DEFAULT_ENGINE_RUN_DURATION

		if settings[AUTO_RESTART]:
			settings[AUTO_RESTART] = int(settings[AUTO_RESTART])
		else:
			setting[AUTO_RESTART] = DEFAULT_AUTO_RESTART

		if settings[BUY_PRICE_FACTOR]:
			settings[BUY_PRICE_FACTOR] = Decimal(settings[BUY_PRICE_FACTOR])
		else:
			setting[BUY_PRICE_FACTOR] = DEFAULT_BUY_PRICE_FACTOR

		if settings[SELL_PRICE_FACTOR]:
			settings[SELL_PRICE_FACTOR] = Decimal(settings[SELL_PRICE_FACTOR])
		else:
			setting[SELL_PRICE_FACTOR] = DEFAULT_SELL_PRICE_FACTOR

		if settings[BUY_AMOUNT_FACTOR]:
			settings[BUY_AMOUNT_FACTOR] = Decimal(settings[BUY_AMOUNT_FACTOR])
		else:
			setting[BUY_AMOUNT_FACTOR] = DEFAULT_BUY_AMOUNT_FACTOR

		if settings[SELL_AMOUNT_FACTOR]:
			settings[SELL_AMOUNT_FACTOR] = Decimal(settings[SELL_AMOUNT_FACTOR])
		else:
			setting[SELL_AMOUNT_FACTOR] = DEFAULT_SELL_AMOUNT_FACTOR

		if settings[ORDER_TIME_DURATION]:
			settings[ORDER_TIME_DURATION] = int(settings[ORDER_TIME_DURATION])
		else:
			setting[ORDER_TIME_DURATION] = DEFAULT_ORDER_TIME_DURATION

		if settings[ORDER_TIME_INTERVAL]:
			settings[ORDER_TIME_INTERVAL] = int(settings[ORDER_TIME_INTERVAL])
		else:
			setting[ORDER_TIME_INTERVAL] = DEFAULT_ORDER_TIME_INTERVAL

		if settings[BASE_CURRENCY] is None:
			setting[BASE_CURRENCY] = DEFAULT_BASE_CURRENCY

		if settings[CRYPTO_CURRENCY] is None:
			setting[CRYPTO_CURRENCY] = DEFAULT_CRYPTO_CURRENCY
	return settings

def promptCommand(text, acceptedValues):
    """Send a message to screen to get an input."""
    command = input(text).lower()
    while command not in acceptedValues:
        command = input(text).lower()
    return command

def sendEmail(message):
	config = getConfiguration(DATA_FILENAME)
	if(config[EMAIL_ADDRESS]):
		fromAddress = 'engine@belfort.crypto'
		toAddress  = config[EMAIL_ADDRESS]
		subject = "Engine execution completed"
		server = 'gmail-smtp-in.l.google.com:25'
		msg = '''
    		From: {fromaddress}
    		To: {toaddress}
    		Subject: {subject}     
    		{text}
		'''
	msg = msg.format(fromaddress =fromAddress, toaddress = toAddress, subject = subject, text = message)
	try:
		server = smtplib.SMTP(server)
		server.starttls()
		server.ehlo("belfort.crypto")
		server.mail(fromAddress)
		server.rcpt(toAddress)
		server.data(msg)
		server.quit()
	except Exception as exc:
		print ("Unable to send email: %s" % (exc))

def getCurrencyPair(BASE_CURRENCY, otherCurrency):
	return otherCurrency + "-" + BASE_CURRENCY

def getDecimalPositions(value):
	result = -1
	if value:
		if "." in value:
			value = str(float(value))
		else:
			value = str(int(value))
		result = value[::-1].find('.')
	return result

def getRoundingFactor(currency):
	result = 1
	if ROUNDING_MINIMUM_ORDER[currency]:
		result = getDecimalPositions(ROUNDING_MINIMUM_ORDER[currency])
	if result == -1:
		result = 0
	return result

def getMinimumOrderAmount(currency):
	result = 0
	if ROUNDING_MINIMUM_ORDER[currency]:
		result = Decimal(ROUNDING_MINIMUM_ORDER[currency])
	return result

def getWallets(client):
    """Retrieve the wallets of an account."""
    accounts = client.get_accounts()
    wallets = {}
    if accounts:
        for account in accounts:
            wallets[account["id"]] = account["balance"] +\
                                    " " + account["currency"]
    return wallets

def getWalletBalance(client, currency):
	accounts = client.get_accounts()
	if accounts:
		for account in accounts:
			if account["currency"] == currency:
				return account["balance"]

def getWalletHold(client, currency):
	accounts = client.get_accounts()
	if accounts:
		for account in accounts:
			if account["currency"] == currency:
				return account["hold"]

def printWallets(client):
    """Print wallet content."""
    print ("\nHere's the list of your wallets:\n")
    wallets = getWallets(client)
    for account in wallets:
    	if Decimal(wallets[account][:-4]) > 0:
        	print ("%s: %s" % (account, wallets[account]))
    return

def printValue(client, settings):
    """Print currency value"""
    settings = updateSettings()
    currencyPair = getCurrencyPair(settings[BASE_CURRENCY], settings[CRYPTO_CURRENCY])
    ticker = client.get_product_ticker(product_id=currencyPair)
    print ("Current %s price is: %s %s" % (settings[CRYPTO_CURRENCY], ticker["price"],
                                              settings[BASE_CURRENCY]))

def getValue(client, baseCurrency, cryptoCurrency):
	currencyPair = getCurrencyPair(baseCurrency, cryptoCurrency)
	ticker = client.get_product_ticker(product_id=currencyPair)
	if ticker:
		return ticker["price"]
	else:
		return ""

def getFills(client, settings):
	return list(client.get_fills(product_id=getCurrencyPair(settings[BASE_CURRENCY], settings[CRYPTO_CURRENCY])))

def cancelObsoleteOrders(client, settings):
	currencyPair = getCurrencyPair(settings[BASE_CURRENCY], settings[CRYPTO_CURRENCY])
	orders = list(client.get_orders())
	for order in orders:
		if order["product_id"] == currencyPair :
			placedAt = datetime.strptime(order["created_at"],'%Y-%m-%dT%H:%M:%S.%fZ')
			limitTime = placedAt + timedelta(seconds = settings[ORDER_TIME_DURATION])
			actualTime = datetime.utcnow()
			if actualTime > limitTime:
				client.cancel_order(order["id"])
				print ("Canceled " + order["side"] + " order " + order["id"] + " of size " + order["size"] + " and price " + order["price"] + " placed at " + str(placedAt))
	return

def getEuroInOpenOrders(client, settings):
	result = Decimal(getWalletHold(client, settings[BASE_CURRENCY]))
	return result

def getCryptoInOpenOrders(client, settings):
	result = Decimal(getWalletHold(client, settings[CRYPTO_CURRENCY]))
	return result

def calculateOrderPrice(client, orderSide, settings):
	#feeMultiplier = -1
	orderFactor = settings[BUY_PRICE_FACTOR]
	if orderSide == ORDER_SIDE_SELL:
	#	feeMultiplier = 1
		orderFactor = settings[SELL_PRICE_FACTOR]
	currentCurrencyPriceText = getValue(client, settings[BASE_CURRENCY], settings[CRYPTO_CURRENCY])
	currentCurrencyPrice = Decimal(currentCurrencyPriceText)
	orderPrice = Decimal(currentCurrencyPrice) * Decimal(orderFactor)
	#orderPrice = orderPrice + Decimal(currentCurrencyPrice)*settings[ORDER_FEE]*feeMultiplier
	orderPrice = round(orderPrice, max(getDecimalPositions(currentCurrencyPriceText),2))
	return orderPrice

def calculateBuySize(euroAvailable, buyPrice, settings):
	buySize = Decimal(euroAvailable)* Decimal(settings[BUY_AMOUNT_FACTOR]) / Decimal(buyPrice)
	buySize = round(buySize, getRoundingFactor(settings[CRYPTO_CURRENCY]))
	return buySize

def calculateSellSize(client, cryptoAvailable, sellPrice, settings):
	fills = getFills(client, settings)
	buyFills = {}
	sellFills = {}
	for fill in fills:
		if fill["side"] == ORDER_SIDE_BUY:
			realFillPrice = Decimal(fill["price"])+Decimal(fill["fee"])/Decimal(fill["size"])
			if realFillPrice not in buyFills:
				buyFills[realFillPrice] = Decimal(0)
			buyFills[realFillPrice] = buyFills[realFillPrice] + Decimal(fill["size"])
		else:
			realFillPrice = Decimal(fill["price"])-Decimal(fill["fee"])/Decimal(fill["size"])
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
	openOrders = list(client.get_orders(product_id = getCurrencyPair(settings[BASE_CURRENCY], settings[CRYPTO_CURRENCY])))
	sellOrders = {}
	for order in openOrders:
		if order["side"] == ORDER_SIDE_SELL:
			if Decimal(order["price"]) not in sellOrders:
				sellOrders[Decimal(order["price"])] = Decimal(0)
			sellOrders[Decimal(order["price"])] = sellOrders[Decimal(order["price"])] + Decimal(order["size"]) - Decimal(order["filled_size"]) 
	orderedOrderPrices = list(sellOrders.keys())
	orderedOrderPrices.sort(reverse = True)
	for orderPriceItem in orderedOrderPrices:
		for buyPriceItem in orderedBuyPrices:
			quantityOrder = sellOrders[orderPriceItem]
			if quantityOrder > 0:
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
		if buyPriceItem < sellPrice:
			amountToSell = amountToSell + buyFills[buyPriceItem]

	cryptoAvailable = min(Decimal(cryptoAvailable), Decimal(amountToSell))
	sellSize = Decimal(cryptoAvailable)* Decimal(settings[SELL_AMOUNT_FACTOR])
	sellSize = round(sellSize, getRoundingFactor(settings[CRYPTO_CURRENCY]))
	return sellSize

def placeOrder(client, orderSide, orderSize, orderPrice, settings):
	if orderSize >= getMinimumOrderAmount(settings[CRYPTO_CURRENCY]):
		print ("Placing a " + orderSide + " order of " + str(orderSize) + " " + settings[CRYPTO_CURRENCY] + " at price of " + str(orderPrice) + " " + settings[BASE_CURRENCY])
		result = client.place_limit_order(product_id=getCurrencyPair(settings[BASE_CURRENCY], settings[CRYPTO_CURRENCY]), 
                  side=orderSide, 
                  price=str(orderPrice), 
                  size=str(orderSize), post_only = True)
		try:
			print (orderSide + " order placed with ID " + result["id"])
		except Exception as exc:
			print ("Error in placing " + orderSide + " order: " + result["message"])
	else:
		print ("Error in placing " + orderSide + " order: " + "Minimum size is " + str(getMinimumOrderAmount(settings[CRYPTO_CURRENCY])) + " " + settings[CRYPTO_CURRENCY])
	return

def placeBuyOrder(client, settings):
	euroBlocked = getEuroInOpenOrders(client, settings)
	print (settings[BASE_CURRENCY] + " already blocked in open orders: " + str(float(euroBlocked)))
	euroAvailable = Decimal(getWalletBalance(client, settings[BASE_CURRENCY])) - euroBlocked
	if euroAvailable > 0:
		buyPrice = calculateOrderPrice(client, ORDER_SIDE_BUY, settings)
		buySize = calculateBuySize(euroAvailable, buyPrice, settings)
		placeOrder(client, ORDER_SIDE_BUY, buySize, buyPrice, settings)
	else:
		print ("You have no available " + settings[BASE_CURRENCY] + " to place a " + ORDER_SIDE_BUY + " order")
	return

def placeSellOrder(client, settings):
	cryptoBlocked = getCryptoInOpenOrders(client, settings)
	print (settings[CRYPTO_CURRENCY] + " already blocked in open orders: " + str(float(cryptoBlocked)))
	cryptoAvailable = Decimal(getWalletBalance(client, settings[CRYPTO_CURRENCY])) - cryptoBlocked
	if cryptoAvailable > 0:
		sellPrice = calculateOrderPrice(client, ORDER_SIDE_SELL, settings)
		sellSize = calculateSellSize(client, cryptoAvailable, sellPrice, settings)
		placeOrder(client, ORDER_SIDE_SELL, sellSize, sellPrice, settings)
	else:
		print ("You have no available " + settings[CRYPTO_CURRENCY] + " to place a " + ORDER_SIDE_SELL + " order")
	return

def executeTradingEngine(client, settings, duration):
	actualTime = datetime.utcnow()
	limitTime = actualTime + timedelta(seconds = duration)
	output = "Engine executed correctly from " + str(actualTime)
	while actualTime < limitTime:
		cancelObsoleteOrders(client, settings)
		placeBuyOrder(client, settings)
		time.sleep(settings[ORDER_TIME_INTERVAL]/2)
		placeSellOrder(client, settings)
		time.sleep(settings[ORDER_TIME_INTERVAL]/2)
		actualTime = datetime.utcnow()
	time.sleep(settings[ORDER_TIME_DURATION] - settings[ORDER_TIME_INTERVAL]/2)
	cancelObsoleteOrders(client, settings)
	output = output + " to " + str(actualTime)
	return output

def startTradingEngine(client, settings):
	output = ""
	try:
		settings = updateSettings()
		print("Engine is going to run for " + str(settings[ENGINE_RUN_DURATION]) + " seconds")
		output = executeTradingEngine(client, settings, settings[ENGINE_RUN_DURATION])
		print(output)
	except Exception as exc:
		output = "Error in the execution of the engine: " + str(exc)
		print(output)
		if(settings[AUTO_RESTART]):
			startTradingEngine(client, settings)
	sendEmail(output)
	return

def printOpenOrders(client):
	print ("\n")
	orders = list(client.get_orders())
	for order in orders:
		print ("ID: " + order["id"])
		print ("Type: " + order["side"])
		print ("Price: " + order["price"])
		print ("Size: " + order["size"])
		print ("Product ID: " + order["product_id"])
		print ("\n")
	return

def printFills(client, settings):
	print ("\n")
	settings = updateSettings()
	fills = getFills(client, settings)
	for fill in fills:
		print ("Order ID: " + fill["order_id"])
		print ("Type: " + fill["side"])
		print ("Price: " + fill["price"] + " " + settings[BASE_CURRENCY])
		print ("Size: " + fill["size"] + " " + settings[CRYPTO_CURRENCY])
		print ("\n")
	return

client = None
accounts = None
config = None
command = ""
commandDisplayWallet = "1"
commandDisplayOpenOrders = "2"
commandDisplayCurrencyValue = "3"
commandStartTradingEngine = "4"
commandDisplayFills = "5"
commandExit = "e"
commandList = [commandDisplayWallet, commandDisplayOpenOrders, commandDisplayCurrencyValue, commandStartTradingEngine, commandDisplayFills, commandExit]
commandMainInput = "What's next?\n" \
    "Press 1 to display your wallets\n" \
    "Press 2 to display your open orders\n" \
    "Press 3 to display current currency value\n" \
    "Press 4 to start the trading engine\n" \
    "Press 5 to display recent fills\n" \
    "Press e (or ctrl+c) to exit the program\n" \
    "Select your choice: "

print ("\nWelcome to Belfort!\n\n")
try:
    config = getConfiguration(DATA_FILENAME)
    settings = updateSettings()
except Exception as exc:
    print ("Catched exception: %s" % (exc))
try:
    while 1:
        command = promptCommand(commandMainInput, commandList)
        client = cbpro.AuthenticatedClient(config[API_KEY], config[API_SECRET],
                                  config[API_PASSPHRASE], api_url=API_URL)
        if command == commandDisplayWallet:
            printWallets(client)
        elif command == commandDisplayOpenOrders:
        	printOpenOrders(client)
        elif command == commandDisplayCurrencyValue:
            printValue(client, settings)
        elif command == commandStartTradingEngine:
        	startTradingEngine(client, settings)
        elif command == commandDisplayFills:
        	printFills(client, settings)
        elif command == commandExit:
            exit()
        print ("\n")
except Exception as exc:
	print ("Catched exception: %s" % (exc))
