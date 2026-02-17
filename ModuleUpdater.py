from .. import loader, utils
import logging
import asyncio

logger = logging.getLogger(__name__)

@loader.tds
class SimpleUpdaterMod(loader.Module):
    """Модуль для быстрого обновления модулей одной командой 🔄"""
    
    strings = {
        "name": "SimpleUpdater",
        "no_module": "❌ <b>Укажи название модуля!</b>\nПример: <code>.autoupd Weather</code>",
        "no_url": "❌ <b>Не знаю URL для модуля {}</b>\nУкажи в конфиге: <code>.config SimpleUpdater</code>",
        "not_found": "❌ <b>Модуль {} не найден!</b>",
        "updating": "🔄 <b>Обновляю модуль {}...</b>",
        "success": "✅ <b>Модуль {} успешно обновлён!</b>",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🔄 Simple Updater</b>

<b>📋 Команда:</b>
<code>.autoupd &lt;название&gt;</code> - обновить модуль

<b>⚙️ Настройка URL в конфиге:</b>
<code>.config SimpleUpdater</code>

<b>✨ Пример:</b>
<code>.autoupd Weather</code>

<b>📝 Сначала укажи URL для модуля:</b>
1. <code>.config SimpleUpdater</code>
2. Добавь поле с названием модуля и URL"""
    }
    
    strings_ru = {
        "name": "SimpleUpdater",
        "no_module": "❌ <b>Укажи название модуля!</b>\nПример: <code>.autoupd Weather</code>",
        "no_url": "❌ <b>Не знаю URL для модуля {}</b>\nУкажи в конфиге: <code>.config SimpleUpdater</code>",
        "not_found": "❌ <b>Модуль {} не найден!</b>",
        "updating": "🔄 <b>Обновляю модуль {}...</b>",
        "success": "✅ <b>Модуль {} успешно обновлён!</b>",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🔄 Simple Updater</b>

<b>📋 Команда:</b>
<code>.autoupd &lt;название&gt;</code> - обновить модуль

<b>⚙️ Настройка URL в конфиге:</b>
<code>.config SimpleUpdater</code>

<b>✨ Пример:</b>
<code>.autoupd Weather</code>

<b>📝 Сначала укажи URL для модуля:</b>
1. <code>.config SimpleUpdater</code>
2. Добавь поле с названием модуля и URL"""
    }
    
    def __init__(self):
        # Конфиг будет заполняться динамически
        self.config = loader.ModuleConfig()
        
        # Словарь с URL по умолчанию
        self.default_urls = {
            "Weather": "https://raw.githubusercontent.com/MrPizvion/Hikka_Modules/main/Weather.py",
            "OsuProfile": "https://raw.githubusercontent.com/MrPizvion/Hikka_Modules/main/osu_profile.py",
            "DaysUntil": "https://raw.githubusercontent.com/MrPizvion/Hikka_Modules/main/DaysUntil.py",
            "VideoToGif": "https://raw.githubusercontent.com/MrPizvion/Hikka_Modules/main/VideoToGif.py",
            "Nsfwart": "https://raw.githubusercontent.com/MrPizvion/Hikka_Modules/main/Nsfwart.py",
            "SimpleUpdater": "https://raw.githubusercontent.com/MrPizvion/Hikka_Modules/main/SimpleUpdater.py"
        }
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        
        # Добавляем URL из конфига в словарь
        for key, value in self.config.items():
            if key not in self.default_urls and value:
                self.default_urls[key] = value
    
    async def autoupdcmd(self, message):
        """.autoupd <название> - Обновить модуль"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, self.strings("no_module"))
            return
        
        module_name = args.strip()
        
        # Ищем URL для модуля
        url = None
        
        # Сначала проверяем в конфиге
        if module_name in self.config:
            url = self.config[module_name]
        
        # Потом в словаре по умолчанию
        if not url and module_name in self.default_urls:
            url = self.default_urls[module_name]
        
        if not url:
            await utils.answer(message, self.strings("no_url").format(module_name))
            return
        
        # Проверяем, существует ли модуль
        modules = self.db.get("hikka.modules", "loaded_modules", {})
        module_key = None
        
        for key in modules:
            if key.lower() == module_name.lower() or key.endswith(module_name):
                module_key = key
                break
        
        if not module_key:
            await utils.answer(message, self.strings("not_found").format(module_name))
            return
        
        # Обновляем
        msg = await utils.answer(message, self.strings("updating").format(module_name))
        
        try:
            # Выгружаем
            logger.info(f"🔄 Выгружаю {module_key}")
            await self.client.unload_module(module_key)
            
            await asyncio.sleep(1)
            
            # Загружаем заново
            logger.info(f"📥 Загружаю из {url}")
            await self.client.load_module(url)
            
            await utils.answer(msg, self.strings("success").format(module_name))
            
        except Exception as e:
            logger.error(f"Ошибка обновления: {e}")
            await utils.answer(msg, self.strings("error").format(str(e)))
    
    async def setupdhelpcmd(self, message):
        """Помощь по модулю"""
        await utils.answer(message, self.strings("help"))
