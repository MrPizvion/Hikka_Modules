from .. import loader, utils
import aiohttp
import datetime
import logging

logger = logging.getLogger(__name__)

# requires: aiohttp

@loader.tds
class WeatherMod(loader.Module):
    """Модуль для получения прогноза погоды ⛅"""
    
    strings = {
        "name": "Weather",
        "no_city": "❌ <b>Укажи город</b>\nПример: <code>.weather Москва</code>",
        "not_found": "❌ <b>Город</b> <code>{}</code> <b>не найден</b>",
        "loading": "🔄 <b>Получаю погоду...</b>",
        "error": "💥 <b>Ошибка:</b> {}",
        "weather": """╔════════════════════════════════╗
║     <b>⛅ ПОГОДА В {city}</b>     ║
╠════════════════════════════════╣
║ 🌍 <b>Страна:</b> {country}
║ 🏠 <a href='{map_url}'>Показать на карте</a>
╠════════════════════════════════╣
║ <b>📊 СЕЙЧАС:</b>
║ 🌡️ <b>Температура:</b> <code>{temp}°C</code> (ощущается {feels_like}°C)
║ ☁️ <b>Описание:</b> {description}
║ 💧 <b>Влажность:</b> <code>{humidity}%</code>
║ 💨 <b>Ветер:</b> <code>{wind_speed} м/с</code>
║ ☀️ <b>Давление:</b> <code>{pressure} гПа</code>
║ 🌅 <b>Восход:</b> <code>{sunrise}</code>
║ 🌇 <b>Закат:</b> <code>{sunset}</code>
╠════════════════════════════════╣
║ <b>📅 ПРОГНОЗ НА 5 ДНЕЙ:</b>
{forecast}
╚════════════════════════════════╝""",
        "forecast_day": "║ {emoji} <b>{date}:</b> {temp_min}°C — {temp_max}°C\n║    {desc}\n",
        "help": """╔════════════════════════════════╗
║     <b>⛅ WEATHER MODULE</b>     ║
╠════════════════════════════════╣
║ <b>📋 Команды:</b>
║ 
║ <code>.weather город</code>
║    погода сейчас + прогноз
║ 
║ <code>.w город</code>
║    быстрая погода
║ 
║ <code>.setcity город</code>
║    сохранить город
║ 
║ <code>.myweather</code>
║    погода для сохранённого
║ 
║ <code>.weatherhelp</code>
║    это сообщение
╠════════════════════════════════╣
║ <b>✨ Примеры:</b>
║ <code>.weather Москва</code>
║ <code>.w Лондон</code>
║ <code>.setcity Киев</code>
╚════════════════════════════════╝"""
    }
    
    strings_ru = {
        "name": "Weather",
        "no_city": "❌ <b>Укажи город</b>\nПример: <code>.weather Москва</code>",
        "not_found": "❌ <b>Город</b> <code>{}</code> <b>не найден</b>",
        "loading": "🔄 <b>Получаю погоду...</b>",
        "error": "💥 <b>Ошибка:</b> {}",
        "weather": """╔════════════════════════════════╗
║     <b>⛅ ПОГОДА В {city}</b>     ║
╠════════════════════════════════╣
║ 🌍 <b>Страна:</b> {country}
║ 🏠 <a href='{map_url}'>Показать на карте</a>
╠════════════════════════════════╣
║ <b>📊 СЕЙЧАС:</b>
║ 🌡️ <b>Температура:</b> <code>{temp}°C</code> (ощущается {feels_like}°C)
║ ☁️ <b>Описание:</b> {description}
║ 💧 <b>Влажность:</b> <code>{humidity}%</code>
║ 💨 <b>Ветер:</b> <code>{wind_speed} м/с</code>
║ ☀️ <b>Давление:</b> <code>{pressure} гПа</code>
║ 🌅 <b>Восход:</b> <code>{sunrise}</code>
║ 🌇 <b>Закат:</b> <code>{sunset}</code>
╠════════════════════════════════╣
║ <b>📅 ПРОГНОЗ НА 5 ДНЕЙ:</b>
{forecast}
╚════════════════════════════════╝""",
        "forecast_day": "║ {emoji} <b>{date}:</b> {temp_min}°C — {temp_max}°C\n║    {desc}\n",
        "help": """╔════════════════════════════════╗
║     <b>⛅ WEATHER MODULE</b>     ║
╠════════════════════════════════╣
║ <b>📋 Команды:</b>
║ 
║ <code>.weather город</code>
║    погода сейчас + прогноз
║ 
║ <code>.w город</code>
║    быстрая погода
║ 
║ <code>.setcity город</code>
║    сохранить город
║ 
║ <code>.myweather</code>
║    погода для сохранённого
║ 
║ <code>.weatherhelp</code>
║    это сообщение
╠════════════════════════════════╣
║ <b>✨ Примеры:</b>
║ <code>.weather Москва</code>
║ <code>.w Лондон</code>
║ <code>.setcity Киев</code>
╚════════════════════════════════╝"""
    }
    
    # Эмодзи для погоды
    weather_emojis = {
        "clear": "☀️",
        "sunny": "☀️",
        "clouds": "☁️",
        "few clouds": "⛅",
        "scattered clouds": "☁️",
        "broken clouds": "☁️",
        "overcast": "☁️",
        "rain": "🌧️",
        "light rain": "🌦️",
        "moderate rain": "🌧️",
        "heavy rain": "💧",
        "thunderstorm": "⛈️",
        "snow": "❄️",
        "light snow": "🌨️",
        "mist": "🌫️",
        "fog": "🌫️",
        "haze": "🌫️",
        "smoke": "💨",
        "dust": "💨",
        "sand": "💨",
        "ash": "🌋",
        "squall": "💨",
        "tornado": "🌪️",
        "небольшая облачность": "⛅",
        "пасмурно": "☁️",
        "ясно": "☀️",
        "снег": "❄️",
        "дождь": "🌧️"
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "default_city",
                None,
                "🌆 Город по умолчанию",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "api_key",
                "b1b15e88fa797225412429c1c50c122a1",
                "🔑 API ключ OpenWeatherMap",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "units",
                "metric",
                "📏 Единицы: metric(°C), imperial(°F)",
                validator=loader.validators.Choice(["metric", "imperial"])
            ),
            loader.ConfigValue(
                "lang",
                "ru",
                "🗣️ Язык: ru, en, ua",
                validator=loader.validators.String()
            ),
        )
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
    
    async def weathercmd(self, message):
        """<город> - Показать погоду"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, self.strings("no_city"))
            return
        
        city = args.strip()
        await self._get_weather(message, city)
    
    async def wcmd(self, message):
        """<город> - Быстрая погода"""
        args = utils.get_args_raw(message)
        
        if not args:
            if self.config["default_city"]:
                city = self.config["default_city"]
            else:
                await utils.answer(message, self.strings("no_city"))
                return
        else:
            city = args.strip()
        
        await self._get_weather(message, city)
    
    async def setcitycmd(self, message):
        """<город> - Сохранить город по умолчанию"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, "❌ <b>Укажи город</b>")
            return
        
        city = args.strip()
        self.config["default_city"] = city
        
        await utils.answer(message, f"✅ <b>Город сохранён:</b> {city}")
    
    async def myweathercmd(self, message):
        """Погода для сохранённого города"""
        if not self.config["default_city"]:
            await utils.answer(message, "❌ <b>Сначала сохрани город через</b> <code>.setcity</code>")
            return
        
        await self._get_weather(message, self.config["default_city"])
    
    async def weatherhelpcmd(self, message):
        """Показать помощь по модулю"""
        await utils.answer(message, self.strings("help"))
    
    async def _get_weather(self, message, city: str):
        """Получение погоды"""
        loading = await utils.answer(message, self.strings("loading"))
        
        try:
            # Получаем координаты города
            geo_url = "http://api.openweathermap.org/geo/1.0/direct"
            geo_params = {
                "q": city,
                "limit": 1,
                "appid": self.config["api_key"]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(geo_url, params=geo_params) as resp:
                    if resp.status != 200:
                        await utils.answer(message, self.strings("error").format(f"HTTP {resp.status}"))
                        return
                    
                    geo_data = await resp.json()
                    
                    if not geo_data:
                        await utils.answer(message, self.strings("not_found").format(city))
                        return
                    
                    lat = geo_data[0]["lat"]
                    lon = geo_data[0]["lon"]
                    city_name = geo_data[0].get("local_names", {}).get(self.config["lang"], geo_data[0]["name"])
                    country = geo_data[0].get("country", "")
                
                # Получаем текущую погоду
                weather_url = "https://api.openweathermap.org/data/2.5/weather"
                weather_params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": self.config["api_key"],
                    "units": self.config["units"],
                    "lang": self.config["lang"]
                }
                
                async with session.get(weather_url, params=weather_params) as resp:
                    if resp.status != 200:
                        await utils.answer(message, self.strings("error").format(f"HTTP {resp.status}"))
                        return
                    
                    weather = await resp.json()
                
                # Получаем прогноз
                forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
                forecast_params = {
                    "lat": lat,
                    "lon": lon,
                    "appid": self.config["api_key"],
                    "units": self.config["units"],
                    "lang": self.config["lang"],
                    "cnt": 5
                }
                
                async with session.get(forecast_url, params=forecast_params) as resp:
                    if resp.status != 200:
                        forecast_data = {"list": []}
                    else:
                        forecast_data = await resp.json()
            
            # Форматируем время
            sunrise = datetime.datetime.fromtimestamp(weather["sys"]["sunrise"]).strftime("%H:%M")
            sunset = datetime.datetime.fromtimestamp(weather["sys"]["sunset"]).strftime("%H:%M")
            
            # Описание погоды с эмодзи
            desc = weather["weather"][0]["description"].lower()
            weather_id = weather["weather"][0]["id"]
            
            # Выбираем эмодзи
            emoji = self._get_weather_emoji(weather_id, desc)
            
            # Прогноз
            forecast_lines = []
            seen_dates = set()
            
            for item in forecast_data.get("list", []):
                dt = datetime.datetime.fromtimestamp(item["dt"])
                date_str = dt.strftime("%d.%m")
                
                if date_str not in seen_dates and len(forecast_lines) < 5:
                    seen_dates.add(date_str)
                    
                    temp_min = round(item["main"]["temp_min"])
                    temp_max = round(item["main"]["temp_max"])
                    desc_day = item["weather"][0]["description"]
                    emoji_day = self._get_weather_emoji(item["weather"][0]["id"], desc_day)
                    
                    forecast_lines.append(self.strings("forecast_day").format(
                        emoji=emoji_day,
                        date=date_str,
                        temp_min=temp_min,
                        temp_max=temp_max,
                        desc=desc_day.capitalize()
                    ))
            
            forecast_text = "".join(forecast_lines) if forecast_lines else "║ ❌ Нет данных\n"
            
            # Карта
            map_url = f"https://openweathermap.org/weathermap?zoom=10&lat={lat}&lon={lon}"
            
            result = self.strings("weather").format(
                city=city_name.upper(),
                country=country,
                map_url=map_url,
                temp=round(weather["main"]["temp"]),
                feels_like=round(weather["main"]["feels_like"]),
                description=f"{emoji} {desc.capitalize()}",
                humidity=weather["main"]["humidity"],
                wind_speed=round(weather["wind"]["speed"], 1),
                pressure=weather["main"]["pressure"],
                sunrise=sunrise,
                sunset=sunset,
                forecast=forecast_text
            )
            
            await utils.answer(message, result)
            
        except Exception as e:
            logger.exception(f"Weather error: {e}")
            await utils.answer(message, self.strings("error").format(str(e)))
    
    def _get_weather_emoji(self, weather_id: int, desc: str) -> str:
        """Выбор эмодзи по коду погоды"""
        # По коду
        if weather_id // 100 == 2:
            return "⛈️"
        elif weather_id // 100 == 3:
            return "🌧️"
        elif weather_id // 100 == 5:
            if weather_id == 500:
                return "🌦️"
            return "🌧️"
        elif weather_id // 100 == 6:
            return "❄️"
        elif weather_id // 100 == 7:
            return "🌫️"
        elif weather_id == 800:
            return "☀️"
        elif weather_id == 801:
            return "⛅"
        elif weather_id == 802:
            return "☁️"
        elif weather_id in [803, 804]:
            return "☁️"
        
        # По описанию
        for key, emoji in self.weather_emojis.items():
            if key in desc:
                return emoji
        
        return "☁️"
