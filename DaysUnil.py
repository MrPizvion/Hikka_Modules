from .. import loader, utils
import datetime
import logging

logger = logging.getLogger(__name__)

@loader.tds
class DaysUntilMod(loader.Module):
    """Модуль для отслеживания дней до событий 🎂"""
    
    strings = {
        "name": "DaysUntil",
        "no_args": "🚫 <b>Укажи команду</b>\nПример: <code>.days 100</code> или <code>.bd</code>",
        "no_date": "🚫 <b>Сначала настрой дату рождения!</b>",
        "days_left": "<b>🎂 До дня рождения:</b> <code>{days} дней</code>",
        "days_custom": "<b>⏳ До {event}:</b> <code>{days} дней</code>",
        "days_saved": "✅ <b>Сохранено:</b> {event} — {days} дней",
        "list_header": "<b>📋 Список событий:</b>\n",
        "list_item": "{num}. {event} — <code>{days} дней</code>\n",
        "no_events": "📭 <b>Нет сохранённых событий</b>",
        "error": "❌ {0}",
        "deleted": "✅ <b>Удалено:</b> {event}",
        "cleared": "🗑️ <b>Все события удалены</b>",
        "set_birthday": "🎂 <b>Выбери месяц рождения:</b>",
        "set_day": "🎂 <b>Выбери день рождения:</b>",
        "birthday_set": "✅ <b>Дата рождения: {day:02d}.{month:02d}</b>",
        "help": """<b>🎂 DaysUntil</b>

<code>.bd</code> - дней до ДР
<code>.days число</code> - дней до N дней
<code>.days название число</code> - сохранить событие
<code>.list</code> - список событий
<code>.del N</code> - удалить событие
<code>.setbd</code> - настроить ДР
<code>.clear</code> - очистить всё

<b>✨ Примеры:</b>
<code>.days 100</code>
<code>.days Маша 45</code>
<code>.days Петя 30</code>
<code>.list</code>"""
    }
    
    strings_ru = {
        "name": "DaysUntil",
        "no_args": "🚫 <b>Укажи команду</b>\nПример: <code>.days 100</code> или <code>.bd</code>",
        "no_date": "🚫 <b>Сначала настрой дату рождения!</b>",
        "days_left": "<b>🎂 До дня рождения:</b> <code>{days} дней</code>",
        "days_custom": "<b>⏳ До {event}:</b> <code>{days} дней</code>",
        "days_saved": "✅ <b>Сохранено:</b> {event} — {days} дней",
        "list_header": "<b>📋 Список событий:</b>\n",
        "list_item": "{num}. {event} — <code>{days} дней</code>\n",
        "no_events": "📭 <b>Нет сохранённых событий</b>",
        "error": "❌ {0}",
        "deleted": "✅ <b>Удалено:</b> {event}",
        "cleared": "🗑️ <b>Все события удалены</b>",
        "set_birthday": "🎂 <b>Выбери месяц рождения:</b>",
        "set_day": "🎂 <b>Выбери день рождения:</b>",
        "birthday_set": "✅ <b>Дата рождения: {day:02d}.{month:02d}</b>",
        "help": """<b>🎂 DaysUntil</b>

<code>.bd</code> - дней до ДР
<code>.days число</code> - дней до N дней
<code>.days название число</code> - сохранить событие
<code>.list</code> - список событий
<code>.del N</code> - удалить событие
<code>.setbd</code> - настроить ДР
<code>.clear</code> - очистить всё

<b>✨ Примеры:</b>
<code>.days 100</code>
<code>.days Маша 45</code>
<code>.days Петя 30</code>
<code>.list</code>"""
    }
    
    months = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн",
              "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue("day", 1, "День рождения"),
            loader.ConfigValue("month", 1, "Месяц рождения"),
        )
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.events = self.db.get("DaysUntil", "events", {})
    
    async def bdcmd(self, message):
        """Показать дней до ДР"""
        day = self.config["day"]
        month = self.config["month"]
        
        now = datetime.datetime.now()
        bd = datetime.datetime(now.year, month, day)
        if bd < now:
            bd = datetime.datetime(now.year + 1, month, day)
        
        delta = bd - now
        
        await utils.answer(message, self.strings("days_left").format(
            days=delta.days
        ))
    
    async def setbdcmd(self, message):
        """Настроить дату рождения"""
        await self.inline.form(
            text=self.strings("set_birthday"),
            message=message,
            reply_markup=self._month_buttons()
        )
    
    async def dayscmd(self, message):
        """Сохранить или показать событие"""
        args = utils.get_args_raw(message).split()
        if not args:
            await utils.answer(message, self.strings("no_args"))
            return
        
        # Если только число
        if len(args) == 1:
            try:
                days = int(args[0])
                now = datetime.datetime.now()
                future = now + datetime.timedelta(days=days)
                delta = future - now
                
                if days % 10 == 1 and days % 100 != 11:
                    word = "дня"
                else:
                    word = "дней"
                
                await utils.answer(message, self.strings("days_custom").format(
                    event=f"{days} {word}",
                    days=delta.days
                ))
            except:
                await utils.answer(message, self.strings("error").format("Не число"))
        
        # Если название и число
        else:
            try:
                days = int(args[-1])
                name = " ".join(args[:-1])
                self.events[name] = days
                self.db.set("DaysUntil", "events", self.events)
                await utils.answer(message, self.strings("days_saved").format(
                    event=name, days=days
                ))
            except:
                await utils.answer(message, self.strings("error").format("Ошибка"))
    
    async def listcmd(self, message):
        """Список всех событий"""
        if not self.events:
            await utils.answer(message, self.strings("no_events"))
            return
        
        text = self.strings("list_header")
        for i, (name, days) in enumerate(self.events.items(), 1):
            text += self.strings("list_item").format(num=i, event=name, days=days)
        await utils.answer(message, text)
    
    async def delcmd(self, message):
        """Удалить событие по номеру"""
        args = utils.get_args_raw(message)
        if not args or not args.isdigit():
            await utils.answer(message, "🚫 <b>Укажи номер из списка .list</b>")
            return
        
        idx = int(args) - 1
        items = list(self.events.items())
        if idx < 0 or idx >= len(items):
            await utils.answer(message, "❌ <b>Неверный номер</b>")
            return
        
        name, days = items[idx]
        del self.events[name]
        self.db.set("DaysUntil", "events", self.events)
        await utils.answer(message, self.strings("deleted").format(event=name))
    
    async def clearcmd(self, message):
        """Очистить все события"""
        self.events = {}
        self.db.set("DaysUntil", "events", {})
        await utils.answer(message, self.strings("cleared"))
    
    def _month_buttons(self):
        """Кнопки выбора месяца"""
        rows = []
        for i in range(0, 12, 3):
            row = []
            for j in range(3):
                if i + j < 12:
                    month_num = i + j + 1
                    row.append({
                        "text": self.months[i + j],
                        "callback": self._month_cb,
                        "args": (month_num,)
                    })
            rows.append(row)
        return rows
    
    async def _month_cb(self, call, month: int):
        """Выбор месяца"""
        await call.edit(
            text=self.strings("set_day"),
            reply_markup=self._day_buttons(month)
        )
    
    def _day_buttons(self, month: int):
        """Кнопки выбора дня"""
        days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        max_days = days_in_month[month - 1]
        
        rows = []
        for i in range(0, max_days, 5):
            row = []
            for j in range(5):
                if i + j < max_days:
                    day = i + j + 1
                    row.append({
                        "text": str(day),
                        "callback": self._day_cb,
                        "args": (month, day)
                    })
            rows.append(row)
        return rows
    
    async def _day_cb(self, call, month: int, day: int):
        """Выбор дня"""
        self.config["month"] = month
        self.config["day"] = day
        await call.edit(
            text=self.strings("birthday_set").format(day=day, month=month)
        )
    
    async def on_unload(self):
        self.db.set("DaysUntil", "events", self.events)
