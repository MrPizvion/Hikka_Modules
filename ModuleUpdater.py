from .. import loader, utils
import logging
import asyncio

logger = logging.getLogger(__name__)

@loader.tds
class SimpleUpdaterMod(loader.Module):
    """Модуль для быстрого обновления модулей одной командой 🔄"""
    
    strings = {
        "name": "SimpleUpdater",
        "no_module": "❌ <b>Укажи название модуля!</b>\nПример: <code>.upd Weather</code>",
        "no_url": "❌ <b>Нет URL для модуля {}</b>\nДобавь в конфиг: <code>.config SimpleUpdater</code>",
        "not_found": "❌ <b>Модуль {} не найден!</b>\nПроверь список: <code>.modules</code>",
        "updating": "🔄 <b>Обновляю модуль {}...</b>",
        "success": "✅ <b>Модуль {} успешно обновлён!</b>",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🔄 Simple Updater</b>

<b>📋 Команда:</b>
<code>.upd название</code> - обновить модуль

<b>⚙️ Настройка URL в конфиге:</b>
<code>.config SimpleUpdater</code>

<b>✨ Пример:</b>
<code>.upd Weather</code>
<code>.upd DaysUntil</code>
<code>.upd OsuProfile</code>"""
    }
    
    strings_ru = {
        "name": "SimpleUpdater",
        "no_module": "❌ <b>Укажи название модуля!</b>\nПример: <code>.upd Weather</code>",
        "no_url": "❌ <b>Нет URL для модуля {}</b>\nДобавь в конфиг: <code>.config SimpleUpdater</code>",
        "not_found": "❌ <b>Модуль {} не найден!</b>\nПроверь список: <code>.modules</code>",
        "updating": "🔄 <b>Обновляю модуль {}...</b>",
        "success": "✅ <b>Модуль {} успешно обновлён!</b>",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🔄 Simple Updater</b>

<b>📋 Команда:</b>
<code>.upd название</code> - обновить модуль

<b>⚙️ Настройка URL в конфиге:</b>
<code>.config SimpleUpdater</code>

<b>✨ Пример:</b>
<code>.upd Weather</code>
<code>.upd DaysUntil</code>
<code>.upd OsuProfile</code>"""
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "Weather",
                "https://raw.githubusercontent.com/MrPizvion/Hikka_Modules/main/Weather.py",
                "URL для Weather модуля",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "DaysUntil",
                "https://raw.githubusercontent.com/MrPizvion/Hikka_Modules/main/DaysUntil.py",
                "URL для DaysUntil модуля",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "OsuProfile",
                "https://raw.githubusercontent.com/MrPizvion/Hikka_Modules/main/osu_profile.py",
                "URL для OsuProfile модуля",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "VideoToGif",
                "https://raw.githubusercontent.com/MrPizvion/Hikka_Modules/main/VideoToGif.py",
                "URL для VideoToGif модуля",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "Nsfwart",
                "https://raw.githubusercontent.com/MrPizvion/Hikka_Modules/main/Nsfwart.py",
                "URL для Nsfwart модуля",
                validator=loader.validators.String()
            ),
        )
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        logger.info("✅ SimpleUpdater готов к работе")
    
    async def updcmd(self, message):
        """<название> - Обновить модуль"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, self.strings("no_module"))
            return
        
        module_name = args.strip()
        logger.info(f"🔄 Запрос на обновление модуля: {module_name}")
        
        # Получаем URL из конфига
        url = self.config.get(module_name, None)
        
        if not url:
            # Пробуем найти похожие названия
            available = []
            for key in self.config.keys():
                if module_name.lower() in key.lower():
                    available.append(key)
            
            if available:
                await utils.answer(message, 
                    f"❌ <b>Модуль '{module_name}' не найден в конфиге!</b>\n"
                    f"📋 Доступные: {', '.join(available)}\n"
                    f"💡 Используй точное название из списка")
            else:
                await utils.answer(message, 
                    f"❌ <b>Нет URL для модуля {module_name}</b>\n"
                    f"Добавь в конфиг: <code>.config SimpleUpdater</code>")
            return
        
        # Получаем список загруженных модулей
        all_modules = self.all_modules
        logger.info(f"📋 Всего модулей загружено: {len(all_modules)}")
        
        # Ищем модуль по имени
        found_module = None
        for mod in all_modules:
            mod_lower = mod.__class__.__name__.lower()
            mod_name_lower = mod.strings.get("name", "").lower()
            
            if (module_name.lower() in mod_lower or 
                module_name.lower() in mod_name_lower or
                mod_lower.endswith(module_name.lower()) or
                mod_name_lower.endswith(module_name.lower())):
                found_module = mod
                logger.info(f"✅ Найден модуль: {mod.__class__.__name__}")
                break
        
        if not found_module:
            logger.warning(f"❌ Модуль {module_name} не найден")
            await utils.answer(message, self.strings("not_found").format(module_name))
            return
        
        # Обновляем
        msg = await utils.answer(message, self.strings("updating").format(module_name))
        
        try:
            # Получаем точное имя класса
            class_name = found_module.__class__.__name__
            logger.info(f"📤 Выгружаю {class_name}")
            
            # Выгружаем
            await self.client.unload_module(class_name)
            
            await asyncio.sleep(2)
            
            # Загружаем заново
            logger.info(f"📥 Загружаю из {url}")
            await self.client.load_module(url)
            
            await utils.answer(msg, self.strings("success").format(module_name))
            
        except Exception as e:
            logger.error(f"Ошибка обновления: {e}")
            await utils.answer(msg, self.strings("error").format(str(e)))
    
    async def updhelpcmd(self, message):
        """Показать помощь"""
        # Получаем список доступных модулей из конфига
        available = ", ".join(self.config.keys())
        
        text = self.strings("help") + f"\n\n📦 <b>Доступные модули:</b>\n{available}"
        await utils.answer(message, text)
