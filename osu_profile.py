from .. import loader, utils
import aiohttp
import re
import logging

logger = logging.getLogger(__name__)

# requires: aiohttp

@loader.tds
class OsuStatsMod(loader.Module):
    """Модуль для получения статистики Osu! игроков"""
    
    strings = {
        "name": "OsuStats",
        "no_nick": "🚫 <b>Укажи никнейм игрока</b>\nПример: <code>.osu peppy</code>",
        "not_found": "❌ <b>Игрок</b> <code>{}</code> <b>не найден</b> на osu!",
        "loading": "🔍 <b>Ищу профиль</b> <code>{}</code><b>...</b>",
        "error": "❌ <b>Ошибка:</b> {}",
        "log_error": "⚠️ <b>Ошибка в модуле OsuStats:</b>\n<code>{}</code>",
        "stats": """<b>🎮 Osu! профиль: {username}</b> <a href='https://osu.ppy.sh/users/{username}'>🔗</a>

<b>📊 Статистика:</b>
🏆 <b>PP:</b> <code>{pp}</code>
📈 <b>Ранг:</b> #{rank}
🎯 <b>Точность:</b> {accuracy}%
▶️ <b>Сыграно:</b> {playcount}
⏰ <b>Уровень:</b> {level}
💯 <b>SS/S/A:</b> {ss}/{s}/{a}"""
    }
    
    strings_ru = {
        "name": "OsuStats",
        "no_nick": "🚫 <b>Укажи никнейм игрока</b>\nПример: <code>.osu peppy</code>",
        "not_found": "❌ <b>Игрок</b> <code>{}</code> <b>не найден</b> на osu!",
        "loading": "🔍 <b>Ищу профиль</b> <code>{}</code><b>...</b>",
        "error": "❌ <b>Ошибка:</b> {}",
        "log_error": "⚠️ <b>Ошибка в модуле OsuStats:</b>\n<code>{}</code>",
        "stats": """<b>🎮 Профиль Osu!: {username}</b> <a href='https://osu.ppy.sh/users/{username}'>🔗</a>

<b>📊 Статистика:</b>
🏆 <b>PP:</b> <code>{pp}</code>
📈 <b>Ранг:</b> #{rank}
🎯 <b>Точность:</b> {accuracy}%
▶️ <b>Сыграно:</b> {playcount}
⏰ <b>Уровень:</b> {level}
💯 <b>SS/S/A:</b> {ss}/{s}/{a}"""
    }
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
    
    async def osucmd(self, message):
        """Получить статистику игрока Osu!"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, self.strings("no_nick"))
            return
        
        nickname = args.strip()
        
        # Показываем что ищем
        await utils.answer(message, self.strings("loading").format(nickname))
        
        try:
            # Получаем статистику
            stats = await self.get_player_stats(nickname)
            
            if not stats:
                error_msg = f"Игрок {nickname} не найден"
                logger.error(error_msg)
                await self.log_error(error_msg)
                await utils.answer(message, self.strings("not_found").format(nickname))
                return
            
            # Отправляем результат
            result = self.strings("stats").format(**stats)
            await utils.answer(message, result)
            
        except Exception as e:
            error_text = str(e)
            logger.exception(f"Ошибка в osucmd: {error_text}")
            await self.log_error(f"osucmd: {error_text}\nНик: {nickname}")
            await utils.answer(message, self.strings("error").format(error_text))
    
    async def get_player_stats(self, nickname):
        """Получение статистики через альтернативный источник"""
        try:
            # Используем другой источник данных
            url = f"https://osu.ppy.sh/users/{nickname}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            logger.info(f"Запрашиваю URL: {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, allow_redirects=True) as resp:
                    logger.info(f"Статус ответа: {resp.status}")
                    
                    if resp.status != 200:
                        logger.error(f"HTTP ошибка: {resp.status}")
                        await self.log_error(f"HTTP {resp.status} для {nickname}")
                        return None
                    
                    html = await resp.text()
                    
                    # Проверяем что это действительно профиль
                    if "profile-username" not in html:
                        logger.error(f"Профиль {nickname} не найден (нет profile-username)")
                        await self.log_error(f"Профиль {nickname} не существует")
                        return None
                    
                    logger.info(f"HTML получен, длина: {len(html)}")
                    
                    # Базовые данные
                    stats = {
                        'username': nickname,
                        'pp': '???',
                        'rank': '???',
                        'accuracy': '???',
                        'playcount': '???',
                        'level': '???',
                        'ss': '0',
                        's': '0',
                        'a': '0'
                    }
                    
                    # Ищем PP
                    pp_pattern = r'([\d,]+)\s*pp'
                    pp_search = re.search(pp_pattern, html, re.IGNORECASE)
                    if pp_search:
                        stats['pp'] = pp_search.group(1)
                        logger.info(f"Найден PP: {stats['pp']}")
                    else:
                        logger.warning("PP не найден в HTML")
                    
                    # Ищем ранг
                    rank_pattern = r'#([\d,]+)'
                    rank_search = re.search(rank_pattern, html)
                    if rank_search:
                        stats['rank'] = rank_search.group(1)
                        logger.info(f"Найден ранг: {stats['rank']}")
                    
                    # Ищем статистику в JSON
                    json_pattern = r'window\.initialData\s*=\s*({.+?});'
                    json_search = re.search(json_pattern, html)
                    
                    if json_search:
                        try:
                            import json
                            json_str = json_search.group(1)
                            logger.info(f"Найден JSON, длина: {len(json_str)}")
                            
                            data = json.loads(json_str)
                            user_data = data.get('user', {})
                            stats_data = user_data.get('statistics', {})
                            
                            if stats_data:
                                logger.info("Найдена статистика в JSON")
                                stats['pp'] = str(stats_data.get('pp', stats['pp']))
                                stats['rank'] = str(stats_data.get('global_rank', stats['rank']))
                                stats['accuracy'] = f"{stats_data.get('hit_accuracy', 0):.2f}"
                                stats['playcount'] = str(stats_data.get('play_count', stats['playcount']))
                                
                                level_data = stats_data.get('level', {})
                                stats['level'] = str(level_data.get('current', stats['level']))
                                
                                grades = stats_data.get('grade_counts', {})
                                stats['ss'] = str(grades.get('ss', 0))
                                stats['s'] = str(grades.get('s', 0))
                                stats['a'] = str(grades.get('a', 0))
                                
                                logger.info(f"Данные из JSON: PP={stats['pp']}, Ранг={stats['rank']}")
                        except Exception as json_error:
                            logger.exception(f"Ошибка парсинга JSON: {json_error}")
                            await self.log_error(f"JSON parse error: {json_error}")
                    else:
                        logger.warning("JSON с данными не найден в HTML")
                    
                    return stats
                    
        except Exception as e:
            logger.exception(f"Ошибка в get_player_stats: {e}")
            await self.log_error(f"get_player_stats: {e}")
            return None
    
    async def log_error(self, error_text):
        """Отправка ошибки в лог-чат Hikka"""
        try:
            # Получаем лог-чат из конфига Hikka
            log_chat = self.db.get("hikka.main", "log_chat", None)
            
            if log_chat:
                await self.client.send_message(
                    log_chat,
                    self.strings("log_error").format(error_text)
                )
                logger.info(f"Ошибка отправлена в лог-чат: {log_chat}")
            else:
                logger.warning("Лог-чат не настроен")
                
        except Exception as e:
            logger.error(f"Не удалось отправить в лог-чат: {e}")
