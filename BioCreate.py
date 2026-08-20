# meta developer: @Edu_kak_xochu
# meta pic: https://img.icons8.com/color/48/000000/biography.png
# meta banner: https://via.placeholder.com/300x100.png?text=Bio+Creator

import asyncio
import re
from telethon.tl.types import Message

from .. import loader, utils

@loader.tds
class BioCreatorMod(loader.Module):
    """Модуль для создания красивой биографии"""
    
    strings = {
        "name": "BioCreator",
        "start_creating": "🎨 <b>Начинаем создание биографии!</b>\n\nЯ задам вам несколько вопросов.\nДля отмены напишите <code>отмена</code>\nДля пропуска вопроса напишите <code>-</code>",
        "cancel": "❌ <b>Создание биографии отменено</b>",
        "bio_created": "✅ <b>Ваша биография:</b>\n\n{new_bio}",
        "choose_color": "🎨 <b>Выберите цвет оформления:</b>\n\n1️⃣ 🔴 Красный\n2️⃣ 🟠 Оранжевый\n3️⃣ 🟡 Желтый\n4️⃣ 🟢 Зеленый\n5️⃣ 🔵 Голубой\n6️⃣ 💙 Синий\n7️⃣ 🟣 Фиолетовый\n8️⃣ 🌸 Розовый\n9️⃣ ⚪ Белый\n🔟 ⚫ Серый",
        "invalid_color": "⚠️ <b>Неверный цвет! Выберите от 1 до 10</b>",
        "invalid_input": "⚠️ <b>Пожалуйста, введите ответ или '-' для пропуска</b>",
        "not_creator": "⚠️ <b>Вы не создаете биографию</b>",
        "creating": "🎨 <b>Создание биографии...</b>",
        "show_help": "📖 <b>Команды BioCreator:</b>\n\n<b>.biocreate</b> - создать биографию\n<b>.biohelp</b> - справка",
        "skipped": "⏭ <b>Вопрос пропущен</b>",
    }
    
    strings_ru = {
        "start_creating": "🎨 <b>Начинаем создание биографии!</b>\n\nЯ задам вам несколько вопросов.\nДля отмены напишите <code>отмена</code>\nДля пропуска вопроса напишите <code>-</code>",
        "cancel": "❌ <b>Создание биографии отменено</b>",
        "bio_created": "✅ <b>Ваша биография:</b>\n\n{new_bio}",
        "choose_color": "🎨 <b>Выберите цвет оформления:</b>\n\n1️⃣ 🔴 Красный\n2️⃣ 🟠 Оранжевый\n3️⃣ 🟡 Желтый\n4️⃣ 🟢 Зеленый\n5️⃣ 🔵 Голубой\n6️⃣ 💙 Синий\n7️⃣ 🟣 Фиолетовый\n8️⃣ 🌸 Розовый\n9️⃣ ⚪ Белый\n🔟 ⚫ Серый",
        "invalid_color": "⚠️ <b>Неверный цвет! Выберите от 1 до 10</b>",
        "invalid_input": "⚠️ <b>Пожалуйста, введите ответ или '-' для пропуска</b>",
        "not_creator": "⚠️ <b>Вы не создаете биографию</b>",
        "creating": "🎨 <b>Создание биографии...</b>",
        "show_help": "📖 <b>Команды BioCreator:</b>\n\n<b>.biocreate</b> - создать биографию\n<b>.biohelp</b> - справка",
        "skipped": "⏭ <b>Вопрос пропущен</b>",
    }

    def __init__(self):
        self.creating_bio = {}
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "use_emoji",
                True,
                "Использовать эмодзи в биографии",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "bio_template",
                "default",
                "Шаблон биографии (default, minimal, creative)",
                validator=loader.validators.Choice(["default", "minimal", "creative"]),
            ),
        )
        
        self.colors = {
            1: ("🔴", "Красный"),
            2: ("🟠", "Оранжевый"),
            3: ("🟡", "Желтый"),
            4: ("🟢", "Зеленый"),
            5: ("🔵", "Голубой"),
            6: ("💙", "Синий"),
            7: ("🟣", "Фиолетовый"),
            8: ("🌸", "Розовый"),
            9: ("⚪", "Белый"),
            10: ("⚫", "Серый"),
        }
        
        self.questions = [
            ("👤", "Как вас зовут?"),
            ("🎂", "Сколько вам лет?"),
            ("📍", "Из какого вы города?"),
            ("🎯", "Ваши увлечения/хобби?"),
            ("📝", "Расскажите о себе (кратко)?"),
            ("🔗", "Ссылки на соцсети (через пробел)?"),
        ]

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self._me = await client.get_me()

    @loader.command()
    async def biocreatecmd(self, message: Message):
        """Создать красивую биографию"""
        user_id = message.sender_id
        self.creating_bio[user_id] = {
            "step": 0,
            "answers": [],
            "color": None,
        }
        
        await utils.answer(message, self.strings("start_creating"))
        await self._ask_question(message)

    @loader.command()
    async def biohelpcmd(self, message: Message):
        """Показать справку по командам"""
        await utils.answer(message, self.strings("show_help"))

    @loader.watcher(out=False)
    async def watcher(self, message: Message):
        """Обрабатывает ответы пользователя"""
        user_id = message.sender_id
        
        if user_id not in self.creating_bio:
            return
        
        if message.text.lower() == "отмена":
            del self.creating_bio[user_id]
            await utils.answer(message, self.strings("cancel"))
            return
        
        bio_data = self.creating_bio[user_id]
        step = bio_data["step"]
        
        if step == 0:
            # Выбор цвета
            try:
                color_num = int(message.text.strip())
                if color_num in self.colors:
                    bio_data["color"] = color_num
                    bio_data["step"] = 1
                    await self._ask_question(message)
                else:
                    await utils.answer(message, self.strings("invalid_color"))
            except ValueError:
                await utils.answer(message, self.strings("invalid_color"))
        
        elif step <= len(self.questions):
            # Сохраняем ответ
            if not message.text.strip():
                await utils.answer(message, self.strings("invalid_input"))
                return
            
            # Проверяем на пропуск
            if message.text.strip() == "-":
                bio_data["answers"].append(None)
                await utils.answer(message, self.strings("skipped"))
            else:
                bio_data["answers"].append(message.text.strip())
            
            bio_data["step"] += 1
            
            if bio_data["step"] <= len(self.questions):
                await self._ask_question(message)
            else:
                # Все вопросы заданы, создаем биографию
                await self._create_bio(message, user_id)

    async def _ask_question(self, message: Message):
        """Задает следующий вопрос"""
        user_id = message.sender_id
        bio_data = self.creating_bio[user_id]
        step = bio_data["step"]
        
        if step == 0:
            # Выбор цвета
            await utils.answer(message, self.strings("choose_color"))
        else:
            # Вопросы
            question_num = step
            emoji, question_text = self.questions[question_num - 1]
            await utils.answer(
                message,
                f"{emoji} <b>Вопрос {question_num} из {len(self.questions)}:</b>\n{question_text}"
            )

    async def _create_bio(self, message: Message, user_id: int):
        """Создает биографию и отправляет как сообщение"""
        bio_data = self.creating_bio[user_id]
        answers = bio_data["answers"]
        color_num = bio_data["color"]
        color_emoji, color_name = self.colors[color_num]
        
        # Создаем биографию в зависимости от шаблона
        template = self.config["bio_template"]
        use_emoji = self.config["use_emoji"]
        
        if template == "default":
            bio = self._create_default_bio(answers, color_emoji, color_name, use_emoji)
        elif template == "minimal":
            bio = self._create_minimal_bio(answers, color_emoji, use_emoji)
        else:  # creative
            bio = self._create_creative_bio(answers, color_emoji, color_name, use_emoji)
        
        # Очищаем данные
        del self.creating_bio[user_id]
        
        # Отправляем биографию как сообщение
        await utils.answer(message, self.strings("bio_created").format(new_bio=bio))

    def _create_default_bio(self, answers, color_emoji, color_name, use_emoji):
        """Создает стандартную биографию"""
        name, age, city, hobby, about, social = answers
        
        bio = f"{color_emoji} <b>{name}</b>\n"
        bio += f"├── 🎂 {age} лет\n"
        bio += f"├── 📍 {city}\n"
        bio += f"├── 🎯 {hobby}\n"
        bio += f"├── 📝 {about}\n"
        
        if social:
            bio += f"└── 🔗 {social}\n"
        
        bio += f"\n✨ <i>Создано с помощью BioCreator</i>"
        
        return bio

    def _create_minimal_bio(self, answers, color_emoji, use_emoji):
        """Создает минималистичную биографию"""
        name, age, city, hobby, about, social = answers
        
        bio = f"<b>{name}</b> • {age}\n"
        bio += f"{city}\n"
        bio += f"{hobby}\n"
        bio += f"{about}\n"
        
        if social:
            bio += f"\n{social}"
        
        return bio

    def _create_creative_bio(self, answers, color_emoji, color_name, use_emoji):
        """Создает креативную биографию"""
        name, age, city, hobby, about, social = answers
        
        bio = f"╔═══ {color_emoji} <b>{name}</b> ═══╗\n"
        bio += f"║ Возраст: {age} лет\n"
        bio += f"║ Город: {city}\n"
        bio += f"║ Хобби: {hobby}\n"
        bio += f"║ О себе: {about}\n"
        
        if social:
            bio += f"║ Соцсети: {social}\n"
        
        bio += f"╚{'═' * 20}╝"
        
        return bio
