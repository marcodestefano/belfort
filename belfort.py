"""Main belfort file."""

from coinbase.wallet.client import Client
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


client = None
accounts = None
config = None
API_KEY = 'APIKey'
API_SECRET = 'APISecret'
try:
    config = getConfiguration()
    client = Client(config[API_KEY], config[API_SECRET])
    accounts = client.get_accounts()
except Exception as exc:
    print "Catched exception: %s" % (exc)
if accounts:
    for account in accounts.data:
        balance = account.balance
        print "%s: %s %s" % (account.name, balance.amount, balance.currency)
        print account.get_transactions()
