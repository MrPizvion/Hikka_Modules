# ---------------------------------------------------------------------------------
# Name: PublicBotInfo
# Description: Дает доступ другим пользователям к команде .info
# meta developer: @edu_kak_xochu
# ---------------------------------------------------------------------------------

import logging
from datetime import datetime

from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class PublicBotInfo(loader.Module):
    """Дает доступ другим пользователям к команде .info"""

    strings = {
        "name": "PublicBotInfo",
        
        "loading": "<b><emoji document_id=5326015457155620929>🔄</emoji> Получаю информацию...</b>",
        
        "no_permission": (
            "<b><emoji document_id=5467672931176010750>❌</emoji> У вас нет доступа к этой команде!</b>\n\n"
            "<b>Доступ только у:</b>\n"
            "<b>• Владельца</b>\n"
            "<b>• Разрешенных пользователей</b>\n"
            "<b>• Всех (если включено)</b>"
        ),
        
        "access_granted": (
            "<b><emoji document_id=5467906724422622902>✅</emoji> Доступ выдан!</b>\n\n"
            "<b>Пользователь:</b> <code>{}</code>\n"
            "<b>Теперь может использовать:</b> <code>.botinfo</code>"
        ),
        
        "access_revoked": (
            "<b><emoji document_id=5467906724422622902>✅</emoji> Доступ отозван!</b>\n\n"
            "<b>Пользователь:</b> <code>{}</code>"
        ),
        
        "user_not_found": (
            "<b><emoji document_id=5467672931176010750>❌</emoji> Пользователь не найден!</b>"
        ),
        
        "allowed_users": (
            "<b><emoji document_id=5431577498364158238>📊</emoji> Разрешенные пользователи:</b>\n\n{}"
        ),
        
        "no_allowed_users": "<b>Список разрешенных пользователей пуст</b>",
        
        "public_enabled": (
            "<b><emoji document_id=5467906724422622902>✅</emoji> Публичный доступ включен!</b>\n\n"
            "<b>Теперь все могут использовать:</b> <code>.botinfo</code>"
        ),
        
        "public_disabled": (
            "<b><emoji document_id=5467906724422622902>✅</emoji> Публичный доступ выключен!</b>\n\n"
            "<b>Только разрешенные пользователи могут использовать:</b> <code>.botinfo</code>"
        ),
        
        "bot_info": (
            "<b><emoji document_id=5431577498364158238>📊</emoji> Информация о юзерботе</b>\n\n"
            "<b><emoji document_id=5258011929993026890>👤</emoji> Владелец:</b> <code>{}</code>\n"
            "<b><emoji document_id=5258093637450866522>🤖</emoji> Username:</b> <code>{}</code>\n"
            "<b><emoji document_id=5258513401784573443>👥</emoji> ID:</b> <code>{}</code>\n"
            "<b><emoji document_id=5852471614628696454>📢</emoji> Бот:</b> <code>{}</code>\n"
            "<b><emoji document_id=5258093637450866522>🤖</emoji> Премиум:</b> <code>{}</code>\n"
            "<b><emoji document_id=5431577498364158238>📊</emoji> Модулей:</b> <code>{}</code>\n"
            "<b><emoji document_id=5258011929993026890>👤</emoji> Чатов:</b> <code>{}</code>\n"
            "<b><emoji document_id=5258093637450866522>🤖</emoji> Запрос от:</b> <code>{}</code>\n"
        ),
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "public_access",
                False,
                lambda: "Публичный доступ к .botinfo (True - все могут использовать)",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "allowed_users",
                [],
                lambda: "Список ID пользователей, которым разрешено использовать .botinfo",
                validator=loader.validators.Series()
            ),
        )

    async def client_ready(self, client, db):
        self.db = db
        self._client = client

    async def _get_bot_owner(self):
        """Получить информацию о владельце"""
        try:
            me = await self._client.get_me()
            return me
        except:
            return None

    async def _count_modules(self):
        """Подсчитать количество модулей"""
        try:
            return len(self.allmodules.modules)
        except:
            return 0

    async def _count_chats(self):
        """Подсчитать количество чатов"""
        try:
            count = 0
            async for _ in self._client.iter_dialogs():
                count += 1
            return count
        except:
            return 0

    @loader.command()
    async def botinfo(self, message):
        """Показать информацию о юзерботе (доступно другим пользователям)"""
        
        user_id = message.from_id
        
        # Проверяем доступ
        if not self.config['public_access']:
            # Проверяем является ли пользователь владельцем
            owner = await self._get_bot_owner()
            if owner and user_id == owner.id:
                pass  # Владелец всегда имеет доступ
            # Проверяем в списке разрешенных
            elif user_id in self.config['allowed_users']:
                pass
            else:
                await utils.answer(message, self.strings['no_permission'])
                return
        
        await utils.answer(message, self.strings['loading'])
        
        owner = await self._get_bot_owner()
        if not owner:
            await utils.answer(message, self.strings['user_not_found'])
            return
            
        # Получаем информацию
        first_name = owner.first_name or ""
        last_name = owner.last_name or ""
        full_name = f"{first_name} {last_name}".strip()
        
        username = f"@{owner.username}" if owner.username else "Нет"
        owner_id = owner.id
        is_bot = "Да" if owner.bot else "Нет"
        is_premium = "Да" if getattr(owner, 'premium', False) else "Нет"
        
        modules_count = await self._count_modules()
        
        # Получаем информацию о запросившем
        requester = await self._client.get_entity(user_id)
        requester_name = requester.first_name or "Неизвестно"
        
        # Считаем чаты (асинхронно, чтобы не блокировать)
        chats_count = await self._count_chats()
        
        await utils.answer(
            message,
            self.strings['bot_info'].format(
                full_name,
                username,
                owner_id,
                is_bot,
                is_premium,
                modules_count,
                chats_count,
                requester_name
            )
        )

    @loader.command()
    async def grantinfo(self, message):
        """Выдать доступ к .botinfo пользователю"""
        
        # Проверяем, что команду использует владелец
        owner = await self._get_bot_owner()
        if not owner or message.from_id != owner.id:
            await utils.answer(message, "<b>Только владелец может выдавать доступ!</b>")
            return
            
        user = None
        reply = await message.get_reply_message()
        
        if reply:
            user = reply.sender
        else:
            args = utils.get_args_raw(message)
            if args:
                try:
                    if args.startswith('@'):
                        user = await self._client.get_entity(args)
                    elif args.isdigit():
                        user = await self._client.get_entity(int(args))
                    else:
                        user = await self._client.get_entity(args)
                except:
                    user = None
        
        if not user:
            await utils.answer(message, self.strings['user_not_found'])
            return
            
        # Добавляем в список разрешенных
        if user.id not in self.config['allowed_users']:
            allowed = list(self.config['allowed_users'])
            allowed.append(user.id)
            self.config['allowed_users'] = allowed
            
        await utils.answer(
            message,
            self.strings['access_granted'].format(user.first_name or "Пользователь")
        )

    @loader.command()
    async def revokeinfo(self, message):
        """Отозвать доступ к .botinfo у пользователя"""
        
        # Проверяем, что команду использует владелец
        owner = await self._get_bot_owner()
        if not owner or message.from_id != owner.id:
            await utils.answer(message, "<b>Только владелец может отзывать доступ!</b>")
            return
            
        user = None
        reply = await message.get_reply_message()
        
        if reply:
            user = reply.sender
        else:
            args = utils.get_args_raw(message)
            if args:
                try:
                    if args.startswith('@'):
                        user = await self._client.get_entity(args)
                    elif args.isdigit():
                        user = await self._client.get_entity(int(args))
                    else:
                        user = await self._client.get_entity(args)
                except:
                    user = None
        
        if not user:
            await utils.answer(message, self.strings['user_not_found'])
            return
            
        # Удаляем из списка разрешенных
        if user.id in self.config['allowed_users']:
            allowed = list(self.config['allowed_users'])
            allowed.remove(user.id)
            self.config['allowed_users'] = allowed
            
        await utils.answer(
            message,
            self.strings['access_revoked'].format(user.first_name or "Пользователь")
        )

    @loader.command()
    async def infolist(self, message):
        """Показать список разрешенных пользователей"""
        
        # Проверяем, что команду использует владелец
        owner = await self._get_bot_owner()
        if not owner or message.from_id != owner.id:
            await utils.answer(message, "<b>Только владелец может просматривать список!</b>")
            return
            
        allowed = self.config['allowed_users']
        
        if not allowed:
            await utils.answer(message, self.strings['no_allowed_users'])
            return
            
        users_info = []
        for user_id in allowed:
            try:
                user = await self._client.get_entity(user_id)
                name = user.first_name or "Неизвестно"
                username = f"@{user.username}" if user.username else "Нет username"
                users_info.append(f"• <b>{name}</b> | <code>{username}</code> | <code>{user_id}</code>")
            except:
                users_info.append(f"• <code>{user_id}</code> (не найден)")
        
        await utils.answer(
            message,
            self.strings['allowed_users'].format('\n'.join(users_info))
        )

    @loader.command()
    async def publicinfo(self, message):
        """Включить/выключить публичный доступ к .botinfo"""
        
        # Проверяем, что команду использует владелец
        owner = await self._get_bot_owner()
        if not owner or message.from_id != owner.id:
            await utils.answer(message, "<b>Только владелец может изменять настройки!</b>")
            return
            
        # Переключаем публичный доступ
        self.config['public_access'] = not self.config['public_access']
        
        if self.config['public_access']:
            await utils.answer(message, self.strings['public_enabled'])
        else:
            await utils.answer(message, self.strings['public_disabled'])
