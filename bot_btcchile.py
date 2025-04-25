import telebot
import threading

import os
import time
# import locale 

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

lock = threading.Lock()
# Cargar variables de entorno
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
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



def start_webhook():
    # Configuración del webhook
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url="https://bitcoin-chile-bot.onrender.com")
    #https://bitcoin-chile-bot.onrender.com
    serve(web_server, host="0.0.0.0", port=5000)


# bienvenida al usuario

@bot.message_handler(commands=['start'])
def cmd_start(message):
    """welcome to user"""
    bot.reply_to(message, "Bienvenido al bot Bitcoin-Precio al instante " + "\n"
                          "✰ ℒiℯხřℯ_ďℯ_₿ọt 🄰🄻🄴🅁🅃 ✰" + "\n"
                          "El bot esta en proceso de optimización" + "\n")            

# comandos del bot

@bot.message_handler(commands=["btc", "eth", "sol", "xrp", "mstr", "tsla", "dominance","gold","dxy","piusd", "ath"])
def price_command(message):
    mensaje_text = message.text
    if '/btc' in mensaje_text.lower(): 
        print("precio de bitcoin")
        symbol = "BTCUSD"
        exchange = "BITSTAMP"
        bot.send_message(message.chat.id, f"BTC $ {coin_price(symbol, exchange)} USD " )
    if '/eth' in mensaje_text.lower(): 
        print("precio de ethereum")
        symbol = "ETHUSD"
        exchange = "BITSTAMP"
        bot.send_message(message.chat.id, f"ETH $ {coin_price(symbol, exchange)} USD " )
    if '/sol' in mensaje_text.lower(): 
        print("precio de solana")
        symbol = "SOLUSDT"
        exchange = "BINANCE"
        bot.send_message(message.chat.id, f"SOL $ {coin_price(symbol, exchange)} USD " )
    if '/xrp' in mensaje_text.lower(): 
        print("precio de solana")
        symbol = "XRPUSD"
        exchange = "BITSTAMP"
        bot.send_message(message.chat.id, f"XRP $ {coin_price(symbol, exchange)} USD " )
    # STOCK SECTION
    if '/mstr' in mensaje_text.lower(): 
        print("precio de solana")
        symbol = "MSTR"
        exchange = "nasdaq"
        bot.send_message(message.chat.id, f"MSTR $ {stock_price(symbol, exchange)} USD " )
    if '/tsla' in mensaje_text.lower(): 
        print("precio de solana")
        symbol = "TSLA"
        exchange = "nasdaq"
        bot.send_message(message.chat.id, f"TSLA $ {stock_price(symbol, exchange)} USD " )
    
    if '/dominance' in mensaje_text.lower(): 
        print("Dominancia de bitcoin")        
        bot.send_message(message.chat.id,  f" BTC.D {get_btc_dominance()} %")

    # SCRAP SECTION
    if '/gold' in mensaje_text.lower(): 
        print("Gold")
        url = "https://www.tradingview.com/symbols/GOLD/"
        bot.send_message(message.chat.id, "GOLD $ " + scrap(url) + " USD " )    
    if '/dxy' in mensaje_text.lower(): 
        print("Dollar index")
        url = "https://www.tradingview.com/symbols/TVC-DXY/"
        bot.send_message(message.chat.id, "DXY $ " + scrap(url) + " USD " )
    if '/piusd' in mensaje_text.lower(): 
        print("Pi Network")
        url = "https://www.tradingview.com/symbols/PIUSDT/?exchange=BITGET"
        bot.send_message(message.chat.id, "PiNetwork $ " + scrp(url)) + " USD " )
    if '/ath' in mensaje_text.lower(): 
        print("Ultimo ATH de bitcoin")
        bot.send_message(message.chat.id, " ATH $ 109.356 USD " )




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
    print("price 1 ", price)
    driver.quit()
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
        # print("type ada", type(price))
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
        # print("type ada", type(price))
        return price



def get_btc_dominance():
    url = "https://api.coingecko.com/api/v3/global"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            btc_dominance = data["data"]["market_cap_percentage"]["btc"]
            return round(btc_dominance, 2)  # Redondear a 2 decimales
        else:
            print(f"Error al acceder a la API: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error al obtener la dominancia de BTC: {e}")
        return None
#formato
# def price):
#     try:        
#         # Eliminar separadores de miles (coma) del string
#         if isinstance(price, str):
#             price = price.replace(",", "")  # Eliminar la coma
#         # Configurar la localización para usar separadores de miles y decimales según tu región
#         locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')  # Cambia 'es_ES.UTF-8' según tu configuración local
#         # Convertir el precio a float y formatearlo con separadores de miles y decimales
#         formatted_price = locale.format_string("%.2f", float(price), grouping=True)
#         return formatted_price
#     except ValueError:
#         print("Error al formatear el precio. Asegúrate de que sea un número válido.")
#         return price

#*************MAIN********************************************************
if __name__ == "__main__":

    
    print("Start the bot")
    
    # Start ngrok server   
    tr_webhook = threading.Thread(name="tr_webhook", target=start_webhook)
    tr_webhook.start()
    
    print("through the threads....")
#*************END*********************************************************
    