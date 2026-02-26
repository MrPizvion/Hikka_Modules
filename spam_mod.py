# meta developer: @user
# meta pic: none
# meta banner: none

from .. import loader, utils
from telethon.tl.types import Message
import asyncio
import logging

logger = logging.getLogger(__name__)

@loader.tds
class SpamMod(loader.Module):
    """💬 Модуль для отправки спам-сообщений"""

    strings = {
        "name": "Spammer",
        "no_args": "<b>❌ Укажи количество и текст!</b>\nПример: .sp 5 Привет",
        "invalid_count": "<b>❌ Количество должно быть числом от 1 до 100</b>",
        "spam_start": "<b>🔄 Начинаю спам {} сообщениями...</b>",
        "spam_done": "<b>✅ Спам завершен!</b>",
        "spam_cancelled": "<b>❌ Спам отменен</b>",
        "spam_stop": "<b>🛑 Спам остановлен</b>",
    }

    def __init__(self):
        self.spam_active = False

    @loader.command()
    async def spamcmd(self, message: Message):
        """Отправить несколько сообщений подряд
        Использование: .spam <количество> <текст>
        Пример: .spam 5 Привет всем!
        """
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_args"))
            return

        try:
            # Разбираем аргументы
            parts = args.split(maxsplit=1)
            if len(parts) != 2:
                await utils.answer(message, self.strings("no_args"))
                return

            count = int(parts[0])
            text = parts[1]

            # Проверка количества
            if count < 1 or count > 100:
                await utils.answer(message, self.strings("invalid_count"))
                return

            # Удаляем команду
            await message.delete()

            # Отправляем сообщение о начале
            status = await message.client.send_message(
                message.chat_id,
                self.strings("spam_start").format(count)
            )

            # Отправляем спам
            for i in range(count):
                await message.client.send_message(message.chat_id, f"{text} [{i+1}/{count}]")
                await asyncio.sleep(0.5)  # Задержка между сообщениями

            # Обновляем статус
            await status.edit(self.strings("spam_done"))

        except ValueError:
            await utils.answer(message, self.strings("invalid_count"))
        except Exception as e:
            logger.error(f"Spam error: {e}")
            await utils.answer(message, f"<b>❌ Ошибка:</b> {str(e)}")

    @loader.command()
    async def spcmd(self, message: Message):
        """Быстрый спам (сокращенная версия)
        Использование: .sp <количество> <текст>
        Пример: .sp 3 Быстрое сообщение
        """
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_args"))
            return

        try:
            parts = args.split(maxsplit=1)
            if len(parts) != 2:
                await utils.answer(message, self.strings("no_args"))
                return

            count = int(parts[0])
            text = parts[1]

            if count < 1 or count > 50:  # Для быстрого спама ограничение 50
                await utils.answer(message, "<b>❌ Количество должно быть от 1 до 50</b>")
                return

            await message.delete()

            for i in range(count):
                await message.client.send_message(message.chat_id, f"<code>{text}</code> [{i+1}]")
                await asyncio.sleep(0.3)

        except ValueError:
            await utils.answer(message, self.strings("invalid_count"))
        except Exception as e:
            logger.error(f"Fast spam error: {e}")

    @loader.command()
    async def sploopcmd(self, message: Message):
        """Бесконечный спам (остановка через .stopspam)
        Использование: .sploop <текст>
        Пример: .sploop Привет
        """
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<b>❌ Укажи текст для спама!</b>")
            return

        self.spam_active = True
        await message.delete()

        status = await message.client.send_message(
            message.chat_id,
            "<b>🔄 Бесконечный спам запущен!</b>\nОстановка: .stopspam"
        )

        count = 0
        try:
            while self.spam_active:
                count += 1
                await message.client.send_message(
                    message.chat_id,
                    f"<code>{args}</code> [{count}]"
                )
                await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Loop spam error: {e}")
        finally:
            await status.edit("<b>⏹ Спам остановлен</b>")

    @loader.command()
    async def stopspamcmd(self, message: Message):
        """Остановить бесконечный спам"""
        self.spam_active = False
        await utils.answer(message, self.strings("spam_stop"))

    @loader.command()
    async def spfastcmd(self, message: Message):
        """Очень быстрый спам (без задержки)
        Использование: .spfast <количество> <текст>
        Внимание: может вызвать флуд-контроль!
        """
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, self.strings("no_args"))
            return

        try:
            parts = args.split(maxsplit=1)
            if len(parts) != 2:
                await utils.answer(message, self.strings("no_args"))
                return

            count = int(parts[0])
            text = parts[1]

            if count < 1 or count > 20:  # Для быстрого спама ограничение 20
                await utils.answer(message, "<b>❌ Количество должно быть от 1 до 20</b>")
                return

            await message.delete()

            # Отправляем все сообщения сразу (очень быстро)
            tasks = []
            for i in range(count):
                tasks.append(message.client.send_message(
                    message.chat_id,
                    f"⚡ {text} [{i+1}]"
                ))
            
            await asyncio.gather(*tasks)

        except ValueError:
            await utils.answer(message, self.strings("invalid_count"))
        except Exception as e:
            logger.error(f"Fast spam error: {e}")

    @loader.command()
    async def sphelpcmd(self, message: Message):
        """Помощь по командам спама"""
        help_text = """
<b>📚 Команды спама:</b>

<b>.spam &lt;количество&gt; &lt;текст&gt;</b>
Обычный спам с задержкой 0.5 сек
Пример: .spam 5 Привет

<b>.sp &lt;количество&gt; &lt;текст&gt;</b>
Быстрый спам (сокращение)
Пример: .sp 3 Тест

<b>.sploop &lt;текст&gt;</b>
Бесконечный спам (остановка .stopspam)
Пример: .sploop Привет

<b>.spfast &lt;количество&gt; &lt;текст&gt;</b>
Очень быстрый спам (без задержки)
Пример: .spfast 5 Быстро

<b>.stopspam</b>
Остановить бесконечный спам

⚠️ <b>Внимание:</b>
- Не спамьте в чужих чатах
- Telegram может забанить за флуд
- Используйте осторожно
"""
        await utils.answer(message, help_text)
