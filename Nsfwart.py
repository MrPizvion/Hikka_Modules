from .. import loader, utils
import aiohttp
import random
import logging
import asyncio

logger = logging.getLogger(__name__)

# requires: aiohttp

@loader.tds
class RandomHentaiMod(loader.Module):
    """Модуль случайных NSFW артов 🔞"""
    
    strings = {
        "name": "RandomHentai",
        "nsfw_warning": "🔞 <b>NSFW КОНТЕНТ!</b>\nТебе есть 18 лет?",
        "loading": "🔄 <b>Загружаю...</b>",
        "error": "💥 <b>Ошибка:</b> {}",
        "no_api": "❌ <b>API ключ не указан!</b>\nПолучи на: https://nekobot.xyz/api",
        "help": """<b>🔞 Random Hentai</b>

<b>📋 Команды:</b>
<code>.hentai</code> - случайный хентай
<code>.neko</code> - случайная neko
<code>.kemono</code> - случайный kemonomimi
<code>.holo</code> - случайный Holo
<code>.nsfw [тег]</code> - NSFW по тегу

<b>📋 Теги для .nsfw:</b>
anal, ass, bdsm, blowjob, boobs, cum, creampie, double, femdom, footjob, gangbang, glasses, hentai, keta, kiss, loli, maid, masturbation, milf, orgy, pantsu, pussy, school, tentacle, threesome, uniform, yaoi, yuri, tattoo, thighs, vagina, smallboobs, bigboobs, ahegao, cuckold, collar, cosplay, dripping, elf, erofeet, ero, feed, futanari, game, gif, gifs, hentaigif, neko, neko_gif, nekotits, netorare, pussy_wank_gif, solo, solo_gif, spank, syuri, trap, uwu, wank, zbk

<b>⚠️ Требуется подтверждение 18+</b>"""
    }
    
    strings_ru = {
        "name": "RandomHentai",
        "nsfw_warning": "🔞 <b>NSFW КОНТЕНТ!</b>\nТебе есть 18 лет?",
        "loading": "🔄 <b>Загружаю...</b>",
        "error": "💥 <b>Ошибка:</b> {}",
        "no_api": "❌ <b>API ключ не указан!</b>\nПолучи на: https://nekobot.xyz/api",
        "help": """<b>🔞 Random Hentai</b>

<b>📋 Команды:</b>
<code>.hentai</code> - случайный хентай
<code>.neko</code> - случайная neko
<code>.kemono</code> - случайный kemonomimi
<code>.holo</code> - случайный Holo
<code>.nsfw [тег]</code> - NSFW по тегу

<b>📋 Теги для .nsfw:</b>
anal, ass, bdsm, blowjob, boobs, cum, creampie, double, femdom, footjob, gangbang, glasses, hentai, keta, kiss, loli, maid, masturbation, milf, orgy, pantsu, pussy, school, tentacle, threesome, uniform, yaoi, yuri, tattoo, thighs, vagina, smallboobs, bigboobs, ahegao, cuckold, collar, cosplay, dripping, elf, erofeet, ero, feed, futanari, game, gif, gifs, hentaigif, neko, neko_gif, nekotits, netorare, pussy_wank_gif, solo, solo_gif, spank, syuri, trap, uwu, wank, zbk

<b>⚠️ Требуется подтверждение 18+</b>"""
    }
    
    # Список доступных эндпоинтов
    endpoints = {
        "hentai": "https://nekobot.xyz/api/image?type=hentai",
        "neko": "https://nekobot.xyz/api/image?type=neko",
        "kemono": "https://nekobot.xyz/api/image?type=kemonomimi",
        "holo": "https://nekobot.xyz/api/image?type=holo",
        "anal": "https://nekobot.xyz/api/image?type=anal",
        "ass": "https://nekobot.xyz/api/image?type=ass",
        "bdsm": "https://nekobot.xyz/api/image?type=bdsm",
        "blowjob": "https://nekobot.xyz/api/image?type=blowjob",
        "boobs": "https://nekobot.xyz/api/image?type=boobs",
        "cum": "https://nekobot.xyz/api/image?type=cum",
        "creampie": "https://nekobot.xyz/api/image?type=creampie",
        "double": "https://nekobot.xyz/api/image?type=double",
        "femdom": "https://nekobot.xyz/api/image?type=femdom",
        "footjob": "https://nekobot.xyz/api/image?type=footjob",
        "gangbang": "https://nekobot.xyz/api/image?type=gangbang",
        "glasses": "https://nekobot.xyz/api/image?type=glasses",
        "hentai": "https://nekobot.xyz/api/image?type=hentai",
        "keta": "https://nekobot.xyz/api/image?type=keta",
        "kiss": "https://nekobot.xyz/api/image?type=kiss",
        "loli": "https://nekobot.xyz/api/image?type=loli",
        "maid": "https://nekobot.xyz/api/image?type=maid",
        "masturbation": "https://nekobot.xyz/api/image?type=masturbation",
        "milf": "https://nekobot.xyz/api/image?type=milf",
        "orgy": "https://nekobot.xyz/api/image?type=orgy",
        "pantsu": "https://nekobot.xyz/api/image?type=pantsu",
        "pussy": "https://nekobot.xyz/api/image?type=pussy",
        "school": "https://nekobot.xyz/api/image?type=school",
        "tentacle": "https://nekobot.xyz/api/image?type=tentacle",
        "threesome": "https://nekobot.xyz/api/image?type=threesome",
        "uniform": "https://nekobot.xyz/api/image?type=uniform",
        "yaoi": "https://nekobot.xyz/api/image?type=yaoi",
        "yuri": "https://nekobot.xyz/api/image?type=yuri",
        "tattoo": "https://nekobot.xyz/api/image?type=tattoo",
        "thighs": "https://nekobot.xyz/api/image?type=thighs",
        "vagina": "https://nekobot.xyz/api/image?type=vagina",
        "smallboobs": "https://nekobot.xyz/api/image?type=smallboobs",
        "bigboobs": "https://nekobot.xyz/api/image?type=bigboobs",
        "ahegao": "https://nekobot.xyz/api/image?type=ahegao",
        "cuckold": "https://nekobot.xyz/api/image?type=cuckold",
        "collar": "https://nekobot.xyz/api/image?type=collar",
        "cosplay": "https://nekobot.xyz/api/image?type=cosplay",
        "dripping": "https://nekobot.xyz/api/image?type=dripping",
        "elf": "https://nekobot.xyz/api/image?type=elf",
        "erofeet": "https://nekobot.xyz/api/image?type=erofeet",
        "ero": "https://nekobot.xyz/api/image?type=ero",
        "feed": "https://nekobot.xyz/api/image?type=feed",
        "futanari": "https://nekobot.xyz/api/image?type=futanari",
        "game": "https://nekobot.xyz/api/image?type=game",
        "gif": "https://nekobot.xyz/api/image?type=gif",
        "gifs": "https://nekobot.xyz/api/image?type=gifs",
        "hentaigif": "https://nekobot.xyz/api/image?type=hentaigif",
        "neko": "https://nekobot.xyz/api/image?type=neko",
        "neko_gif": "https://nekobot.xyz/api/image?type=neko_gif",
        "nekotits": "https://nekobot.xyz/api/image?type=nekotits",
        "netorare": "https://nekobot.xyz/api/image?type=netorare",
        "pussy_wank_gif": "https://nekobot.xyz/api/image?type=pussy_wank_gif",
        "solo": "https://nekobot.xyz/api/image?type=solo",
        "solo_gif": "https://nekobot.xyz/api/image?type=solo_gif",
        "spank": "https://nekobot.xyz/api/image?type=spank",
        "syuri": "https://nekobot.xyz/api/image?type=syuri",
        "trap": "https://nekobot.xyz/api/image?type=trap",
        "uwu": "https://nekobot.xyz/api/image?type=uwu",
        "wank": "https://nekobot.xyz/api/image?type=wank",
        "zbk": "https://nekobot.xyz/api/image?type=zbk"
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "api_key",
                None,
                "🔑 API ключ NekoBot (необязательно)",
                validator=loader.validators.String()
            ),
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
        self.confirmed_users = self.db.get("RandomHentai", "confirmed", {})
    
    async def nsfwcmd(self, message):
        """.nsfw [тег] - Получить NSFW по тегу"""
        if not self.config["confirm_18"] and message.chat_id not in self.confirmed_users:
            await self._ask_confirmation(message, "nsfw", None)
            return
        
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "❌ <b>Укажи тег!</b>\nПример: <code>.nsfw boobs</code>")
            return
        
        tag = args.strip().lower()
        if tag not in self.endpoints:
            # Показываем похожие теги
            similar = [t for t in self.endpoints.keys() if tag in t][:5]
            if similar:
                await utils.answer(message, f"❌ <b>Тег '{tag}' не найден!</b>\nПохожие: {', '.join(similar)}")
            else:
                await utils.answer(message, f"❌ <b>Тег '{tag}' не найден!</b>\nСписок тегов: <code>.nsfwhelp</code>")
            return
        
        await self._get_nsfw(message, tag)
    
    async def hentaicmd(self, message):
        """Случайный хентай"""
        if not self.config["confirm_18"] and message.chat_id not in self.confirmed_users:
            await self._ask_confirmation(message, "hentai", None)
            return
        await self._get_nsfw(message, "hentai")
    
    async def nekocmd(self, message):
        """Случайная neko"""
        if not self.config["confirm_18"] and message.chat_id not in self.confirmed_users:
            await self._ask_confirmation(message, "neko", None)
            return
        await self._get_nsfw(message, "neko")
    
    async def kemonocmd(self, message):
        """Случайный kemonomimi"""
        if not self.config["confirm_18"] and message.chat_id not in self.confirmed_users:
            await self._ask_confirmation(message, "kemono", None)
            return
        await self._get_nsfw(message, "kemonomimi")
    
    async def holocmd(self, message):
        """Случайный Holo"""
        if not self.config["confirm_18"] and message.chat_id not in self.confirmed_users:
            await self._ask_confirmation(message, "holo", None)
            return
        await self._get_nsfw(message, "holo")
    
    async def nsfwhelpcmd(self, message):
        """Список всех тегов"""
        tags = list(self.endpoints.keys())
        # Разбиваем на группы
        lines = []
        for i in range(0, len(tags), 10):
            lines.append(", ".join(tags[i:i+10]))
        
        text = "<b>🔞 Доступные теги:</b>\n\n"
        text += "\n".join(lines)
        text += "\n\n<b>Пример:</b> <code>.nsfw boobs</code>"
        
        await utils.answer(message, text)
    
    async def _ask_confirmation(self, message, cmd, tag):
        """Спрашивает подтверждение 18+"""
        self.confirmed_users[message.chat_id] = False
        
        await self.inline.form(
            text=self.strings("nsfw_warning"),
            message=message,
            reply_markup=[
                [
                    {"text": "✅ Да, мне есть 18", "callback": self._confirm_cb, "args": (cmd, tag)},
                    {"text": "❌ Нет", "callback": self._cancel_cb}
                ]
            ]
        )
    
    async def _confirm_cb(self, call, cmd, tag):
        """Подтверждение 18+"""
        self.confirmed_users[call.chat_id] = True
        self.db.set("RandomHentai", "confirmed", self.confirmed_users)
        
        await call.delete()
        
        if cmd == "nsfw":
            await self._get_nsfw(call, tag)
        else:
            await self._get_nsfw(call, cmd)
    
    async def _cancel_cb(self, call):
        """Отмена"""
        await call.delete()
        await call.answer("❌ Доступ запрещён")
    
    async def _get_nsfw(self, message, tag: str):
        """Получение NSFW контента"""
        msg = await utils.answer(message, self.strings("loading"))
        
        try:
            url = self.endpoints.get(tag, self.endpoints["hentai"])
            
            # Добавляем API ключ если есть
            if self.config["api_key"]:
                url += f"&key={self.config['api_key']}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    if resp.status != 200:
                        await utils.answer(msg, self.strings("error").format(f"HTTP {resp.status}"))
                        return
                    
                    data = await resp.json()
                    
                    if not data.get("success"):
                        await utils.answer(msg, self.strings("error").format("API вернул ошибку"))
                        return
                    
                    image_url = data.get("message")
                    if not image_url:
                        await utils.answer(msg, self.strings("error").format("Нет URL"))
                        return
                    
                    # Отправляем картинку
                    await self.client.send_file(
                        message.chat_id if hasattr(message, 'chat_id') else message.chat.id,
                        image_url,
                        reply_to=message.reply_to_msg_id if hasattr(message, 'reply_to_msg_id') else None,
                        caption=f"🔞 <b>{tag.upper()}</b>"
                    )
                    
                    await msg.delete()
            
        except asyncio.TimeoutError:
            await utils.answer(msg, self.strings("error").format("Таймаут"))
        except Exception as e:
            logger.exception(f"NSFW error: {e}")
            await utils.answer(msg, self.strings("error").format(str(e)))
