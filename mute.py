# meta developer: @your_username
# meta pic: https://example.com/mute_icon.png
# scope: hikka_only
# scope: hikka_min 1.2.10

from .. import loader, utils
import datetime
import asyncio
from typing import Dict, Optional

@loader.tds
class SilentMuteMod(loader.Module):
    """Модуль для тихого мута (удаление сообщений)"""
    
    strings = {
        "name": "SilentMute",
        "no_args": "🚫 Укажите пользователя и время.",
        "user_not_found": "👤 Пользователь не найден.",
        "invalid_time": "⏰ Укажите корректное время (например: 5m, 1h, 2d).",
        "already_muted": "🔇 Пользователь уже в муте.",
        "not_muted": "✅ Пользователь не в муте.",
        "muted": "🔇 Пользователь {user} замьючен на {time}.",
        "unmuted": "🔊 Пользователь {user} размьючен.",
        "mute_list": "📋 Список замьюченных пользователей:\n{users}",
        "no_muted_users": "📭 Нет замьюченных пользователей.",
        "mute_timeout": "⏰ Мут пользователя {user} истёк.",
        "config_timeout": "Время мута по умолчанию (в минутах)",
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "default_mute_time",
                5,
                "Время мута по умолчанию (в минутах)",
                validator=loader.validators.Integer(minimum=1, maximum=1440),
            ),
        )
        self.muted_users: Dict[int, Dict] = {}  # user_id: {"until": datetime, "chat_id": int}
        self._tasks = []
    
    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self.muted_users = self.db.get("SilentMute", "muted_users", {})
        
        # Восстановление таймеров после перезагрузки
        for user_id, data in self.muted_users.items():
            if data.get("until"):
                until = datetime.datetime.fromisoformat(data["until"])
                if until > datetime.datetime.now():
                    self._schedule_unmute(int(user_id), until, data.get("chat_id"))
                else:
                    await self._unmute_user(int(user_id), data.get("chat_id"))
    
    async def on_message(self, message):
        """Обработчик новых сообщений"""
        if not message.out and message.sender_id in self.muted_users:
            chat_id = self.muted_users[message.sender_id].get("chat_id")
            if chat_id == message.chat_id:
                try:
                    await message.delete()
                    return True
                except Exception:
                    pass
        return False
    
    async def mutecmd(self, message):
        """🔇 Замутить пользователя (тихое удаление сообщений)
        Использование: .mute <@username/reply> <время>
        Пример: .mute @username 5m
        Время: s - секунды, m - минуты, h - часы, d - дни"""
        
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        
        # Определяем пользователя
        user = None
        if reply:
            user = reply.sender_id
            args_parts = args.split()
            time_str = args_parts[0] if args_parts else None
        else:
            if not args:
                return await utils.answer(message, self.strings("no_args"))
            args_parts = args.split()
            try:
                user = await self.client.get_entity(args_parts[0])
                user = user.id
                time_str = args_parts[1] if len(args_parts) > 1 else None
            except Exception:
                return await utils.answer(message, self.strings("user_not_found"))
        
        # Парсим время
        if not time_str:
            time_minutes = self.config["default_mute_time"]
        else:
            time_seconds = self._parse_time(time_str)
            if time_seconds is None:
                return await utils.answer(message, self.strings("invalid_time"))
            time_minutes = time_seconds / 60
        
        # Проверяем, не замьючен ли уже
        if user in self.muted_users and self.muted_users[user].get("chat_id") == message.chat_id:
            return await utils.answer(message, self.strings("already_muted"))
        
        # Вычисляем время окончания
        until = datetime.datetime.now() + datetime.timedelta(minutes=time_minutes)
        
        # Сохраняем в базу данных
        self.muted_users[str(user)] = {
            "until": until.isoformat(),
            "chat_id": message.chat_id,
        }
        self.db.set("SilentMute", "muted_users", self.muted_users)
        
        # Запускаем таймер
        self._schedule_unmute(user, until, message.chat_id)
        
        user_entity = await self.client.get_entity(user)
        await utils.answer(
            message,
            self.strings("muted").format(
                user=utils.escape_html(user_entity.first_name or str(user)),
                time=self._format_time(time_minutes * 60)
            )
        )
    
    async def unmutecmd(self, message):
        """🔊 Размутить пользователя
        Использование: .unmute <@username/reply>"""
        
        args = utils.get_args_raw(message)
        reply = await message.get_reply_message()
        
        user = None
        if reply:
            user = reply.sender_id
        elif args:
            try:
                user = await self.client.get_entity(args)
                user = user.id
            except Exception:
                return await utils.answer(message, self.strings("user_not_found"))
        else:
            return await utils.answer(message, self.strings("no_args"))
        
        if user not in self.muted_users:
            return await utils.answer(message, self.strings("not_muted"))
        
        chat_id = self.muted_users[user].get("chat_id")
        await self._unmute_user(user, chat_id)
        
        user_entity = await self.client.get_entity(user)
        await utils.answer(
            message,
            self.strings("unmuted").format(
                user=utils.escape_html(user_entity.first_name or str(user))
            )
        )
    
    async def mutelistcmd(self, message):
        """📋 Показать список замьюченных пользователей"""
        if not self.muted_users:
            return await utils.answer(message, self.strings("no_muted_users"))
        
        users_list = []
        for user_id, data in self.muted_users.items():
            try:
                user_entity = await self.client.get_entity(int(user_id))
                name = user_entity.first_name or str(user_id)
            except Exception:
                name = f"User {user_id}"
            
            until = datetime.datetime.fromisoformat(data["until"])
            remaining = until - datetime.datetime.now()
            if remaining.total_seconds() > 0:
                time_left = self._format_time(remaining.total_seconds())
                users_list.append(f"• {utils.escape_html(name)} - {time_left}")
            else:
                users_list.append(f"• {utils.escape_html(name)} - ⏰ истекло")
        
        if not users_list:
            return await utils.answer(message, self.strings("no_muted_users"))
        
        await utils.answer(
            message,
            self.strings("mute_list").format(users="\n".join(users_list))
        )
    
    def _parse_time(self, time_str: str) -> Optional[int]:
        """Парсит время из строки (5m, 1h, 30s, 2d)"""
        if not time_str:
            return None
        
        time_str = time_str.lower().strip()
        if time_str[-1].isdigit():
            # Если нет суффикса, считаем минутами
            try:
                return int(time_str) * 60
            except ValueError:
                return None
        
        unit = time_str[-1]
        try:
            value = int(time_str[:-1])
        except ValueError:
            return None
        
        multipliers = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400,
        }
        
        if unit in multipliers:
            return value * multipliers[unit]
        return None
    
    def _format_time(self, seconds: int) -> str:
        """Форматирует время в человекочитаемый вид"""
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        parts = []
        if days > 0:
            parts.append(f"{int(days)}д")
        if hours > 0:
            parts.append(f"{int(hours)}ч")
        if minutes > 0:
            parts.append(f"{int(minutes)}м")
        if secs > 0 and not parts:
            parts.append(f"{int(secs)}с")
        
        return " ".join(parts) if parts else "0м"
    
    def _schedule_unmute(self, user_id: int, until: datetime.datetime, chat_id: int):
        """Запускает таймер для размута"""
        async def unmute_task():
            now = datetime.datetime.now()
            if until > now:
                await asyncio.sleep((until - now).total_seconds())
                await self._unmute_user(user_id, chat_id)
        
        task = asyncio.create_task(unmute_task())
        self._tasks.append(task)
    
    async def _unmute_user(self, user_id: int, chat_id: int):
        """Размучивает пользователя"""
        user_id_str = str(user_id)
        if user_id_str in self.muted_users:
            del self.muted_users[user_id_str]
            self.db.set("SilentMute", "muted_users", self.muted_users)
            
            try:
                user_entity = await self.client.get_entity(user_id)
                await self.client.send_message(
                    chat_id,
                    self.strings("mute_timeout").format(
                        user=utils.escape_html(user_entity.first_name or str(user_id))
                    )
                )
            except Exception:
                pass
    
    async def on_unload(self):
        """Отмена всех таймеров при выгрузке модуля"""
        for task in self._tasks:
            if not task.done():
                task.cancel()
