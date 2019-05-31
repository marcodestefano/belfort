"""Main belfort file."""

import cbpro
import os
import time
from decimal import Decimal
from datetime import datetime
from datetime import timedelta

ORDER_SIDE_BUY = "buy"
ORDER_SIDE_SELL = "sell"

BUY_PRICE_FACTOR = 0.5
SELL_PRICE_FACTOR = 1.5

BASE_CURRENCY = "EUR"
CRYPTO_CURRENCY = "XLM"

def getConfiguration():
    """Retrieve the configuration file."""
    fileName = 'data.cfg'

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


def promptCommand(text, acceptedValues):
    """Send a message to screen to get an input."""
    command = input(text).lower()
    while command not in acceptedValues:
        command = input(text).lower()
    return command

def getCurrencyPair(baseCurrency, otherCurrency):
	return otherCurrency + "-" + baseCurrency

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


def printValues(client):
    """Print currency values."""
    currencies = ["BTC", "ETH", "LTC", "XLM"]
    baseCurrency = BASE_CURRENCY
    print ("\nHere the current values of cryptocurrencies:\n")
    for currency in currencies:
        currencyPair = getCurrencyPair(baseCurrency, currency)
        ticker = client.get_product_ticker(product_id=currencyPair)
        print ("Current %s price is: %s %s" % (currency, ticker["price"],
                                              baseCurrency))

def getValue(client, baseCurrency, cryptoCurrency):
	currencyPair = getCurrencyPair(baseCurrency, cryptoCurrency)
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
			limitTime = placedAt + timedelta(seconds = 10)
			actualTime = datetime.utcnow()
			if actualTime > limitTime:
				client.cancel_order(order["id"])
				print ("Canceled " + order["side"] + " order " + order["id"] + " of size " + order["size"] + " and price " + order["price"] + "placed at " + str(placedAt))
	return

def getEuroInOpenOrders(client):
	orders = list(client.get_orders())
	result = Decimal(0.00)
	for order in orders:
		if order["side"] == ORDER_SIDE_BUY:
			result = result + Decimal(order["price"]) * Decimal(order["size"])
	return result

def placeBuyOrder(client):
	euroBlocked = getEuroInOpenOrders(client)
	print (baseCurrency + " already blocked in open orders: " + str(euroBlocked))
	euroAvailable = Decimal(getWallet(client, baseCurrency)) - euroBlocked
	currentCurrencyPrice = Decimal(getValue(client, baseCurrency, currencyOrder))
	buyPrice = Decimal(currentCurrencyPrice) * Decimal(BUY_PRICE_FACTOR)
	buySize = Decimal(euroAvailable)* Decimal(0.5) / Decimal(buyPrice)
	buyPrice = round(buyPrice,6)
	buySize = round(buySize, 0)
	print ("Placing an order of " + str(buySize) + " " + currencyOrder + " at price of " + str(buyPrice) + " " + baseCurrency)
	result = client.place_limit_order(product_id=getCurrencyPair(baseCurrency, currencyOrder), 
                  side='buy', 
                  price=str(buyPrice), 
                  size=str(buySize))
	#print (result)
	return

def startTradingEngine(client):
	currencyOrder = CRYPTO_CURRENCY
	baseCurrency = BASE_CURRENCY 
	i = 0
	while i<5:
		cancelObsoleteOrders(client)
		placeBuyOrder(client)
		placeSellOrder(client)
		time.sleep(5)
		i = i+1


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
    config = getConfiguration()
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
