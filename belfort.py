"""Main belfort file."""
import traceback
from utils import authenticateClient, updateSettings, printWallets, printOpenOrders, printValue, printBalance, printActiveFills, startTradingEngine, sellActiveFills

def promptCommand(text, acceptedValues):
    """Send a message to screen to get an input."""
    command = str(input(text)).lower()
    while command not in acceptedValues:
        command = str(input(text)).lower()
    return command

client = None
accounts = None
config = None
command = ""
commandDisplayWallet = "1"
commandDisplayOpenOrders = "2"
commandDisplayCurrencyValue = "3"
commandPrintBalance = "4"
commandPrintActiveFills = "5"
commandStartTradingEngine = "6"
commandSellActiveFills = "7"
commandExit = "e"
commandList = [commandDisplayWallet, commandDisplayOpenOrders, commandDisplayCurrencyValue, commandPrintBalance, commandPrintActiveFills, commandStartTradingEngine, commandSellActiveFills, commandExit]
commandMainInput = "What's next?\n" \
    "Press 1 to display your wallets\n" \
    "Press 2 to display your open orders\n" \
    "Press 3 to display current currency value\n" \
    "Press 4 to print your current balance\n" \
    "Press 5 to print the active fills\n" \
    "Press 6 to start the trading engine\n" \
    "Press 7 to sell the active fills\n" \
    "Press e (or ctrl+c at any time) to exit the program\n" \
    "Select your choice: "

print ("\nWelcome to Belfort!\n\n")
try:
    while 1:
        command = promptCommand(commandMainInput, commandList)
        client = authenticateClient()
        settings = updateSettings(client)
        if command == commandDisplayWallet:
            printWallets(client)
        elif command == commandDisplayOpenOrders:
        	printOpenOrders(client)
        elif command == commandDisplayCurrencyValue:
            printValue(client, settings)
        elif command == commandPrintBalance:
        	printBalance(client, settings)
        elif command == commandPrintActiveFills:
        	printActiveFills(client, settings)
        elif command == commandStartTradingEngine:
        	startTradingEngine(client, settings)
        elif command == commandSellActiveFills:
        	sellActiveFills(client, settings)
        elif command == commandExit:
            exit()
        print ("\n")
except Exception:
	print ("Catched exception: %s" % (traceback.print_exc()))
