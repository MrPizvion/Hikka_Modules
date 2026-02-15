from .. import loader, utils
import aiohttp
import re

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
        "stats": """<b>🎮 Профиль Osu!: {username}</b> <a href='https://osu.ppy.sh/users/{username}'>🔗</a>

<b>📊 Статистика:</b>
🏆 <b>PP:</b> <code>{pp}</code>
📈 <b>Ранг:</b> #{rank}
🎯 <b>Точность:</b> {accuracy}%
▶️ <b>Сыграно:</b> {playcount}
⏰ <b>Уровень:</b> {level}
💯 <b>SS/S/A:</b> {ss}/{s}/{a}"""
    }
    
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
                await utils.answer(message, self.strings("not_found").format(nickname))
                return
            
            # Отправляем результат
            result = self.strings("stats").format(**stats)
            await utils.answer(message, result)
            
        except Exception as e:
            await utils.answer(message, self.strings("error").format(str(e)))
    
    async def get_player_stats(self, nickname):
        """Получение статистики через альтернативный источник"""
        try:
            # Используем другой источник данных
            url = f"https://osu.ppy.sh/users/{nickname}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, allow_redirects=True) as resp:
                    if resp.status != 200:
                        return None
                    
                    # Проверяем что это действительно профиль
                    if "profile-username" not in await resp.text():
                        return None
                    
                    html = await resp.text()
                    
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
                    
                    # Ищем ранг
                    rank_pattern = r'#([\d,]+)'
                    rank_search = re.search(rank_pattern, html)
                    if rank_search:
                        stats['rank'] = rank_search.group(1)
                    
                    # Ищем статистику в JSON
                    json_pattern = r'window\.initialData\s*=\s*({.+?});'
                    json_search = re.search(json_pattern, html)
                    
                    if json_search:
                        import json
                        try:
                            data = json.loads(json_search.group(1))
                            user_data = data.get('user', {})
                            stats_data = user_data.get('statistics', {})
                            
                            if stats_data:
                                stats['pp'] = str(stats_data.get('pp', '???'))
                                stats['rank'] = str(stats_data.get('global_rank', '???'))
                                stats['accuracy'] = f"{stats_data.get('hit_accuracy', 0):.2f}"
                                stats['playcount'] = str(stats_data.get('play_count', '???'))
                                stats['level'] = str(stats_data.get('level', {}).get('current', '???'))
                                
                                grades = stats_data.get('grade_counts', {})
                                stats['ss'] = str(grades.get('ss', 0))
                                stats['s'] = str(grades.get('s', 0))
                                stats['a'] = str(grades.get('a', 0))
                        except:
                            pass
                    
                    return stats
                    
        except Exception as e:
            print(f"Error: {e}")
            return None
