from .. import loader, utils
import aiohttp
from bs4 import BeautifulSoup
import re

# requires: beautifulsoup4

@loader.tds
class OsuStatsMod(loader.Module):
    """Модуль для получения полной статистики Osu! игроков"""
    
    strings = {
        "name": "OsuStats",
        "no_nick": "🚫 <b>Укажи никнейм игрока</b>\nПример: <code>.osu peppy</code>",
        "not_found": "❌ <b>Игрок</b> <code>{}</code> <b>не найден</b>",
        "loading": "🔍 <b>Получаю статистику</b> <code>{}</code><b>...</b>",
        "error": "❌ <b>Ошибка при получении данных</b>",
        "stats": """<b>🎮 Статистика Osu! | {username}</b> <a href='{profile_url}'>🔗</a>

<b>📊 Основное:</b>
👤 <b>Ник:</b> {username}
🆔 <b>ID:</b> <code>{user_id}</code>
🌍 <b>Страна:</b> {country}

<b>⚡ Рейтинг:</b>
🏆 <b>PP:</b> <code>{pp}</code>
📈 <b>Мировой ранг:</b> #{global_rank}
🎯 <b>Точность:</b> {accuracy}%

<b>🎮 Статистика игр:</b>
▶️ <b>Сыграно:</b> {playcount}
⏰ <b>Время в игре:</b> {playtime} ч
👑 <b>Уровень:</b> {level}

<b>🏅 Ранги:</b>
💯 <b>SS:</b> {count_ss}  |  <b>SSH:</b> {count_ssh}
🌟 <b>S:</b> {count_s}  |  <b>SH:</b> {count_sh}
💚 <b>A:</b> {count_a}"""
    }
    
    strings_ru = {
        "name": "OsuStats",
        "no_nick": "🚫 <b>Укажи никнейм игрока</b>\nПример: <code>.osu peppy</code>",
        "not_found": "❌ <b>Игрок</b> <code>{}</code> <b>не найден</b>",
        "loading": "🔍 <b>Получаю статистику</b> <code>{}</code><b>...</b>",
        "error": "❌ <b>Ошибка при получении данных</b>",
        "stats": """<b>🎮 Статистика Osu! | {username}</b> <a href='{profile_url}'>🔗</a>

<b>📊 Основное:</b>
👤 <b>Ник:</b> {username}
🆔 <b>ID:</b> <code>{user_id}</code>
🌍 <b>Страна:</b> {country}

<b>⚡ Рейтинг:</b>
🏆 <b>PP:</b> <code>{pp}</code>
📈 <b>Мировой ранг:</b> #{global_rank}
🎯 <b>Точность:</b> {accuracy}%

<b>🎮 Статистика игр:</b>
▶️ <b>Сыграно:</b> {playcount}
⏰ <b>Время в игре:</b> {playtime} ч
👑 <b>Уровень:</b> {level}

<b>🏅 Ранги:</b>
💯 <b>SS:</b> {count_ss}  |  <b>SSH:</b> {count_ssh}
🌟 <b>S:</b> {count_s}  |  <b>SH:</b> {count_sh}
💚 <b>A:</b> {count_a}"""
    }
    
    async def osucmd(self, message):
        """.osu <ник> - Получить полную статистику игрока Osu!"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, self.strings("no_nick"))
            return
        
        nickname = args.strip()
        
        # Показываем что ищем
        loading = await utils.answer(message, self.strings("loading").format(nickname))
        
        # Получаем статистику
        stats = await self.get_stats(nickname)
        
        if not stats:
            await utils.answer(message, self.strings("not_found").format(nickname))
            return
        
        # Форматируем и отправляем результат
        result = self.strings("stats").format(**stats)
        await utils.answer(message, result)
    
    async def get_stats(self, nickname):
        """Парсинг статистики с сайта osu.ppy.sh"""
        try:
            async with aiohttp.ClientSession() as session:
                # Сначала получаем ID игрока через поиск
                search_url = f"https://osu.ppy.sh/users/{nickname}"
                
                async with session.get(search_url, allow_redirects=True) as response:
                    if response.status != 200:
                        return None
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Проверяем, что профиль существует
                    if "The user you are looking for cannot be found" in html:
                        return None
                    
                    # Пытаемся найти ID игрока в HTML
                    user_id_match = re.search(r'data-user-id="(\d+)"', html)
                    user_id = user_id_match.group(1) if user_id_match else "???"
                    
                    # Извлекаем статистику (через API профиля)
                    # У Osu есть скрытые данные в JavaScript
                    
                    # Никнейм (может отличаться по регистру)
                    username_elem = soup.find('span', {'class': 'profile-username'})
                    username = username_elem.text if username_elem else nickname
                    
                    # Страна
                    country_elem = soup.find('div', {'class': 'profile-country__name'})
                    country = country_elem.text if country_elem else "???"
                    
                    # PP
                    pp_elem = soup.find('div', {'class': 'profile-detail__values'})
                    pp_text = "0"
                    if pp_elem:
                        pp_match = re.search(r'([\d,]+)\s*pp', pp_elem.text, re.IGNORECASE)
                        if pp_match:
                            pp_text = pp_match.group(1).replace(',', '')
                    
                    # Ранг
                    rank_elem = soup.find('div', {'class': 'profile-detail__rank'})
                    global_rank = "???"
                    if rank_elem:
                        rank_match = re.search(r'#([\d,]+)', rank_elem.text)
                        if rank_match:
                            global_rank = rank_match.group(1).replace(',', '')
                    
                    # Точность
                    accuracy = "???"
                    acc_elem = soup.find('div', {'class': 'profile-detail__accuracy'})
                    if acc_elem:
                        acc_match = re.search(r'([\d.]+)%', acc_elem.text)
                        if acc_match:
                            accuracy = acc_match.group(1)
                    
                    # Уровень
                    level = "???"
                    level_elem = soup.find('div', {'class': 'profile-detail__level'})
                    if level_elem:
                        level_match = re.search(r'([\d.]+)', level_elem.text)
                        if level_match:
                            level = level_match.group(1)
                    
                    # Количество игр
                    playcount = "???"
                    playtime = "???"
                    
                    # Пытаемся найти статистику в JSON данных
                    json_match = re.search(r'window\.initialData\s*=\s*({.+?});', html)
                    if json_match:
                        import json
                        try:
                            data = json.loads(json_match.group(1))
                            user_data = data.get('user', {})
                            
                            # Дополнительные данные из JSON
                            if 'statistics' in user_data:
                                stats = user_data['statistics']
                                playcount = str(stats.get('play_count', '???'))
                                playtime = str(round(stats.get('play_time', 0) / 3600, 1))
                                
                                # Ранги
                                count_ss = stats.get('grade_counts', {}).get('ss', 0)
                                count_ssh = stats.get('grade_counts', {}).get('ssh', 0)
                                count_s = stats.get('grade_counts', {}).get('s', 0)
                                count_sh = stats.get('grade_counts', {}).get('sh', 0)
                                count_a = stats.get('grade_counts', {}).get('a', 0)
                            else:
                                count_ss = count_ssh = count_s = count_sh = count_a = 0
                        except:
                            count_ss = count_ssh = count_s = count_sh = count_a = 0
                    else:
                        count_ss = count_ssh = count_s = count_sh = count_a = 0
                    
                    return {
                        "username": username,
                        "user_id": user_id,
                        "country": country,
                        "pp": pp_text,
                        "global_rank": global_rank,
                        "accuracy": accuracy,
                        "playcount": playcount,
                        "playtime": playtime,
                        "level": level,
                        "count_ss": count_ss,
                        "count_ssh": count_ssh,
                        "count_s": count_s,
                        "count_sh": count_sh,
                        "count_a": count_a,
                        "profile_url": search_url
                    }
                    
        except Exception as e:
            print(f"Error: {e}")
            return None
