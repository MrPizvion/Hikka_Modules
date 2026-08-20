# meta developer: @your_username
# meta pic: https://img.icons8.com/color/48/000000/biography.png
# meta banner: https://via.placeholder.com/300x100.png?text=Bio+Creator

import asyncio
import re
from telethon.tl.types import Message
from telethon.tl.functions.account import UpdateProfileRequest

from .. import loader, utils

@loader.tds
class BioCreatorMod(loader.Module):
    """Модуль для создания красивой биографии с настройкой цветов"""
    
    strings = {
        "name": "BioCreator",
        "start_creating": "🎨 <b>Начинаем создание биографии!</b>\n\nЯ задам вам несколько вопросов.\nДля отмены напишите <code>отмена</code>\nДля пропуска вопроса напишите <code>-</code>",
        "cancel": "❌ <b>Создание биографии отменено</b>",
        "bio_updated": "✅ <b>Биография успешно обновлена!</b>\n\n<b>Новая биография:</b>\n{new_bio}",
        "bio_saved": "💾 <b>Биография сохранена в конфиг</b>",
        "bio_deleted": "🗑 <b>Биография удалена</b>",
        "no_bio": "⚠️ <b>У вас нет сохраненной биографии</b>",
        "current_bio": "📝 <b>Текущая биография:</b>\n{current_bio}",
        "choose_color": "🎨 <b>Выберите цвет оформления:</b>\n\n1️⃣ 🔴 Красный\n2️⃣ 🟠 Оранжевый\n3️⃣ 🟡 Желтый\n4️⃣ 🟢 Зеленый\n5️⃣ 🔵 Голубой\n6️⃣ 💙 Синий\n7️⃣ 🟣 Фиолетовый\n8️⃣ 🌸 Розовый\n9️⃣ ⚪ Белый\n🔟 ⚫ Серый",
        "invalid_color": "⚠️ <b>Неверный цвет! Выберите от 1 до 10</b>",
        "invalid_input": "⚠️ <b>Пожалуйста, введите ответ или '-' для пропуска</b>",
        "not_creator": "⚠️ <b>Вы не создаете биографию</b>",
        "creating": "🎨 <b>Создание биографии...</b>",
        "show_help": "📖 <b>Команды BioCreator:</b>\n\n<b>.biocreate</b> - создать биографию\n<b>.biosave</b> - сохранить текущую биографию\n<b>.biorestore</b> - восстановить сохраненную\n<b>.bioclear</b> - удалить биографию\n<b>.bioshow</b> - показать текущую\n<b>.biohelp</b> - справка",
        "skipped": "⏭ <b>Вопрос пропущен</b>",
        "bio_too_long": "⚠️ <b>Биография слишком длинная! Максимум 70 символов для Telegram</b>",
    }
    
    strings_ru = {
        "start_creating": "🎨 <b>Начинаем создание биографии!</b>\n\nЯ задам вам несколько вопросов.\nДля отмены напишите <code>отмена</code>\nДля пропуска вопроса напишите <code>-</code>",
        "cancel": "❌ <b>Создание биографии отменено</b>",
        "bio_updated": "✅ <b>Биография успешно обновлена!</b>\n\n<b>Новая биография:</b>\n{new_bio}",
        "bio_saved": "💾 <b>Биография сохранена в конфиг</b>",
        "bio_deleted": "🗑 <b>Биография удалена</b>",
        "no_bio": "⚠️ <b>У вас нет сохраненной биографии</b>",
        "current_bio": "📝 <b>Текущая биография:</b>\n{current_bio}",
        "choose_color": "🎨 <b>Выберите цвет оформления:</b>\n\n1️⃣ 🔴 Красный\n2️⃣ 🟠 Оранжевый\n3️⃣ 🟡 Желтый\n4️⃣ 🟢 Зеленый\n5️⃣ 🔵 Голубой\n6️⃣ 💙 Синий\n7️⃣ 🟣 Фиолетовый\n8️⃣ 🌸 Розовый\n9️⃣ ⚪ Белый\n🔟 ⚫ Серый",
        "invalid_color": "⚠️ <b>Неверный цвет! Выберите от 1 до 10</b>",
        "invalid_input": "⚠️ <b>Пожалуйста, введите ответ или '-' для пропуска</b>",
        "not_creator": "⚠️ <b>Вы не создаете биографию</b>",
        "creating": "🎨 <b>Создание биографии...</b>",
        "show_help": "📖 <b>Команды BioCreator:</b>\n\n<b>.biocreate</b> - создать биографию\n<b>.biosave</b> - сохранить текущую биографию\n<b>.biorestore</b> - восстановить сохраненную\n<b>.bioclear</b> - удалить биографию\n<b>.bioshow</b> - показать текущую\n<b>.biohelp</b> - справка",
        "skipped": "⏭ <b>Вопрос пропущен</b>",
        "bio_too_long": "⚠️ <b>Биография слишком длинная! Максимум 70 символов для Telegram</b>",
    }

    def __init__(self):
        self.creating_bio = {}
        self.saved_bio = None
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
            loader.ConfigValue(
                "max_bio_length",
                70,
                "Максимальная длина биографии",
                validator=loader.validators.Integer(minimum=1, maximum=70),
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
            ("👤", "Ваше полное имя, дата и место рождения"),
            ("👨‍👩‍👧", "Где и в какой семье вы родились"),
            ("🧸", "Ваше раннее детство: ключевые воспоминания, место жительства"),
            ("🏫", "Школьные годы: любимые предметы, увлечения, друзья"),
            ("🎓", "Высшее или среднее специальное образование: где, специальность, годы"),
            ("💼", "Первое место работы, должность, впечатления"),
            ("📈", "Основные этапы вашей карьеры (смена мест, должностей)"),
            ("🏆", "Самый значимый профессиональный успех"),
            ("💍", "Важные личные события: брак, рождение детей"),
            ("🏠", "Где и как вы жили в разные периоды жизни (переезды)"),
            ("🎨", "Ваши главные увлечения, хобби в разные годы"),
            ("🤝", "Ключевые люди, повлиявшие на вашу жизнь"),
            ("💪", "Самые трудные решения или кризисы и их преодоление"),
            ("✈️", "Путешествия или жизнь за границей: когда и где"),
            ("💎", "Ваши основные жизненные принципы и ценности"),
            ("🌟", "Чем вы гордитесь больше всего в жизни"),
            ("😔", "О чём жалеете или что бы изменили"),
            ("🕊", "Ваши отношения с религией, духовностью, философией"),
            ("🏅", "Общественная деятельность, волонтёрство, награды"),
            ("🏃", "Ваше здоровье и образ жизни (спорт, привычки)"),
            ("🎭", "Периоды творчества, изобретений, авторских проектов"),
            ("⏰", "Как вы проводите свободное время сейчас"),
            ("🔮", "Ваши планы и мечты на будущее"),
            ("📜", "Каким вы хотите, чтобы вас запомнили"),
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
    async def biosavecmd(self, message: Message):
        """Сохранить текущую биографию"""
        me = await self.client.get_me()
        if me.about:
            self.saved_bio = me.about
            await utils.answer(message, self.strings("bio_saved"))
        else:
            await utils.answer(message, self.strings("no_bio"))

    @loader.command()
    async def biorestorecmd(self, message: Message):
        """Восстановить сохраненную биографию"""
        if self.saved_bio:
            await self.client(UpdateProfileRequest(about=self.saved_bio))
            await utils.answer(message, self.strings("bio_updated").format(new_bio=self.saved_bio))
        else:
            await utils.answer(message, self.strings("no_bio"))

    @loader.command()
    async def bioclearcmd(self, message: Message):
        """Удалить биографию"""
        await self.client(UpdateProfileRequest(about=""))
        await utils.answer(message, self.strings("bio_deleted"))

    @loader.command()
    async def bioshowcmd(self, message: Message):
        """Показать текущую биографию"""
        me = await self.client.get_me()
        if me.about:
            await utils.answer(message, self.strings("current_bio").format(current_bio=me.about))
        else:
            await utils.answer(message, self.strings("no_bio"))

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
        """Создает биографию на основе ответов"""
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
        
        # Проверяем длину
        max_length = self.config["max_bio_length"]
        if len(bio) > max_length:
            bio = bio[:max_length-3] + "..."
        
        # Обновляем биографию
        await self.client(UpdateProfileRequest(about=bio))
        
        # Очищаем данные
        del self.creating_bio[user_id]
        
        # Показываем результат
        await utils.answer(message, self.strings("bio_updated").format(new_bio=bio))

    def _create_default_bio(self, answers, color_emoji, color_name, use_emoji):
        """Создает стандартную биографию"""
        # Берем только ключевые ответы для краткой биографии
        name = answers[0] if answers[0] else "Без имени"
        education = answers[4] if answers[4] else ""
        career = answers[6] if answers[6] else ""
        hobby = answers[10] if answers[10] else ""
        principles = answers[14] if answers[14] else ""
        
        bio = f"{color_emoji} {name}\n"
        
        if education:
            bio += f"├── 🎓 {education}\n"
        if career:
            bio += f"├── 💼 {career}\n"
        if hobby:
            bio += f"├── 🎨 {hobby}\n"
        if principles:
            bio += f"├── 💎 {principles}\n"
        
        bio += f"└── ✨ Создано с BioCreator"
        
        return bio

    def _create_minimal_bio(self, answers, color_emoji, use_emoji):
        """Создает минималистичную биографию"""
        name = answers[0] if answers[0] else ""
        education = answers[4] if answers[4] else ""
        hobby = answers[10] if answers[10] else ""
        principles = answers[14] if answers[14] else ""
        
        bio_parts = []
        if name:
            bio_parts.append(name)
        if education:
            bio_parts.append(education)
        if hobby:
            bio_parts.append(hobby)
        if principles:
            bio_parts.append(principles)
        
        return " • ".join(bio_parts) if bio_parts else "Биография"

    def _create_creative_bio(self, answers, color_emoji, color_name, use_emoji):
        """Создает креативную биографию"""
        name = answers[0] if answers[0] else "Без имени"
        education = answers[4] if answers[4] else ""
        career = answers[6] if answers[6] else ""
        hobby = answers[10] if answers[10] else ""
        achievements = answers[15] if answers[15] else ""
        dreams = answers[22] if answers[22] else ""
        
        bio = f"╔═══ {color_emoji} {name} ═══╗\n"
        
        if education:
            bio += f"║ 📚 {education}\n"
        if career:
            bio += f"║ 💼 {career}\n"
        if hobby:
            bio += f"║ 🎯 {hobby}\n"
        if achievements:
            bio += f"║ 🏆 {achievements}\n"
        if dreams:
            bio += f"║ 🔮 {dreams}\n"
        
        bio += f"╚{'═' * 20}╝"
        
        return bio
