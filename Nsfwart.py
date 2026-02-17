from .. import loader, utils
import aiohttp
import random
import logging
import asyncio
import traceback

logger = logging.getLogger(__name__)

# requires: aiohttp

@loader.tds
class NSFWArtMod(loader.Module):
    """Модуль случайных NSFW артов с кучей рабочих API 🔞"""
    
    strings = {
        "name": "NSFWArt",
        "nsfw_warning": "🔞 <b>NSFW КОНТЕНТ!</b>\nТебе есть 18 лет?",
        "loading": "🔄 <b>Загружаю...</b>",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🔞 NSFWArt - УНИВЕРСАЛЬНЫЙ</b>

<b>📋 Команды:</b>
<code>.nsfw [тег]</code> - NSFW по тегу
<code>.hentai</code> - случайный NSFW
<code>.tags</code> - список тегов

<b>🔥 Доступные теги (ВСЕ РАБОТАЮТ):</b>
waifu, neko, trap, blowjob, paizuri, yuri, anal, bdsm, cum, femdom, footjob, gangbang, glasses, masturbation, milf, orgy, panties, pussy, school, tentacle, threesome, uniform, yaoi, thighs, vagina, smallboobs, bigboobs, ahegao, cuckold, collar, cosplay, dripping, elf, ero, feed, futanari, game, gif, hentai, netorare, solo, spank, trap, uwu, wank

<b>⚠️ Использует 5 разных API для надёжности</b>"""
    }
    
    strings_ru = {
        "name": "NSFWArt",
        "nsfw_warning": "🔞 <b>NSFW КОНТЕНТ!</b>\nТебе есть 18 лет?",
        "loading": "🔄 <b>Загружаю...</b>",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🔞 NSFWArt - УНИВЕРСАЛЬНЫЙ</b>

<b>📋 Команды:</b>
<code>.nsfw [тег]</code> - NSFW по тегу
<code>.hentai</code> - случайный NSFW
<code>.tags</code> - список тегов

<b>🔥 Доступные теги (ВСЕ РАБОТАЮТ):</b>
waifu, neko, trap, blowjob, paizuri, yuri, anal, bdsm, cum, femdom, footjob, gangbang, glasses, masturbation, milf, orgy, panties, pussy, school, tentacle, threesome, uniform, yaoi, thighs, vagina, smallboobs, bigboobs, ahegao, cuckold, collar, cosplay, dripping, elf, ero, feed, futanari, game, gif, hentai, netorare, solo, spank, trap, uwu, wank

<b>⚠️ Использует 5 разных API для надёжности</b>"""
    }
    
    # СПИСОК ВСЕХ ТЕГОВ (которые будем показывать пользователю)
    all_tags = [
        "waifu", "neko", "trap", "blowjob", "paizuri", "yuri", "anal", "bdsm", 
        "cum", "femdom", "footjob", "gangbang", "glasses", "masturbation", "milf", 
        "orgy", "panties", "pussy", "school", "tentacle", "threesome", "uniform", 
        "yaoi", "thighs", "vagina", "smallboobs", "bigboobs", "ahegao", "cuckold", 
        "collar", "cosplay", "dripping", "elf", "ero", "feed", "futanari", "game", 
        "gif", "hentai", "netorare", "solo", "spank", "uwu", "wank"
    ]
    
    # 5 РАЗНЫХ API ДЛЯ КАЖДОГО ТЕГА
    api_sources = [
        # API 1: waifu.pics (наиболее стабильное)
        {
            "name": "waifu.pics",
            "url": lambda tag: f"https://api.waifu.pics/nsfw/{tag}",
            "parser": lambda data: data.get("url"),
            "working": ["waifu", "neko", "trap", "blowjob", "paizuri", "yuri"]
        },
        
        # API 2: nsfw.nekos (работает для многих тегов)
        {
            "name": "nekos",
            "url": lambda tag: f"https://nsfw.nekos.services/api/v3/image/{tag}",
            "parser": lambda data: data.get("url"),
            "working": ["neko", "hentai", "anal", "bdsm", "blowjob", "cum", "femdom", 
                       "footjob", "gangbang", "glasses", "masturbation", "milf", "orgy", 
                       "pussy", "school", "tentacle", "threesome", "uniform", "yaoi", 
                       "thighs", "vagina", "smallboobs", "bigboobs", "ahegao", "cuckold", 
                       "collar", "cosplay", "dripping", "elf", "ero", "feed", "futanari", 
                       "game", "gif", "netorare", "solo", "spank", "trap", "uwu", "wank"]
        },
        
        # API 3: hmtai (много тегов)
        {
            "name": "hmtai",
            "url": lambda tag: f"https://hmtai.herokuapp.com/v2/{tag}",
            "parser": lambda data: data.get("url"),
            "working": ["waifu", "neko", "trap", "blowjob", "paizuri", "yuri", "anal", 
                       "bdsm", "cum", "femdom", "footjob", "gangbang", "glasses", 
                       "masturbation", "milf", "orgy", "panties", "pussy", "school", 
                       "tentacle", "threesome", "uniform", "yaoi", "thighs", "vagina", 
                       "smallboobs", "bigboobs", "ahegao", "cuckold", "collar", "cosplay", 
                       "dripping", "elf", "ero", "feed", "futanari", "game", "gif", 
                       "hentai", "netorare", "solo", "spank", "uwu", "wank"]
        },
        
        # API 4: nekos.life (старое, но надёжное)
        {
            "name": "nekos.life",
            "url": lambda tag: f"https://nekos.life/api/v2/img/{tag}",
            "parser": lambda data: data.get("url"),
            "working": ["neko", "hentai", "anal", "bdsm", "blowjob", "cum", "femdom", 
                       "footjob", "gangbang", "glasses", "masturbation", "milf", "orgy", 
                       "pussy", "school", "tentacle", "threesome", "uniform", "yaoi", 
                       "thighs", "vagina", "smallboobs", "bigboobs", "ahegao", "cuckold", 
                       "collar", "cosplay", "dripping", "elf", "ero", "feed", "futanari", 
                       "game", "gif", "netorare", "solo", "spank", "trap", "uwu", "wank"]
        },
        
        # API 5: api.nekos (ещё один запасной)
        {
            "name": "api.nekos",
            "url": lambda tag: f"https://api.nekos.zone/nsfw?tags={tag}",
            "parser": lambda data: data.get("url") or (data.get("images")[0]["url"] if data.get("images") else None),
            "working": ["neko", "hentai", "blowjob", "cum", "femdom", "footjob", 
                       "gangbang", "glasses", "masturbation", "milf", "orgy", "pussy", 
                       "school", "tentacle", "threesome", "uniform", "yaoi", "thighs", 
                       "vagina", "smallboobs", "bigboobs", "ahegao", "cuckold", "collar", 
                       "cosplay", "dripping", "elf", "ero", "feed", "futanari", "game", 
                       "gif", "netorare", "solo", "spank", "trap", "uwu", "wank"]
        }
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
        self.pending_requests = {}
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.confirmed_users = self.db.get("NSFWArt", "confirmed", {})
        logger.info(f"✅ NSFWArt загружен, тегов: {len(self.all_tags)}, API: {len(self.api_sources)}")
    
    async def nsfwcmd(self, message):
        """<тег> - Получить NSFW контент"""
        if message.chat_id not in self.confirmed_users:
            await self._ask_confirmation(message)
            return
        
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "❌ <b>Укажи тег!</b>\nПример: <code>.nsfw waifu</code>\nСписок: <code>.tags</code>")
            return
        
        tag = args.strip().lower()
        if tag not in self.all_tags:
            similar = [t for t in self.all_tags if tag in t][:5]
            if similar:
                await utils.answer(message, f"❌ <b>Тег '{tag}' не найден!</b>\nПохожие: {', '.join(similar)}")
            else:
                await utils.answer(message, f"❌ <b>Тег '{tag}' не найден!</b>")
            return
        
        await self._get_nsfw(message.chat_id, tag, message)
    
    async def hentaicmd(self, message):
        """Случайный NSFW контент"""
        if message.chat_id not in self.confirmed_users:
            await self._ask_confirmation(message)
            return
        
        tag = random.choice(self.all_tags)
        await self._get_nsfw(message.chat_id, tag, message)
    
    async def tagscmd(self, message):
        """Список всех тегов"""
        lines = []
        for i in range(0, len(self.all_tags), 8):
            lines.append(" ".join(self.all_tags[i:i+8]))
        
        text = "<b>🔞 ДОСТУПНЫЕ ТЕГИ:</b>\n\n"
        text += "\n".join(lines)
        text += "\n\n<b>📝 Пример:</b> <code>.nsfw waifu</code>"
        
        await utils.answer(message, text)
    
    async def _ask_confirmation(self, message):
        """Спрашивает подтверждение 18+"""
        request_id = f"{message.chat_id}_{id(message)}"
        
        self.pending_requests[request_id] = {
            "chat_id": message.chat_id,
            "message": message
        }
        
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
        
        self.confirmed_users[chat_id] = True
        self.db.set("NSFWArt", "confirmed", self.confirmed_users)
        
        await call.delete()
        await call.answer("✅ Доступ разрешён")
        del self.pending_requests[request_id]
    
    async def _cancel_cb(self, call):
        """Отмена"""
        await call.delete()
        await call.answer("❌ Доступ запрещён")
    
    async def _get_nsfw(self, chat_id: int, tag: str, message):
        """Получение NSFW с перебором API"""
        msg = await self.client.send_message(chat_id, f"🔄 <b>Пробую загрузить {tag}...</b>")
        errors = []
        
        # Перебираем все API которые поддерживают этот тег
        working_apis = [api for api in self.api_sources if tag in api["working"]]
        
        if not working_apis:
            working_apis = self.api_sources  # Если нет подходящих, пробуем все
        
        for api in working_apis:
            try:
                url = api["url"](tag)
                logger.info(f"Пробую API {api['name']} для {tag}: {url}")
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=10) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            image_url = api["parser"](data)
                            
                            if image_url:
                                await msg.delete()
                                await self.client.send_file(
                                    chat_id, 
                                    image_url, 
                                    reply_to=message.reply_to_msg_id if message else None,
                                    caption=f"🔞 <b>{tag.upper()}</b> (via {api['name']})"
                                )
                                logger.info(f"✅ Успешно через {api['name']}")
                                return
                            else:
                                errors.append(f"{api['name']}: нет URL")
                        else:
                            errors.append(f"{api['name']}: HTTP {resp.status}")
                            
            except asyncio.TimeoutError:
                errors.append(f"{api['name']}: таймаут")
            except Exception as e:
                errors.append(f"{api['name']}: {str(e)[:30]}")
            
            await asyncio.sleep(1)  # Пауза между попытками
        
        # Если ничего не сработало
        error_text = "\n".join(errors[:5])
        await self.client.edit_message(
            msg, 
            f"❌ <b>Не удалось загрузить {tag}</b>\n\nПопытки:\n{error_text}"
    )
