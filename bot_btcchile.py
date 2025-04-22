import telebot
import threading
from dotenv import load_dotenv
import os
from flask import Flask, request
import time 
from waitress import serve # entorno de produccion

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# from pyngrok import ngrok, conf  # to create tunneling bt host and server

from requests_html import HTMLSession
from bs4 import BeautifulSoup
import requests

lock = threading.Lock()


# Cargar variables de entorno
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
NGROK_TOKEN =os.getenv("NGROK_TOKEN")
print(f"TELEGRAM_TOKEN: '{TELEGRAM_TOKEN}'")  # Depuración
bot = telebot.TeleBot(TELEGRAM_TOKEN)


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
        url = "https://www.tradingview.com/symbols/BTCUSD/?exchange=BITSTAMP"
        bot.send_message(message.chat.id, "$" + scrap(url) + " USD " )
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



#scrap functions

def scrap(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Ejecutar en modo headless (opcional)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    source = driver.page_source
    print("inside scrap")
    print("url: ", url)
    soup = BeautifulSoup(source, 'lxml')
    price = soup.find('span', class_="last-zoF9r75I js-symbol-last").text # tradingview
    print("price 1 ", price)
    driver.quit()
    return price

# setting webhook
web_server = Flask(__name__)
@web_server.route('/', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(request.stream.read().decode('UTF-8'))
        bot.process_new_updates([update])
        return 'ok', 200 
    

def start_webhook():
    # Configuración del webhook
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url="https://telebot-bitcoinchile.onrender.com")
    serve(web_server, host="0.0.0.0", port=5000)
    
#setting ngrok
# def function_bot():
#     print("cargando ngrok")
#     conf.get_default().config_path = "./config_ngrok.yml"
#     conf.get_default().region = "sa"
#     ngrok.set_auth_token(NGROK_TOKEN)
#     ngrok_tunel = ngrok.connect(5000, bind_tls=True)
#     ngrok_url = ngrok_tunel.public_url
#     bot.remove_webhook()
#     time.sleep(1)
#     bot.set_webhook(url=ngrok_url)
#     serve(web_server, host="0.0.0.0", port=5000)
#     print("start nuevo server")
    
#*************MAIN********************************************************
if __name__ == "__main__":

    
    print("Start the bot")
    
    # Start ngrok server   
    tr_webhook = threading.Thread(name="tr_webhook", target=start_webhook)
    tr_webhook.start()
    # tr_webhook = threading.Thread(name="tr_webhook", target=function_bot)
    # tr_webhook.start()
    
    print("through the threads....")
#*************END*********************************************************
    