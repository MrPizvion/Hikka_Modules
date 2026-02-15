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
        "not_found": "❌ <b>Игрок</b> <code>{}</code> <b>не найден</b>",
        "loading": "🔍 <b>Получаю статистику</b> <code>{}</code><b>...</b>",
        "error": "❌ <b>Ошибка при получении данных</b>",
        "stats": """<b>🎮 Osu! профиль: {username}</b> <a href='https://osu.ppy.sh/users/{username}'>🔗</a>

<b>📊 Статистика (osu!standard):</b>
🏆 <b>PP:</b> <code>{pp}</code>
📈 <b>Мировой ранг:</b> #{rank}
🎯 <b>Точность:</b> {accuracy}%
▶️ <b>Сыграно карт:</b> {playcount}
⏰ <b>Уровень:</b> {level}

💯 <b>SS:</b> {ss}  |  <b>S:</b> {s}  |  <b>A:</b> {a}"""
    }
    
    strings_ru = {
        "name": "OsuStats",
        "no_nick": "🚫 <b>Укажи никнейм игрока</b>\nПример: <code>.osu peppy</code>",
        "not_found": "❌ <b>Игрок</b> <code>{}</code> <b>не найден</b>",
        "loading": "🔍 <b>Получаю статистику</b> <code>{}</code><b>...</b>",
        "error": "❌ <b>Ошибка при получении данных</b>",
        "stats": """<b>🎮 Профиль Osu!: {username}</b> <a href='https://osu.ppy.sh/users/{username}'>🔗</a>

<b>📊 Статистика (osu!standard):</b>
🏆 <b>PP:</b> <code>{pp}</code>
📈 <b>Мировой ранг:</b> #{rank}
🎯 <b>Точность:</b> {accuracy}%
▶️ <b>Сыграно карт:</b> {playcount}
⏰ <b>Уровень:</b> {level}

💯 <b>SS:</b> {ss}  |  <b>S:</b> {s}  |  <b>A:</b> {a}"""
    }
    
    async def osucmd(self, message):
        """.osu <ник> - Получить статистику игрока Osu!"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, self.strings("no_nick"))
            return
        
        nickname = args.strip()
        
        # Показываем что ищем
        await utils.answer(message, self.strings("loading").format(nickname))
        
        # Получаем статистику
        stats = await self.parse_profile(nickname)
        
        if not stats:
            await utils.answer(message, self.strings("not_found").format(nickname))
            return
        
        # Отправляем результат
        result = self.strings("stats").format(
            username=nickname,
            pp=stats.get('pp', '???'),
            rank=stats.get('rank', '???'),
            accuracy=stats.get('accuracy', '???'),
            playcount=stats.get('playcount', '???'),
            level=stats.get('level', '???'),
            ss=stats.get('ss', '0'),
            s=stats.get('s', '0'),
            a=stats.get('a', '0')
        )
        
        await utils.answer(message, result)
    
    async def parse_profile(self, nickname):
        """Парсинг профиля Osu!"""
        try:
            url = f"https://osu.ppy.sh/users/{nickcome}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, allow_redirects=True) as response:
                    if response.status != 200:
                        return None
                    
                    html = await response.text()
                    
                    # Проверяем, что профиль существует
                    if "The user you are looking for cannot be found" in html:
                        return None
                    
                    stats = {}
                    
                    # Ищем PP
                    pp_match = re.search(r'<div[^>]*class="value"[^>]*>([\d,]+)\s*pp', html, re.IGNORECASE)
                    if pp_match:
                        stats['pp'] = pp_match.group(1)
                    
                    # Ищем ранг
                    rank_match = re.search(r'#([\d,]+)[^<>]*<[^<>]*class="rank-value', html)
                    if rank_match:
                        stats['rank'] = rank_match.group(1)
                    
                    # Ищем точность
                    acc_match = re.search(r'([\d.]+)%[^<>]*<[^<>]*class="accuracy-value', html)
                    if acc_match:
                        stats['accuracy'] = acc_match.group(1)
                    
                    # Ищем количество сыгранных карт
                    playcount_match = re.search(r'Play count[^<>]*<[^<>]*>([\d,]+)', html, re.IGNORECASE)
                    if playcount_match:
                        stats['playcount'] = playcount_match.group(1)
                    
                    # Ищем уровень
                    level_match = re.search(r'Level[^<>]*<[^<>]*>([\d.]+)', html, re.IGNORECASE)
                    if level_match:
                        stats['level'] = level_match.group(1)
                    
                    # Ищем ранги (SS, S, A)
                    ss_match = re.search(r'SS[^<>]*<[^<>]*>(\d+)', html)
                    s_match = re.search(r'S[^<>]*<[^<>]*>(\d+)', html)
                    a_match = re.search(r'A[^<>]*<[^<>]*>(\d+)', html)
                    
                    if ss_match:
                        stats['ss'] = ss_match.group(1)
                    if s_match:
                        stats['s'] = s_match.group(1)
                    if a_match:
                        stats['a'] = a_match.group(1)
                    
                    return stats if stats else None
                    
        except Exception as e:
            print(f"Parse error: {e}")
            return None
