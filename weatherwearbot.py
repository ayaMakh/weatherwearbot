from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import json 
import requests
import os

PORT = int(os.environ.get('PORT', 5000))

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = "994393242:AAFxy876QkspgxJykO4y0laS92qinXER6Q0"
OWM_KEY = "f633ff1ebe91b1eac93dd130d504d3b7"
URL_OWM = f"http://api.openweathermap.org/data/2.5/weather?appid={OWM_KEY}&units=metric"

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I am a weather bot.")

def userhelp(update, context):
	context.bot.send_message(chat_id=update.effective_chat.id, text="Example request: /weather Vancouver")

def error(update, context, error):
	logger.warning(f"Update {context} caused error {error}")

def weather_info(location):
	url = URL_OWM + f"&q={location}"
	req = requests.get(url)
	resp = json.loads(req.content.decode("utf8")) 
	temp = resp["main"]["temp"]
	clouds = resp["clouds"]["all"]
	temp_min = resp["main"]["temp_min"]
	temp_max = resp["main"]["temp_max"]
	description = resp["weather"][0]["description"]

	result = {"temp": temp, "clouds": clouds, "temp_min": temp_min, "temp_max": temp_max, "description": description}
	return result

def recommend(info):
	if "rain" in info["description"]:
		umbrella = "Bring an umbrella ☂."
	else:
		umbrella = ""

	if info["clouds"] < 50:
		sunglasses = "Bring sunglasses 😎."
	else:
		sunglasses = ""

	top, bottom = outfit(info["temp_min"], info["temp_max"])

	report = f"Forecast for today 🌦: {info['description']}, {info['temp']} degrees Celcius. Suggested outfit: 👚 {top} and 👖{bottom}. {umbrella} {sunglasses}"
	return report

def outfit(temp_min, temp_max):
	top = ""
	bottom = ""
	if temp_min >= 20:
		top = "Top shirt or dress"
		bottom = "Shorts or skirt"
	elif temp_min >= 10 and temp_max < 20:
		top = "Top shirt"
		bottom = "Jeans"
	elif temp_min >= 0 and temp_max < 10:
		top = "Shirt and light jacket"
		bottom = "Pants"
	elif temp_max  < 0:
		top = "Warm jacket and sweater"
		bottom = "Warm pants"

	return top, bottom

def weather(update, context):
	location = "".join(context.args)
	weather = weather_info(location)
	final_report = recommend(weather)
	context.bot.send_message(chat_id=update.effective_chat.id, text=final_report)

def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Command not recognised, see /help")

def main():
	updater = Updater(token=TOKEN, use_context=True)
	dispatcher = updater.dispatcher

	start_handler = CommandHandler("start", start)
	help_handler = CommandHandler("help", userhelp)
	weather_handler = CommandHandler("weather", weather)
	unknown_handler = MessageHandler(Filters.command, unknown)

	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(help_handler)
	dispatcher.add_handler(weather_handler)
	dispatcher.add_handler(unknown_handler)

	dispatcher.add_error_handler(error)

	updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=TOKEN)
	updater.bot.setWebhook('https://enigmatic-forest-02058.herokuapp.com/' + TOKEN)

	updater.idle()


if __name__ == '__main__':
	main()