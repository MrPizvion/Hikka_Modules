# meta developer: @твой_юзернейм
# scope: hikka_only
# meta pic: none
# meta banner: https://example.com/banner.jpg

from .. import loader, utils
import aiohttp
import asyncio
import logging

logger = logging.getLogger(__name__)

@loader.tds
class DeepSeekAIMod(loader.Module):
    """DeepSeek AI модуль с официальным API"""
    
    strings = {
        "name": "DeepSeek AI",
        "no_token": "❌ <b>Установи токен:</b> <code>.set_token sk-... ключ</code>",
        "no_query": "❌ <b>Что спросить?</b>",
        "thinking": "⏳ <b>DeepSeek думает...</b>",
        "error": "❌ <b>Ошибка:</b> {}",
        "token_set": "✅ <b>Токен установлен!</b>",
    }
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "api_token",
                None,
                "API ключ DeepSeek",
                validator=loader.validators.Hidden()
            ),
            loader.ConfigValue(
                "model",
                "deepseek-chat",
                "Модель",
                validator=loader.validators.Choice(["deepseek-chat", "deepseek-coder"])
            )
        )
        
    @loader.command()
    async def set_token(self, message):
        """<токен> - Сохранить API ключ"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "❌ Укажи токен")
            return
        self.config["api_token"] = args.strip()
        await utils.answer(message, self.strings("token_set"))
        
    @loader.command()
    async def ai(self, message):
        """<вопрос> - Спросить у DeepSeek"""
        query = utils.get_args_raw(message)
        if not query:
            await utils.answer(message, self.strings("no_query"))
            return
            
        token = self.config["api_token"]
        if not token:
            await utils.answer(message, self.strings("no_token"))
            return
            
        # Отправляем "думаю"
        msg = await utils.answer(message, self.strings("thinking"))
        
        try:
            # Делаем запрос к API
            response = await self._ask_deepseek(query, token)
            
            # Форматируем ответ
            text = response.strip()
            if len(text) > 4000:
                text = text[:4000] + "..."
                
            await utils.answer(msg, f"🤖 <b>DeepSeek:</b>\n\n{text}")
            
        except Exception as e:
            await utils.answer(msg, self.strings("error").format(str(e)))
            
    async def _ask_deepseek(self, query, token):
        """Отправка запроса к DeepSeek API"""
        url = "https://api.deepseek.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config["model"],
            "messages": [
                {"role": "system", "content": "Ты полезный ассистент"},
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise Exception(f"HTTP {resp.status}: {error_text[:200]}")
                    
                result = await resp.json()
                
                # Проверяем структуру ответа
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    raise Exception("Странный ответ от API: " + str(result)[:200])
