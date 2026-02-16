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
        "help": """<b>🔞 Random Hentai - МНОГО NSFW!</b>

<b>📋 Команды:</b>
<code>.hentai</code> - случайный хентай
<code>.nsfw [тег]</code> - NSFW по тегу
<code>.nsfwlist</code> - список тегов
<code>.sfw [тег]</code> - SFW по тегу

<b>🔥 NSFW теги (18+):</b>
waifu, neko, trap, blowjob, hentai, ass, bdsm, cum, creampie, double, femdom, footjob, gangbang, glasses, masturbation, milf, orgy, pantsu, pussy, school, tentacle, threesome, uniform, yaoi, yuri, tattoo, thighs, vagina, smallboobs, bigboobs, ahegao, cuckold, collar, cosplay, dripping, elf, erofeet, ero, feed, futanari, game, gif, hentaigif, neko_gif, nekotits, netorare, pussy_wank_gif, solo, solo_gif, spank, syuri, trap, uwu, wank, zbk

<b>✨ SFW теги (без 18+):</b>
waifu, neko, shinobu, megumin, bully, cuddle, cry, hug, awoo, kiss, lick, pat, smug, bonk, yeet, blush, smile, wave, highfive, handhold, nom, bite, glomp, slap, kill, kick, happy, wink, poke, dance, cringe

<b>⚠️ NSFW теги требуют подтверждения 18+</b>"""
    }
    
    strings_ru = {
        "name": "RandomHentai",
        "nsfw_warning": "🔞 <b>NSFW КОНТЕНТ!</b>\nТебе есть 18 лет?",
        "loading": "🔄 <b>Загружаю...</b>",
        "error": "💥 <b>Ошибка:</b> {}",
        "help": """<b>🔞 Random Hentai - МНОГО NSFW!</b>

<b>📋 Команды:</b>
<code>.hentai</code> - случайный хентай
<code>.nsfw [тег]</code> - NSFW по тегу
<code>.nsfwlist</code> - список тегов
<code>.sfw [тег]</code> - SFW по тегу

<b>🔥 NSFW теги (18+):</b>
waifu, neko, trap, blowjob, hentai, ass, bdsm, cum, creampie, double, femdom, footjob, gangbang, glasses, masturbation, milf, orgy, pantsu, pussy, school, tentacle, threesome, uniform, yaoi, yuri, tattoo, thighs, vagina, smallboobs, bigboobs, ahegao, cuckold, collar, cosplay, dripping, elf, erofeet, ero, feed, futanari, game, gif, hentaigif, neko_gif, nekotits, netorare, pussy_wank_gif, solo, solo_gif, spank, syuri, trap, uwu, wank, zbk

<b>✨ SFW теги (без 18+):</b>
waifu, neko, shinobu, megumin, bully, cuddle, cry, hug, awoo, kiss, lick, pat, smug, bonk, yeet, blush, smile, wave, highfive, handhold, nom, bite, glomp, slap, kill, kick, happy, wink, poke, dance, cringe

<b>⚠️ NSFW теги требуют подтверждения 18+</b>"""
    }
    
    # NSFW теги (18+)
    nsfw_tags = {
        # Основные
        "hentai": "https://api.waifu.pics/nsfw/waifu",
        "waifu": "https://api.waifu.pics/nsfw/waifu",
        "neko": "https://api.waifu.pics/nsfw/neko",
        "trap": "https://api.waifu.pics/nsfw/trap",
        "blowjob": "https://api.waifu.pics/nsfw/blowjob",
        
        # Популярные теги
        "ass": "https://nekobot.xyz/api/image?type=ass",
        "bdsm": "https://nekobot.xyz/api/image?type=bdsm",
        "cum": "https://nekobot.xyz/api/image?type=cum",
        "creampie": "https://nekobot.xyz/api/image?type=creampie",
        "double": "https://nekobot.xyz/api/image?type=double",
        "femdom": "https://nekobot.xyz/api/image?type=femdom",
        "footjob": "https://nekobot.xyz/api/image?type=footjob",
        "gangbang": "https://nekobot.xyz/api/image?type=gangbang",
        "glasses": "https://nekobot.xyz/api/image?type=glasses",
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
        "neko_gif": "https://nekobot.xyz/api/image?type=neko_gif",
        "nekotits": "https://nekobot.xyz/api/image?type=nekotits",
        "netorare": "https://nekobot.xyz/api/image?type=netorare",
        "pussy_wank_gif": "https://nekobot.xyz/api/image?type=pussy_wank_gif",
        "solo": "https://nekobot.xyz/api/image?type=solo",
        "solo_gif": "https://nekobot.xyz/api/image?type=solo_gif",
        "spank": "https://nekobot.xyz/api/image?type=spank",
        "syuri": "https://nekobot.xyz/api/image?type=syuri",
        "uwu": "https://nekobot.xyz/api/image?type=uwu",
        "wank": "https://nekobot.xyz/api/image?type=wank",
        "zbk": "https://nekobot.xyz/api/image?type=zbk"
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
        logger.info("✅ RandomHentai модуль инициализирован")
        logger.info(f"📊 NSFW тегов: {len(self.nsfw_tags)}, SFW тегов: {len(self.sfw_tags)}")
    
    async def nsfwcmd(self, message):
        """.nsfw [тег] - Получить NSFW 18+ контент"""
        logger.info(f"📝 Команда .nsfw от {message.chat_id}")
        
        if message.chat_id not in self.confirmed_users:
            logger.info(f"🔞 Требуется подтверждение для {message.chat_id}")
            await self._ask_confirmation(message, "nsfw", None)
            return
        
        args = utils.get_args_raw(message)
        if not args:
            logger.warning("❌ Не указан тег")
            await utils.answer(message, "❌ <b>Укажи тег!</b>\nПример: <code>.nsfw hentai</code>\nСписок: <code>.nsfwlist</code>")
            return
        
        tag = args.strip().lower()
        logger.info(f"🔍 Запрошен NSFW тег: {tag}")
        
        if tag not in self.nsfw_tags:
            logger.warning(f"❌ NSFW тег '{tag}' не найден")
            similar = [t for t in self.nsfw_tags.keys() if tag in t][:5]
            if similar:
                await utils.answer(message, f"❌ <b>Тег '{tag}' не найден!</b>\nПохожие NSFW: {', '.join(similar)}")
            else:
                await utils.answer(message, f"❌ <b>Тег '{tag}' не найден!</b>\nСписок NSFW тегов: <code>.nsfwlist</code>")
            return
        
        await self._get_nsfw_by_id(message.chat_id, tag, message.reply_to_msg_id, is_nsfw=True)
    
    async def sfwcmd(self, message):
        """.sfw [тег] - Получить SFW контент (без 18+)"""
        logger.info(f"📝 Команда .sfw от {message.chat_id}")
        
        args = utils.get_args_raw(message)
        if not args:
            logger.warning("❌ Не указан тег")
            await utils.answer(message, "❌ <b>Укажи тег!</b>\nПример: <code>.sfw waifu</code>\nСписок: <code>.nsfwlist</code>")
            return
        
        tag = args.strip().lower()
        logger.info(f"🔍 Запрошен SFW тег: {tag}")
        
        if tag not in self.sfw_tags:
            logger.warning(f"❌ SFW тег '{tag}' не найден")
            similar = [t for t in self.sfw_tags.keys() if tag in t][:5]
            if similar:
                await utils.answer(message, f"❌ <b>Тег '{tag}' не найден!</b>\nПохожие SFW: {', '.join(similar)}")
            else:
                await utils.answer(message, f"❌ <b>Тег '{tag}' не найден!</b>\nСписок тегов: <code>.nsfwlist</code>")
            return
        
        await self._get_nsfw_by_id(message.chat_id, tag, message.reply_to_msg_id, is_nsfw=False)
    
    async def hentaicmd(self, message):
        """Случайный NSFW контент"""
        logger.info(f"📝 Команда .hentai от {message.chat_id}")
        
        if message.chat_id not in self.confirmed_users:
            logger.info(f"🔞 Требуется подтверждение для {message.chat_id}")
            await self._ask_confirmation(message, "hentai", None)
            return
        
        # Случайный тег из NSFW
        tag = random.choice(list(self.nsfw_tags.keys()))
        logger.info(f"🎲 Случайный NSFW тег: {tag}")
        await self._get_nsfw_by_id(message.chat_id, tag, message.reply_to_msg_id, is_nsfw=True)
    
    async def nsfwlistcmd(self, message):
        """Список всех тегов"""
        logger.info(f"📝 Команда .nsfwlist от {message.chat_id}")
        
        nsfw_list = list(self.nsfw_tags.keys())
        sfw_list = list(self.sfw_tags.keys())
        
        # Разбиваем на группы для красивого вывода
        nsfw_lines = []
        for i in range(0, len(nsfw_list), 10):
            nsfw_lines.append(" ".join(nsfw_list[i:i+10]))
        
        sfw_lines = []
        for i in range(0, len(sfw_list), 10):
            sfw_lines.append(" ".join(sfw_list[i:i+10]))
        
        text = "<b>🔞 ДОСТУПНЫЕ ТЕГИ:</b>\n\n"
        
        text += "<b>🔥 NSFW (18+):</b>\n"
        text += "\n".join(nsfw_lines)
        text += "\n\n"
        
        text += "<b>✨ SFW (без 18+):</b>\n"
        text += "\n".join(sfw_lines)
        text += "\n\n"
        
        text += "<b>📝 Примеры:</b>\n"
        text += "<code>.nsfw hentai</code> - NSFW\n"
        text += "<code>.sfw waifu</code> - SFW\n"
        text += "<code>.hentai</code> - случайный NSFW"
        
        await utils.answer(message, text)
    
    async def _ask_confirmation(self, message, cmd, tag):
        """Спрашивает подтверждение 18+"""
        request_id = f"{message.chat_id}_{cmd}_{tag or 'none'}_{id(message)}"
        logger.info(f"🔐 Создан запрос подтверждения: {request_id}")
        
        self.pending_requests[request_id] = {
            "chat_id": message.chat_id,
            "cmd": cmd,
            "tag": tag,
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
        logger.info(f"✅ Подтверждение получено для request_id: {request_id}")
        
        request = self.pending_requests.get(request_id)
        if not request:
            logger.error(f"❌ Запрос {request_id} не найден")
            await call.answer("❌ Запрос устарел")
            await call.delete()
            return
        
        chat_id = request["chat_id"]
        cmd = request["cmd"]
        tag = request["tag"]
        
        logger.info(f"📊 Данные запроса: chat_id={chat_id}, cmd={cmd}, tag={tag}")
        
        self.confirmed_users[chat_id] = True
        self.db.set("RandomHentai", "confirmed", self.confirmed_users)
        logger.info(f"💾 Пользователь {chat_id} подтверждён")
        
        await call.delete()
        del self.pending_requests[request_id]
        
        if cmd == "nsfw" and tag:
            await self._get_nsfw_by_id(chat_id, tag, None, is_nsfw=True)
        elif cmd == "hentai":
            tag = random.choice(list(self.nsfw_tags.keys()))
            await self._get_nsfw_by_id(chat_id, tag, None, is_nsfw=True)
    
    async def _cancel_cb(self, call):
        """Отмена"""
        logger.info("❌ Пользователь отменил подтверждение")
        await call.delete()
        await call.answer("❌ Доступ запрещён")
    
    async def _get_nsfw_by_id(self, chat_id: int, tag: str, reply_to=None, is_nsfw: bool = True):
        """Получение контента по ID чата"""
        logger.info(f"🔄 _get_nsfw_by_id: chat_id={chat_id}, tag={tag}, is_nsfw={is_nsfw}")
        
        try:
            msg = await self.client.send_message(chat_id, self.strings("loading"))
            logger.info(f"📨 Отправлено сообщение загрузки в {chat_id}")
        except Exception as e:
            logger.error(f"❌ Не удалось отправить сообщение: {e}")
            return
        
        try:
            # Выбираем нужный словарь тегов
            if is_nsfw:
                url = self.nsfw_tags.get(tag, self.nsfw_tags["hentai"])
            else:
                url = self.sfw_tags.get(tag, self.sfw_tags["waifu"])
            
            logger.info(f"🔗 URL запроса: {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=15) as resp:
                    logger.info(f"📊 Статус ответа: {resp.status}")
                    
                    if resp.status != 200:
                        error_text = f"HTTP {resp.status}"
                        logger.error(f"❌ Ошибка API: {error_text}")
                        await self.client.edit_message(msg, self.strings("error").format(error_text))
                        return
                    
                    data = await resp.json()
                    
                    # Разные API имеют разный формат ответа
                    if "url" in data:
                        image_url = data["url"]
                    elif "message" in data:
                        image_url = data["message"]
                    else:
                        logger.error("❌ Неизвестный формат ответа")
                        await self.client.edit_message(msg, self.strings("error").format("Неизвестный ответ API"))
                        return
                    
                    logger.info(f"🖼️ Получен URL: {image_url[:50]}...")
                    
                    await msg.delete()
                    
                    # Отправляем картинку
                    await self.client.send_file(
                        chat_id,
                        image_url,
                        reply_to=reply_to,
                        caption=f"🔞 <b>{tag.upper()}</b>" if is_nsfw else f"✨ <b>{tag.upper()}</b>"
                    )
                    logger.info("✅ Файл успешно отправлен")
            
        except asyncio.TimeoutError:
            logger.error("⏱️ Таймаут при запросе")
            await self.client.edit_message(msg, self.strings("error").format("Таймаут"))
        except Exception as e:
            logger.error(f"💥 Ошибка: {e}")
            logger.error(traceback.format_exc())
            await self.client.edit_message(msg, self.strings("error").format(str(e)))
