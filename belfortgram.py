import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from utils import authenticateClient, printWalletsTelegram, updateSettings

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

def start(update, context):
    if(isAuthorized(update)):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to Belfort! Use /help to retrieve the command list")

def displayHelp(update, context):
    if isAuthorized(update):
        helpMessage = "Here's the command list:\n" \
        "/wallet to display your wallets\n" \
        "/orders to display your open orders\n" \
        "/currency to display current currency value\n" \
        "/balance to print your current balance\n" \
        "/fills to print the active fills\n" \
        "/startEngine to start the trading engine\n" \
        "/sellFills to sell the active fills"
        context.bot.send_message(chat_id=update.effective_chat.id, text=helpMessage)


def displayWallet(update, context):
    if isAuthorized(update):
        output = "Here there are your wallets: " + printWalletsTelegram(client)
        context.bot.send_message(chat_id=update.effective_chat.id, text=output)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

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
unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(displayCommand_handler)
dispatcher.add_handler(displayWallet_handler)
dispatcher.add_handler(unknown_handler)
updater.start_polling()
updater.idle()
