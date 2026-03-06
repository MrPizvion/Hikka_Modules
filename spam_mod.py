# meta developer: @yourusername
# meta pic: none
# meta banner: none

from .. import loader, utils
import asyncio
import logging

logger = logging.getLogger(__name__)

@loader.tds
class SpamMod(loader.Module):
    """Модуль для спама сообщениями"""
    strings = {
        "name": "Spammer",
        "no_args": "🚫 <b>Укажи количество и текст для спама!</b>",
        "invalid_count": "🚫 <b>Количество должно быть от 1 до 100!</b>",
        "spam_start": "✅ <b>Спам запущен!</b>\nКоличество: {}",
        "spam_done": "✅ <b>Спам завершен!</b>",
        "spam_cancelled": "❌ <b>Спам отменен!</b>",
        "usage": "❌ <b>Использование:</b> <code>.sp [количество] [текст]</code>",
    }

    def __init__(self):
        self.spam_active = False

    async def spcmd(self, message):
        """<количество от 1 до 100> <текст> - Запустить спам"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, self.strings("usage"))
            return
            
        try:
            count = int(args.split()[0])
            text = " ".join(args.split()[1:])
        except (ValueError, IndexError):
            await utils.answer(message, self.strings("no_args"))
            return
            
        if count < 1 or count > 100:
            await utils.answer(message, self.strings("invalid_count"))
            return
            
        if not text:
            await utils.answer(message, self.strings("no_args"))
            return
            
        self.spam_active = True
        await utils.answer(message, self.strings("spam_start").format(count))
        
        try:
            for i in range(count):
                if not self.spam_active:
                    break
                await message.client.send_message(message.chat_id, text)
                await asyncio.sleep(0.5)  # Задержка между сообщениями
                
            if self.spam_active:
                await utils.answer(message, self.strings("spam_done"))
                
        except Exception as e:
            logger.error(f"Ошибка при спаме: {e}")
            await utils.answer(message, f"❌ <b>Ошибка:</b> {e}")
            
    async def stopcmd(self, message):
        """Остановить текущий спам"""
        if self.spam_active:
            self.spam_active = False
            await utils.answer(message, self.strings("spam_cancelled"))
        else:
            await utils.answer(message, "🚫 <b>Нет активного спама</b>")
