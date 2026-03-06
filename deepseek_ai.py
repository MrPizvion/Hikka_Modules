# meta developer: @твой_юзернейм
# meta pic: none
# meta banner: https://example.com/banner.jpg

from .. import loader, utils
import aiohttp
import asyncio
import logging

logger = logging.getLogger(__name__)

@loader.tds
class DeepSeekAIMod(loader.Module):
    """Модуль для работы с DeepSeek AI (официальное API)"""
    
    strings = {
        "name": "DeepSeek AI",
        "no_query": "❓ <b>Что спросить?</b>\nИспользование: <code>.ai [вопрос]</code>",
        "thinking": "🤔 <b>Думаю...</b>",
        "error": "❌ <b>Ошибка:</b> {}",
        "no_token": "❌ <b>Токен не найден!</b>\nУстановите токен: <code>.set_token [токен]</code>",
        "token_set": "✅ <b>Токен успешно установлен!</b>",
        "api_error": "🌐 <b>Ошибка API:</b> {}",
        "help": """<b>🆘 Помощь по модулю DeepSeek AI</b>

<b>Основные команды:</b>
<code>.ai [вопрос]</code> - Задать вопрос DeepSeek
<code>.ai_chat [текст]</code> - Продолжить диалог
<code>.ai_clear</code> - Очистить историю диалога
<code>.set_token [токен]</code> - Установить API токен
<code>.ai_help</code> - Показать это сообщение

<b>Примеры:</b>
<code>.ai Привет, как дела?</code>
<code>.ai_chat Расскажи подробнее</code>

<b>Токен нужно получить на:</b> platform.deepseek.com"""
    }
    
    strings_ru = {
        "name": "DeepSeek AI",
        "no_query": "❓ <b>Что спросить?</b>\nИспользование: <code>.ai [вопрос]</code>",
        "thinking": "🤔 <b>Думаю...</b>",
        "error": "❌ <b>Ошибка:</b> {}",
        "no_token": "❌ <b>Токен не найден!</b>\nУстановите токен: <code>.set_token [токен]</code>",
        "token_set": "✅ <b>Токен успешно установлен!</b>",
        "api_error": "🌐 <b>Ошибка API:</b> {}",
        "help": """<b>🆘 Помощь по модулю DeepSeek AI</b>

<b>Основные команды:</b>
<code>.ai [вопрос]</code> - Задать вопрос DeepSeek
<code>.ai_chat [текст]</code> - Продолжить диалог
<code>.ai_clear</code> - Очистить историю диалога
<code>.set_token [токен]</code> - Установить API токен
<code>.ai_help</code> - Показать это сообщение

<b>Примеры:</b>
<code>.ai Привет, как дела?</code>
<code>.ai_chat Расскажи подробнее</code>

<b>Токен нужно получить на:</b> platform.deepseek.com"""
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "api_token",
                None,
                "API токен DeepSeek",
                validator=loader.validators.Hidden()
            ),
            loader.ConfigValue(
                "model",
                "deepseek-chat",
                "Модель DeepSeek (deepseek-chat или deepseek-coder)",
                validator=loader.validators.Choice(["deepseek-chat", "deepseek-coder"])
            ),
            loader.ConfigValue(
                "temperature",
                0.7,
                "Температура генерации (0.0 - 2.0)",
                validator=loader.validators.Float(minimum=0.0, maximum=2.0)
            ),
            loader.ConfigValue(
                "max_history",
                10,
                "Максимальное количество сообщений в истории",
                validator=loader.validators.Integer(minimum=1, maximum=50)
            )
        )
        
        self.history = []
        
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        
    @loader.command()
    async def set_token(self, message):
        """<токен> - Установить API токен DeepSeek"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "❌ <b>Укажите токен!</b>")
            return
            
        self.config["api_token"] = args.strip()
        await utils.answer(message, self.strings("token_set"))
        
    @loader.command()
    async def ai_help(self, message):
        """Показать помощь по модулю"""
        await utils.answer(message, self.strings("help"))
        
    @loader.command()
    async def ai_clear(self, message):
        """Очистить историю диалога"""
        self.history = []
        await utils.answer(message, "✅ <b>История диалога очищена!</b>")
        
    @loader.command()
    async def ai(self, message):
        """<вопрос> - Задать вопрос DeepSeek"""
        query = utils.get_args_raw(message)
        if not query:
            await utils.answer(message, self.strings("no_query"))
            return
            
        # Проверяем наличие токена
        token = self.config["api_token"]
        if not token:
            await utils.answer(message, self.strings("no_token"))
            return
            
        # Отправляем сообщение о начале обработки
        thinking_msg = await utils.answer(message, self.strings("thinking"))
        
        try:
            # Формируем сообщения для API
            messages = []
            
            # Добавляем историю (если есть)
            for msg in self.history[-self.config["max_history"]*2:]:
                messages.append(msg)
                
            # Добавляем новый запрос
            messages.append({"role": "user", "content": query})
            
            # Отправляем запрос к API
            response = await self._call_deepseek_api(messages)
            
            # Сохраняем в историю
            self.history.append({"role": "user", "content": query})
            self.history.append({"role": "assistant", "content": response})
            
            # Ограничиваем историю
            if len(self.history) > self.config["max_history"] * 2:
                self.history = self.history[-(self.config["max_history"] * 2):]
            
            # Форматируем ответ
            formatted_response = self._format_response(response)
            await utils.answer(thinking_msg, formatted_response)
            
        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            await utils.answer(thinking_msg, self.strings("api_error").format(str(e)))
            
    @loader.command()
    async def ai_chat(self, message):
        """<текст> - Продолжить диалог"""
        await self.ai(message)
        
    async def _call_deepseek_api(self, messages):
        """Отправка запроса к DeepSeek API"""
        token = self.config["api_token"]
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config["model"],
            "messages": messages,
            "temperature": self.config["temperature"],
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise Exception(f"HTTP {resp.status}: {error_text}")
                    
                result = await resp.json()
                return result["choices"][0]["message"]["content"]
                
    def _format_response(self, text):
        """Форматирование ответа для Telegram"""
        # Ограничиваем длину сообщения (Telegram лимит ~4096 символов)
        if len(text) > 4000:
            text = text[:4000] + "...\n\n<i>Сообщение обрезано из-за лимита Telegram</i>"
            
        # Экранируем HTML
        text = text.replace("<", "&lt;").replace(">", "&gt;")
        
        # Добавляем красивый заголовок
        return f"🤖 <b>DeepSeek AI:</b>\n\n{text}"
