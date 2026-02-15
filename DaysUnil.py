from .. import loader, utils
import datetime
import logging

logger = logging.getLogger(__name__)

@loader.tds
class DaysUntilMod(loader.Module):
    """Модуль для отслеживания дней до дня рождения 🎂"""
    
    strings = {
        "name": "DaysUntil",
        "no_args": "🚫 <b>Укажи команду</b>\nПример: <code>.days 100</code> или <code>.bd</code>",
        "no_date": "🚫 <b>Сначала настрой дату рождения!</b>",
        "days_left": """<b>🎂 До дня рождения осталось:</b>
<b>{days} дней</b>

⏰ {hours} ч {minutes} мин {seconds} сек""",
        "days_custom": """<b>⏳ До {event}:</b>
<b>{days} дней</b>

⏰ {hours} ч {minutes} мин {seconds} сек""",
        "days_saved": "✅ <b>Сохранено:</b> {days} дней до {event}",
        "list_header": "<b>📋 События:</b>\n",
        "list_item": "{num}. {event} — {days} дн\n",
        "no_events": "📭 <b>Нет событий</b>",
        "error": "❌ {0}",
        "deleted": "✅ <b>Удалено:</b> {event}",
        "cleared": "🗑️ <b>Все события удалены</b>",
        "set_birthday": "🎂 <b>Выбери месяц рождения:</b>",
        "set_day": "🎂 <b>Выбери день рождения:</b>",
        "birthday_set": "✅ <b>Дата рождения сохранена: {day:02d}.{month:02d}</b>",
        "help": """<b>🎂 DaysUntil</b>

<code>.bd</code> - дней до ДР
<code>.days N</code> - дней до N
<code>.days НГ 30</code> - сохранить
<code>.list</code> - список
<code>.del N</code> - удалить
<code>.setbd</code> - настроить ДР"""
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
        h = delta.seconds // 3600
        m = (delta.seconds % 3600) // 60
        s = delta.seconds % 60
        
        await utils.answer(message, self.strings("days_left").format(
            days=delta.days, hours=h, minutes=m, seconds=s
        ))
    
    async def setbdcmd(self, message):
        """Настроить дату рождения через инлайн"""
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
        
        if len(args) == 1:
            try:
                days = int(args[0])
                await self._show_days(message, days)
            except:
                await utils.answer(message, self.strings("error").format("Не число"))
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
        """Список событий"""
        if not self.events:
            await utils.answer(message, self.strings("no_events"))
            return
        
        text = self.strings("list_header")
        for i, (e, d) in enumerate(self.events.items(), 1):
            text += self.strings("list_item").format(num=i, event=e, days=d)
        await utils.answer(message, text)
    
    async def delcmd(self, message):
        """Удалить событие"""
        args = utils.get_args_raw(message)
        if not args or not args.isdigit():
            await utils.answer(message, "🚫 Укажи номер")
            return
        
        idx = int(args) - 1
        items = list(self.events.items())
        if idx < 0 or idx >= len(items):
            await utils.answer(message, "❌ Неверный номер")
            return
        
        name, _ = items[idx]
        del self.events[name]
        self.db.set("DaysUntil", "events", self.events)
        await utils.answer(message, self.strings("deleted").format(event=name))
    
    async def clearcmd(self, message):
        """Очистить всё"""
        self.events = {}
        self.db.set("DaysUntil", "events", {})
        await utils.answer(message, self.strings("cleared"))
    
    async def _show_days(self, message, target: int):
        """Показать дней до N"""
        now = datetime.datetime.now()
        future = now + datetime.timedelta(days=target)
        delta = future - now
        h = delta.seconds // 3600
        m = (delta.seconds % 3600) // 60
        s = delta.seconds % 60
        
        if target % 10 == 1 and target % 100 != 11:
            word = "дня"
        else:
            word = "дней"
        
        await utils.answer(message, self.strings("days_custom").format(
            event=f"{target} {word}",
            days=delta.days, hours=h, minutes=m, seconds=s
        ))
    
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
        """Обработчик выбора месяца"""
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
        """Обработчик выбора дня"""
        self.config["month"] = month
        self.config["day"] = day
        
        await call.edit(
            text=self.strings("birthday_set").format(day=day, month=month)
        )
    
    async def on_unload(self):
        self.db.set("DaysUntil", "events", self.events)
