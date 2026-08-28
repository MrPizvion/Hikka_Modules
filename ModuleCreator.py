# ---------------------------------------------------------------------------------
# Name: ModuleCreator
# Description: Создание модулей через чат Telegram с GitHub авторизацией
# meta developer: @edu_kak_xochu
# ---------------------------------------------------------------------------------

import asyncio
import logging
import re
import base64
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
            "<code>.newrepo</code> <i>название_репозитория</i>\n"
            "<b>Или выберите существующий:</b>\n"
            "<code>.selectrepo</code> <i>название_репозитория</i>"
        ),
        
        "repo_created": (
            "<b><emoji document_id=5467906724422622902>✅</emoji> Репозиторий создан!</b>\n\n"
            "<b>Название:</b> <code>{}</code>\n"
            "<b>URL:</b> <code>{}</code>"
        ),
        
        "repo_deleted": (
            "<b><emoji document_id=5467906724422622902>✅</emoji> Репозиторий удален!</b>\n\n"
            "<b>Название:</b> <code>{}</code>"
        ),
        
        "repo_not_found": (
            "<b><emoji document_id=5467672931176010750>❌</emoji> Репозиторий не найден!</b>\n\n"
            "<b>Проверьте название:</b> <code>{}</code>"
        ),
        
        "module_creating": "<b><emoji document_id=5326015457155620929>🔄</emoji> Создаю модуль...</b>",
        
        "module_created": (
            "<b><emoji document_id=5467906724422622902>✅</emoji> Модуль создан!</b>\n\n"
            "<b>Файл:</b> <code>{}</code>\n"
            "<b>Репозиторий:</b> <code>{}</code>\n\n"
            "<b>Ссылка на файл:</b>\n"
            "<code>{}</code>"
        ),
        
        "module_deleted": (
            "<b><emoji document_id=5467906724422622902>✅</emoji> Модуль удален!</b>\n\n"
            "<b>Файл:</b> <code>{}</code>\n"
            "<b>Репозиторий:</b> <code>{}</code>"
        ),
        
        "module_not_found": (
            "<b><emoji document_id=5467672931176010750>❌</emoji> Модуль не найден!</b>\n\n"
            "<b>Проверьте название файла:</b> <code>{}</code>"
        ),
        
        "creating_repo": "<b><emoji document_id=5326015457155620929>🔄</emoji> Создаю репозиторий...</b>",
        
        "repos_list": "<b><emoji document_id=5431577498364158238>📊</emoji> Ваши репозитории:</b>\n\n{}",
        
        "repo_selected": "<b><emoji document_id=5467906724422622902>✅</emoji> Репозиторий выбран:</b>\n<code>{}</code>",
        
        "modules_list": "<b><emoji document_id=5431577498364158238>📊</emoji> Модули в репозитории {}:</b>\n\n{}",
        
        "no_modules": "<b><emoji document_id=5431577498364158238>📊</emoji> В репозитории нет модулей</b>",
        
        "editing_module": "<b><emoji document_id=5326015457155620929>🔄</emoji> Открываю редактор модуля...</b>",
        
        "module_updated": (
            "<b><emoji document_id=5467906724422622902>✅</emoji> Модуль обновлен!</b>\n\n"
            "<b>Файл:</b> <code>{}</code>"
        ),
        
        "edit_cancelled": "<b><emoji document_id=5467672931176010750>❌</emoji> Редактирование отменено</b>",
        
        "edit_timeout": "<b><emoji document_id=5467672931176010750>❌</emoji> Время редактирования истекло</b>",
        
        "edit_prompt": (
            "<b><emoji document_id=5431577498364158238>📝</emoji> Редактирование модуля:</b> <code>{}</code>\n\n"
            "<b>Отправьте новый код модуля.</b>\n"
            "<b>Для отмены отправьте:</b> <code>.cancel</code>"
        ),
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
        self._editing = {}
        self._username = None
        self._session = None

    async def client_ready(self, client, db):
        self.db = db
        self._client = client
        import aiohttp
        self._session = aiohttp.ClientSession()

    async def _get_headers(self):
        """Получить заголовки для запросов"""
        return {
            "Authorization": f"token {self.config['github_token']}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Hikka-ModuleCreator"
        }

    async def _github_request(self, method, url, data=None):
        """Выполнить запрос к GitHub API"""
        headers = await self._get_headers()
        
        async with self._session.request(method, url, headers=headers, json=data) as response:
            if method == "DELETE":
                return None, response.status
            return await response.json(), response.status

    async def _get_username(self, force=False):
        """Получить username пользователя (кэшируется)"""
        if self._username and not force:
            return self._username
            
        user_data, status = await self._github_request("GET", "https://api.github.com/user")
        if status == 200:
            self._username = user_data.get('login')
            return self._username
        return None

    @loader.command()
    async def ghauth(self, message):
        """Авторизация GitHub - указать токен"""
        
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<b>Использование:</b> <code>.ghauth ваш_github_token</code>")
            return
            
        self.config['github_token'] = args
        self._username = None  # Сбрасываем кэш
        
        # Проверяем токен
        username = await self._get_username(force=True)
        
        if username:
            await utils.answer(
                message,
                self.strings['auth_success'].format(
                    username,
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
    async def delrep(self, message):
        """Удалить репозиторий"""
        
        if not self.config['github_token']:
            await utils.answer(message, self.strings['not_authorized'])
            return
            
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<b>Использование:</b> <code>.delrep название_репозитория</code>")
            return
            
        username = await self._get_username()
        if not username:
            await utils.answer(message, self.strings['auth_error'])
            return
            
        _, status = await self._github_request(
            "DELETE",
            f"https://api.github.com/repos/{username}/{args}"
        )
        
        if status == 204:
            if self.config['current_repo'] == args:
                self.config['current_repo'] = None
            await utils.answer(message, self.strings['repo_deleted'].format(args))
        elif status == 404:
            await utils.answer(message, self.strings['repo_not_found'].format(args))
        else:
            await utils.answer(message, f"<b>Ошибка удаления репозитория. Статус:</b> <code>{status}</code>")

    @loader.command()
    async def repos(self, message):
        """Список репозиториев"""
        
        if not self.config['github_token']:
            await utils.answer(message, self.strings['not_authorized'])
            return
            
        repos_data, status = await self._github_request("GET", "https://api.github.com/user/repos?per_page=50")
        
        if status == 200:
            repos_text = []
            for repo in repos_data:
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
        
        module_code = self._generate_module_code(module_name, description, command)
        
        username = await self._get_username()
        if not username:
            await utils.answer(message, self.strings['auth_error'])
            return
        
        filename = f"{module_name.lower()}.py"
        file_data, status = await self._github_request(
            "PUT",
            f"https://api.github.com/repos/{username}/{self.config['current_repo']}/contents/{filename}",
            {
                "message": f"Add {filename} module",
                "content": base64.b64encode(module_code.encode('utf-8')).decode('ascii')
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

    @loader.command()
    async def delmod(self, message):
        """Удалить модуль из репозитория"""
        
        if not self.config['github_token']:
            await utils.answer(message, self.strings['not_authorized'])
            return
            
        if not self.config['current_repo']:
            await utils.answer(message, self.strings['no_repo'])
            return
            
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<b>Использование:</b> <code>.delmod название_файла.py</code>")
            return
            
        filename = args if args.endswith('.py') else f"{args}.py"
        
        username = await self._get_username()
        if not username:
            await utils.answer(message, self.strings['auth_error'])
            return
            
        # Получаем информацию о файле
        file_data, status = await self._github_request(
            "GET",
            f"https://api.github.com/repos/{username}/{self.config['current_repo']}/contents/{filename}"
        )
        
        if status == 404:
            await utils.answer(message, self.strings['module_not_found'].format(filename))
            return
            
        if status != 200:
            await utils.answer(message, f"<b>Ошибка получения файла:</b> <code>{file_data.get('message', 'Unknown error')}</code>")
            return
            
        # Удаляем файл с правильным форматом данных
        _, delete_status = await self._github_request(
            "DELETE",
            f"https://api.github.com/repos/{username}/{self.config['current_repo']}/contents/{filename}",
            {
                "message": f"Delete {filename}",
                "sha": file_data['sha']
            }
        )
        
        if delete_status == 200:
            await utils.answer(message, self.strings['module_deleted'].format(filename, self.config['current_repo']))
        else:
            await utils.answer(message, f"<b>Ошибка удаления модуля. Статус:</b> <code>{delete_status}</code>")

    @loader.command()
    async def modlist(self, message):
        """Список модулей в репозитории"""
        
        if not self.config['github_token']:
            await utils.answer(message, self.strings['not_authorized'])
            return
            
        if not self.config['current_repo']:
            await utils.answer(message, self.strings['no_repo'])
            return
            
        username = await self._get_username()
        if not username:
            await utils.answer(message, self.strings['auth_error'])
            return
            
        # Получаем список файлов
        files_data, status = await self._github_request(
            "GET",
            f"https://api.github.com/repos/{username}/{self.config['current_repo']}/contents/"
        )
        
        if status != 200:
            await utils.answer(message, f"<b>Ошибка получения файлов:</b> <code>{files_data.get('message', 'Unknown error')}</code>")
            return
            
        # Создаем задачи для параллельного получения описаний
        tasks = []
        py_files = [f for f in files_data if f['name'].endswith('.py')]
        
        async def get_module_info(file):
            file_content, content_status = await self._github_request("GET", file['url'])
            description = "Нет описания"
            if content_status == 200:
                content = file_content.get('content', '')
                if content:
                    try:
                        decoded_content = base64.b64decode(content).decode('utf-8')
                        desc_match = re.search(r'# Description: (.+)', decoded_content)
                        if desc_match:
                            description = desc_match.group(1)
                    except:
                        pass
            return f"• <code>{file['name']}</code> - {description}"
        
        # Параллельно получаем описания
        tasks = [get_module_info(file) for file in py_files]
        modules = await asyncio.gather(*tasks)
        
        if modules:
            await utils.answer(
                message,
                self.strings['modules_list'].format(self.config['current_repo'], '\n'.join(modules))
            )
        else:
            await utils.answer(message, self.strings['no_modules'])

    @loader.command()
    async def editmod(self, message):
        """Редактировать модуль"""
        
        if not self.config['github_token']:
            await utils.answer(message, self.strings['not_authorized'])
            return
            
        if not self.config['current_repo']:
            await utils.answer(message, self.strings['no_repo'])
            return
            
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<b>Использование:</b> <code>.editmod название_файла.py</code>")
            return
            
        filename = args if args.endswith('.py') else f"{args}.py"
        
        username = await self._get_username()
        if not username:
            await utils.answer(message, self.strings['auth_error'])
            return
            
        # Проверяем существование файла
        file_data, status = await self._github_request(
            "GET",
            f"https://api.github.com/repos/{username}/{self.config['current_repo']}/contents/{filename}"
        )
        
        if status == 404:
            await utils.answer(message, self.strings['module_not_found'].format(filename))
            return
            
        if status != 200:
            await utils.answer(message, f"<b>Ошибка получения файла:</b> <code>{file_data.get('message', 'Unknown error')}</code>")
            return
            
        # Сохраняем информацию о файле для редактирования
        self._editing[message.from_id] = {
            'filename': filename,
            'sha': file_data['sha'],
            'started': datetime.now()
        }
        
        await utils.answer(message, self.strings['edit_prompt'].format(filename))

    @loader.watcher()
    async def watcher(self, message):
        """Обработчик для редактирования модулей"""
        
        if message.from_id not in self._editing:
            return
            
        edit_info = self._editing[message.from_id]
        
        # Проверяем на отмену
        if message.text.lower() == '.cancel':
            del self._editing[message.from_id]
            await utils.answer(message, self.strings['edit_cancelled'])
            return
            
        # Проверяем на таймаут (5 минут)
        time_diff = (datetime.now() - edit_info['started']).total_seconds()
        if time_diff > 300:
            del self._editing[message.from_id]
            await utils.answer(message, self.strings['edit_timeout'])
            return
            
        # Получаем код модуля
        module_code = message.text
        
        username = await self._get_username()
        if not username:
            await utils.answer(message, self.strings['auth_error'])
            return
            
        # Обновляем файл
        file_data, status = await self._github_request(
            "PUT",
            f"https://api.github.com/repos/{username}/{self.config['current_repo']}/contents/{edit_info['filename']}",
            {
                "message": f"Update {edit_info['filename']}",
                "content": base64.b64encode(module_code.encode('utf-8')).decode('ascii'),
                "sha": edit_info['sha']
            }
        )
        
        if status in [200, 201]:
            await utils.answer(message, self.strings['module_updated'].format(edit_info['filename']))
        else:
            await utils.answer(message, f"<b>Ошибка обновления модуля:</b> <code>{file_data.get('message', 'Unknown error')}</code>")
            
        # Удаляем из списка редактирования
        del self._editing[message.from_id]

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
