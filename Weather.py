from .. import loader, utils
import aiohttp
import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)

# requires: aiohttp

@loader.tds
class WeatherMod(loader.Module):
    """⚡ СУПЕР-БЫСТРЫЙ модуль погоды"""
    
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
║ 🏠 <a href='{map_url}'>Карта</a>
╠════════════════════════════════╣
║ <b>📊 СЕЙЧАС:</b>
║ 🌡️ <b>{temp}°C</b> (ош. {feels_like}°C)
║ ☁️ {description}
║ 💧 {humidity}% • 💨 {wind_speed} м/с
║ 🌅 {sunrise} • 🌇 {sunset}
╠════════════════════════════════╣
║ <b>📅 ПРОГНОЗ:</b>
{forecast}
╚════════════════════════════════╝""",
        "forecast_day": "║ {emoji} <b>{date}:</b> {temp_min}°C—{temp_max}°C\n║    {desc}\n",
        "help": """╔════════════════════════════════╗
║     <b>⚡ WEATHER</b>     ║
╠════════════════════════════════╣
║ <code>.w город</code> - быстро
║ <code>.setcity город</code>
║ <code>.myweather</code>
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
║ 🏠 <a href='{map_url}'>Карта</a>
╠════════════════════════════════╣
║ <b>📊 СЕЙЧАС:</b>
║ 🌡️ <b>{temp}°C</b> (ош. {feels_like}°C)
║ ☁️ {description}
║ 💧 {humidity}% • 💨 {wind_speed} м/с
║ 🌅 {sunrise} • 🌇 {sunset}
╠════════════════════════════════╣
║ <b>📅 ПРОГНОЗ:</b>
{forecast}
╚════════════════════════════════╝""",
        "forecast_day": "║ {emoji} <b>{date}:</b> {temp_min}°C—{temp_max}°C\n║    {desc}\n",
        "help": """╔════════════════════════════════╗
