import telebot
import threading
from dotenv import load_dotenv
import os
from flask import Flask, request
import time 
from waitress import serve # entorno de produccion

from pyngrok import ngrok, conf  # to create tunneling bt host and server

# Cargar variables de entorno
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NGROK_TOKEN =os.getenv("NGROK_TOKEN")
print(f"TELEGRAM_TOKEN: '{TELEGRAM_TOKEN}'")  # Depuración
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# webhook
web_server = Flask(__name__)
@web_server.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(request.stream.read().decode('UTF-8'))
        bot.process_new_updates([update])
        return 'ok', 200 



# def start_webhook():
#     # Configuración del webhook
#     bot.remove_webhook()
#     time.sleep(1)
#     bot.set_webhook(url="https://telebot-bitcoinchile.onrender.com")
#     serve(web_server, host="0.0.0.0", port=5000)


# bienvenida al usuario

@bot.message_handler(commands=['start'])
def cmd_start(message):
    """welcome to user"""
    bot.reply_to(message, "Bienvenido al bot Bitcoin-Precio al instante " + "\n"
                          "✰ ℒiℯხřℯ_ďℯ_₿ọt 🄰🄻🄴🅁🅃 ✰" + "\n"
                          "El bot esta en reparacion y en proceso de busqueda de servidor" + "\n")            

# comandos del bot

@bot.message_handler(commands=["btc", "eth", "dominance", "ath"])
def price_command(message):
    mensaje_text = message.text
    if '/btc' in mensaje_text.lower(): 
        print("precio de bitcoin")
        bot.send_message(message.chat.id, "Numbers goes up!" )
    if '/dominance' in mensaje_text.lower(): 
        print("Dominancia de bitcoin")
        bot.send_message(message.chat.id, "Muy alta, tristemente para los shitcoinlovers" )
    if '/eth' in mensaje_text.lower(): 
        print("precio de ethereum")
        bot.send_message(message.chat.id, "Numbers goes down!" )
    if '/ath' in mensaje_text.lower(): 
        print("Ultimo ATH de bitcoin")
        bot.send_message(message.chat.id, " $109.000 USD " )




bot.set_my_commands([
    telebot.types.BotCommand("/start", "Descripción del bot"),
    telebot.types.BotCommand("/btc", "BTC/USD"),
    telebot.types.BotCommand("/eth", "ETH/USD"),
    telebot.types.BotCommand("/dominance", "Dominancia de BTC"),
    telebot.types.BotCommand("/ath", "Ultimo ATH de BTC")])


#seting ngrok
def function_bot():
    # define path config file of ngrok
    conf.get_default().config_path = "./config_ngrok.yml"
    # region "sa" = south america
    conf.get_default().region = "sa"
    # credentials file from ngrok
    ngrok.set_auth_token(NGROK_TOKEN)
    # create tunnel https port 5000
    ngrok_tunel = ngrok.connect(5000, bind_tls=True)
    # urls from created tunnel
    ngrok_url = ngrok_tunel.public_url
    # remove former webhook
    bot.remove_webhook()
    # littl pause
    time.sleep(1)
    # define webhook
    bot.set_webhook(url=ngrok_url)
    # start web server
    serve(web_server, host="0.0.0.0", port=5000)
    print("start nuevo server")
    # print("bot iniciado, ejecutando whale alert...")

#*************MAIN********************************************************
if __name__ == "__main__":

    
    print("Start the bot")
    
    # Start ngrok server   
    # tr_webhook = threading.Thread(name="tr_webhook", target=start_webhook)
    # tr_webhook.start()
    tr_webhook = threading.Thread(name="tr_webhook", target=function_bot)
    tr_webhook.start()
    
    print("through the threads....")
#*************END*********************************************************
    