"""Main belfort file."""

import gdax
import os


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


def getWallets(accounts):
    """Retrieve the wallets of an account."""
    wallets = {}
    if accounts:
        for account in accounts.data:
            balance = account.balance
            wallets[account.name] = balance.amount + " " + balance.currency
    return wallets


def promptCommand(text, acceptedValues):
    """Send a message to screen to get an input."""
    command = raw_input(text).lower()
    while command not in acceptedValues:
        command = raw_input(text).lower()
    return command


def printWallets(accounts):
    """Print wallet content."""
    print "\nHere's the list of your wallets:\n"
    wallets = getWallets(accounts)
    for account in wallets:
        print "%s: %s" % (account, wallets[account])


def printValues(client):
    """Print currency values."""
    currencies = ["BTC", "ETH", "LTC"]
    baseCurrency = "EUR"
    print "\nHere the current values of cryptocurrencies:\n"
    for currency in currencies:
        currencyPair = currency + "-" + baseCurrency
        price = client.get_sell_price(currency_pair=currencyPair)
        print "Current %s price is: %s %s" % (currency, price, baseCurrency)


client = None
accounts = None
config = None
command = ""
commandDisplayWallet = "1"
commandDisplayTransactions = "2"
commandDisplayCurrencyValues = "3"
commandExit = "e"
commandList = ["1", "2", "3", "e"]
commandMainInput = "What's next?\n" \
    "Press 1 to display your wallets\n" \
    "Press 2 to display your transactions\n" \
    "Press 3 to display current currency values\n" \
    "Press e (or ctrl+c) to exit the program\n" \
    "Select your choice: "
API_KEY = 'APIKey'
API_SECRET = 'APISecret'
API_PASSPHRASE = 'APIPassphrase'
api_url = "https://api-public.sandbox.gdax.com"

print "\nWelcome to Belfort!\n\n"
try:
    config = getConfiguration()
    client = gdax.AuthenticatedClient(config[API_KEY], config[API_SECRET],
                                      config[API_PASSPHRASE], api_url=api_url)
    accounts = client.get_accounts()
except Exception as exc:
    print "Catched exception: %s" % (exc)
if accounts:
    while 1:
        command = promptCommand(commandMainInput, commandList)
        if command == commandDisplayWallet:
            printWallets(accounts)
        elif command == commandDisplayCurrencyValues:
            printValues(client)
        elif command == commandExit:
            exit()
        print "\n"
