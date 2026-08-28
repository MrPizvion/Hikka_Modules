# ---------------------------------------------------------------------------------
# Name: UserInfo
# Description: Показывает информацию о пользователе из чата
# meta developer: @edu_kak_xochu
# ---------------------------------------------------------------------------------

import logging
from datetime import datetime

from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class UserInfo(loader.Module):
    """Показывает информацию о пользователе из чата"""

    strings = {
        "name": "UserInfo",
        
        "no_reply": (
            "<b><emoji document_id=5467672931176010750>❌</emoji> Ошибка!</b>\n\n"
            "<b>Использование:</b>\n"
            "<code>.uinfo</code> <i>в ответ на сообщение</i>\n"
            "или\n"
            "<code>.uinfo @username</code>\n"
            "или\n"
            "<code>.uinfo ID</code>"
        ),
        
        "user_not_found": (
            "<b><emoji document_id=5467672931176010750>❌</emoji> Пользователь не найден!</b>"
        ),
        
        "loading": "<b><emoji document_id=5326015457155620929>🔄</emoji> Получаю информацию...</b>",
        
        "info": (
            "<b><emoji document_id=5431577498364158238>📊</emoji> Информация о пользователе</b>\n\n"
            "<b><emoji document_id=5258011929993026890>👤</emoji> Имя:</b> <code>{}</code>\n"
            "<b><emoji document_id=5258093637450866522>🤖</emoji> Username:</b> <code>{}</code>\n"
            "<b><emoji document_id=5258513401784573443>👥</emoji> ID:</b> <code>{}</code>\n"
            "<b><emoji document_id=5852471614628696454>📢</emoji> Бот:</b> <code>{}</code>\n"
            "<b><emoji document_id=5258093637450866522>🤖</emoji> Премиум:</b> <code>{}</code>\n"
            "<b><emoji document_id=5258011929993026890>👤</emoji> Статус:</b> <code>{}</code>\n"
            "<b><emoji document_id=5431577498364158238>📊</emoji> В сети:</b> <code>{}</code>\n"
        ),
    }

    async def client_ready(self, client, db):
        self.db = db
        self._client = client

    async def _get_user_info(self, user):
        """Получить информацию о пользователе"""
        first_name = user.first_name or ""
        last_name = user.last_name or ""
        full_name = f"{first_name} {last_name}".strip()
        
        username = f"@{user.username}" if user.username else "Нет"
        user_id = user.id
        is_bot = "Да" if user.bot else "Нет"
        is_premium = "Да" if getattr(user, 'premium', False) else "Нет"
        
        # Получаем статус
        status = "Неизвестно"
        last_seen = "Неизвестно"
        
        try:
            if hasattr(user, 'status'):
                if hasattr(user.status, 'was_online'):
                    last_seen = user.status.was_online.strftime("%d.%m.%Y %H:%M:%S") if user.status.was_online else "Недавно"
                    status = "Был(а) в сети"
                elif hasattr(user.status, 'expires'):
                    status = "Премиум активен"
                    last_seen = user.status.expires.strftime("%d.%m.%Y %H:%M:%S")
                elif hasattr(user.status, 'type'):
                    status_map = {
                        'online': 'В сети',
                        'offline': 'Не в сети',
                        'recently': 'Был(а) недавно',
                        'last_week': 'Был(а) на этой неделе',
                        'last_month': 'Был(а) в этом месяце',
                        'userStatusEmpty': 'Неизвестно'
                    }
                    status = status_map.get(user.status.type, 'Неизвестно')
        except:
            pass
            
        return full_name, username, user_id, is_bot, is_premium, status, last_seen

    @loader.command()
    async def uinfo(self, message):
        """Показать информацию о пользователе"""
        
        await utils.answer(message, self.strings['loading'])
        
        user = None
        
        # Проверяем реплай
        reply = await message.get_reply_message()
        if reply:
            user = reply.sender
        else:
            # Проверяем аргументы
            args = utils.get_args_raw(message)
            if args:
                try:
                    # Пробуем получить по username
                    if args.startswith('@'):
                        user = await self._client.get_entity(args)
                    # Пробуем получить по ID
                    elif args.isdigit():
                        user = await self._client.get_entity(int(args))
                    # Пробуем получить по имени
                    else:
                        user = await self._client.get_entity(args)
                except:
                    user = None
        
        if not user:
            await utils.answer(message, self.strings['user_not_found'])
            return
            
        # Получаем информацию
        full_name, username, user_id, is_bot, is_premium, status, last_seen = await self._get_user_info(user)
        
        await utils.answer(
            message,
            self.strings['info'].format(
                full_name,
                username,
                user_id,
                is_bot,
                is_premium,
                status,
                last_seen
            )
        )

    @loader.command()
    async def uinfoall(self, message):
        """Показать информацию о всех участниках чата"""
        
        if not message.is_group:
            await utils.answer(message, "<b>Эта команда работает только в группах!</b>")
            return
            
        await utils.answer(message, self.strings['loading'])
        
        users_info = []
        count = 0
        
        async for user in self._client.iter_participants(message.chat_id, limit=50):
            count += 1
            full_name, username, user_id, is_bot, is_premium, status, last_seen = await self._get_user_info(user)
            
            user_info = (
                f"{count}. <b>{full_name}</b>\n"
                f"   ├ <b>ID:</b> <code>{user_id}</code>\n"
                f"   ├ <b>Username:</b> <code>{username}</code>\n"
                f"   ├ <b>Бот:</b> {is_bot}\n"
                f"   └ <b>Статус:</b> {status}\n"
            )
            users_info.append(user_info)
            
            if count >= 50:
                break
        
        if users_info:
            result = (
                f"<b><emoji document_id=5431577498364158238>📊</emoji> Информация об участниках чата</b>\n\n"
                f"<b>Всего показано:</b> <code>{count}</code>\n\n"
                f"{''.join(users_info)}"
            )
        else:
            result = "<b>Не удалось получить информацию об участниках</b>"
            
        await utils.answer(message, result)
