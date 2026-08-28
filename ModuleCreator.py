# ---------------------------------------------------------------------------------
# Name: ModuleCreator
# Description: Создание модулей через чат Telegram с GitHub авторизацией
# meta developer: @edu_kak_xochu
# ---------------------------------------------------------------------------------

import asyncio
import logging
import re
from datetime import datetime

from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class ModuleCreator(loader.Module):
    """Создание модулей через чат Telegram"""

    strings = {
        "name": "ModuleCreator",
        
        "not_authorized": (
            "<b><emoji document_id=5467672931176010750>❌</emoji> Ошибка авторизации!</b>\n\n"
            "<b>Вы не авторизовали свой GitHub аккаунт.</b>\n\n"
            "<b>Для авторизации используйте команду:</b>\n"
            "<code>.ghauth</code> <i>ваш_github_token</i>\n\n"
            "<b>Получить токен можно здесь:</b>\n"
            "https://github.com/settings/tokens"
        ),
        
        "auth_success": (
            "<b><emoji document_id=5467906724422622902>✅</emoji> GitHub авторизация успешна!</b>\n\n"
            "<b>Пользователь:</b> <code>{}</code>\n"
            "<b>Репозиторий:</b> <code>{}</code>\n\n"
            "<b>Теперь вы можете создавать модули!</b>"
        ),
        
        "auth_error": (
            "<b><emoji document_id=5467672931176010750>❌</emoji> Ошибка авторизации!</b>\n\n"
            "<b>Неверный токен или пользователь не найден.</b>"
        ),
        
        "no_repo": (
            "<b><emoji document_id=5467672931176010750>❌</emoji> Репозиторий не выбран!</b>\n\n"
            "<b>Создайте репозиторий командой:</b>\n"
            "<code>.newrepo</code> <i>название_репозитория</i>"
        ),
        
        "repo_created": (
            "<b><emoji document_id=5467906724422622902>✅</emoji> Репозиторий создан!</b>\n\n"
            "<b>Название:</b> <code>{}</code>\n"
            "<b>URL:</b> <code>{}</code>"
        ),
        
        "module_creating": "<b><emoji document_id=5326015457155620929>🔄</emoji> Создаю модуль...</b>",
        
        "module_created": (
            "<b><emoji document_id=5467906724422622902>✅</emoji> Модуль создан!</b>\n\n"
            "<b>Файл:</b> <code>{}</code>\n"
            "<b>Репозиторий:</b> <code>{}</code>\n\n"
            "<b>Ссылка на файл:</b>\n"
            "<code>{}</code>"
        ),
        
        "creating_repo": "<b><emoji document_id=5326015457155620929>🔄</emoji> Создаю репозиторий...</b>",
        
        "repos_list": "<b><emoji document_id=5431577498364158238>📊</emoji> Ваши репозитории:</b>\n\n{}",
        
        "repo_selected": "<b><emoji document_id=5467906724422622902>✅</emoji> Репозиторий выбран:</b>\n<code>{}</code>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "github_token",
                None,
                lambda: "GitHub токен для авторизации",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "current_repo",
                None,
                lambda: "Текущий репозиторий",
                validator=loader.validators.String()
            ),
        )

    async def client_ready(self, client, db):
        self.db = db
        self._client = client

    async def _github_request(self, method, url, data=None):
        """Выполнить запрос к GitHub API"""
        import aiohttp
        
        headers = {
            "Authorization": f"token {self.config['github_token']}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        async with aiohttp.ClientSession() as session:
            if method == "GET":
                async with session.get(url, headers=headers) as response:
                    return await response.json(), response.status
            elif method == "POST":
                async with session.post(url, headers=headers, json=data) as response:
                    return await response.json(), response.status
            elif method == "PUT":
                async with session.put(url, headers=headers, json=data) as response:
                    return await response.json(), response.status

    @loader.command()
    async def ghauth(self, message):
        """Авторизация GitHub - указать токен"""
        
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<b>Использование:</b> <code>.ghauth ваш_github_token</code>")
            return
            
        self.config['github_token'] = args
        
        # Проверяем токен
        user_data, status = await self._github_request("GET", "https://api.github.com/user")
        
        if status == 200:
            await utils.answer(
                message,
                self.strings['auth_success'].format(
                    user_data.get('login', 'Unknown'),
                    self.config['current_repo'] or 'Не выбран'
                )
            )
        else:
            self.config['github_token'] = None
            await utils.answer(message, self.strings['auth_error'])

    @loader.command()
    async def newrepo(self, message):
        """Создать новый репозиторий"""
        
        if not self.config['github_token']:
            await utils.answer(message, self.strings['not_authorized'])
            return
            
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<b>Использование:</b> <code>.newrepo название_репозитория</code>")
            return
            
        await utils.answer(message, self.strings['creating_repo'])
        
        repo_data, status = await self._github_request(
            "POST",
            "https://api.github.com/user/repos",
            {
                "name": args,
                "description": "Модули для Hikka Userbot",
                "private": False,
                "auto_init": True
            }
        )
        
        if status == 201:
            self.config['current_repo'] = args
            await utils.answer(
                message,
                self.strings['repo_created'].format(
                    repo_data['name'],
                    repo_data['html_url']
                )
            )
        else:
            await utils.answer(message, f"<b>Ошибка создания репозитория:</b> <code>{repo_data.get('message', 'Unknown error')}</code>")

    @loader.command()
    async def repos(self, message):
        """Список репозиториев"""
        
        if not self.config['github_token']:
            await utils.answer(message, self.strings['not_authorized'])
            return
            
        repos_data, status = await self._github_request("GET", "https://api.github.com/user/repos")
        
        if status == 200:
            repos_text = []
            for repo in repos_data[:20]:  # Показываем первые 20
                repos_text.append(f"• <code>{repo['name']}</code> - {repo.get('description', 'Нет описания')}")
            
            await utils.answer(
                message,
                self.strings['repos_list'].format('\n'.join(repos_text))
            )
        else:
            await utils.answer(message, f"<b>Ошибка получения репозиториев:</b> <code>{repos_data.get('message', 'Unknown error')}</code>")

    @loader.command()
    async def selectrepo(self, message):
        """Выбрать репозиторий"""
        
        if not self.config['github_token']:
            await utils.answer(message, self.strings['not_authorized'])
            return
            
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<b>Использование:</b> <code>.selectrepo название_репозитория</code>")
            return
            
        self.config['current_repo'] = args
        await utils.answer(message, self.strings['repo_selected'].format(args))

    @loader.command()
    async def crtmodule(self, message):
        """Создать новый модуль"""
        
        if not self.config['github_token']:
            await utils.answer(message, self.strings['not_authorized'])
            return
            
        if not self.config['current_repo']:
            await utils.answer(message, self.strings['no_repo'])
            return
            
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(
                message,
                "<b>Использование:</b> <code>.crtmodule название_модуля | описание | команда</code>"
            )
            return
            
        # Разбираем аргументы
        parts = args.split('|')
        if len(parts) < 3:
            await utils.answer(
                message,
                "<b>Неверный формат!</b>\n\n<b>Использование:</b>\n<code>.crtmodule название_модуля | описание | команда</code>"
            )
            return
            
        module_name = parts[0].strip()
        description = parts[1].strip()
        command = parts[2].strip()
        
        await utils.answer(message, self.strings['module_creating'])
        
        # Генерируем код модуля
        module_code = self._generate_module_code(module_name, description, command)
        
        # Получаем username для репозитория
        user_data, _ = await self._github_request("GET", "https://api.github.com/user")
        username = user_data.get('login', 'user')
        
        # Создаем файл в репозитории
        filename = f"{module_name.lower()}.py"
        file_data, status = await self._github_request(
            "PUT",
            f"https://api.github.com/repos/{username}/{self.config['current_repo']}/contents/{filename}",
            {
                "message": f"Add {filename} module",
                "content": module_code.encode('utf-8').hex()
            }
        )
        
        if status in [200, 201]:
            await utils.answer(
                message,
                self.strings['module_created'].format(
                    filename,
                    self.config['current_repo'],
                    file_data.get('html_url', 'Unknown')
                )
            )
        else:
            await utils.answer(
                message,
                f"<b>Ошибка создания модуля:</b> <code>{file_data.get('message', 'Unknown error')}</code>"
            )

    def _generate_module_code(self, module_name, description, command):
        """Генерация кода модуля"""
        return f"""# ---------------------------------------------------------------------------------
# Name: {module_name}
# Description: {description}
# meta developer: @{self._client.tg_id if hasattr(self._client, 'tg_id') else 'unknown'}
# ---------------------------------------------------------------------------------

import logging
from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class {module_name}(loader.Module):
    \"\"\"{description}\"\"\"

    strings = {{
        "name": "{module_name}",
        "response": "<b>{module_name} работает!</b>"
    }}

    async def client_ready(self, client, db):
        self.db = db
        self._client = client

    @loader.command()
    async def {command}(self, message):
        \"\"\"{description}\"\"\"
        await utils.answer(message, self.strings['response'])
"""
