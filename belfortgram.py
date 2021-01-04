import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from utils import authenticateClient, updateSettings, getWalletsText, getOpenOrdersText, getBalanceText, getFillsText, sellActiveFillsText

BOT_TOKEN = 'TelegramBotToken'
TOKEN_FILENAME = 'telegram.cfg'
USERS_FILENAME = 'users.cfg'

def getTokenConfig(fileName):
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
                pair = line.split("/")
                if len(pair) == 2:
                    conf[pair[0]] = pair[1]
    return conf

def getUsers(fileName):
    """Retrieve the configuration file."""
    directory = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    )
    conf = []
    filePath = os.path.join(directory, fileName)
    with open(filePath, 'r') as f:
        for line in f:
            if (line[0] != "#") and len(line) > 0:
                line = line[:len(line)-1]
                conf.append(line)
    return conf

def isAuthorized(update):
    return update.effective_user.username in users

def genericHandler(update, context, function, client=None, settings=None):
    if(isAuthorized(update)):
        if client and settings:
            output = function(client, settings)
        elif client:
            output = function(client)
        else:
            output = function()
        context.bot.send_message(chat_id=update.effective_chat.id, text=output)

def getStartMessage():
    return "Welcome to Belfort! Use /help to retrieve the command list"

def getHelpMessage():
    return "Here's the command list:\n" \
        "/wallet to display your wallets\n" \
        "/orders to display your open orders\n" \
        "/balance to print your current balance\n" \
        "/fills to print the active fills\n" \
        "/startEngine to start the trading engine\n" \
        "/sellFills to sell the active fills"

def getUnknownMessage():
    return "Sorry, I didn't understand that command."

def start(update, context):
    genericHandler(update,context,getStartMessage)

def displayHelp(update, context):
    genericHandler(update, context, getHelpMessage)

def displayWallet(update, context):
    genericHandler(update, context, getWalletsText, client)

def displayOrders(update, context):
    genericHandler(update, context, getOpenOrdersText, client)

def displayBalance(update, context):
    genericHandler(update, context, getBalanceText, client, settings)

def displayFills(update, context):
    genericHandler(update, context, getFillsText, client, settings)

def sellFills(update, context):
    genericHandler(update, context, sellActiveFillsText, client, settings)

def unknown(update, context):
    genericHandler(update, context, getUnknownMessage)

client = authenticateClient()
settings = updateSettings(client)
users = getUsers(USERS_FILENAME)
print("Authorized users are: " + str(users))
tokenData = getTokenConfig(TOKEN_FILENAME)[BOT_TOKEN]
updater = Updater(token=tokenData)
dispatcher = updater.dispatcher
start_handler = CommandHandler('start', start)
displayCommand_handler = CommandHandler('help', displayHelp)
displayWallet_handler = CommandHandler('wallet', displayWallet)
displayOrders_handler = CommandHandler('orders', displayOrders)
displayBalance_handler = CommandHandler('balance', displayBalance)
displayFills_handler = CommandHandler('fills', displayFills)
sellFills_handler = CommandHandler('sellFills', sellFills)
unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(displayCommand_handler)
dispatcher.add_handler(displayWallet_handler)
dispatcher.add_handler(displayOrders_handler)
dispatcher.add_handler(displayBalance_handler)
dispatcher.add_handler(displayFills_handler)
dispatcher.add_handler(sellFills_handler)
dispatcher.add_handler(unknown_handler)
updater.start_polling()
print("Bot is active and running")
updater.idle()
