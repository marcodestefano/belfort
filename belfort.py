"""Main belfort file."""

import cbpro
import os
import time
from decimal import Decimal
from datetime import datetime
from datetime import timedelta

ORDER_SIDE_BUY = "buy"
ORDER_SIDE_SELL = "sell"

#BUY_PRICE_FACTOR = 0.995
#SELL_PRICE_FACTOR = 1.005

BUY_PRICE_FACTOR = 0.5
SELL_PRICE_FACTOR = 1.5

BUY_AMOUNT_FACTOR = 0.5
SELL_AMOUNT_FACTOR = 0.5

ROUNDING_BASE_CURRENCY = 6
ROUNDING_CRYPTO_CURRENCY = 0

ORDER_TIME_DURATION = 10
ORDER_TIME_INTERVAL = 5

BASE_CURRENCY = "EUR"
CRYPTO_CURRENCY = "XLM"

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

def modifySettings(settings):
	if settings:
		if settings["BUY_PRICE_FACTOR"]:
			BUY_PRICE_FACTOR = Decimal(settings["BUY_PRICE_FACTOR"])
	return


def promptCommand(text, acceptedValues):
    """Send a message to screen to get an input."""
    command = input(text).lower()
    while command not in acceptedValues:
        command = input(text).lower()
    return command

def getCurrencyPair(BASE_CURRENCY, otherCurrency):
	return otherCurrency + "-" + BASE_CURRENCY

def getWallets(client):
    """Retrieve the wallets of an account."""
    accounts = client.get_accounts()
    wallets = {}
    if accounts:
        for account in accounts:
            wallets[account["id"]] = account["balance"] +\
                                    " " + account["currency"]
    return wallets

def getWallet(client, currency):
	accounts = client.get_accounts()
	if accounts:
		for account in accounts:
			if account["currency"] == currency:
				return account["balance"]

def printWallets(client):
    """Print wallet content."""
    print ("\nHere's the list of your wallets:\n")
    wallets = getWallets(client)
    for account in wallets:
    	if Decimal(wallets[account][:-4]) > 0:
        	print ("%s: %s" % (account, wallets[account]))
    return


def printValues(client):
    """Print currency values."""
    currencies = ["BTC", "ETH", "LTC", "XLM"]
    print ("\nHere the current values of cryptocurrencies:\n")
    for currency in currencies:
        currencyPair = getCurrencyPair(BASE_CURRENCY, currency)
        ticker = client.get_product_ticker(product_id=currencyPair)
        print ("Current %s price is: %s %s" % (currency, ticker["price"],
                                              BASE_CURRENCY))

def getValue(client, BASE_CURRENCY, cryptoCurrency):
	currencyPair = getCurrencyPair(BASE_CURRENCY, cryptoCurrency)
	ticker = client.get_product_ticker(product_id=currencyPair)
	if ticker:
		return ticker["price"]
	else:
		return ""

def cancelObsoleteOrders(client):
	currencyPair = getCurrencyPair(BASE_CURRENCY, CRYPTO_CURRENCY)
	orders = list(client.get_orders())
	for order in orders:
		if order["product_id"] == currencyPair :
			placedAt = datetime.strptime(order["created_at"],'%Y-%m-%dT%H:%M:%S.%fZ')
			limitTime = placedAt + timedelta(seconds = ORDER_TIME_DURATION)
			actualTime = datetime.utcnow()
			if actualTime > limitTime:
				client.cancel_order(order["id"])
				print ("Canceled " + order["side"] + " order " + order["id"] + " of size " + order["size"] + " and price " + order["price"] + "placed at " + str(placedAt))
	return

def getEuroInOpenOrders(client):
	orders = list(client.get_orders())
	result = Decimal(0)
	for order in orders:
		if order["side"] == ORDER_SIDE_BUY:
			result = result + Decimal(order["price"]) * Decimal(order["size"])
	return result

def getCryptoInOpenOrders(client):
	orders = list(client.get_orders())
	result = Decimal(0)
	for order in orders:
		if (order["side"] == ORDER_SIDE_SELL) and (order["product_id"] == getCurrencyPair(BASE_CURRENCY, CRYPTO_CURRENCY)):
			result = result + Decimal(order["size"])
	return result

