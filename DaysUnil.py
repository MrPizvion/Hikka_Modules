from .. import loader, utils
import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)

@loader.tds
class DaysUntilMod(loader.Module):
    """Модуль для автообновления фамилии количеством дней до ДР 🎂"""
    
    strings = {
        "name": "DaysUntil",
        "no_date": "🚫 <b>Сначала настрой дату рождения!</b>\nИспользуй <code>.setbd</code>",
        "updated": "✅ <b>Фамилия обновлена:</b> {days} дней",
        "started": "🔄 <b>Автообновление запущено! Фамилия будет меняться каждый день</b>",
        "stopped": "⏹️ <b>Автообновление остановлено</b>",
        "set_birthday": "🎂 <b>Выбери месяц рождения:</b>",
        "set_day": "🎂 <b>Выбери день рождения:</b>",
        "birthday_set": "✅ <b>Дата рождения: {day:02d}.{month:02d}</b>\n🔄 <b>Фамилия будет обновлена автоматически</b>",
        "help": """<b>🎂 DaysUntil</b>

<b>📋 Команды:</b>
<code>.setbd</code> - настроить дату рождения
<code>.update</code> - обновить фамилию сейчас
<code>.autoupdate</code> - включить автообновление
<code>.stop</code> - выключить автообновление

<b>✨ Что делает:</b>
Меняет твою фамилию в профиле на количество дней до ДР
Пример: "154 дня"
"""
    }
    
    strings_ru = {
        "name": "DaysUntil",
        "no_date": "🚫 <b>Сначала настрой дату рождения!</b>\nИспользуй <code>.setbd</code>",
        "updated": "✅ <b>Фамилия обновлена:</b> {days} дней",
        "started": "🔄 <b>Автообновление запущено! Фамилия будет меняться каждый день</b>",
        "stopped": "⏹️ <b>Автообновление остановлено</b>",
        "set_birthday": "🎂 <b>Выбери месяц рождения:</b>",
        "set_day": "🎂 <b>Выбери день рождения:</b>",
        "birthday_set": "✅ <b>Дата рождения: {day:02d}.{month:02d}</b>\n🔄 <b>Фамилия будет обновлена автоматически</b>",
        "help": """<b>🎂 DaysUntil</b>

<b>📋 Команды:</b>
<code>.setbd</code> - настроить дату рождения
<code>.update</code> - обновить фамилию сейчас
<code>.autoupdate</code> - включить автообновление
<code>.stop</code> - выключить автообновление

<b>✨ Что делает:</b>
Меняет твою фамилию в профиле на количество дней до ДР
Пример: "154 дня"
"""
    }
    
    months = ["Янв", "Фев", "Мар", "Апр", "Май", "Июн",
              "Июл", "Авг", "Сен", "Окт", "Ноя", "Дек"]
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue("day", None, "День рождения"),
            loader.ConfigValue("month", None, "Месяц рождения"),
            loader.ConfigValue("auto", False, "Автообновление включено?"),
        )
        self.task = None
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        
        # Запускаем автообновление если было включено
        if self.config["auto"] and self.config["day"] and self.config["month"]:
            self.task = asyncio.ensure_future(self._auto_update())
    
    async def setbdcmd(self, message):
        """Настроить дату рождения через инлайн"""
        await self.inline.form(
            text=self.strings("set_birthday"),
            message=message,
            reply_markup=self._month_buttons()
        )
    
    async def updatecmd(self, message):
        """Обновить фамилию сейчас"""
        if not self.config["day"] or not self.config["month"]:
            await utils.answer(message, self.strings("no_date"))
            return
        
        days = self._get_days_until()
        await self._update_lastname(days)
        await utils.answer(message, self.strings("updated").format(days=days))
    
    async def autoupdatecmd(self, message):
        """Включить автообновление"""
        if not self.config["day"] or not self.config["month"]:
            await utils.answer(message, self.strings("no_date"))
            return
        
        self.config["auto"] = True
        
        if self.task:
            self.task.cancel()
        
        self.task = asyncio.ensure_future(self._auto_update())
        await utils.answer(message, self.strings("started"))
    
    async def stopcmd(self, message):
        """Выключить автообновление"""
        self.config["auto"] = False
        if self.task:
            self.task.cancel()
            self.task = None
        await utils.answer(message, self.strings("stopped"))
    
    def _get_days_until(self):
        """Посчитать дней до ДР"""
        now = datetime.datetime.now()
        day = self.config["day"]
        month = self.config["month"]
        
        bd = datetime.datetime(now.year, month, day)
        if bd < now:
            bd = datetime.datetime(now.year + 1, month, day)
        
        delta = bd - now
        return delta.days
    
    async def _update_lastname(self, days: int):
        """Изменить фамилию в профиле"""
        try:
            # Получаем текущий профиль
            me = await self.client.get_me()
            
            # Формируем новую фамилию
            if days % 10 == 1 and days % 100 != 11:
                lastname = f"{days} день"
            elif 2 <= days % 10 <= 4 and (days % 100 < 10 or days % 100 >= 20):
                lastname = f"{days} дня"
            else:
                lastname = f"{days} дней"
            
            # Обновляем профиль
            await self.client(UpdateProfileRequest(
                first_name=me.first_name,
                last_name=lastname
            ))
            
            logger.info(f"Фамилия обновлена: {lastname}")
            
        except Exception as e:
            logger.error(f"Ошибка обновления фамилии: {e}")
    
    async def _auto_update(self):
        """Автоматическое обновление каждый день"""
        while self.config["auto"]:
            try:
                days = self._get_days_until()
                await self._update_lastname(days)
                
                # Ждём до следующего дня (24 часа)
                await asyncio.sleep(24 * 60 * 60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ошибка в автообновлении: {e}")
                await asyncio.sleep(60)  # Если ошибка, подождать минуту
    
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
        
        # Сразу обновляем фамилию
        days = self._get_days_until()
        await self._update_lastname(days)
        
        await call.edit(
            text=self.strings("birthday_set").format(day=day, month=month)
        )
    
    async def on_unload(self):
        """При выгрузке модуля"""
        if self.task:
            self.task.cancel()
        self.config["auto"] = False