║     <b>⚡ WEATHER</b>     ║
╠════════════════════════════════╣
║ <code>.w город</code> - быстро
║ <code>.setcity город</code>
║ <code>.myweather</code>
╚════════════════════════════════╝"""
    }
    
    # Кэш для городов (чтобы не искать координаты каждый раз)
    city_cache = {}
    
    # Быстрые эмодзи
    emoji_cache = {
        2: "⛈️", 3: "🌧️", 5: "🌧️", 500: "🌦️", 6: "❄️", 7: "🌫️",
        800: "☀️", 801: "⛅", 802: "☁️", 803: "☁️", 804: "☁️"
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "default_city",
                None,
                "🌆 Город",
                validator=loader.validators.String()
            )
        )
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        # Загружаем кэш
        self.city_cache = self.db.get("Weather", "city_cache", {})
    
    async def weathercmd(self, message):
        """<город> - Показать погоду"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_city"))
            return
        await self._fast_weather(message, args.strip())
    
    async def wcmd(self, message):
        """<город> - Быстрая погода"""
        args = utils.get_args_raw(message)
        if not args:
            if self.config["default_city"]:
                await self._fast_weather(message, self.config["default_city"])
            else:
                await utils.answer(message, self.strings("no_city"))
        else:
            await self._fast_weather(message, args.strip())
    
    async def setcitycmd(self, message):
        """<город> - Сохранить город"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "❌ <b>Укажи город</b>")
            return
        self.config["default_city"] = args.strip()
        await utils.answer(message, f"✅ <b>Сохранено:</b> {args.strip()}")
    
    async def myweathercmd(self, message):
        """Погода для сохранённого"""
        if not self.config["default_city"]:
            await utils.answer(message, "❌ <b>Сначала .setcity</b>")
            return
        await self._fast_weather(message, self.config["default_city"])
    
    async def weatherhelpcmd(self, message):
        """Помощь"""
        await utils.answer(message, self.strings("help"))
    
    async def _fast_weather(self, message, city: str):
        """СУПЕР-БЫСТРОЕ получение погоды"""
        # Сразу отправляем "загрузка"
        msg = await utils.answer(message, self.strings("loading"))
        
        try:
            # Проверяем кэш координат
            cache_key = city.lower().strip()
            if cache_key in self.city_cache:
                lat, lon, city_name, country = self.city_cache[cache_key]
            else:
                # Быстрый запрос координат (без local_names)
                geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid=b1b15e88fa797225412429c1c50c122a1"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(geo_url, timeout=5) as resp:
                        if resp.status != 200:
                            await utils.answer(msg, self.strings("not_found").format(city))
                            return
                        
                        geo_data = await resp.json()
                        if not geo_data:
                            await utils.answer(msg, self.strings("not_found").format(city))
                            return
                        
                        lat = geo_data[0]["lat"]
                        lon = geo_data[0]["lon"]
                        city_name = geo_data[0]["name"]
                        country = geo_data[0].get("country", "")
                        
                        # Сохраняем в кэш
                        self.city_cache[cache_key] = (lat, lon, city_name, country)
                        self.db.set("Weather", "city_cache", self.city_cache)
            
            # ОДИН быстрый запрос на всё (current + forecast)
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid=b1b15e88fa797225412429c1c50c122a1&units=metric&lang=ru"
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid=b1b15e88fa797225412429c1c50c122a1&units=metric&lang=ru&cnt=5"
            
            async with aiohttp.ClientSession() as session:
                # Запускаем оба запроса ПАРАЛЛЕЛЬНО
                weather_task = session.get(weather_url, timeout=5)
                forecast_task = session.get(forecast_url, timeout=5)
                
                weather_resp, forecast_resp = await asyncio.gather(weather_task, forecast_task)
                
                weather = await weather_resp.json()
                forecast_data = await forecast_resp.json()
            
            # Быстрое форматирование
            sunrise = datetime.datetime.fromtimestamp(weather["sys"]["sunrise"]).strftime("%H:%M")
            sunset = datetime.datetime.fromtimestamp(weather["sys"]["sunset"]).strftime("%H:%M")
            
            weather_id = weather["weather"][0]["id"]
            desc = weather["weather"][0]["description"]
            
            # Быстрый выбор эмодзи
            if weather_id // 100 == 2:
                emoji = "⛈️"
            elif weather_id // 100 == 3:
                emoji = "🌧️"
            elif weather_id // 100 == 5:
                emoji = "🌦️" if weather_id == 500 else "🌧️"
            elif weather_id // 100 == 6:
                emoji = "❄️"
            elif weather_id // 100 == 7:
                emoji = "🌫️"
            elif weather_id == 800:
                emoji = "☀️"
            elif weather_id == 801:
                emoji = "⛅"
            else:
                emoji = "☁️"
            
            # Прогноз (только 3 дня для скорости)
            forecast_lines = []
            seen = set()
            for item in forecast_data.get("list", [])[:8]:  # Больше данных для выбора
                date = datetime.datetime.fromtimestamp(item["dt"]).strftime("%d.%m")
                if date not in seen and len(forecast_lines) < 3:
                    seen.add(date)
                    w_id = item["weather"][0]["id"]
                    
                    # Эмодзи для прогноза
                    if w_id // 100 == 2:
                        e = "⛈️"
                    elif w_id // 100 == 3:
                        e = "🌧️"
                    elif w_id // 100 == 5:
                        e = "🌦️" if w_id == 500 else "🌧️"
                    elif w_id // 100 == 6:
                        e = "❄️"
                    elif w_id == 800:
                        e = "☀️"
                    elif w_id == 801:
                        e = "⛅"
                    else:
                        e = "☁️"
                    
                    forecast_lines.append(self.strings("forecast_day").format(
                        emoji=e,
                        date=date,
                        temp_min=round(item["main"]["temp_min"]),
                        temp_max=round(item["main"]["temp_max"]),
                        desc=item["weather"][0]["description"]
                    ))
            
            result = self.strings("weather").format(
                city=city_name.upper(),
                country=country,
                map_url=f"https://openweathermap.org/weathermap?zoom=10&lat={lat}&lon={lon}",
                temp=round(weather["main"]["temp"]),
                feels_like=round(weather["main"]["feels_like"]),
                description=f"{emoji} {desc}",
                humidity=weather["main"]["humidity"],
                wind_speed=round(weather["wind"]["speed"], 1),
                pressure=weather["main"]["pressure"],
                sunrise=sunrise,
                sunset=sunset,
                forecast="".join(forecast_lines) if forecast_lines else "║ ❌ Нет данных\n"
            )
            
            await utils.answer(msg, result)
            
        except asyncio.TimeoutError:
            await utils.answer(msg, "⏱️ <b>Таймаут. Попробуй ещё.</b>")
        except Exception as e:
            logger.exception(f"Weather error: {e}")
            await utils.answer(msg, self.strings("error").format(str(e)))
