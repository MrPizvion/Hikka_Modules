from .. import loader, utils
import random
import logging

logger = logging.getLogger(__name__)

@loader.tds
class TumbochkaMod(loader.Module):
    """Фан-модуль Тумбочка (4 в 1) с русскими командами"""
    strings = {"name": "Tumbochka Fun"}

    @loader.command(ru_doc="Просто тумбочка")
    async def тумбочкаcmd(self, message):
        """Просто тумбочка"""
        await utils.answer(message, "<b>🪑 Тумбочка</b>\n(самая обычная, без фото)")

    @loader.command(ru_doc="Тумба (без фото)")
    async def тумбаcmd(self, message):
        """Тумба (без фото)"""
        await utils.answer(message, "<b>🗄️ Тумба</b>\n(тоже без фото, просто тумба)")

    @loader.command(ru_doc="Тумба с рандомным фото")
    async def тумба_рандомcmd(self, message):
        """Тумба с рандомным фото"""
        photos = [
            "https://i.imgur.com/6W8xM6j.jpg",
            "https://i.imgur.com/3LZqX2b.jpg",
            "https://i.imgur.com/K9ZkQrW.jpg",
            "https://i.imgur.com/Q5p3cUf.jpg",
            "https://i.imgur.com/RtV4sMp.jpg",
        ]
        photo = random.choice(photos)
        caption = "<b>📸 Рандомная тумба</b>\n(фото сгенерировано случайно)"
        await utils.answer(message, caption, photo=photo)

    @loader.command(ru_doc="Тумба 18+ (обычное тумбочка)")
    async def тумба_18cmd(self, message):
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
