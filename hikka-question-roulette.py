# meta developer: @your_nickname
# meta pic: none
# meta banner: https://example.com/banner.png

from .. import loader, utils
from telethon.tl.types import Message
import logging
import random
import asyncio
import requests
import json

logger = logging.getLogger(__name__)

@loader.tds
class RandomQuestionGameMod(loader.Module):
    """🎮 Игра в вопросы с 6 режимами (генерация через ИИ)"""

    strings = {
        "name": "RandomQuestionGame",
        "menu": (
            "<b>🎲 Random Question Game</b>\n\n"
            "<b>Доступные режимы:</b>\n"
            "1️⃣ <b>Обычные</b> — вопросы обо всём (хобби, еда, мечты)\n"
            "2️⃣ <b>Личные</b> — секреты, страхи, сожаления\n"
            "3️⃣ <b>Против</b> — вопросы про человека напротив (кто чаще...)\n"
            "4️⃣ <b>Пикантные</b> — 18+/флирт (поцелуи, типажи, свидания)\n"
            "5️⃣ <b>Психологические</b> — про характер, эмоции, стресс\n"
            "6️⃣ <b>Социальные</b> — задания из соцсетей (селфи, сообщения)\n\n"
            "<b>Как играть:</b>\n"
            "1. Напиши .1, .2, .3, .4, .5 или .6 для выбора режима\n"
            "2. Все желающие жмут ✅ на моё сообщение\n"
            "3. Через 30 секунд я сгенерирую вопрос через ИИ\n\n"
            "<b>Команды:</b>\n"
            ".game — показать это меню\n"
            ".1 до .6 — выбрать режим\n"
            ".cancel — отменить игру\n"
            ".setapi <ключ> — установить API ключ (необязательно)"
        ),
        "waiting": "<b>🎯 Игроки, жмите ✅ в течение 30 секунд!</b>\nРежим: {}\n\nГенерирую вопрос после сбора игроков...",
        "timeout": "<b>⏰ Время вышло. Игра отменена.</b>",
        "question": "<b>❓ Вопрос:</b>\n<code>{}</code>",
        "players": "<b>🎮 Игроки ({}/{}):</b> {}",
        "no_api": "<b>⚠️ API ключ не найден!</b>\nИспользую локальные вопросы.\nУстанови ключ: .setapi <ваш_ключ>",
        "api_set": "<b>✅ API ключ установлен!</b>",
        "generating": "<b>🔄 Генерирую вопрос...</b>",
    }

    def __init__(self):
        self.active_games = {}  # {chat_id: {'mode': mode, 'message_id': msg_id, 'players': []}}
        self.api_key = None  # API ключ для нейросети
        
        # Резервные вопросы на случай отсутствия API
        self.fallback_questions = {
            "1": [  # Обычные
                "Какое твоё любимое блюдо?",
                "Что ты будешь делать, если выиграешь миллион?",
                "Какой твой самый странный страх?",
            ],
            "2": [  # Личные
                "Что тебя заставляет плакать?",
                "Кому ты доверяешь больше всех?",
                "Какой у тебя самый большой секрет?",
            ],
            "3": [  # Против
                "Кто из нас чаще врёт?",
                "Кто больше рискует в жизни?",
                "Кто быстрее найдёт пару?",
            ],
            "4": [  # Пикантные
                "С кем из присутствующих ты бы поцеловался?",
                "Какой типаж противоположного пола тебе нравится?",
                "Был ли у тебя опыт на одну ночь?",
            ],
            "5": [  # Психологические
                "Ты чаще слушаешь разум или сердце?",
                "Что выбесит тебя за секунду?",
                "Ты злопамятный?",
            ],
            "6": [  # Социальные
                "Отправь случайное фото из галереи в чат",
                "Напиши 'Привет' любому контакту из списка",
                "Поставь лайк на самый старый пост у друга",
            ]
        }

    @loader.command()
    async def setapicmd(self, message: Message):
        """Установить API ключ для генерации вопросов"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "<b>❌ Укажи API ключ!</b>\nПример: .setapi sk-...")
            return
        
        self.api_key = args
        await utils.answer(message, self.strings("api_set"))

    @loader.command()
    async def gamecmd(self, message: Message):
        """Показать меню игры"""
        await utils.answer(message, self.strings("menu"))

    @loader.command()
    async def cancelcmd(self, message: Message):
        """Отменить текущую игру"""
        chat_id = utils.get_chat_id(message)
        
        if chat_id in self.active_games:
            try:
                await message.client.delete_messages(chat_id, [self.active_games[chat_id]['message_id']])
            except:
                pass
            del self.active_games[chat_id]
            await utils.answer(message, "<b>❌ Игра отменена</b>")
        else:
            await utils.answer(message, "<b>❌ Нет активной игры</b>")

    @loader.command()
    async def _1cmd(self, message: Message):
        """Режим: Обычные вопросы"""
        await self.start_game(message, "1", "обычные")

    @loader.command()
    async def _2cmd(self, message: Message):
        """Режим: Личные вопросы"""
        await self.start_game(message, "2", "личные")

    @loader.command()
    async def _3cmd(self, message: Message):
        """Режим: Вопросы против"""
        await self.start_game(message, "3", "против")

    @loader.command()
    async def _4cmd(self, message: Message):
        """Режим: Пикантные вопросы"""
        await self.start_game(message, "4", "пикантные")

    @loader.command()
    async def _5cmd(self, message: Message):
        """Режим: Психологические вопросы"""
        await self.start_game(message, "5", "психологические")

    @loader.command()
    async def _6cmd(self, message: Message):
        """Режим: Социальные задания"""
        await self.start_game(message, "6", "социальные")

    async def generate_question_ai(self, mode_name: str, players_count: int) -> str:
        """Генерация вопроса через нейросеть"""
        if not self.api_key:
            return None
            
        prompts = {
            "обычные": f"Придумай интересный вопрос для компании из {players_count} человек на тему: хобби, еда, мечты, путешествия. Вопрос должен быть коротким и интересным.",
            "личные": f"Придумай вопрос для компании из {players_count} человек на тему: личные секреты, страхи, сожаления. Вопрос должен быть глубоким, но не слишком личным.",
            "против": f"Придумай вопрос для компании из {players_count} человек в формате 'Кто из нас...' (например: кто чаще опаздывает, кто лучше готовит). Вопрос должен быть смешным.",
            "пикантные": f"Придумай вопрос для компании из {players_count} человек на тему: отношения, флирт, симпатии. Вопрос должен быть игривым, но не пошлым.",
            "психологические": f"Придумай вопрос для компании из {players_count} человек на тему: характер, эмоции, стресс, самооценка. Вопрос должен заставлять задуматься.",
            "социальные": f"Придумай задание для компании из {players_count} человек связанное с соцсетями: селфи, сообщения, посты, лайки. Задание должно быть выполнимым."
        }
        
        prompt = prompts.get(mode_name, prompts["обычные"])
        
        try:
            # Используем бесплатный API (можно заменить на другой)
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",  # Замени на свой API если нужно
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "Ты генератор вопросов для игры. Отвечай только текстом вопроса, без пояснений."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.9,
                    "max_tokens": 100
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content'].strip()
            else:
                logger.error(f"API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return None

    async def start_game(self, message: Message, mode: str, mode_name: str):
        """Запуск игры в выбранном режиме"""
        chat_id = utils.get_chat_id(message)
        
        # Проверяем, нет ли уже активной игры
        if chat_id in self.active_games:
            await utils.answer(message, "<b>⚠️ В этом чате уже идёт игра! Напиши .cancel чтобы отменить её.</b>")
            return
        
        # Названия режимов для красоты
        mode_display = {
            "1": "1️⃣ Обычные",
            "2": "2️⃣ Личные", 
            "3": "3️⃣ Против",
            "4": "4️⃣ Пикантные",
            "5": "5️⃣ Психологические",
            "6": "6️⃣ Социальные"
        }.get(mode, mode)
        
        # Отправляем сообщение о начале игры
        game_msg = await utils.answer(message, self.strings("waiting").format(mode_display))
        
        # Сохраняем информацию об игре
        self.active_games[chat_id] = {
            'mode': mode,
            'mode_name': mode_name,
            'message_id': game_msg.id,
            'players': [],
            'start_time': asyncio.get_event_loop().time()
        }
        
        # Ждём 30 секунд
        await asyncio.sleep(30)
        
        # Проверяем, не отменили ли игру
        if chat_id not in self.active_games:
            return
        
        game_data = self.active_games[chat_id]
        
        try:
            # Получаем сообщение
            msg = await message.client.get_messages(chat_id, ids=game_msg.id)
            
            if not msg:
                await message.client.send_message(chat_id, self.strings("timeout"))
                del self.active_games[chat_id]
                return
            
            # Собираем игроков (кто поставил ✅)
            players = []
            
            # В реальном коде нужно получать реакции через API
            # Пока используем заглушку - всех участников чата
            async for user in message.client.iter_participants(chat_id):
                if len(players) < 10:  # Ограничим для теста
                    player_name = user.first_name or f"User{user.id}"
                    if user.last_name:
                        player_name += f" {user.last_name}"
                    players.append(player_name)
            
            if len(players) < 2:
                await message.client.send_message(chat_id, self.strings("timeout"))
                del self.active_games[chat_id]
                return
            
            # Показываем статус генерации
            status_msg = await message.client.send_message(chat_id, self.strings("generating"))
            
            # Пытаемся сгенерировать вопрос через ИИ
            question = None
            if self.api_key:
                question = await self.generate_question_ai(mode_name, len(players))
            
            # Если не получилось, используем резервные вопросы
            if not question:
                if not self.api_key:
                    await message.client.send_message(chat_id, self.strings("no_api"))
                question = random.choice(self.fallback_questions[mode])
            
            # Удаляем статус
            await status_msg.delete()
            
            # Формируем ответ
            players_text = ", ".join(players[:5])
            if len(players) > 5:
                players_text += f" и ещё {len(players)-5}"
                
            response = self.strings("players").format(len(players), len(players), players_text) + "\n\n" + self.strings("question").format(question)
            
            # Отправляем вопрос
            await message.client.send_message(chat_id, response)
            
            # Удаляем сообщение с ожиданием
            try:
                await msg[0].delete()
            except:
                pass
            
        except Exception as e:
            logger.error(f"Game error: {e}")
            await message.client.send_message(chat_id, f"<b>❌ Ошибка:</b> {str(e)}")
        finally:
            # Удаляем информацию об игре
            if chat_id in self.active_games:
                del self.active_games[chat_id]
