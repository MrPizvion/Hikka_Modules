# meta developer: @Edu_kak_xochu
# meta pic: https://img.icons8.com/color/48/000000/poll.png
# meta banner: https://via.placeholder.com/300x100.png?text=Poll+Creator

import asyncio
from telethon.tl.types import Message

from .. import loader, utils

@loader.tds
class PollCreatorMod(loader.Module):
    """Создание опросов с таймером"""
    
    strings = {
        "name": "PollCreator",
        "no_chats": "⚠️ <b>Чат развлечений не создан!</b>\n\nСоздайте командой <code>.createchats</code>",
        "poll_created": "✅ <b>Опрос создан и отправлен!</b>",
        "poll_question": "📊 <b>Создание опроса:</b>\n\nВведите: <code>вопрос | вариант1 | вариант2 | ... | таймер_в_секундах</code>",
        "invalid_poll": "⚠️ <b>Нужно минимум 2 варианта ответа!</b>",
    }
    
    strings_ru = {
        "no_chats": "⚠️ <b>Чат развлечений не создан!</b>\n\nСоздайте командой <code>.createchats</code>",
        "poll_created": "✅ <b>Опрос создан и отправлен!</b>",
        "poll_question": "📊 <b>Создание опроса:</b>\n\nВведите: <code>вопрос | вариант1 | вариант2 | ... | таймер_в_секундах</code>",
        "invalid_poll": "⚠️ <b>Нужно минимум 2 варианта ответа!</b>",
    }

    async def pollcmd(self, message: Message):
        """Создать опрос: .poll вопрос | вариант1 | вариант2 | ... | таймер"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("poll_question"))
            return
        
        parts = [p.strip() for p in args.split("|")]
        
        if len(parts) < 3:
            await utils.answer(message, self.strings("invalid_poll"))
            return
        
        # Проверяем, есть ли таймер
        timer = None
        if parts[-1].isdigit():
            timer = int(parts[-1])
            parts = parts[:-1]
        
        question = parts[0]
        options = parts[1:]
        
        if len(options) < 2:
            await utils.answer(message, self.strings("invalid_poll"))
            return
        
        # Создаем текст опроса
        poll_text = f"📊 <b>{question}</b>\n\n"
        for i, option in enumerate(options, 1):
            poll_text += f"{i}. {option}\n"
        
        if timer:
            poll_text += f"\n⏱ <b>Таймер: {timer} секунд</b>"
        
        # Отправляем в чат развлечений
        chat_manager = self.lookup("ChatManagerMod")
        if chat_manager and chat_manager.chats_created:
            try:
                chat_id = int(chat_manager.config["entertainment_chat_id"])
                await self.client.send_message(chat_id, poll_text)
                await utils.answer(message, self.strings("poll_created"))
            except Exception as e:
                await utils.answer(message, f"❌ <b>Ошибка:</b> {e}")
        else:
            await utils.answer(message, self.strings("no_chats"))
