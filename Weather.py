from .. import loader, utils
import aiohttp
import datetime
import logging

logger = logging.getLogger(__name__)

# requires: aiohttp

@loader.tds
class WeatherMod(loader.Module):
    """Модуль для получения прогноза погоды ⛅ (без API ключа)"""
    
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
        "cloudy": "☁️",
        "partly cloudy": "⛅",
        "overcast": "☁️",
        "rain": "🌧️",
        "light rain": "🌦️",
        "heavy rain": "🌧️",
        "thunderstorm": "⛈️",
        "snow": "❄️",
        "light snow": "🌨️",
        "mist": "🌫️",
        "fog": "🌫️",
        "ясно": "☀️",
        "облачно": "☁️",
        "пасмурно": "☁️",
        "небольшая облачность": "⛅",
        "дождь": "🌧️",
        "снег": "❄️",
        "туман": "🌫️"
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "default_city",
                None,
                "🌆 Город по умолчанию",
                validator=loader.validators.String()
            )
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
        """Получение погоды через wttr.in (без API ключа)"""
        loading = await utils.answer(message, self.strings("loading"))
        
        try:
            # Используем wttr.in - бесплатное API без ключа
            url = f"https://wttr.in/{city}?format=j1"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await utils.answer(message, self.strings("not_found").format(city))
                        return
                    
                    data = await resp.json()
            
            # Парсим данные
            current = data["current_condition"][0]
            weather_desc = current["weatherDesc"][0]["value"].lower()
            area = data["nearest_area"][0]
            city_name = area["areaName"][0]["value"]
            country = area["country"][0]["value"]
            
            # Координаты для карты
            lat = area["latitude"]
            lon = area["longitude"]
            
            # Текущая погода
            temp = int(current["temp_C"])
            feels_like = int(current["FeelsLikeC"])
            humidity = current["humidity"]
            wind_speed = float(current["windspeedKmph"]) / 3.6  # км/ч -> м/с
            pressure = current["pressure"]
            
            # Восход/закат
            sunrise = current["sunrise"]
            sunset = current["sunset"]
            
            # Прогноз
            forecast_lines = []
            weather_data = data.get("weather", [])
            
            for day in weather_data[:5]:  # 5 дней
                date = datetime.datetime.strptime(day["date"], "%Y-%m-%d").strftime("%d.%m")
                temp_min = int(day["mintempC"])
                temp_max = int(day["maxtempC"])
                
                # Описание на день (берем из первого часа)
                hour_data = day.get("hourly", [{}])[0]
                desc_day = hour_data.get("weatherDesc", [{}])[0].get("value", "").lower()
                
                emoji = self._get_weather_emoji(desc_day)
                
                forecast_lines.append(self.strings("forecast_day").format(
                    emoji=emoji,
                    date=date,
                    temp_min=temp_min,
                    temp_max=temp_max,
                    desc=desc_day.capitalize()
                ))
            
            forecast_text = "".join(forecast_lines) if forecast_lines else "║ ❌ Нет данных\n"
            
            # Описание сейчас
            emoji_now = self._get_weather_emoji(weather_desc)
            
            # Карта
            map_url = f"https://www.google.com/maps/@{lat},{lon},10z"
            
            result = self.strings("weather").format(
                city=city_name.upper(),
                country=country,
                map_url=map_url,
                temp=temp,
                feels_like=feels_like,
                description=f"{emoji_now} {weather_desc.capitalize()}",
                humidity=humidity,
                wind_speed=round(wind_speed, 1),
                pressure=pressure,
                sunrise=sunrise,
                sunset=sunset,
                forecast=forecast_text
            )
            
            await utils.answer(message, result)
            
        except Exception as e:
            logger.exception(f"Weather error: {e}")
            await utils.answer(message, self.strings("error").format(str(e)))
    
    def _get_weather_emoji(self, desc: str) -> str:
        """Выбор эмодзи по описанию"""
        desc_lower = desc.lower()
        
        for key, emoji in self.weather_emojis.items():
            if key in desc_lower:
                return emoji
        
        return "☁️"
