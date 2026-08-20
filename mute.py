# meta developer: @your_username
# meta pic: https://img.icons8.com/color/48/000000/mute.png
# meta banner: https://via.placeholder.com/300x100.png?text=Mute+Module

import asyncio
import re
import time

from telethon.tl.types import Message
from telethon.tl.functions.messages import DeleteMessagesRequest

from .. import loader, utils

@loader.tds
class MuteMod(loader.Module):
    """Модуль для временного мута пользователей с удалением сообщений"""
    
    strings = {
        "name": "MuteMod",
        "no_reply": "🚫 <b>Нужно ответить на сообщение пользователя!</b>",
        "no_user": "🚫 <b>Не удалось определить пользователя!</b>",
        "no_time": "🚫 <b>Укажите время! Пример: 5m, 30s, 1h, 2d</b>",
        "muted": "🔇 <b>{user} замучен на {time}</b>\n📝 <b>Все его сообщения будут удаляться</b>",
        "unmuted": "🔈 <b>Мут {user} снят</b>",
        "already_muted": "⚠️ <b>Пользователь уже замучен!</b>",
        "not_muted": "⚠️ <b>Пользователь не замучен!</b>",
        "auto_unmute": "✅ <b>Время мута истекло. {user} размучен</b>",
    }
    
    strings_ru = {
        "no_reply": "🚫 <b>Нужно ответить на сообщение пользователя!</b>",
        "no_user": "🚫 <b>Не удалось определить пользователя!</b>",
        "no_time": "🚫 <b>Укажите время! Пример: 5m, 30s, 1h, 2d</b>",
        "muted": "🔇 <b>{user} замучен на {time}</b>\n📝 <b>Все его сообщения будут удаляться</b>",
        "unmuted": "🔈 <b>Мут {user} снят</b>",
        "already_muted": "⚠️ <b>Пользователь уже замучен!</b>",
        "not_muted": "⚠️ <b>Пользователь не замучен!</b>",
        "auto_unmute": "✅ <b>Время мута истекло. {user} размучен</b>",
    }

    def __init__(self):
        self.muted_users = {}
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "delete_service_messages",
                True,
                "Удалять служебные сообщения о муте",
                validator=loader.validators.Boolean(),
            ),
        )

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self._me = await client.get_me()
        
    @loader.watcher(out=False)
    async def watcher(self, message: Message):
        """Следит за новыми сообщениями и удаляет их если пользователь замучен"""
        user_id = message.sender_id
        
        # Игнорируем свои сообщения
        if user_id == self._me.id:
            return
        
        # Проверяем, замучен ли отправитель
        if user_id not in self.muted_users:
            return
            
        mute_data = self.muted_users[user_id]
        
        # Проверяем не истекло ли время
        if time.time() >= mute_data["until"]:
            del self.muted_users[user_id]
            return
        
        # Удаляем сообщение
        try:
            if message.is_private:
                # В ЛС пробуем разные методы удаления
                try:
                    # Сначала пробуем через delete_messages
                    await self.client.delete_messages(
                        message.chat_id,
                        [message.id],
                        revoke=True
                    )
                except:
                    try:
                        # Если не получилось, пробуем через прямой вызов
                        await self.client(DeleteMessagesRequest(
                            id=[message.id],
                            revoke=True
                        ))
                    except:
                        # Последний вариант - просто message.delete()
                        await message.delete()
            else:
                # В группах используем обычный метод
                await message.delete()
        except Exception as e:
            # Логируем ошибку для отладки
            try:
                await self.client.send_message("me", f"❌ Ошибка удаления: {e}")
            except:
                pass

    async def mutecmd(self, message: Message):
        """Ответом на сообщение: .mute <время> или .mute @user <время>"""
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        
        if not reply and not args:
            await utils.answer(message, self.strings("no_reply"))
            return
        
        # Определяем пользователя
        user = None
        time_str = None
        
        if reply:
            user = await message.client.get_entity(reply.sender_id)
            time_str = args
        else:
            parts = args.split()
            if len(parts) >= 2:
                username = parts[0]
                time_str = ' '.join(parts[1:])
                try:
                    user = await message.client.get_entity(username)
                except:
                    await utils.answer(message, self.strings("no_user"))
                    return
            else:
                await utils.answer(message, self.strings("no_user"))
                return
        
        if not user:
            await utils.answer(message, self.strings("no_user"))
            return
            
        if not time_str:
            await utils.answer(message, self.strings("no_time"))
            return
        
        # Парсим время
        mute_seconds = self._parse_time(time_str)
        if mute_seconds is None:
            await utils.answer(message, self.strings("no_time"))
            return
        
        user_id = user.id
        
        # Проверяем не замучен ли уже
        if user_id in self.muted_users:
            if time.time() < self.muted_users[user_id]["until"]:
                await utils.answer(message, self.strings("already_muted"))
                return
        
        # Устанавливаем мут
        unmute_time = time.time() + mute_seconds
        self.muted_users[user_id] = {
            "until": unmute_time,
            "username": user.first_name or user.username or str(user.id)
        }
        
        # Форматируем время для отображения
        time_display = self._format_time(mute_seconds)
        
        user_name = f'<a href="tg://user?id={user.id}">{utils.escape_html(user.first_name or user.username or str(user.id))}</a>'
        await utils.answer(message, self.strings("muted").format(user=user_name, time=time_display))
        
        # Создаем задачу для автоматического размута
        asyncio.ensure_future(self._auto_unmute(user_id, mute_seconds, message, user_name))

    async def unmuteallcmd(self, message: Message):
        """Снять мут со всех пользователей"""
        count = len(self.muted_users)
        self.muted_users.clear()
        await utils.answer(message, f"🔈 <b>Снят мут с {count} пользователей</b>")
    
    async def mutelistcmd(self, message: Message):
        """Показать список замученных пользователей"""
        current_time = time.time()
        text = "🔇 <b>Замученные пользователи:</b>\n\n"
        
        for user_id, data in list(self.muted_users.items()):
            if current_time >= data["until"]:
                del self.muted_users[user_id]
                continue
            
            remaining = int(data["until"] - current_time)
            time_left = self._format_time(remaining)
            text += f"• {data['username']} | Осталось: {time_left}\n"
        
        if not self.muted_users:
            text = "📋 <b>Список замученных пуст</b>"
        
        await utils.answer(message, text)

    async def _auto_unmute(self, user_id, seconds, message, user_name):
        """Автоматически снимает мут по истечении времени"""
        await asyncio.sleep(seconds)
        
        if user_id in self.muted_users:
            del self.muted_users[user_id]
            
            try:
                await utils.answer(message, self.strings("auto_unmute").format(user=user_name))
            except:
                pass
    
    def _parse_time(self, time_str: str):
        """Парсит строку времени в секунды"""
        time_str = time_str.strip().lower()
        
        # Поддерживаем форматы: 5s, 10m, 2h, 1d
        match = re.match(r'^(\d+)\s*(s|m|h|d)$', time_str)
        if not match:
            return None
        
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit == 's':
            return value
        elif unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 3600
        elif unit == 'd':
            return value * 86400
        
        return None
    
    def _format_time(self, seconds: int) -> str:
        """Форматирует секунды в читаемый вид"""
        if seconds < 60:
            return f"{seconds}с"
        elif seconds < 3600:
            return f"{seconds // 60}м"
        elif seconds < 86400:
            return f"{seconds // 3600}ч"
        else:
            return f"{seconds // 86400}д"
