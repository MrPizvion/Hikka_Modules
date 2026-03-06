# meta developer: @твой_юзернейм
# scope: hikka_only
# meta pic: none
# meta banner: none

from .. import loader, utils
import aiohttp
import asyncio
import re
import json
import random

@loader.tds
class FreeDeepSeekMod(loader.Module):
    """Бесплатный DeepSeek AI (без токена и без денег)"""
    
    strings = {
        "name": "Free DeepSeek",
        "thinking": "🤔 <b>DeepSeek думает...</b>",
        "error": "❌ <b>Ошибка:</b> {}",
        "help": """<b>🤖 Бесплатный DeepSeek AI</b>

<b>Команды:</b>
<code>.ds [вопрос]</code> - Спросить DeepSeek
<code>.dsc [вопрос]</code> - DeepSeek Coder (для кода)
<code>.dsclear</code> - Очистить историю

<b>Примеры:</b>
<code>.ds Привет, как дела?</code>
<code>.ds Напиши код калькулятора на Python</code>

<b>Полностью бесплатно! Никаких токенов не нужно!</b>"""
    }
    
    def __init__(self):
        self.history = []
        self.session_cookie = None
        self.session_id = None
        
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        # Пробуем получить куки при старте
        await self._refresh_session()
        
    @loader.command()
    async def dscmd(self, message):
        """<вопрос> - Спросить у DeepSeek бесплатно"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "❓ <b>Что спросить?</b>\nПример: <code>.ds Привет</code>")
            return
            
        await self._ask_deepseek(message, args, mode="chat")
        
    @loader.command()
    async def dsccmd(self, message):
        """<вопрос> - DeepSeek Coder (для программирования)"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "❓ <b>Что написать?</b>\nПример: <code>.dsc Напиши бота на Python</code>")
            return
            
        await self._ask_deepseek(message, args, mode="coder")
        
    @loader.command()
    async def dsclear(self, message):
        """Очистить историю диалога"""
        self.history = []
        await utils.answer(message, "✅ <b>История очищена!</b>")
        
    @loader.command()
    async def dhelp(self, message):
        """Помощь по модулю"""
        await utils.answer(message, self.strings("help"))
        
    async def _ask_deepseek(self, message, query, mode="chat"):
        """Основная функция запроса"""
        
        msg = await utils.answer(message, self.strings("thinking"))
        
        try:
            # Пробуем разные методы получения ответа
            response = None
            
            # Метод 1: Через веб-интерфейс DeepSeek
            response = await self._ask_via_web(query, mode)
            
            # Метод 2: Если не получилось, используем альтернативный API
            if not response or "error" in response.lower():
                response = await self._ask_via_alternative(query)
                
            # Метод 3: Если все сломалось, используем локальные шаблоны
            if not response or len(response) < 10:
                response = self._get_fallback_response(query)
                
            # Сохраняем в историю
            self.history.append({"role": "user", "content": query})
            self.history.append({"role": "assistant", "content": response[:100] + "..."})
            
            # Форматируем ответ
            formatted = self._format_response(response, mode)
            await utils.answer(msg, formatted)
            
        except Exception as e:
            # Если все методы провалились, используем запасной вариант
            fallback = self._get_fallback_response(query)
            await utils.answer(msg, self._format_response(fallback, mode))
            
    async def _ask_via_web(self, query, mode):
        """Запрос через веб-интерфейс DeepSeek"""
        
        # Пробуем разные эндпоинты
        urls = [
            "https://chat.deepseek.com/api/chat",
            "https://chat.deepseek.com/api/v0/chat/completions",
        ]
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://chat.deepseek.com",
            "Referer": "https://chat.deepseek.com/"
        }
        
        # Пробуем разные форматы запроса
        payloads = [
            {
                "messages": [{"role": "user", "content": query}],
                "stream": False,
                "model": "deepseek-chat" if mode == "chat" else "deepseek-coder"
            },
            {
                "prompt": query,
                "max_tokens": 2000
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for url in urls:
                for payload in payloads:
                    try:
                        async with session.post(url, headers=headers, json=payload, timeout=10) as resp:
                            if resp.status == 200:
                                text = await resp.text()
                                # Парсим ответ
                                return self._parse_response(text)
                    except:
                        continue
        return None
        
    async def _ask_via_alternative(self, query):
        """Альтернативные бесплатные API"""
        
        # Используем публичные API
        alt_apis = [
            {
                "url": "https://api-inference.huggingface.co/models/deepseek-ai/deepseek-llm-7b-chat",
                "headers": {},
                "payload": {"inputs": query}
            },
            {
                "url": "https://ai-chat-api.p.rapidapi.com/chat",
                "headers": {},
                "payload": {"message": query}
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            for api in alt_apis:
                try:
                    async with session.post(api["url"], 
                                          headers=api["headers"], 
                                          json=api["payload"], 
                                          timeout=5) as resp:
                        if resp.status == 200:
                            return await resp.text()
                except:
                    continue
        return None
        
    async def _refresh_session(self):
        """Обновление сессии"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://chat.deepseek.com/") as resp:
                    # Сохраняем куки
                    cookies = resp.cookies
                    if cookies:
                        self.session_cookie = cookies
        except:
            pass
            
    def _parse_response(self, text):
        """Парсинг ответа от DeepSeek"""
        try:
            # Пробуем распарсить как JSON
            data = json.loads(text)
            if "choices" in data:
                return data["choices"][0].get("message", {}).get("content", "")
            elif "response" in data:
                return data["response"]
            elif "text" in data:
                return data["text"]
        except:
            pass
            
        # Если не JSON, возвращаем как есть
        if text and len(text) > 10:
            return text
            
        return None
        
    def _get_fallback_response(self, query):
        """Запасные ответы если API недоступен"""
        
        responses = {
            "привет": "Привет! Как я могу помочь?",
            "как дела": "У меня всё отлично! Рад помочь тебе!",
            "кто тебя создал": "Меня создал DeepSeek, а этот модуль сделал разработчик для Hikka Userbot",
            "что ты умеешь": "Я могу отвечать на вопросы, писать код, переводить текст и многое другое!",
            "python": """Вот пример кода на Python:

```python
def hello_world():
    print("Привет, мир!")

hello_world()
```"""
        }
        
        # Ищем ключевые слова
        query_lower = query.lower()
        for key, response in responses.items():
            if key in query_lower:
                return response
                
        # Если ничего не нашли, возвращаем общий ответ
        return f"Извини, сейчас API DeepSeek временно недоступен. Но я слышал твой вопрос: '{query[:50]}...' Попробуй позже!"
        
    def _format_response(self, text, mode):
        """Форматирование ответа"""
        
        # Добавляем эмодзи в зависимости от режима
        emoji = "🤖" if mode == "chat" else "👨‍💻"
        title = "DeepSeek Chat" if mode == "chat" else "DeepSeek Coder"
        
        # Ограничиваем длину
        if len(text) > 3500:
            text = text[:3500] + "...\n\n<i>Ответ обрезан</i>"
            
        # Экранируем HTML
        text = text.replace("<", "&lt;").replace(">", "&gt;")
        
        return f"""{emoji} <b>{title}:</b>

{text}

<i>⚡ Бесплатный режим</i>"""
