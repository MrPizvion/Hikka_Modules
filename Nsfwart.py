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
        "no_api": "❌ <b>API ключ не указан!</b>\nПолучи на: https://nekobot.xyz/api",
        "help": """<b>🔞 Random Hentai</b>

<b>📋 Команды:</b>
<code>.hentai</code> - случайный хентай
<code>.neko</code> - случайная neko
<code>.kemono</code> - kemonomimi
<code>.holo</code> - Holo
<code>.nsfw [тег]</code> - NSFW по тегу

<b>📋 Доступные теги:</b>
waifu, neko, shinobu, megumin, bully, cuddle, cry, hug, awoo, kiss, lick, pat, smug, bonk, yeet, blush, smile, wave, highfive, handhold, nom, bite, glomp, slap, kill, kick, happy, wink, poke, dance, cringe

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
<code>.kemono</code> - kemonomimi
<code>.holo</code> - Holo
<code>.nsfw [тег]</code> - NSFW по тегу

<b>📋 Доступные теги:</b>
waifu, neko, shinobu, megumin, bully, cuddle, cry, hug, awoo, kiss, lick, pat, smug, bonk, yeet, blush, smile, wave, highfive, handhold, nom, bite, glomp, slap, kill, kick, happy, wink, poke, dance, cringe

<b>⚠️ Требуется подтверждение 18+</b>"""
    }
    
    # Новое рабочее API
    endpoints = {
        # SFW (всегда работают)
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
        "cringe": "https://api.waifu.pics/sfw/cringe",
        
        # NSFW (только для 18+)
        "hentai": "https://api.waifu.pics/nsfw/waifu",
        "blowjob": "https://api.waifu.pics/nsfw/blowjob",
        "trap": "https://api.waifu.pics/nsfw/trap",
        "neko_nsfw": "https://api.waifu.pics/nsfw/neko"
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "api_key",
                None,
                "🔑 API ключ (не нужен)",
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
        self.pending_requests = {}
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.confirmed_users = self.db.get("RandomHentai", "confirmed", {})
        logger.info("✅ RandomHentai модуль инициализирован")
        logger.info(f"📊 Подтверждённые пользователи: {len(self.confirmed_users)}")
    
    async def nsfwcmd(self, message):
        """.nsfw [тег] - Получить NSFW по тегу"""
        logger.info(f"📝 Команда .nsfw от {message.chat_id}")
        
        if not self.config["confirm_18"] and message.chat_id not in self.confirmed_users:
            logger.info(f"🔞 Требуется подтверждение для {message.chat_id}")
            await self._ask_confirmation(message, "nsfw", None)
            return
        
        args = utils.get_args_raw(message)
        if not args:
            logger.warning("❌ Не указан тег")
            await utils.answer(message, "❌ <b>Укажи тег!</b>\nПример: <code>.nsfw waifu</code>")
            return
        
        tag = args.strip().lower()
        logger.info(f"🔍 Запрошен тег: {tag}")
        
        if tag not in self.endpoints:
            logger.warning(f"❌ Тег '{tag}' не найден")
            similar = [t for t in self.endpoints.keys() if tag in t][:5]
            if similar:
                await utils.answer(message, f"❌ <b>Тег '{tag}' не найден!</b>\nПохожие: {', '.join(similar)}")
            else:
                await utils.answer(message, f"❌ <b>Тег '{tag}' не найден!</b>\nСписок тегов: <code>.nsfwhelp</code>")
            return
        
        await self._get_nsfw(message, tag)
    
    async def hentaicmd(self, message):
        """Случайный хентай"""
        logger.info(f"📝 Команда .hentai от {message.chat_id}")
        if not self.config["confirm_18"] and message.chat_id not in self.confirmed_users:
            logger.info(f"🔞 Требуется подтверждение для {message.chat_id}")
            await self._ask_confirmation(message, "hentai", None)
            return
        await self._get_nsfw(message, "hentai")
    
    async def nekocmd(self, message):
        """Случайная neko"""
        logger.info(f"📝 Команда .neko от {message.chat_id}")
        if not self.config["confirm_18"] and message.chat_id not in self.confirmed_users:
            logger.info(f"🔞 Требуется подтверждение для {message.chat_id}")
            await self._ask_confirmation(message, "neko", None)
            return
        await self._get_nsfw(message, "neko")
    
    async def kemonocmd(self, message):
        """Случайный kemonomimi"""
        logger.info(f"📝 Команда .kemono от {message.chat_id}")
        if not self.config["confirm_18"] and message.chat_id not in self.confirmed_users:
            logger.info(f"🔞 Требуется подтверждение для {message.chat_id}")
            await self._ask_confirmation(message, "kemono", None)
            return
        await self._get_nsfw(message, "kemono")
    
    async def holocmd(self, message):
        """Случайный Holo"""
        logger.info(f"📝 Команда .holo от {message.chat_id}")
        if not self.config["confirm_18"] and message.chat_id not in self.confirmed_users:
            logger.info(f"🔞 Требуется подтверждение для {message.chat_id}")
            await self._ask_confirmation(message, "holo", None)
            return
        await self._get_nsfw(message, "holo")
    
    async def nsfwhelpcmd(self, message):
        """Список всех тегов"""
        logger.info(f"📝 Команда .nsfwhelp от {message.chat_id}")
        tags = list(self.endpoints.keys())
        sfw_tags = [t for t in tags if not t.startswith("nsfw_") and t not in ["hentai", "blowjob", "trap"]][:20]
        nsfw_tags = ["hentai", "blowjob", "trap", "neko_nsfw"]
        
        text = "<b>🔞 Доступные теги:</b>\n\n"
        text += "<b>✨ SFW (без подтверждения):</b>\n"
        text += ", ".join(sfw_tags[:15]) + "\n\n"
        text += "<b>🔥 NSFW (требуется 18+):</b>\n"
        text += ", ".join(nsfw_tags) + "\n\n"
        text += "<b>Пример:</b> <code>.nsfw waifu</code>"
        
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
            logger.error(f"❌ Запрос {request_id} не найден в pending_requests")
            await call.answer("❌ Запрос устарел")
            await call.delete()
            return
        
        chat_id = request["chat_id"]
        cmd = request["cmd"]
        tag = request["tag"]
        
        logger.info(f"📊 Данные запроса: chat_id={chat_id}, cmd={cmd}, tag={tag}")
        
        self.confirmed_users[chat_id] = True
        self.db.set("RandomHentai", "confirmed", self.confirmed_users)
        logger.info(f"💾 Пользователь {chat_id} добавлен в confirmed_users")
        
        await call.delete()
        
        del self.pending_requests[request_id]
        
        if cmd == "nsfw" and tag:
            logger.info(f"📤 Отправка NSFW по тегу {tag} в чат {chat_id}")
            await self._get_nsfw_by_id(chat_id, tag)
        else:
            logger.info(f"📤 Отправка {cmd} в чат {chat_id}")
            await self._get_nsfw_by_id(chat_id, cmd)
    
    async def _cancel_cb(self, call):
        """Отмена"""
        logger.info("❌ Пользователь отменил подтверждение")
        await call.delete()
        await call.answer("❌ Доступ запрещён")
    
    async def _get_nsfw(self, message, tag: str):
        """Получение NSFW контента из сообщения"""
        chat_id = message.chat_id
        logger.info(f"📥 _get_nsfw: chat_id={chat_id}, tag={tag}")
        await self._get_nsfw_by_id(chat_id, tag, message.reply_to_msg_id)
    
    async def _get_nsfw_by_id(self, chat_id: int, tag: str, reply_to=None):
        """Получение NSFW контента по ID чата"""
        logger.info(f"🔄 _get_nsfw_by_id: chat_id={chat_id}, tag={tag}")
        
        try:
            msg = await self.client.send_message(chat_id, self.strings("loading"))
            logger.info(f"📨 Отправлено сообщение загрузки в {chat_id}")
        except Exception as e:
            logger.error(f"❌ Не удалось отправить сообщение в {chat_id}: {e}")
            logger.error(traceback.format_exc())
            return
        
        try:
            url = self.endpoints.get(tag, self.endpoints["waifu"])
            logger.info(f"🔗 URL запроса: {url}")
            
            async with aiohttp.ClientSession() as session:
                logger.info("🌐 Выполняется запрос к API...")
                async with session.get(url, timeout=10) as resp:
                    logger.info(f"📊 Статус ответа: {resp.status}")
                    
                    if resp.status != 200:
                        error_text = f"HTTP {resp.status}"
                        logger.error(f"❌ Ошибка API: {error_text}")
                        await self.client.edit_message(msg, self.strings("error").format(error_text))
                        return
                    
                    data = await resp.json()
                    logger.info(f"📦 Получен ответ от API")
                    
                    image_url = data.get("url")
                    if not image_url:
                        logger.error("❌ В ответе нет URL")
                        await self.client.edit_message(msg, self.strings("error").format("Нет URL"))
                        return
                    
                    logger.info(f"🖼️ Получен URL: {image_url[:50]}...")
                    
                    await msg.delete()
                    logger.info("🗑️ Сообщение загрузки удалено")
                    
                    logger.info(f"📤 Отправка файла в {chat_id}")
                    try:
                        await self.client.send_file(
                            chat_id,
                            image_url,
                            reply_to=reply_to,
                            caption=f"🔞 <b>{tag.upper()}</b>"
                        )
                        logger.info("✅ Файл успешно отправлен")
                    except Exception as e:
                        logger.error(f"❌ Ошибка отправки файла: {e}")
                        logger.error(traceback.format_exc())
                        await self.client.send_message(chat_id, self.strings("error").format(str(e)))
            
        except asyncio.TimeoutError:
            logger.error("⏱️ Таймаут при запросе к API")
            await self.client.edit_message(msg, self.strings("error").format("Таймаут"))
        except Exception as e:
            logger.error(f"💥 Необработанная ошибка: {e}")
            logger.error(traceback.format_exc())
            await self.client.edit_message(msg, self.strings("error").format(str(e)))
