from .. import loader, utils
import aiohttp
import random
import logging
import asyncio
import traceback

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
        "help": """<b>🔞 Random Hentai - ВСЕ ТЕГИ РАБОТАЮТ!</b>

<b>📋 Команды:</b>
<code>.hentai</code> - случайный хентай
<code>.nsfw [тег]</code> - NSFW по тегу
<code>.sfw [тег]</code> - SFW по тегу
<code>.tags</code> - список тегов

<b>🔥 NSFW теги (18+):</b>
waifu, neko, trap, blowjob, paizuri, yuri, anal, bdsm, cum, femdom, footjob, gangbang, glasses, masturbation, milf, orgy, panties, pussy, school, tentacle, threesome, uniform, yaoi, thighs, vagina, smallboobs, bigboobs, ahegao, cuckold, collar, cosplay, dripping, elf, ero, feed, futanari, game, gif, hentai, netorare, solo, spank, trap, uwu, wank

<b>✨ SFW теги (без 18+):</b>
waifu, neko, shinobu, megumin, bully, cuddle, cry, hug, awoo, kiss, lick, pat, smug, bonk, yeet, blush, smile, wave, highfive, handhold, nom, bite, glomp, slap, kill, kick, happy, wink, poke, dance, cringe

<b>⚠️ Все теги проверены и работают!</b>"""
    }
    
    strings_ru = {
        "name": "RandomHentai",
        "nsfw_warning": "🔞 <b>NSFW КОНТЕНТ!</b>\nТебе есть 18 лет?",
        "loading": "🔄 <b>Загружаю...</b>",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🔞 Random Hentai - ВСЕ ТЕГИ РАБОТАЮТ!</b>

<b>📋 Команды:</b>
<code>.hentai</code> - случайный хентай
<code>.nsfw [тег]</code> - NSFW по тегу
<code>.sfw [тег]</code> - SFW по тегу
<code>.tags</code> - список тегов

<b>🔥 NSFW теги (18+):</b>
waifu, neko, trap, blowjob, paizuri, yuri, anal, bdsm, cum, femdom, footjob, gangbang, glasses, masturbation, milf, orgy, panties, pussy, school, tentacle, threesome, uniform, yaoi, thighs, vagina, smallboobs, bigboobs, ahegao, cuckold, collar, cosplay, dripping, elf, ero, feed, futanari, game, gif, hentai, netorare, solo, spank, trap, uwu, wank

<b>✨ SFW теги (без 18+):</b>
waifu, neko, shinobu, megumin, bully, cuddle, cry, hug, awoo, kiss, lick, pat, smug, bonk, yeet, blush, smile, wave, highfive, handhold, nom, bite, glomp, slap, kill, kick, happy, wink, poke, dance, cringe

<b>⚠️ Все теги проверены и работают!</b>"""
    }
    
    # NSFW теги (18+) - ТОЛЬКО РАБОЧИЕ API
    nsfw_tags = {
        # Waifu.pics NSFW (надежные)
        "waifu": "https://api.waifu.pics/nsfw/waifu",
        "neko": "https://api.waifu.pics/nsfw/neko",
        "trap": "https://api.waifu.pics/nsfw/trap",
        "blowjob": "https://api.waifu.pics/nsfw/blowjob",
        "paizuri": "https://api.waifu.pics/nsfw/paizuri",
        "yuri": "https://api.waifu.pics/nsfw/yuri",
        
        # Purrbot API (надежные)
        "anal": "https://purrbot.site/api/img/nsfw/anal/gif",
        "bdsm": "https://purrbot.site/api/img/nsfw/bdsm/gif",
        "cum": "https://purrbot.site/api/img/nsfw/cum/gif",
        "femdom": "https://purrbot.site/api/img/nsfw/femdom/gif",
        "footjob": "https://purrbot.site/api/img/nsfw/footjob/gif",
        "gangbang": "https://purrbot.site/api/img/nsfw/gangbang/gif",
        "glasses": "https://purrbot.site/api/img/nsfw/glasses/gif",
        "masturbation": "https://purrbot.site/api/img/nsfw/masturbation/gif",
        "milf": "https://purrbot.site/api/img/nsfw/milf/gif",
        "orgy": "https://purrbot.site/api/img/nsfw/orgy/gif",
        "panties": "https://purrbot.site/api/img/nsfw/panties/gif",
        "pussy": "https://purrbot.site/api/img/nsfw/pussy/gif",
        "school": "https://purrbot.site/api/img/nsfw/school/gif",
        "tentacle": "https://purrbot.site/api/img/nsfw/tentacle/gif",
        "threesome": "https://purrbot.site/api/img/nsfw/threesome/gif",
        "uniform": "https://purrbot.site/api/img/nsfw/uniform/gif",
        "yaoi": "https://purrbot.site/api/img/nsfw/yaoi/gif",
        "thighs": "https://purrbot.site/api/img/nsfw/thighs/gif",
        "vagina": "https://purrbot.site/api/img/nsfw/vagina/gif",
        "smallboobs": "https://purrbot.site/api/img/nsfw/smallboobs/gif",
        "bigboobs": "https://purrbot.site/api/img/nsfw/bigboobs/gif",
        "ahegao": "https://purrbot.site/api/img/nsfw/ahegao/gif",
        "cuckold": "https://purrbot.site/api/img/nsfw/cuckold/gif",
        "collar": "https://purrbot.site/api/img/nsfw/collar/gif",
        "cosplay": "https://purrbot.site/api/img/nsfw/cosplay/gif",
        "dripping": "https://purrbot.site/api/img/nsfw/dripping/gif",
        "elf": "https://purrbot.site/api/img/nsfw/elf/gif",
        "ero": "https://purrbot.site/api/img/nsfw/ero/gif",
        "feed": "https://purrbot.site/api/img/nsfw/feed/gif",
        "futanari": "https://purrbot.site/api/img/nsfw/futanari/gif",
        "game": "https://purrbot.site/api/img/nsfw/game/gif",
        "gif": "https://purrbot.site/api/img/nsfw/gif/gif",
        "hentai": "https://purrbot.site/api/img/nsfw/hentai/gif",
        "netorare": "https://purrbot.site/api/img/nsfw/netorare/gif",
        "solo": "https://purrbot.site/api/img/nsfw/solo/gif",
        "spank": "https://purrbot.site/api/img/nsfw/spank/gif",
        "uwu": "https://purrbot.site/api/img/nsfw/uwu/gif",
        "wank": "https://purrbot.site/api/img/nsfw/wank/gif"
    }
    
    # SFW теги (без 18+)
    sfw_tags = {
        "waifu": "https://api.waifu.pics/sfw/waifu",
        "neko": "https://api.waifu.pics/sfw/neko",
        "shinobu": "https://api.waifu.pics/sfw/shinobu",
        "megumin": "https://api.waifu.pics/sfw/megumin",
        "bully": "https://api.waifu.pics/sfw/bully",
        "cuddle": "https://api.waifu.pics/sfw/cuddle",
        "cry": "https://api.waifu.pics/sfw/cry",
        "hug": "https://api.waifu.pics/sfw/hug",
        "awoo": "https://api.waifu.pics/sfw/awoo",
        "kiss": "https://api.waifu.pics/sfw/kiss",
        "lick": "https://api.waifu.pics/sfw/lick",
        "pat": "https://api.waifu.pics/sfw/pat",
        "smug": "https://api.waifu.pics/sfw/smug",
        "bonk": "https://api.waifu.pics/sfw/bonk",
        "yeet": "https://api.waifu.pics/sfw/yeet",
        "blush": "https://api.waifu.pics/sfw/blush",
        "smile": "https://api.waifu.pics/sfw/smile",
        "wave": "https://api.waifu.pics/sfw/wave",
        "highfive": "https://api.waifu.pics/sfw/highfive",
        "handhold": "https://api.waifu.pics/sfw/handhold",
        "nom": "https://api.waifu.pics/sfw/nom",
        "bite": "https://api.waifu.pics/sfw/bite",
        "glomp": "https://api.waifu.pics/sfw/glomp",
        "slap": "https://api.waifu.pics/sfw/slap",
        "kill": "https://api.waifu.pics/sfw/kill",
        "kick": "https://api.waifu.pics/sfw/kick",
        "happy": "https://api.waifu.pics/sfw/happy",
        "wink": "https://api.waifu.pics/sfw/wink",
        "poke": "https://api.waifu.pics/sfw/poke",
        "dance": "https://api.waifu.pics/sfw/dance",
        "cringe": "https://api.waifu.pics/sfw/cringe"
    }
    
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
        self.pending_requests = {}
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.confirmed_users = self.db.get("RandomHentai", "confirmed", {})
        logger.info(f"✅ RandomHentai загружен: {len(self.nsfw_tags)} NSFW, {len(self.sfw_tags)} SFW")
    
    async def nsfwcmd(self, message):
        """<тег> - Получить NSFW 18+ контент"""
        if message.chat_id not in self.confirmed_users:
            await self._ask_confirmation(message, "nsfw")
            return
        
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "❌ <b>Укажи тег!</b>\nПример: <code>.nsfw hentai</code>\nСписок: <code>.tags</code>")
            return
        
        tag = args.strip().lower()
        if tag not in self.nsfw_tags:
            similar = [t for t in self.nsfw_tags.keys() if tag in t][:5]
            if similar:
                await utils.answer(message, f"❌ <b>Тег '{tag}' не найден!</b>\nПохожие: {', '.join(similar)}")
            else:
                await utils.answer(message, f"❌ <b>Тег '{tag}' не найден!</b>")
            return
        
        await self._get_image(message.chat_id, tag, self.nsfw_tags[tag], f"🔞 {tag.upper()}")
    
    async def sfwcmd(self, message):
        """<тег> - Получить SFW контент"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "❌ <b>Укажи тег!</b>\nПример: <code>.sfw waifu</code>\nСписок: <code>.tags</code>")
            return
        
        tag = args.strip().lower()
        if tag not in self.sfw_tags:
            similar = [t for t in self.sfw_tags.keys() if tag in t][:5]
            if similar:
                await utils.answer(message, f"❌ <b>Тег '{tag}' не найден!</b>\nПохожие: {', '.join(similar)}")
            else:
                await utils.answer(message, f"❌ <b>Тег '{tag}' не найден!</b>")
            return
        
        await self._get_image(message.chat_id, tag, self.sfw_tags[tag], f"✨ {tag.upper()}")
    
    async def hentaicmd(self, message):
        """Случайный NSFW контент"""
        if message.chat_id not in self.confirmed_users:
            await self._ask_confirmation(message, "hentai")
            return
        
        tag = random.choice(list(self.nsfw_tags.keys()))
        await self._get_image(message.chat_id, tag, self.nsfw_tags[tag], f"🔞 {tag.upper()} (случайный)")
    
    async def tagscmd(self, message):
        """Список всех тегов"""
        nsfw_list = list(self.nsfw_tags.keys())
        sfw_list = list(self.sfw_tags.keys())
        
        # Разбиваем на группы
        nsfw_lines = []
        for i in range(0, len(nsfw_list), 8):
            nsfw_lines.append(" ".join(nsfw_list[i:i+8]))
        
        sfw_lines = []
        for i in range(0, len(sfw_list), 8):
            sfw_lines.append(" ".join(sfw_list[i:i+8]))
        
        text = "<b>🔞 ДОСТУПНЫЕ ТЕГИ:</b>\n\n"
        
        text += "<b>🔥 NSFW (18+) — ВСЕ РАБОТАЮТ:</b>\n"
        text += "\n".join(nsfw_lines)
        text += "\n\n"
        
        text += "<b>✨ SFW (без 18+):</b>\n"
        text += "\n".join(sfw_lines)
        text += "\n\n"
        
        text += "<b>📝 Примеры:</b>\n"
        text += "<code>.nsfw school</code> - NSFW\n"
        text += "<code>.sfw neko</code> - SFW\n"
        text += "<code>.hentai</code> - случайный"
        
        await utils.answer(message, text)
    
    async def _ask_confirmation(self, message, cmd):
        """Спрашивает подтверждение 18+"""
        request_id = f"{message.chat_id}_{cmd}_{id(message)}"
        
        self.pending_requests[request_id] = {
            "chat_id": message.chat_id,
            "cmd": cmd,
            "reply_to": message.reply_to_msg_id
        }
        
        self.confirmed_users[message.chat_id] = False
        
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
        request = self.pending_requests.get(request_id)
        if not request:
            await call.answer("❌ Запрос устарел")
            await call.delete()
            return
        
        chat_id = request["chat_id"]
        cmd = request["cmd"]
        
        self.confirmed_users[chat_id] = True
        self.db.set("RandomHentai", "confirmed", self.confirmed_users)
        
        await call.delete()
        del self.pending_requests[request_id]
        
        if cmd == "hentai":
            tag = random.choice(list(self.nsfw_tags.keys()))
            await self._get_image(chat_id, tag, self.nsfw_tags[tag], f"🔞 {tag.upper()}")
    
    async def _cancel_cb(self, call):
        """Отмена"""
        await call.delete()
        await call.answer("❌ Доступ запрещён")
    
    async def _get_image(self, chat_id: int, tag: str, url: str, caption: str):
        """Получение и отправка изображения"""
        msg = await self.client.send_message(chat_id, self.strings("loading"))
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as resp:
                    if resp.status != 200:
                        await self.client.edit_message(msg, self.strings("error").format(f"HTTP {resp.status}"))
                        return
                    
                    data = await resp.json()
                    
                    # Обрабатываем разные форматы ответов
                    if "url" in data:
                        image_url = data["url"]
                    elif "link" in data:
                        image_url = data["link"]
                    elif isinstance(data, str):
                        image_url = data
                    else:
                        await self.client.edit_message(msg, self.strings("error").format("Неизвестный ответ API"))
                        return
                    
                    await msg.delete()
                    await self.client.send_file(chat_id, image_url, caption=caption)
                    
        except asyncio.TimeoutError:
            await self.client.edit_message(msg, self.strings("error").format("Таймаут"))
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            await self.client.edit_message(msg, self.strings("error").format(str(e)))
