from .. import loader, utils
import logging
import asyncio
import aiohttp
import re

logger = logging.getLogger(__name__)

# requires: aiohttp

@loader.tds
class AutoUpdaterMod(loader.Module):
    """Автоматически обновляет модули из твоего GitHub репозитория 🔄"""

    strings = {
        "name": "AutoUpdater",
        "no_repo": "❌ <b>Укажи ссылку на репозиторий в конфиге!</b>\nПример: <code>MrPizvion/Hikka_Modules</code>",
        "checking": "🔍 <b>Проверяю обновления...</b>",
        "updating": "🔄 <b>Обновляю {}</b>",
        "success": "✅ <b>Обновлено:</b> {}",
        "no_updates": "✅ <b>Все модули актуальны</b>",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🔄 Auto Updater</b>

<b>📋 Команды:</b>
<code>.update</code> - проверить и обновить все модули
<code>.update Название</code> - обновить конкретный модуль

<b>⚙️ Настройка в конфиге:</b>
<code>.config AutoUpdater</code>
- <b>repo</b> = Твой репозиторий (например: MrPizvion/Hikka_Modules)

<b>✨ Пример:</b>
<code>.config AutoUpdater repo MrPizvion/Hikka_Modules</code>
<code>.update</code>"""
    }

    strings_ru = {
        "name": "AutoUpdater",
        "no_repo": "❌ <b>Укажи ссылку на репозиторий в конфиге!</b>\nПример: <code>MrPizvion/Hikka_Modules</code>",
        "checking": "🔍 <b>Проверяю обновления...</b>",
        "updating": "🔄 <b>Обновляю {}</b>",
        "success": "✅ <b>Обновлено:</b> {}",
        "no_updates": "✅ <b>Все модули актуальны</b>",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🔄 Auto Updater</b>

<b>📋 Команды:</b>
<code>.update</code> - проверить и обновить все модули
<code>.update Название</code> - обновить конкретный модуль

<b>⚙️ Настройка в конфиге:</b>
<code>.config AutoUpdater</code>
- <b>repo</b> = Твой репозиторий (например: MrPizvion/Hikka_Modules)

<b>✨ Пример:</b>
<code>.config AutoUpdater repo MrPizvion/Hikka_Modules</code>
<code>.update</code>"""
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "repo",
                "MrPizvion/Hikka_Modules",
                "Твой репозиторий (например: пользователь/репозиторий)",
                validator=loader.validators.String()
            )
        )

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    async def updatecmd(self, message):
        """.update [название] - Обновить модули из репозитория"""
        args = utils.get_args_raw(message)
        repo = self.config["repo"]

        if not repo:
            await utils.answer(message, self.strings("no_repo"))
            return

        msg = await utils.answer(message, self.strings("checking"))

        try:
            # Получаем список файлов из репозитория через GitHub API
            api_url = f"https://api.github.com/repos/{repo}/contents/"
            headers = {"Accept": "application/vnd.github.v3+json"}

            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=headers, timeout=15) as resp:
                    if resp.status != 200:
                        await utils.answer(msg, self.strings("error").format(f"GitHub API вернул {resp.status}"))
                        return

                    files = await resp.json()

            # Собираем все .py файлы
            py_files = {}
            for file in files:
                if file["name"].endswith(".py") and file["name"] != __file__.split("/")[-1]:
                    py_files[file["name"].replace(".py", "")] = file["download_url"]

            if not py_files:
                await utils.answer(msg, self.strings("error").format("В репозитории нет .py файлов"))
                return

            # Если указано конкретное имя модуля
            if args:
                module_name = args.strip()
                found = False
                for name, url in py_files.items():
                    if module_name.lower() in name.lower():
                        await self._update_single(msg, name, url)
                        found = True
                        break
                if not found:
                    await utils.answer(msg, f"❌ <b>Модуль '{module_name}' не найден в репозитории</b>")
                return

            # Обновляем все модули
            updated = []
            errors = []

            for name, url in py_files.items():
                try:
                    if await self._update_module(name, url):
                        updated.append(name)
                    await asyncio.sleep(1)
                except Exception as e:
                    errors.append(f"{name} ({e})")

            # Формируем результат
            result = ""
            if updated:
                result += f"✅ <b>Обновлено:</b> {', '.join(updated)}\n"
            if errors:
                result += f"❌ <b>Ошибки:</b> {', '.join(errors)}"
            if not result:
                result = self.strings("no_updates")

            await utils.answer(msg, result)

        except asyncio.TimeoutError:
            await utils.answer(msg, self.strings("error").format("Таймаут при запросе к GitHub"))
        except Exception as e:
            logger.exception("Ошибка обновления")
            await utils.answer(msg, self.strings("error").format(str(e)))

    async def _update_single(self, msg, name, url):
        """Обновляет один модуль и показывает результат"""
        try:
            if await self._update_module(name, url):
                await utils.answer(msg, self.strings("success").format(name))
            else:
                await utils.answer(msg, f"✅ <b>{name}</b> уже актуален")
        except Exception as e:
            await utils.answer(msg, self.strings("error").format(str(e)))

    async def _update_module(self, name, url) -> bool:
        """Пытается обновить модуль, возвращает True если обновлён"""
        logger.info(f"🔄 Проверяю {name}")

        # Ищем загруженный модуль
        found = None
        for mod in self.all_modules:
            mod_class = mod.__class__.__name__
            mod_name = mod.strings.get("name", "")

            if (name.lower() in mod_class.lower() or
                name.lower() in mod_name.lower()):
                found = mod
                break

        if not found:
            logger.info(f"Модуль {name} не загружен, пропускаю")
            return False

        # Выгружаем
        class_name = found.__class__.__name__
        logger.info(f"Выгружаю {class_name}")
        await self.client.unload_module(class_name)

        await asyncio.sleep(2)

        # Загружаем заново
        logger.info(f"Загружаю из {url}")
        await self.client.load_module(url)

        return True

    async def updatehelpcmd(self, message):
        """Помощь по модулю"""
        await utils.answer(message, self.strings("help"))
