"""Main belfort file."""

import cbpro
import os
import time
from decimal import Decimal

ORDER_SIDE_BUY = "buy"

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

def getWallets(accounts):
    """Retrieve the wallets of an account."""
    wallets = {}
    if accounts:
        for account in accounts:
            wallets[account["id"]] = account["balance"] +\
                                    " " + account["currency"]
    return wallets

def getWallet(accounts, currency):
	if accounts:
		for account in accounts:
			if account["currency"] == currency:
				return account["balance"]

def printWallets(accounts):
    """Print wallet content."""
    print ("\nHere's the list of your wallets:\n")
    wallets = getWallets(accounts)
    print(wallets)
    for account in wallets:
        print ("%s: %s" % (account, wallets[account]))


def printValues(client):
    """Print currency values."""
    currencies = ["BTC", "ETH", "LTC", "XLM"]
    baseCurrency = "EUR"
    print ("\nHere the current values of cryptocurrencies:\n")
    for currency in currencies:
        currencyPair = getCurrencyPair(baseCurrency, currency)
        ticker = client.get_product_ticker(product_id=currencyPair)
        print ("Current %s price is: %s %s" % (currency, ticker["price"],
                                              baseCurrency))

def getValue(client, baseCurrency, otherCurrency):
	currencyPair = getCurrencyPair(baseCurrency, otherCurrency)
	ticker = client.get_product_ticker(product_id=currencyPair)
	if ticker:
		return ticker["price"]
	else:
		return ""

def cancelObsoleteOrders(client):
	return

def getEuroInOpenOrders(orders):
	result = Decimal(0.00)
	for order in orders:
		if order["side"] == ORDER_SIDE_BUY:
			result = result + Decimal(order["price"]) * Decimal(order["size"])
	return result

def placeOrder(client):
	# play with XLM only to start with
	currencyOrder = "XLM"
	baseCurrency = "EUR" 
	i = 0
	while i<5:
		accounts = client.get_accounts()
		cancelObsoleteOrders(client)
		orders = list(client.get_orders())
		euroBlocked = getEuroInOpenOrders(orders)
		print (baseCurrency + " already blocked in open orders: " + str(euroBlocked))
		euroAvailableText = getWallet(accounts, baseCurrency)
		currentCurrencyPriceText = getValue(client, baseCurrency, currencyOrder)
		if euroAvailableText:
			euroAvailable = Decimal(euroAvailableText) - euroBlocked
			if currentCurrencyPriceText:
				currentCurrencyPrice = Decimal(currentCurrencyPriceText)
				buyPrice = Decimal(currentCurrencyPrice) * Decimal(0.5)
				buySize = Decimal(euroAvailable)* Decimal(0.5) / Decimal(buyPrice)
				buyPrice = round(buyPrice,6)
				buySize = round(buySize, 0)
				print ("Placing an order of " + str(buySize) + " " + currencyOrder + " at price of " + str(buyPrice) + " " + baseCurrency)
				result = client.place_limit_order(product_id=getCurrencyPair(baseCurrency, currencyOrder), 
                              side='buy', 
                              price=str(buyPrice), 
                              size=str(buySize))
				print (result)
				print ("\n")
				time.sleep(5)
		i = i+1


def printOpenOrders(client):
	print ("\n")
	orders = list(client.get_orders())
	for order in orders:
		print ("ID: " + order["id"])
		print ("Type:" + order["side"])
		print ("Price: " + order["price"])
		print ("Size: " + order["size"])
		print ("Product ID: " + order["product_id"])
		print ("\n")


client = None
accounts = None
config = None
command = ""
commandDisplayWallet = "1"
commandDisplayOpenOrders = "2"
commandDisplayCurrencyValues = "3"
commandPlaceOrder = "4"
commandExit = "e"
commandList = [commandDisplayWallet, commandDisplayOpenOrders, commandDisplayCurrencyValues, commandPlaceOrder, commandExit]
commandMainInput = "What's next?\n" \
    "Press 1 to display your wallets\n" \
    "Press 2 to display your open orders\n" \
    "Press 3 to display current currency values\n" \
    "Press 4 to place an order\n" \
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
    public_client = cbpro.PublicClient()
    accounts = client.get_accounts()
except Exception as exc:
    print ("Catched exception: %s" % (exc))
if accounts:
    while 1:
        command = promptCommand(commandMainInput, commandList)
        if command == commandDisplayWallet:
            printWallets(accounts)
        elif command == commandDisplayOpenOrders:
        	printOpenOrders(client)
        elif command == commandDisplayCurrencyValues:
            printValues(client)
        elif command == commandPlaceOrder:
        	placeOrder(client)
        elif command == commandExit:
            exit()
        print ("\n")
