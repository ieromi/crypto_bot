This telegram bot is built on aiogram3 + CoinMarketCap API using HTTP requests.
/start - command to start the bot and follow the instructions.
PS You can specify several currencies at once in one message, for example,
“btc 60000 64000 eth 3000 3500”, or split it into several messages and add one at a time.
By command /list - you can see all active tracks.
The /clear command clears the list of your active tracks.
If the bot was unable to recognize a crypto by its abbreviation,
an error will appear in the group chat, and the track itself will be cancelled.