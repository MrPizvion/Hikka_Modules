from .. import loader, utils
import random
import logging

logger = logging.getLogger(__name__)

@loader.tds
class TumbochkaMod(loader.Module):
    """Фан-модуль Тумбочка (4 в 1)"""
    strings = {"name": "Tumbochka Fun"}

    async def tумбочкаcmd(self, message):
        """Просто тумбочка"""
        await utils.answer(message, "<b>🪑 Тумбочка</b>\n(самая обычная, без фото)")

    async def tумбаcmd(self, message):
        """Тумба (без фото)"""
        await utils.answer(message, "<b>🗄️ Тумба</b>\n(тоже без фото, просто тумба)")

    async def tумба_рандомcmd(self, message):
        """Тумба с рандомным фото"""
        photos = [
            "https://i.imgur.com/6W8xM6j.jpg",  # обычная тумба
            "https://i.imgur.com/3LZqX2b.jpg",  # деревянная тумба
            "https://i.imgur.com/K9ZkQrW.jpg",  # современная тумба
            "https://i.imgur.com/Q5p3cUf.jpg",  # тумба с ящиками
            "https://i.imgur.com/RtV4sMp.jpg",  # белая тумба
        ]
        photo = random.choice(photos)
        caption = "<b>📸 Рандомная тумба</b>\n(фото сгенерировано случайно)"
        await utils.answer(message, caption, photo=photo)

    async def tумба_18cmd(self, message):
        """Тумба 18+ (обычное тумбочка)"""
        await utils.answer(
            message,
            "<b>🔞 ТУМБА 18+</b>\n\n"
            "<i>Предупреждение: контент для взрослых</i>\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            "🪑 Обычное тумбочка\n"
            "🪑 Обычное тумбочка\n"
            "🪑 Обычное тумбочка\n"
            "▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
            "<b>Ничего лишнего, просто тумбочка</b>"
        )
