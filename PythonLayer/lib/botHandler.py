import time
import telepot

def botRunner(config):
    #loop to intercept messages on the bot to provide data
    def handle(msg):
        temperature = config['LOG']['temperature']
        humidity = config['LOG']['humidity']
        weather = config['LOG']['weather']
        chat_id = msg['chat']['id']
        command = msg['text']
        if command == 'temperature':
            bot.sendMessage(chat_id, "Temperature = "+temperature+" , Humidity = "+humidity)
        elif command == 'weather':
            bot.sendMessage(chat_id, weather)

#bot initialization
    bot = telepot.Bot(config['API']['bot'])
    bot.message_loop(handle)

    while 1:
        time.sleep(10)