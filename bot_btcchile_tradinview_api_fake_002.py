import telebot
import threading

import os
import time 

from flask import Flask, request
from waitress import serve # entorno de produccion
from pyngrok import ngrok, conf  # to create tunneling bt host and server

import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from tradingview_ta import TA_Handler, Interval, Exchange
from dotenv import load_dotenv

CHAT_ID=1421658840

lock = threading.Lock()

# Cargar variables de entorno
load_dotenv(override=True)
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
                          "Version de pruebas " + "\n"
                          "El bot esta en proceso de  optimización" + "\n")            

# comandos del bot

@bot.message_handler(commands=["btc", "eth", "sol", "xrp", "mstr", "tsla", "dominance","gold","dxy","piusd", "ath"])
def price_command(message):
    mensaje_text = message.text
    if '/btc' in mensaje_text.lower(): 
        print("precio de bitcoin")
        symbol = "BTCUSD"
        exchange = "BITSTAMP"
        bot.send_message(message.chat.id, f"BTC  $  {format_price(coin_price(symbol, exchange))} USD " )
    if '/eth' in mensaje_text.lower(): 
        print("precio de ethereum")
        symbol = "ETHUSD"  
        exchange = "BITSTAMP"
        bot.send_message(message.chat.id, f"ETH  $  {format_price(coin_price(symbol, exchange))} USD " )
    if '/sol' in mensaje_text.lower(): 
        print("precio de solana")
        symbol = "SOLUSDT"
        exchange = "BINANCE"
        bot.send_message(message.chat.id, f"SOL  $  {format_price(coin_price(symbol, exchange))} USD " )
    if '/xrp' in mensaje_text.lower(): 
        print("precio de solana")
        symbol = "XRPUSD"
        exchange = "BITSTAMP"
        bot.send_message(message.chat.id, f"XRP  $  {format_price(coin_price(symbol, exchange))} USD " )
    # STOCK SECTION
    if '/mstr' in mensaje_text.lower(): 
        print("precio de solana")
        symbol = "MSTR"
        exchange = "nasdaq"
        bot.send_message(message.chat.id, f"MSTR  $  {format_price(stock_price(symbol, exchange))} USD " )
    if '/tsla' in mensaje_text.lower(): 
        print("precio de solana")
        symbol = "TSLA"
        exchange = "nasdaq"
        bot.send_message(message.chat.id, f"TSLA  $  {format_price(stock_price(symbol, exchange))} USD " )
    
    if '/dominance' in mensaje_text.lower(): 
        print("Dominancia de bitcoin")        
        bot.send_message(message.chat.id,  f" BTC.D $  {format_price(get_btc_dominance())} %")

    # SCRAP SECTION
    if '/gold' in mensaje_text.lower(): 
        print("Gold")
        url = "https://www.tradingview.com/symbols/GOLD/"
        bot.send_message(message.chat.id, "GOLD $" + format_price(scrap(url)) + " USD " )    
    if '/dxy' in mensaje_text.lower(): 
        print("Dollar index")
        url = "https://www.tradingview.com/symbols/TVC-DXY/"
        bot.send_message(message.chat.id, "DXY $" + format_price(scrap(url)) + " USD " )
    if '/piusd' in mensaje_text.lower(): 
        print("Pi Network")
        url = "https://www.tradingview.com/symbols/PIUSDT/?exchange=BITGET"
        bot.send_message(message.chat.id, "PiNetwork $" + format_price(scrap(url)) + " USD " )
    if '/ath' in mensaje_text.lower(): 
        print("Ultimo ATH de bitcoin")
        bot.send_message(message.chat.id, " ATH $109.356 USD " )


bot.set_my_commands([
    telebot.types.BotCommand("/start", "Descripción del bot"),
    telebot.types.BotCommand("/btc", "BTC/USD"),
    telebot.types.BotCommand("/eth", "ETH/USD"),
    telebot.types.BotCommand("/sol", "SOL/USD"),
    telebot.types.BotCommand("/xrp", "XRP/USD"),
    telebot.types.BotCommand("/mstr", "MSTR/USD"),
    telebot.types.BotCommand("/tsla", "TSLA/USD"),
    telebot.types.BotCommand("/dominance", "Dominancia de BTC"),
    telebot.types.BotCommand("/gold", "Gold/USD"),
    telebot.types.BotCommand("/dxy", "Dollar index"),
    telebot.types.BotCommand("/piusd", "Pi Network"),
    telebot.types.BotCommand("/ath", "Ultimo ATH de BTC")])

# ["btc", "eth", "sol", "xrp", "mstr", "tsla", "dominance","gold","dxy","piusd", "ath"]


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
    # print("price 1 ", price)
    # Detener la animación
    
    driver.quit()
    print("finalizando el webscrap")
    return price

# api functions
def get_coin_price(symbol, exchange):
    coin = TA_Handler(
        symbol=symbol,
        screener="crypto",
        exchange=exchange,
        interval=Interval.INTERVAL_1_MINUTE
    )
    analysis = coin.get_analysis()
    return analysis.indicators["close"]
def coin_price(symbol, exchange):
    with lock:
        price = get_coin_price(symbol, exchange)
        print(f"{symbol} price: ", price)
        return price


def get_stock_price(symbol, exchange):
    coin = TA_Handler(
        symbol=symbol,
        screener="america",
        exchange=exchange,
        interval=Interval.INTERVAL_1_MINUTE
    )
    analysis = coin.get_analysis()
    return analysis.indicators["close"]
def stock_price(symbol, exchange):
    with lock:
        price = get_stock_price(symbol, exchange)
        print(f"{symbol} price: ", price)
        return price



def get_btc_dominance():
    url = "https://api.coingecko.com/api/v3/globl"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            btc_dominance = data["data"]["market_cap_percentage"]["btc"]
            return round(btc_dominance, 2)  # Redondear a 2 decimales
        else:
            print(f"Error de api....scraping {e}")
            url="https://www.tradingview.com/symbols/CRYPTOCAP-BTC.D/"
            btc_dominance = scrap(url)
            return btc_dominance
    except Exception as e:
        print(f"Error de api....scraping  {e}")
        url="https://www.tradingview.com/symbols/CRYPTOCAP-BTC.D/"
        btc_dominance = scrap(url)
        return btc_dominance
    
#formato
def format_price(price):
    try:
        # Eliminar separadores de miles si existen
        if isinstance(price, str):
            price = price.replace(",", "")
        # Convertir a float y formatear manualmente
        formatted_price = "{:,.2f}".format(float(price)).replace(",", "X").replace(".", ",").replace("X", ".")
        return formatted_price
    except ValueError:
        print("Error al formatear el precio. Asegúrate de que sea un número válido.")
        return price

# setting webhook
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
#     #bot.set_webhook(url="https://telebot-bitcoinchile.onrender.com")
#     bot.set_webhook(url="https://bitcoin-chile-telebot.onrender.com")
#     serve(web_server, host="0.0.0.0", port=5000)

#setting ngrok
def function_bot():
    print("cargando ngrok")
    load_dotenv()
    conf.get_default().config_path = "./config_ngrok.yml"
    conf.get_default().region = "sa"
    ngrok.set_auth_token(NGROK_TOKEN)
    ngrok_tunel = ngrok.connect(5000, bind_tls=True)
    ngrok_url = ngrok_tunel.public_url
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=ngrok_url)
    serve(web_server, host="0.0.0.0", port=5000)
    print("start nuevo server")
    
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
    