def placeBuyOrder(client):
	euroBlocked = getEuroInOpenOrders(client)
	print (BASE_CURRENCY + " already blocked in open orders: " + str(euroBlocked))
	euroAvailable = Decimal(getWallet(client, BASE_CURRENCY)) - euroBlocked
	currentCurrencyPrice = Decimal(getValue(client, BASE_CURRENCY, CRYPTO_CURRENCY))
	buyPrice = Decimal(currentCurrencyPrice) * Decimal(BUY_PRICE_FACTOR)
	buySize = Decimal(euroAvailable)* Decimal(BUY_AMOUNT_FACTOR) / Decimal(buyPrice)
	buyPrice = round(buyPrice, ROUNDING_BASE_CURRENCY)
	buySize = round(buySize, ROUNDING_CRYPTO_CURRENCY)
	print ("Placing a " + ORDER_SIDE_BUY + " order of " + str(buySize) + " " + CRYPTO_CURRENCY + " at price of " + str(buyPrice) + " " + BASE_CURRENCY)
	result = client.place_limit_order(product_id=getCurrencyPair(BASE_CURRENCY, CRYPTO_CURRENCY), 
                  side=ORDER_SIDE_BUY, 
                  price=str(buyPrice), 
                  size=str(buySize), post_only = True)
	#print (result)
	return

def placeSellOrder(client):
	cryptoBlocked = getCryptoInOpenOrders(client)
	print (CRYPTO_CURRENCY + " already blocked in open orders: " + str(cryptoBlocked))
	cryptoAvailable = Decimal(getWallet(client, CRYPTO_CURRENCY)) - cryptoBlocked
	currentCurrencyPrice = Decimal(getValue(client, BASE_CURRENCY, CRYPTO_CURRENCY))
	sellPrice = Decimal(currentCurrencyPrice) * Decimal(SELL_PRICE_FACTOR)
	sellSize = Decimal(cryptoAvailable)* Decimal(SELL_AMOUNT_FACTOR)
	sellPrice = round(sellPrice, ROUNDING_BASE_CURRENCY)
	sellSize = round(sellSize, ROUNDING_CRYPTO_CURRENCY)
	print ("Placing a " + ORDER_SIDE_SELL + " order of " + str(sellSize) + " " + CRYPTO_CURRENCY + " at price of " + str(sellPrice) + " " + BASE_CURRENCY)
	result = client.place_limit_order(product_id=getCurrencyPair(BASE_CURRENCY, CRYPTO_CURRENCY), 
                  side=ORDER_SIDE_SELL, 
                  price=str(sellPrice), 
                  size=str(sellSize), post_only = True)
	return

def startTradingEngine(client):
	i = 0
	while i<5:
		cancelObsoleteOrders(client)
		placeBuyOrder(client)
		placeSellOrder(client)
		time.sleep(ORDER_TIME_INTERVAL)
		i = i+1
	time.sleep(ORDER_TIME_DURATION - ORDER_TIME_INTERVAL)
	cancelObsoleteOrders(client)
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

def printFills(client):
	print ("\n")
	fills = list(client.get_fills(product_id=getCurrencyPair(BASE_CURRENCY, CRYPTO_CURRENCY)))
	for fill in fills:
		print ("Order ID: " + fill["order_id"])
		print ("Type: " + fill["side"])
		print ("Price: " + fill["price"] + " " + BASE_CURRENCY)
		print ("Size: " + fill["size"] + " " + CRYPTO_CURRENCY)
		print ("\n")
	return

client = None
accounts = None
config = None
command = ""
commandDisplayWallet = "1"
commandDisplayOpenOrders = "2"
commandDisplayCurrencyValues = "3"
commandStartTradingEngine = "4"
commandDisplayFills = "5"
commandExit = "e"
commandList = [commandDisplayWallet, commandDisplayOpenOrders, commandDisplayCurrencyValues, commandStartTradingEngine, commandDisplayFills, commandExit]
commandMainInput = "What's next?\n" \
    "Press 1 to display your wallets\n" \
    "Press 2 to display your open orders\n" \
    "Press 3 to display current currency values\n" \
    "Press 4 to start the trading engine\n" \
    "Press 5 to display recent fills\n" \
    "Press e (or ctrl+c) to exit the program\n" \
    "Select your choice: "
API_KEY = 'APIKey'
API_SECRET = 'APISecret'
API_PASSPHRASE = 'APIPassphrase'
# api_url = "https://api-public.sandbox.pro.coinbase.com"
api_url = "https://api.pro.coinbase.com"


print ("\nWelcome to Belfort!\n\n")
try:
    config = getConfiguration('data.cfg')
    #settings = getConfiguration('settings.cfg')
    client = cbpro.AuthenticatedClient(config[API_KEY], config[API_SECRET],
                                      config[API_PASSPHRASE], api_url=api_url)
except Exception as exc:
    print ("Catched exception: %s" % (exc))
if client:
	try:
	    while 1:
	        command = promptCommand(commandMainInput, commandList)
	        if command == commandDisplayWallet:
	            printWallets(client)
	        elif command == commandDisplayOpenOrders:
	        	printOpenOrders(client)
	        elif command == commandDisplayCurrencyValues:
	            printValues(client)
	        elif command == commandStartTradingEngine:
	        	startTradingEngine(client)
	        elif command == commandDisplayFills:
	        	printFills(client)
	        elif command == commandExit:
	            exit()
	        print ("\n")
	except Exception as exc:
		print ("Catched exception: %s" % (exc))
