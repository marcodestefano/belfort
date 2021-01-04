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
commandPrintBalance = "3"
commandPrintActiveFills = "4"
commandStartTradingEngine = "5"
commandSellActiveFills = "6"
commandExit = "e"
commandList = [commandDisplayWallet, commandDisplayOpenOrders, commandPrintBalance, commandPrintActiveFills, commandStartTradingEngine, commandSellActiveFills, commandExit]
commandMainInput = "What's next?\n" \
    "Press "+ commandDisplayWallet +" to display your wallets\n" \
    "Press "+ commandDisplayOpenOrders +" to display your open orders\n" \
    "Press "+ commandPrintBalance +" to print your current balance\n" \
    "Press "+ commandPrintActiveFills +" to print the active fills\n" \
    "Press "+ commandStartTradingEngine +" to start the trading engine\n" \
    "Press "+ commandSellActiveFills +" to sell the active fills\n" \
    "Press "+ commandExit +" (or ctrl+c at any time) to exit the program\n" \
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
