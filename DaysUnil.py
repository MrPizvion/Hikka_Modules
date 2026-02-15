from .. import loader, utils
import datetime
import logging

logger = logging.getLogger(__name__)

@loader.tds
class DaysUntilMod(loader.Module):
    """Модуль для отслеживания дней до дня рождения и других событий 🎂"""
    
    strings = {
        "name": "DaysUntil",
        "no_args": "🚫 <b>Укажи команду</b>\nПример: <code>.days 100</code> или <code>.bd</code>",
        "no_date": "🚫 <b>Сначала настрой дату рождения в конфиге!</b>\nИспользуй <code>.config DaysUntil</code>",
        "days_left": """<b>🎂 Дней до дня рождения: {days}</b>

📅 <b>Точное время:</b>
⏰ {days} дней
🕐 {hours} часов
⏱️ {minutes} минут
⚡ {seconds} секунд

📊 <b>Прогресс:</b>
{progress_bar} {percent}%

🎯 <b>Дата рождения:</b> {birthday}
📆 <b>Текущая дата:</b> {today}""",

        "days_custom": """<b>⏳ До {event}: {days} дней</b>

📅 <b>Точное время:</b>
⏰ {days} дней
🕐 {hours} часов
⏱️ {minutes} минут
⚡ {seconds} секунд""",

        "days_saved": "✅ <b>Сохранено:</b> {days} дней до {event}",
        "list_header": "<b>📋 Список сохранённых событий:</b>\n\n",
        "list_item": "{num}. {event} — <b>{days} дней</b>\n",
        "no_events": "📭 <b>Нет сохранённых событий</b>",
        "error": "❌ <b>Ошибка:</b> {}",
        "deleted": "✅ <b>Удалено:</b> {event} — {days} дней",
        "cleared": "🗑️ <b>Все события удалены</b>",
        "invalid_number": "🚫 <b>Укажи номер события из списка</b>\nПример: <code>.del 2</code>",
        "wrong_number": "❌ <b>Неверный номер события</b>",
        "help": """<b>🎂 DaysUntil Module</b>

<b>Основные команды:</b>
<code>.bd</code> - показать дней до ДР
<code>.days N</code> - показать дней до N-дней
<code>.days название N</code> - сохранить событие
<code>.list</code> - список всех событий
<code>.del НОМЕР</code> - удалить событие
<code>.clear</code> - очистить все

<b>⚙️ Настройка ДР в конфиге:</b>
<code>.config DaysUntil</code>

<b>✨ Примеры:</b>
<code>.days 100</code>
<code>.days НГ 30</code>
<code>.list</code>
<code>.del 2</code>"""
    }
    
    strings_ru = {
        "name": "DaysUntil",
        "no_args": "🚫 <b>Укажи команду</b>\nПример: <code>.days 100</code> или <code>.bd</code>",
        "no_date": "🚫 <b>Сначала настрой дату рождения в конфиге!</b>\nИспользуй <code>.config DaysUntil</code>",
        "days_left": """<b>🎂 Дней до дня рождения: {days}</b>

📅 <b>Точное время:</b>
⏰ {days} дней
🕐 {hours} часов
⏱️ {minutes} минут
⚡ {seconds} секунд

📊 <b>Прогресс:</b>
{progress_bar} {percent}%

🎯 <b>Дата рождения:</b> {birthday}
📆 <b>Текущая дата:</b> {today}""",

        "days_custom": """<b>⏳ До {event}: {days} дней</b>

📅 <b>Точное время:</b>
⏰ {days} дней
🕐 {hours} часов
⏱️ {minutes} минут
⚡ {seconds} секунд""",

        "days_saved": "✅ <b>Сохранено:</b> {days} дней до {event}",
        "list_header": "<b>📋 Список сохранённых событий:</b>\n\n",
        "list_item": "{num}. {event} — <b>{days} дней</b>\n",
        "no_events": "📭 <b>Нет сохранённых событий</b>",
        "error": "❌ <b>Ошибка:</b> {}",
        "deleted": "✅ <b>Удалено:</b> {event} — {days} дней",
        "cleared": "🗑️ <b>Все события удалены</b>",
        "invalid_number": "🚫 <b>Укажи номер события из списка</b>\nПример: <code>.del 2</code>",
        "wrong_number": "❌ <b>Неверный номер события</b>",
        "help": """<b>🎂 DaysUntil Module</b>

<b>Основные команды:</b>
<code>.bd</code> - показать дней до ДР
<code>.days N</code> - показать дней до N-дней
<code>.days название N</code> - сохранить событие
<code>.list</code> - список всех событий
<code>.del НОМЕР</code> - удалить событие
<code>.clear</code> - очистить все

<b>⚙️ Настройка ДР в конфиге:</b>
<code>.config DaysUntil</code>

<b>✨ Примеры:</b>
<code>.days 100</code>
<code>.days НГ 30</code>
<code>.list</code>
<code>.del 2</code>"""
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "birthday_day",
                1,
                "День рождения (1-31)",
                validator=loader.validators.Integer(minimum=1, maximum=31)
            ),
            loader.ConfigValue(
                "birthday_month",
                1,
                "Месяц рождения (1-12)",
                validator=loader.validators.Integer(minimum=1, maximum=12)
            ),
        )
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        # Загружаем сохранённые события
        self.events = self.db.get("DaysUntil", "events", {})
        logger.info(f"DaysUntil: Загружено {len(self.events)} событий")
    
    async def bdcmd(self, message):
        """<ник> [:<режим>] - Показать дней до дня рождения"""
        day = self.config["birthday_day"]
        month = self.config["birthday_month"]
        
        if not day or not month:
            await utils.answer(message, self.strings("no_date"))
            return
        
        now = datetime.datetime.now()
        current_year = now.year
        
        # Дата рождения в этом году
        birthday = datetime.datetime(current_year, month, day)
        
        # Если ДР уже прошёл в этом году, берём следующий год
        if birthday < now:
            birthday = datetime.datetime(current_year + 1, month, day)
        
        # Разница
        delta = birthday - now
        
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60
        
        # Прогресс-бар
        if birthday.year > current_year:
            # ДР в следующем году
            year_start = datetime.datetime(current_year + 1, 1, 1)
            year_end = datetime.datetime(current_year + 1, 12, 31)
            total_days = (year_end - year_start).days
            days_passed = (birthday - year_start).days
            percent = int((days_passed / total_days) * 100)
        else:
            # ДР в этом году
            year_start = datetime.datetime(current_year, 1, 1)
            total_days = 365
            days_passed = (birthday - year_start).days
            percent = int((days_passed / total_days) * 100)
        
        progress_bar = self._make_progress_bar(percent)
        
        await utils.answer(message, self.strings("days_left").format(
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            progress_bar=progress_bar,
            percent=percent,
            birthday=f"{day:02d}.{month:02d}",
            today=now.strftime("%d.%m.%Y %H:%M")
        ))
    
    async def dayscmd(self, message):
        """.days [название] <число> - Показать дней до N-дней или сохранить событие"""
        args = utils.get_args_raw(message).split()
        
        if not args:
            await utils.answer(message, self.strings("no_args"))
            return
        
        # Если только число
        if len(args) == 1:
            try:
                days = int(args[0])
                await self._show_days_until(message, days)
            except ValueError:
                await utils.answer(message, self.strings("error").format("Неверный формат числа"))
        
        # Если название и число
        elif len(args) >= 2:
            try:
                days = int(args[-1])
                event_name = " ".join(args[:-1])
                
                # Сохраняем событие
                self.events[event_name] = days
                self.db.set("DaysUntil", "events", self.events)
                logger.info(f"DaysUntil: Сохранено событие '{event_name}' на {days} дней")
                
                await utils.answer(message, self.strings("days_saved").format(
                    event=event_name,
                    days=days
                ))
            except ValueError:
                await utils.answer(message, self.strings("error").format("Неверный формат числа"))
    
    async def listcmd(self, message):
        """Показать список всех сохранённых событий"""
        if not self.events:
            await utils.answer(message, self.strings("no_events"))
            return
        
        text = self.strings("list_header")
        for i, (event, days) in enumerate(self.events.items(), 1):
            text += self.strings("list_item").format(num=i, event=event, days=days)
        
        text += "\n<b>💡 Используй:</b> <code>.del НОМЕР</code> чтобы удалить"
        await utils.answer(message, text)
    
    async def delcmd(self, message):
        """.del <номер> - Удалить событие из списка"""
        args = utils.get_args_raw(message)
        
        if not args or not args.isdigit():
            await utils.answer(message, self.strings("invalid_number"))
            return
        
        index = int(args) - 1
        events_list = list(self.events.items())
        
        if index < 0 or index >= len(events_list):
            await utils.answer(message, self.strings("wrong_number"))
            return
        
        event_name, days = events_list[index]
        del self.events[event_name]
        self.db.set("DaysUntil", "events", self.events)
        logger.info(f"DaysUntil: Удалено событие '{event_name}'")
        
        await utils.answer(message, self.strings("deleted").format(
            event=event_name,
            days=days
        ))
    
    async def clearcmd(self, message):
        """Очистить все сохранённые события"""
        self.events = {}
        self.db.set("DaysUntil", "events", {})
        logger.info("DaysUntil: Все события удалены")
        await utils.answer(message, self.strings("cleared"))
    
    async def daysuntilhelpcmd(self, message):
        """Показать помощь по модулю"""
        await utils.answer(message, self.strings("help"))
    
    async def _show_days_until(self, message, target_days: int):
        """Показать дней до N-дней"""
        now = datetime.datetime.now()
        
        # Дата через N дней
        future_date = now + datetime.timedelta(days=target_days)
        
        # Разница
        delta = future_date - now
        
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60
        
        # Определяем окончание
        if target_days % 10 == 1 and target_days % 100 != 11:
            word = "дня"
        elif 2 <= target_days % 10 <= 4 and (target_days % 100 < 10 or target_days % 100 >= 20):
            word = "дней"
        else:
            word = "дней"
        
        await utils.answer(message, self.strings("days_custom").format(
            event=f"{target_days} {word}",
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds
        ))
    
    def _make_progress_bar(self, percent: int, length: int = 10) -> str:
        """Создаёт прогресс-бар"""
        filled = int(percent / 100 * length)
        empty = length - filled
        return "█" * filled + "░" * empty

    async def on_unload(self):
        """Сохраняем данные при выгрузке"""
        self.db.set("DaysUntil", "events", self.events)
        logger.info("DaysUntil: Данные сохранены")
