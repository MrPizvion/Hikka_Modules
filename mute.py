# meta developer: @your_username
# meta pic: https://example.com/mute_icon.png
# scope: hikka_only
# scope: hikka_min 1.2.10

from .. import loader, utils
import datetime
import asyncio
from telethon import events

@loader.tds
class SilentMuteMod(loader.Module):
    """Модуль для тихого мута (удаление сообщений)"""
    
    strings = {
        "name": "SilentMute",
        "no_args": "🚫 Ответьте на сообщение пользователя или укажите ID.",
        "user_not_found": "👤 Пользователь не найден.",
        "invalid_time": "⏰ Укажите корректное время (например: 5m, 1h, 2d).",
        "already_muted": "🔇 Пользователь уже в муте.",
        "not_muted": "✅ Пользователь не в муте.",
        "muted": "🔇 Пользователь {user} замьючен на {time}.",
        "unmuted": "🔊 Пользователь {user} размьючен.",
        "mute_list": "📋 Список замьюченных пользователей:\n{users}",
        "no_muted_users": "📭 Нет замьюченных пользователей.",
        "mute_timeout": "⏰ Мут пользователя {user} истёк.",
        "deleted_message": "🗑️ Сообщение удалено (мут)",
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
        self.muted_users: dict = {}
        self._tasks = []
        self._handler = None
    
    async def client_ready(self, client, db):
        self.db = db
        self.client = client
        self.muted_users = self.db.get("SilentMute", "muted_users", {})
        
        # Восстановление таймеров после перезагрузки
        for user_id, data in list(self.muted_users.items()):
            try:
                until = datetime.datetime.fromisoformat(data["until"])
                if until > datetime.datetime.now():
                    self._schedule_unmute(int(user_id), until, data.get("chat_id"))
                else:
                    await self._unmute_user(int(user_id), data.get("chat_id"))
            except:
                pass
        
        # Регистрируем обработчик
        await self._register_handler()
    
    async def _register_handler(self):
        """Регистрирует обработчик для удаления сообщений"""
        if self._handler:
            self.client.remove_event_handler(self._handler)
        
        @self.client.on(events.NewMessage)
        async def message_handler(event):
            if event.out:
                return
            
            # Проверяем, есть ли пользователь в муте
            if event.sender_id in self.muted_users:
                mute_data = self.muted_users[event.sender_id]
                
                # Проверяем, что это тот же чат и мут не истек
                if mute_data.get("chat_id") == event.chat_id:
                    try:
                        until = datetime.datetime.fromisoformat(mute_data["until"])
                        if until > datetime.datetime.now():
                            # Удаляем сообщение
                            await event.delete()
                            return True
                        else:
                            # Если мут истек - размучиваем
                            await self._unmute_user(event.sender_id, event.chat_id)
                    except Exception as e:
                        pass
            return False
        
        self._handler = message_handler
    
    @loader.command()
    async def mutecmd(self, message):
        """🔇 Замутить пользователя (ответом на сообщение)
        Использование: .mute <время> (ответом на сообщение)
        Пример: .mute 5m (ответом на сообщение пользователя)"""
        
        reply = await message.get_reply_message()
        if not reply:
            return await utils.answer(message, "🚫 Ответьте на сообщение пользователя, которого хотите замутить!")
        
        user_id = reply.sender_id
        chat_id = message.chat_id
        
        # Проверяем, не админ ли это
        try:
            participant = await self.client.get_permissions(chat_id, user_id)
            if participant.is_admin or participant.is_creator:
                return await utils.answer(message, "❌ Нельзя замутить администратора!")
        except:
            pass
        
        # Парсим время
        args = utils.get_args_raw(message)
        if args:
            time_seconds = self._parse_time(args)
            if time_seconds is None:
                return await utils.answer(message, self.strings("invalid_time"))
            time_minutes = time_seconds / 60
        else:
            time_minutes = self.config["default_mute_time"]
        
        # Проверяем, не замьючен ли уже
        if user_id in self.muted_users and self.muted_users[user_id].get("chat_id") == chat_id:
            return await utils.answer(message, self.strings("already_muted"))
        
        # Вычисляем время окончания
        until = datetime.datetime.now() + datetime.timedelta(minutes=time_minutes)
        
        # Сохраняем в базу данных
        self.muted_users[user_id] = {
            "until": until.isoformat(),
            "chat_id": chat_id,
        }
        self.db.set("SilentMute", "muted_users", self.muted_users)
        
        # Запускаем таймер
        self._schedule_unmute(user_id, until, chat_id)
        
        user_entity = await self.client.get_entity(user_id)
        await utils.answer(
            message,
            self.strings("muted").format(
                user=utils.escape_html(user_entity.first_name or str(user_id)),
                time=self._format_time(time_minutes * 60)
            )
        )
    
    @loader.command()
    async def unmutecmd(self, message):
        """🔊 Размутить пользователя (ответом на сообщение)
        Использование: .unmute (ответом на сообщение)"""
        
        reply = await message.get_reply_message()
        if not reply:
            return await utils.answer(message, "🚫 Ответьте на сообщение пользователя, которого хотите размутить!")
        
        user_id = reply.sender_id
        chat_id = message.chat_id
        
        if user_id not in self.muted_users:
            return await utils.answer(message, self.strings("not_muted"))
        
        if self.muted_users[user_id].get("chat_id") != chat_id:
            return await utils.answer(message, "❌ Этот пользователь не замьючен в этом чате!")
        
        await self._unmute_user(user_id, chat_id)
        
        user_entity = await self.client.get_entity(user_id)
        await utils.answer(
            message,
            self.strings("unmuted").format(
                user=utils.escape_html(user_entity.first_name or str(user_id))
            )
        )
    
    @loader.command()
    async def mutelistcmd(self, message):
        """📋 Показать список замьюченных пользователей"""
        if not self.muted_users:
            return await utils.answer(message, self.strings("no_muted_users"))
        
        users_list = []
        current_time = datetime.datetime.now()
        chat_id = message.chat_id
        
        for user_id, data in list(self.muted_users.items()):
            if data.get("chat_id") != chat_id:
                continue
                
            try:
                user_entity = await self.client.get_entity(int(user_id))
                name = user_entity.first_name or str(user_id)
            except:
                name = f"User {user_id}"
            
            try:
                until = datetime.datetime.fromisoformat(data["until"])
                remaining = until - current_time
                if remaining.total_seconds() > 0:
                    time_left = self._format_time(remaining.total_seconds())
                    users_list.append(f"• {utils.escape_html(name)} - {time_left}")
                else:
                    users_list.append(f"• {utils.escape_html(name)} - ⏰ истекло (скоро будет размучен)")
                    # Автоматически размучиваем, если время истекло
                    await self._unmute_user(int(user_id), chat_id)
            except:
                pass
        
        if not users_list:
            return await utils.answer(message, self.strings("no_muted_users"))
        
        await utils.answer(
            message,
            self.strings("mute_list").format(users="\n".join(users_list))
        )
    
    def _parse_time(self, time_str: str):
        """Парсит время из строки (5m, 1h, 30s, 2d)"""
        if not time_str:
            return None
        
        time_str = time_str.lower().strip()
        
        # Если просто число - считаем минутами
        if time_str.isdigit():
            return int(time_str) * 60
        
        # Парсим с суффиксом
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
        seconds = int(seconds)
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}д")
        if hours > 0:
            parts.append(f"{hours}ч")
        if minutes > 0:
            parts.append(f"{minutes}м")
        if secs > 0 and not parts:
            parts.append(f"{secs}с")
        
        return " ".join(parts) if parts else "0м"
    
    def _schedule_unmute(self, user_id: int, until: datetime.datetime, chat_id: int):
        """Запускает таймер для размута"""
        async def unmute_task():
            try:
                now = datetime.datetime.now()
                if until > now:
                    await asyncio.sleep((until - now).total_seconds())
                    await self._unmute_user(user_id, chat_id)
            except Exception as e:
                pass
        
        task = asyncio.create_task(unmute_task())
        self._tasks.append(task)
    
    async def _unmute_user(self, user_id: int, chat_id: int):
        """Размучивает пользователя"""
        if user_id in self.muted_users:
            del self.muted_users[user_id]
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
        if self._handler:
            try:
                self.client.remove_event_handler(self._handler)
            except:
                pass
        
        for task in self._tasks:
            if not task.done():
                task.cancel()
