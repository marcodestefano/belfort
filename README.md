# belfort
A python tool to trade cryptocurrencies on Coinbase Pro

Dependencies:
cbpro (pip install cbpro)
python-telegram-bot (pip install python-telegram-bot)

Usage:
You need to rename the file data.cfg.bak into data.cfg and put your own Coinbase Pro APIKey, APISecret and Passphrase

File settings.cfg contains settings used in running the engine, that can be customized

Advanced Usage:
You can also activate and control belfort via a telegram bot. To know how to define a bot, please follow the official guide here: https://core.telegram.org/bots#6-botfather

Once done, you need to rename the telegram.cfg.bak into telegram.cfg and put your own TelegramBotToken after the / character.
To limit users that can access the otherwise publicly available bot, you need to rename users.cfg.bak into users.cfg and list your authorized telegram usernames, one on each line.
