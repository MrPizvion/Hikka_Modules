from .. import loader, utils
import logging
import asyncio
import datetime
import re

logger = logging.getLogger(__name__)

@loader.tds
class ModuleUpdaterMod(loader.Module):
    """Модуль для автоматического обновления других модулей 🔄"""
    
    strings = {
        "name": "ModuleUpdater",
        "no_module": "❌ <b>Укажи название модуля!</b>\nПример: <code>.autoupd Weather</code>",
        "no_url": "❌ <b>Укажи URL для модуля {}</b>\nИспользуй: <code>.seturl {} https://raw.github...</code>",
        "already": "✅ <b>Модуль {} уже в списке автообновления</b>",
        "added": "✅ <b>Модуль {} добавлен в автообновление</b>\n⏱️ Проверка каждый час",
        "removed": "✅ <b>Модуль {} удалён из автообновления</b>",
        "cleared": "🗑️ <b>Все модули удалены из автообновления</b>",
        "no_modules": "📭 <b>Нет модулей в автообновлении</b>",
        "checking": "🔄 <b>Проверяю обновления...</b>",
        "updated": "✅ <b>Модуль {} обновлён!</b>\n📥 Новая версия установлена",
        "error": "💥 <b>Ошибка:</b> {}",
        "list_header": "<b>📋 Модули в автообновлении:</b>\n\n",
        "list_item": "{num}. <b>{name}</b> — <code>{url}</code>\n",
        "help": """<b>🔄 Module Updater</b>

<b>📋 Команды:</b>
<code>.autoupd &lt;модуль&gt;</code> - добавить модуль
<code>.seturl &lt;модуль&gt; &lt;url&gt;</code> - установить URL
<code>.remupd &lt;модуль&gt;</code> - удалить из списка
<code>.listupd</code> - список модулей
<code>.clearupd</code> - очистить всё
<code>.checkupd</code> - проверить сейчас
<code>.autoupdhelp</code> - это сообщение

<b>✨ Примеры:</b>
<code>.autoupd Weather</code>
<code>.seturl Weather https://raw.github.com/.../Weather.py</code>
<code>.listupd</code>

<b>⚙️ Проверка каждый час автоматически</b>"""
    }
    
    strings_ru = {
        "name": "ModuleUpdater",
        "no_module": "❌ <b>Укажи название модуля!</b>\nПример: <code>.autoupd Weather</code>",
        "no_url": "❌ <b>Укажи URL для модуля {}</b>\nИспользуй: <code>.seturl {} https://raw.github...</code>",
        "already": "✅ <b>Модуль {} уже в списке автообновления</b>",
        "added": "✅ <b>Модуль {} добавлен в автообновление</b>\n⏱️ Проверка каждый час",
        "removed": "✅ <b>Модуль {} удалён из автообновления</b>",
        "cleared": "🗑️ <b>Все модули удалены из автообновления</b>",
        "no_modules": "📭 <b>Нет модулей в автообновлении</b>",
        "checking": "🔄 <b>Проверяю обновления...</b>",
        "updated": "✅ <b>Модуль {} обновлён!</b>\n📥 Новая версия установлена",
        "error": "💥 <b>Ошибка:</b> {}",
        "list_header": "<b>📋 Модули в автообновлении:</b>\n\n",
        "list_item": "{num}. <b>{name}</b> — <code>{url}</code>\n",
        "help": """<b>🔄 Module Updater</b>

<b>📋 Команды:</b>
<code>.autoupd &lt;модуль&gt;</code> - добавить модуль
<code>.seturl &lt;модуль&gt; &lt;url&gt;</code> - установить URL
<code>.remupd &lt;модуль&gt;</code> - удалить из списка
<code>.listupd</code> - список модулей
<code>.clearupd</code> - очистить всё
<code>.checkupd</code> - проверить сейчас
<code>.autoupdhelp</code> - это сообщение

<b>✨ Примеры:</b>
<code>.autoupd Weather</code>
<code>.seturl Weather https://raw.github.com/.../Weather.py</code>
<code>.listupd</code>

<b>⚙️ Проверка каждый час автоматически</b>"""
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "check_interval",
                60,
                "Интервал проверки (в минутах)",
                validator=loader.validators.Integer(minimum=5, maximum=1440)
            )
        )
        self.modules = {}  # {имя_модуля: url}
        self.task = None
        self.last_check = {}
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.modules = self.db.get("ModuleUpdater", "modules", {})
        logger.info(f"✅ ModuleUpdater загружен: {len(self.modules)} модулей")
        
        # Запускаем автообновление
        if self.modules:
            self.task = asyncio.ensure_future(self._auto_check())
    
    async def autoupdcmd(self, message):
        """.autoupd <модуль> - Добавить модуль в автообновление"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_module"))
            return
        
        module_name = args.strip()
        
        if module_name in self.modules:
            await utils.answer(message, self.strings("already").format(module_name))
            return
        
        # Добавляем без URL (нужно будет установить через .seturl)
        self.modules[module_name] = None
        self.db.set("ModuleUpdater", "modules", self.modules)
        
        # Запускаем задачу если ещё не запущена
        if not self.task and self.modules:
            self.task = asyncio.ensure_future(self._auto_check())
        
        await utils.answer(message, self.strings("added").format(module_name))
    
    async def seturlcmd(self, message):
        """.seturl <модуль> <url> - Установить URL для модуля"""
        args = utils.get_args_raw(message).split(maxsplit=1)
        
        if len(args) < 2:
            await utils.answer(message, "❌ <b>Используй:</b> <code>.seturl Модуль https://ссылка</code>")
            return
        
        module_name, url = args[0].strip(), args[1].strip()
        
        # Проверяем URL
        if not url.startswith(("http://", "https://")):
            await utils.answer(message, "❌ <b>Неверный URL!</b>\nДолжен начинаться с http:// или https://")
            return
        
        if module_name not in self.modules:
            # Добавляем если нет
            self.modules[module_name] = url
            text = self.strings("added").format(module_name)
        else:
            # Обновляем URL
            self.modules[module_name] = url
            text = f"✅ <b>URL для модуля {module_name} обновлён!</b>"
        
        self.db.set("ModuleUpdater", "modules", self.modules)
        await utils.answer(message, text)
    
    async def remupdcmd(self, message):
        """.remupd <модуль> - Удалить модуль из автообновления"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_module"))
            return
        
        module_name = args.strip()
        
        if module_name not in self.modules:
            await utils.answer(message, self.strings("no_modules"))
            return
        
        del self.modules[module_name]
        self.db.set("ModuleUpdater", "modules", self.modules)
        
        # Останавливаем задачу если список пуст
        if not self.modules and self.task:
            self.task.cancel()
            self.task = None
        
        await utils.answer(message, self.strings("removed").format(module_name))
    
    async def listupdcmd(self, message):
        """Показать список модулей в автообновлении"""
        if not self.modules:
            await utils.answer(message, self.strings("no_modules"))
            return
        
        text = self.strings("list_header")
        for i, (name, url) in enumerate(self.modules.items(), 1):
            url_text = url if url else "⚠️ URL не указан"
            text += self.strings("list_item").format(num=i, name=name, url=url_text)
        
        text += f"\n<b>⏱️ Проверка каждые {self.config['check_interval']} минут</b>"
        await utils.answer(message, text)
    
    async def clearupdcmd(self, message):
        """Очистить весь список"""
        self.modules = {}
        self.db.set("ModuleUpdater", "modules", {})
        
        if self.task:
            self.task.cancel()
            self.task = None
        
        await utils.answer(message, self.strings("cleared"))
    
    async def checkupdcmd(self, message):
        """Проверить обновления сейчас"""
        if not self.modules:
            await utils.answer(message, self.strings("no_modules"))
            return
        
        msg = await utils.answer(message, self.strings("checking"))
        updated = []
        errors = []
        
        for module_name, url in self.modules.items():
            if not url:
                errors.append(f"{module_name} (нет URL)")
                continue
            
            try:
                if await self._update_module(module_name, url):
                    updated.append(module_name)
                await asyncio.sleep(1)  # Пауза между обновлениями
            except Exception as e:
                errors.append(f"{module_name} ({str(e)})")
        
        text = ""
        if updated:
            text += f"✅ Обновлены: {', '.join(updated)}\n"
        if errors:
            text += f"❌ Ошибки: {', '.join(errors)}"
        if not text:
            text = "✅ Все модули актуальны"
        
        await utils.answer(msg, text)
    
    async def autoupdhelpcmd(self, message):
        """Помощь по модулю"""
        await utils.answer(message, self.strings("help"))
    
    async def _auto_check(self):
        """Автоматическая проверка обновлений"""
        while True:
            try:
                # Ждём указанное время
                minutes = self.config["check_interval"]
                await asyncio.sleep(minutes * 60)
                
                if not self.modules:
                    continue
                
                logger.info(f"🔄 Автопроверка {len(self.modules)} модулей...")
                
                for module_name, url in list(self.modules.items()):
                    if not url:
                        continue
                    
                    try:
                        await self._update_module(module_name, url)
                        await asyncio.sleep(2)  # Пауза между обновлениями
                    except Exception as e:
                        logger.error(f"Ошибка обновления {module_name}: {e}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ошибка в автообновлении: {e}")
                await asyncio.sleep(60)
    
    async def _update_module(self, module_name: str, url: str) -> bool:
        """Обновляет модуль: удаляет и скачивает заново"""
        try:
            # Проверяем, существует ли модуль
            modules = self.db.get("hikka.modules", "loaded_modules", {})
            module_key = None
            
            for key in modules:
                if key.lower() == module_name.lower() or key.endswith(module_name):
                    module_key = key
                    break
            
            if not module_key:
                logger.info(f"Модуль {module_name} не найден, пропускаем")
                return False
            
            # Проверяем, нужно ли обновлять
            last = self.last_check.get(module_name, 0)
            now = datetime.datetime.now().timestamp()
            
            # Если проверяли меньше часа назад - пропускаем
            if now - last < 3600:
                return False
            
            self.last_check[module_name] = now
            
            # Выгружаем модуль
            logger.info(f"🔄 Выгружаю {module_name}")
            await self.client.unload_module(module_key)
            
            # Немного ждём
            await asyncio.sleep(1)
            
            # Загружаем заново
            logger.info(f"📥 Загружаю {module_name} из {url}")
            await self.client.load_module(url)
            
            logger.info(f"✅ Модуль {module_name} обновлён")
            
            # Отправляем уведомление в лог-чат
            log_chat = self.db.get("hikka.main", "log_chat", None)
            if log_chat:
                await self.client.send_message(
                    log_chat,
                    self.strings("updated").format(module_name)
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка обновления {module_name}: {e}")
            raise
    
    async def on_unload(self):
        """При выгрузке модуля"""
        if self.task:
            self.task.cancel()
        self.db.set("ModuleUpdater", "modules", self.modules)
