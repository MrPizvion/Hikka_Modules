from .. import loader, utils
import aiohttp
import random
import logging
import asyncio

logger = logging.getLogger(__name__)

# requires: aiohttp

@loader.tds
class NSFWArtMod(loader.Module):
    """Простой NSFW модуль с рабочим API 🔞"""
    
    strings = {
        "name": "NSFWArt",
        "nsfw_warning": "🔞 <b>NSFW КОНТЕНТ!</b>\nТебе есть 18 лет?",
        "loading": "🔄 <b>Загружаю...</b>",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🔞 NSFWArt - ПРОСТОЙ И РАБОЧИЙ</b>

<b>📋 Команды:</b>
<code>.nsfw</code> - случайный NSFW
<code>.hentai</code> - то же самое
<code>.pics</code> - ещё один случайный

<b>⚠️ Без выбора тегов, только случайные изображения</b>
<b>✅ Использует 3 надёжных API</b>"""
    }
    
    strings_ru = {
        "name": "NSFWArt",
        "nsfw_warning": "🔞 <b>NSFW КОНТЕНТ!</b>\nТебе есть 18 лет?",
        "loading": "🔄 <b>Загружаю...</b>",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🔞 NSFWArt - ПРОСТОЙ И РАБОЧИЙ</b>

<b>📋 Команды:</b>
<code>.nsfw</code> - случайный NSFW
<code>.hentai</code> - то же самое
<code>.pics</code> - ещё один случайный

<b>⚠️ Без выбора тегов, только случайные изображения</b>
<b>✅ Использует 3 надёжных API</b>"""
    }
    
    # Три простых API которые работают 100%
    apis = [
        "https://api.waifu.pics/nsfw/waifu",
        "https://api.waifu.pics/nsfw/neko",
        "https://api.waifu.pics/nsfw/trap",
        "https://api.waifu.pics/nsfw/blowjob",
        "https://nekobot.xyz/api/image?type=hentai",
        "https://nekobot.xyz/api/image?type=neko",
        "https://nekobot.xyz/api/image?type=holo"
    ]
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "confirm_18",
                False,
                "🔞 Подтверждение 18+",
                validator=loader.validators.Boolean()
            )
        )
        self.confirmed_users = {}
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.confirmed_users = self.db.get("NSFWArt", "confirmed", {})
    
    async def nsfwcmd(self, message):
        """Случайный NSFW контент"""
        if message.chat_id not in self.confirmed_users:
            await self._ask_confirmation(message)
            return
        
        await self._send_random(message)
    
    async def hentaicmd(self, message):
        """Случайный NSFW контент"""
        if message.chat_id not in self.confirmed_users:
            await self._ask_confirmation(message)
            return
        
        await self._send_random(message)
    
    async def picscmd(self, message):
        """Случайный NSFW контент"""
        if message.chat_id not in self.confirmed_users:
            await self._ask_confirmation(message)
            return
        
        await self._send_random(message)
    
    async def _ask_confirmation(self, message):
        """Спрашивает подтверждение 18+"""
        request_id = f"{message.chat_id}_{id(message)}"
        
        await self.inline.form(
            text=self.strings("nsfw_warning"),
            message=message,
            reply_markup=[
                [
                    {"text": "✅ Да, мне есть 18", "callback": self._confirm_cb, "args": (request_id,)},
                    {"text": "❌ Нет", "callback": self._cancel_cb}
                ]
            ]
        )
    
    async def _confirm_cb(self, call, request_id):
        """Подтверждение 18+"""
        self.confirmed_users[call.chat.id] = True
        self.db.set("NSFWArt", "confirmed", self.confirmed_users)
        
        await call.delete()
        await call.answer("✅ Доступ разрешён")
    
    async def _cancel_cb(self, call):
        """Отмена"""
        await call.delete()
        await call.answer("❌ Доступ запрещён")
    
    async def _send_random(self, message):
        """Отправляет случайное NSFW изображение"""
        msg = await utils.answer(message, self.strings("loading"))
        
        # Пробуем разные API пока не получится
        random.shuffle(self.apis)
        
        for api_url in self.apis:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url, timeout=10) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            
                            # Разные API возвращают по-разному
                            if "url" in data:
                                image_url = data["url"]
                            elif "message" in data:
                                image_url = data["message"]
                            else:
                                continue
                            
                            await msg.delete()
                            await self.client.send_file(
                                message.chat_id,
                                image_url,
                                reply_to=message.reply_to_msg_id,
                                caption="🔞 <b>NSFW</b>"
                            )
                            return
                            
            except:
                continue
        
        await utils.answer(msg, self.strings("error").format("Все API временно недоступны"))
