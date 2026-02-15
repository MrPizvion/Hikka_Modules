from .. import loader, utils
import aiohttp
import datetime
import logging
import asyncio

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
        "timeout": "⏱️ <b>Превышено время ожидания. Попробуй ещё раз.</b>",
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
        "timeout": "⏱️ <b>Превышено время ожидания. Попробуй ещё раз.</b>",
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
        """Получение погоды с таймаутом и запасным API"""
        await utils.answer(message, self.strings("loading"))
        
        try:
            # Пробуем первый API (wttr.in) с таймаутом
            try:
                data = await self._fetch_wttr(city)
                if data:
                    await self._send_weather(message, data, city)
                    return
            except asyncio.TimeoutError:
                logger.warning("wttr.in timeout, trying open-meteo...")
            
            # Если первый не сработал, пробуем второй API
            data = await self._fetch_openmeteo(city)
            if data:
                await self._send_weather(message, data, city)
                return
            
            await utils.answer(message, self.strings("not_found").format(city))
            
        except Exception as e:
            logger.exception(f"Weather error: {e}")
            await utils.answer(message, self.strings("error").format(str(e)))
    
    async def _fetch_wttr(self, city: str):
        """Получение погоды через wttr.in"""
        url = f"https://wttr.in/{city}?format=j1"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    return None
                return await resp.json()
    
    async def _fetch_openmeteo(self, city: str):
        """Запасной API без ключа"""
        # Сначала получаем координаты
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(geo_url, timeout=10) as resp:
                if resp.status != 200:
                    return None
                
                geo_data = await resp.json()
                if not geo_data.get("results"):
                    return None
                
                lat = geo_data["results"][0]["latitude"]
                lon = geo_data["results"][0]["longitude"]
                city_name = geo_data["results"][0]["name"]
                country = geo_data["results"][0].get("country", "")
                
                # Получаем погоду
                weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=weathercode,temperature_2m_max,temperature_2m_min,sunrise,sunset&timezone=auto"
                
                async with session.get(weather_url, timeout=10) as wresp:
                    if wresp.status != 200:
                        return None
                    
                    weather_data = await wresp.json()
                    
                    # Преобразуем в формат как у wttr
                    return self._convert_openmeteo(weather_data, city_name, country, lat, lon)
    
    def _convert_openmeteo(self, data: dict, city: str, country: str, lat: float, lon: float):
        """Конвертирует данные open-meteo в формат как у wttr"""
        current = data.get("current_weather", {})
        daily = data.get("daily", {})
        
        # Коды погоды в эмодзи
        weather_codes = {
            0: "Ясно",
            1: "Преимущественно ясно",
            2: "Переменная облачность",
            3: "Пасмурно",
            45: "Туман",
            48: "Туман",
            51: "Легкая морось",
            53: "Морось",
            55: "Сильная морось",
            56: "Легкая ледяная морось",
            57: "Ледяная морось",
            61: "Небольшой дождь",
            63: "Дождь",
            65: "Сильный дождь",
            66: "Ледяной дождь",
            67: "Сильный ледяной дождь",
            71: "Небольшой снег",
            73: "Снег",
            75: "Сильный снег",
            77: "Снежная крупа",
            80: "Небольшой ливень",
            81: "Ливень",
            82: "Сильный ливень",
            85: "Небольшой снегопад",
            86: "Снегопад",
            95: "Гроза",
            96: "Гроза с градом",
            99: "Гроза с сильным градом"
        }
        
        # Текущая погода
        weather_code = current.get("weathercode", 0)
        desc = weather_codes.get(weather_code, "Неизвестно")
        
        # Прогноз
        forecast = []
        for i in range(min(5, len(daily.get("time", [])))):
            forecast.append({
                "date": daily["time"][i],
                "temp_min": daily["temperature_2m_min"][i],
                "temp_max": daily["temperature_2m_max"][i],
                "desc": weather_codes.get(daily["weathercode"][i], "Неизвестно")
            })
        
        return {
            "city": city,
            "country": country,
            "lat": lat,
            "lon": lon,
            "current": {
                "temp": current.get("temperature", 0),
                "feels_like": current.get("temperature", 0),
                "desc": desc,
                "humidity": 0,  # open-meteo не даёт влажность в бесплатной версии
                "wind_speed": current.get("windspeed", 0) / 3.6,  # км/ч -> м/с
                "pressure": 0,
                "sunrise": daily.get("sunrise", [""])[0][11:16] if daily.get("sunrise") else "??:??",
                "sunset": daily.get("sunset", [""])[0][11:16] if daily.get("sunset") else "??:??"
            },
            "forecast": forecast
        }
    
    async def _send_weather(self, message, data, original_city):
        """Отправка погоды"""
        if "current_condition" in data:  # wttr формат
            current = data["current_condition"][0]
            weather_desc = current["weatherDesc"][0]["value"].lower()
            area = data["nearest_area"][0]
            city_name = area["areaName"][0]["value"]
            country = area["country"][0]["value"]
            lat = area["latitude"]
            lon = area["longitude"]
            
            temp = int(current["temp_C"])
            feels_like = int(current["FeelsLikeC"])
            humidity = current["humidity"]
            wind_speed = float(current["windspeedKmph"]) / 3.6
            pressure = current["pressure"]
            sunrise = current["sunrise"]
            sunset = current["sunset"]
            
            # Прогноз
            forecast_lines = []
            weather_data = data.get("weather", [])
            
            for day in weather_data[:5]:
                date = datetime.datetime.strptime(day["date"], "%Y-%m-%d").strftime("%d.%m")
                temp_min = int(day["mintempC"])
                temp_max = int(day["maxtempC"])
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
            
            emoji_now = self._get_weather_emoji(weather_desc)
            
        else:  # open-meteo формат
            city_name = data["city"]
            country = data["country"]
            lat = data["lat"]
            lon = data["lon"]
            current = data["current"]
            
            temp = round(current["temp"])
            feels_like = round(current["feels_like"])
            weather_desc = current["desc"].lower()
            humidity = current["humidity"] or "?"
            wind_speed = current["wind_speed"]
            pressure = current["pressure"] or "?"
            sunrise = current["sunrise"]
            sunset = current["sunset"]
            
            # Прогноз
            forecast_lines = []
            for day in data["forecast"]:
                date = datetime.datetime.strptime(day["date"], "%Y-%m-%d").strftime("%d.%m")
                temp_min = round(day["temp_min"])
                temp_max = round(day["temp_max"])
                desc_day = day["desc"].lower()
                emoji = self._get_weather_emoji(desc_day)
                
                forecast_lines.append(self.strings("forecast_day").format(
                    emoji=emoji,
                    date=date,
                    temp_min=temp_min,
                    temp_max=temp_max,
                    desc=desc_day.capitalize()
                ))
            
            emoji_now = self._get_weather_emoji(weather_desc)
        
        forecast_text = "".join(forecast_lines) if forecast_lines else "║ ❌ Нет данных\n"
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
    
    def _get_weather_emoji(self, desc: str) -> str:
        """Выбор эмодзи по описанию"""
        desc_lower = desc.lower()
        
        for key, emoji in self.weather_emojis.items():
            if key in desc_lower:
                return emoji
        
        return "☁️"
