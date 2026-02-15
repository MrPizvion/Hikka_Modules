from .. import loader, utils
import aiohttp
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# requires: aiohttp

@loader.tds
class OsuProfileMod(loader.Module):
    """Модуль для osu! с поддержкой премиум эмодзи 🌟"""
    
    strings = {
        "name": "OsuProfile",
        "no_nick": "🚫 <b>Укажи никнейм игрока</b>\nПример: <code>.osu peppy</code>",
        "no_query": "🚫 <b>Укажи запрос</b>\nПример: <code>.map The Big Black</code>",
        "not_found": "❌ <b>Игрок</b> <code>{}</code> <b>не найден</b>",
        "map_not_found": "❌ <b>Карта</b> <code>{}</code> <b>не найдена</b>",
        "loading": "🔄 <b>Загрузка...</b>",
        "error": "💥 <b>Ошибка:</b> {}",
        "config_done": "✅ <b>Настройки эмодзи сохранены!</b>",
        
        # Статистика игрока с шаблонами для премиум эмодзи
        "user_stats": """<b>{username_emoji} Osu! профиль: {username}</b> <a href='https://osu.ppy.sh/users/{user_id}'>🔗</a>

╔══════════════════════╗
<b>📊 Статистика [{mode}]</b>
╠══════════════════════╣
╠ {pp_emoji} <b>PP:</b> <code>{pp}</code>
╠ {rank_emoji} <b>Мировой ранг:</b> #{global_rank}
╠ {country_emoji} <b>Ранг в стране [{country}]:</b> #{country_rank}
╠ {accuracy_emoji} <b>Точность:</b> {accuracy}%
╠ {playcount_emoji} <b>Сыграно карт:</b> {playcount}
╠ {time_emoji} <b>Время в игре:</b> {playtime} ч
╠ {level_emoji} <b>Уровень:</b> {level}
╚ {ranks_emoji} <b>Ранги:</b> {ss_emoji}{ss} {s_emoji}{s} {a_emoji}{a}""",

        # Информация о карте с шаблонами для премиум эмодзи
        "map_info": """<b>{music_emoji} {artist} - {title}</b> <a href='https://osu.ppy.sh/s/{mapset_id}'>🔗</a>

╔══════════════════════╗
<b>📋 Информация о карте</b>
╠══════════════════════╣
╠ {mapper_emoji} <b>Маппер:</b> <a href='https://osu.ppy.sh/users/{creator_id}'>{creator}</a>
╠ {status_emoji} <b>Статус:</b> {status}
╠ {stats_emoji} <b>Статистика:</b> {plays_emoji}{plays} {favourites_emoji}{favourites}
╠ {video_emoji} <b>Видео:</b> {video}
╚ {diffs_emoji} <b>Сложностей:</b> {diff_count}

<b>🎯 Сложности:</b>
{diffs}""",
        
        # Помощь
        "help_text": """<b>🎮 OsuProfile Module - Премиум эмодзи!</b>

╔══════════════════════╗
<b>📋 Доступные команды:</b>
╠══════════════════════╣
╠ 🔍 <code>.osu ник</code> - статистика игрока
╠ 🔍 <code>.osu ник:taiko</code> - статистика в Taiko
╠ 🔍 <code>.osu ник:mania</code> - статистика в Mania
╠ 🎵 <code>.map название</code> - поиск карты
╠ 🎵 <code>.map ID</code> - карта по ID
╠ ⚙️ <code>.osuconfig</code> - настройка премиум эмодзи
╚ ❓ <code>.osuhelp</code> - это сообщение

<b>✨ Примеры:</b>
<code>.osu peppy</code>
<code>.osu cookiezi:mania</code>
<code>.map The Big Black</code>
<code>.map 774532</code>

<b>🎯 Режимы:</b> osu, taiko, catch, mania""",

        # Настройки эмодзи
        "config_text": """<b>⚙️ Настройка премиум эмодзи для OsuProfile</b>

Используй формат: <code>[эмодзи](ID)</code>
Пример: <code>[🔥](5451765549757400442)</code>

<b>📝 Текущие настройки:</b>
👤 <b>Username:</b> {username_emoji}
🔥 <b>PP:</b> {pp_emoji}
🏆 <b>Ранг:</b> {rank_emoji}
🌍 <b>Страна:</b> {country_emoji}
🎯 <b>Точность:</b> {accuracy_emoji}
🎮 <b>Игры:</b> {playcount_emoji}
⏰ <b>Время:</b> {time_emoji}
👑 <b>Уровень:</b> {level_emoji}
🏅 <b>Ранги:</b> {ranks_emoji}
💯 <b>SS:</b> {ss_emoji}
✨ <b>S:</b> {s_emoji}
🅰️ <b>A:</b> {a_emoji}
🎵 <b>Музыка:</b> {music_emoji}
👤 <b>Маппер:</b> {mapper_emoji}
✅ <b>Статус:</b> {status_emoji}
📊 <b>Стат:</b> {stats_emoji}
👁️ <b>Просмотры:</b> {plays_emoji}
❤️ <b>Избранное:</b> {favourites_emoji}
🎥 <b>Видео:</b> {video_emoji}
⭐ <b>Сложности:</b> {diffs_emoji}

<b>Команды для настройки:</b>
<code>.set_emoji [ключ] [значение]</code>
Пример: <code>.set_emoji pp_emoji [🔥](5451765549757400442)</code>

<b>Доступные ключи:</b>
username_emoji, pp_emoji, rank_emoji, country_emoji, accuracy_emoji,
playcount_emoji, time_emoji, level_emoji, ranks_emoji, ss_emoji, s_emoji, a_emoji,
music_emoji, mapper_emoji, status_emoji, stats_emoji, plays_emoji,
favourites_emoji, video_emoji, diffs_emoji""",
        
        # Статусы карт
        "status_graveyard": "🪦 Заброшенная",
        "status_wip": "🔧 В разработке",
        "status_pending": "⏳ В ожидании",
        "status_ranked": "✅ Рейтинговая",
        "status_approved": "👍 Одобренная",
        "status_qualified": "🎯 Квалифицированная",
        "status_loved": "❤️ Любимая",
        
        # Режимы игры
        "mode_osu": "🔴 osu!",
        "mode_taiko": "🥁 Taiko",
        "mode_catch": "🍏 Catch",
        "mode_mania": "🎹 Mania",
        
        "video_yes": "✅ Есть",
        "video_no": "❌ Нет",
    }
    
    # Константы
    API_KEY_V1 = "3e0c7c9baf734a70f780f2960332d825c50c4690"
    API_URL_V1 = "https://osu.ppy.sh/api/get_user"
    API_BEATMAP_V1 = "https://osu.ppy.sh/api/get_beatmaps"
    
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "username_emoji",
                "👤",
                "Эмодзи для ника (можно премиум [🔥](ID))",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "pp_emoji",
                "🔥",
                "Эмодзи для PP",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "rank_emoji",
                "🏆",
                "Эмодзи для ранга",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "country_emoji",
                "🌍",
                "Эмодзи для страны",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "accuracy_emoji",
                "🎯",
                "Эмодзи для точности",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "playcount_emoji",
                "🎮",
                "Эмодзи для игр",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "time_emoji",
                "⏰",
                "Эмодзи для времени",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "level_emoji",
                "👑",
                "Эмодзи для уровня",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "ranks_emoji",
                "🏅",
                "Эмодзи для рангов",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "ss_emoji",
                "💯",
                "Эмодзи для SS",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "s_emoji",
                "✨",
                "Эмодзи для S",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "a_emoji",
                "🅰️",
                "Эмодзи для A",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "music_emoji",
                "🎵",
                "Эмодзи для музыки",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "mapper_emoji",
                "👤",
                "Эмодзи для маппера",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "status_emoji",
                "📊",
                "Эмодзи для статуса",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "stats_emoji",
                "📈",
                "Эмодзи для статистики",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "plays_emoji",
                "👁️",
                "Эмодзи для просмотров",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "favourites_emoji",
                "❤️",
                "Эмодзи для избранного",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "video_emoji",
                "🎥",
                "Эмодзи для видео",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "diffs_emoji",
                "⭐",
                "Эмодзи для сложностей",
                validator=loader.validators.String()
            ),
        )
    
    async def client_ready(self, client, db):
        self.client = client
        self.db = db
    
    async def osucmd(self, message):
        """.osu <ник> [:<режим>] - Получить статистику игрока"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, self.strings("no_nick"))
            return
        
        # Парсим режим если есть
        mode = 0
        nickname = args
        
        if ':' in args:
            parts = args.rsplit(':', 1)
            nickname = parts[0].strip()
            mode_str = parts[1].strip().lower()
            
            mode_map = {
                "osu": 0, "std": 0,
                "taiko": 1, "t": 1,
                "catch": 2, "c": 2, "ctb": 2,
                "mania": 3, "m": 3
            }
            mode = mode_map.get(mode_str, 0)
        
        await utils.answer(message, self.strings("loading"))
        
        try:
            stats = await self.get_user_stats(nickname, mode)
            
            if not stats:
                await utils.answer(message, self.strings("not_found").format(nickname))
                return
            
            # Форматируем числа с разделителями
            stats['pp'] = f"{float(stats['pp']):,.0f}".replace(',', ' ')
            stats['global_rank'] = f"{int(stats['global_rank']):,}".replace(',', ' ')
            stats['country_rank'] = f"{int(stats['country_rank']):,}".replace(',', ' ')
            stats['accuracy'] = f"{float(stats['accuracy']):.2f}"
            stats['playcount'] = f"{int(stats['playcount']):,}".replace(',', ' ')
            
            # Название режима
            mode_names = ["🔴 osu!", "🥁 Taiko", "🍏 Catch", "🎹 Mania"]
            stats['mode'] = mode_names[mode]
            
            # Добавляем эмодзи из конфига
            stats['username_emoji'] = self.config["username_emoji"]
            stats['pp_emoji'] = self.config["pp_emoji"]
            stats['rank_emoji'] = self.config["rank_emoji"]
            stats['country_emoji'] = self.config["country_emoji"]
            stats['accuracy_emoji'] = self.config["accuracy_emoji"]
            stats['playcount_emoji'] = self.config["playcount_emoji"]
            stats['time_emoji'] = self.config["time_emoji"]
            stats['level_emoji'] = self.config["level_emoji"]
            stats['ranks_emoji'] = self.config["ranks_emoji"]
            stats['ss_emoji'] = self.config["ss_emoji"]
            stats['s_emoji'] = self.config["s_emoji"]
            stats['a_emoji'] = self.config["a_emoji"]
            
            result = self.strings("user_stats").format(**stats)
            await utils.answer(message, result)
            
        except Exception as e:
            logger.exception(f"Ошибка: {e}")
            await utils.answer(message, self.strings("error").format(str(e)))
    
    async def mapcmd(self, message):
        """.map <название или ID> - Найти информацию о карте"""
        args = utils.get_args_raw(message)
        
        if not args:
            await utils.answer(message, self.strings("no_query"))
            return
        
        query = args.strip()
        await utils.answer(message, self.strings("loading"))
        
        try:
            map_data = await self.get_map_info(query)
            
            if not map_data:
                await utils.answer(message, self.strings("map_not_found").format(query))
                return
            
            # Добавляем эмодзи из конфига
            map_data['music_emoji'] = self.config["music_emoji"]
            map_data['mapper_emoji'] = self.config["mapper_emoji"]
            map_data['status_emoji'] = self.config["status_emoji"]
            map_data['stats_emoji'] = self.config["stats_emoji"]
            map_data['plays_emoji'] = self.config["plays_emoji"]
            map_data['favourites_emoji'] = self.config["favourites_emoji"]
            map_data['video_emoji'] = self.config["video_emoji"]
            map_data['diffs_emoji'] = self.config["diffs_emoji"]
            
            result = self.strings("map_info").format(**map_data)
            await utils.answer(message, result)
            
        except Exception as e:
            logger.exception(f"Ошибка: {e}")
            await utils.answer(message, self.strings("error").format(str(e)))
    
    async def osuhelpcmd(self, message):
        """Показать помощь по командам"""
        await utils.answer(message, self.strings("help_text"))
    
    async def osuconfigcmd(self, message):
        """Показать текущие настройки эмодзи"""
        config_values = {
            'username_emoji': self.config["username_emoji"],
            'pp_emoji': self.config["pp_emoji"],
            'rank_emoji': self.config["rank_emoji"],
            'country_emoji': self.config["country_emoji"],
            'accuracy_emoji': self.config["accuracy_emoji"],
            'playcount_emoji': self.config["playcount_emoji"],
            'time_emoji': self.config["time_emoji"],
            'level_emoji': self.config["level_emoji"],
            'ranks_emoji': self.config["ranks_emoji"],
            'ss_emoji': self.config["ss_emoji"],
            's_emoji': self.config["s_emoji"],
            'a_emoji': self.config["a_emoji"],
            'music_emoji': self.config["music_emoji"],
            'mapper_emoji': self.config["mapper_emoji"],
            'status_emoji': self.config["status_emoji"],
            'stats_emoji': self.config["stats_emoji"],
            'plays_emoji': self.config["plays_emoji"],
            'favourites_emoji': self.config["favourites_emoji"],
            'video_emoji': self.config["video_emoji"],
            'diffs_emoji': self.config["diffs_emoji"],
        }
        
        await utils.answer(message, self.strings("config_text").format(**config_values))
    
    async def set_emojicmd(self, message):
        """.set_emoji <ключ> <значение> - Установить премиум эмодзи"""
        args = utils.get_args_raw(message).split(maxsplit=1)
        
        if len(args) < 2:
            await utils.answer(message, "❌ <b>Использование:</b> <code>.set_emoji [ключ] [значение]</code>")
            return
        
        key, value = args[0].strip(), args[1].strip()
        
        # Проверяем что такой ключ существует
        valid_keys = [
            'username_emoji', 'pp_emoji', 'rank_emoji', 'country_emoji', 'accuracy_emoji',
            'playcount_emoji', 'time_emoji', 'level_emoji', 'ranks_emoji', 'ss_emoji', 's_emoji', 'a_emoji',
            'music_emoji', 'mapper_emoji', 'status_emoji', 'stats_emoji', 'plays_emoji',
            'favourites_emoji', 'video_emoji', 'diffs_emoji'
        ]
        
        if key not in valid_keys:
            await utils.answer(message, f"❌ <b>Неверный ключ!</b>\nДоступные: {', '.join(valid_keys)}")
            return
        
        # Сохраняем в конфиг
        self.config[key] = value
        await utils.answer(message, self.strings("config_done"))
    
    async def get_user_stats(self, nickname: str, mode: int = 0) -> dict:
        """Получение статистики игрока через API"""
        params = {
            'k': self.API_KEY_V1,
            'u': nickname,
            'm': mode,
            'type': 'string'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.API_URL_V1, params=params) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                
                if not data or len(data) == 0:
                    return None
                
                user = data[0]
                
                # Конвертируем время
                playtime_seconds = int(user.get('total_seconds_played', 0))
                playtime_hours = round(playtime_seconds / 3600, 1)
                
                return {
                    'username': user.get('username', nickname),
                    'user_id': user.get('user_id', '?'),
                    'pp': user.get('pp_raw', '0'),
                    'global_rank': user.get('pp_rank', '0'),
                    'country_rank': user.get('pp_country_rank', '0'),
                    'accuracy': user.get('accuracy', '0'),
                    'playcount': user.get('playcount', '0'),
                    'playtime': playtime_hours,
                    'level': round(float(user.get('level', 0)), 2),
                    'ss': int(user.get('count_rank_ss', 0)) + int(user.get('count_rank_ssh', 0)),
                    's': int(user.get('count_rank_s', 0)) + int(user.get('count_rank_sh', 0)),
                    'a': user.get('count_rank_a', 0),
                    'country': user.get('country', '??')
                }
    
    async def get_map_info(self, query: str) -> dict:
        """Получение информации о карте"""
        if query.isdigit():
            params = {
                'k': self.API_KEY_V1,
                's': query
            }
        else:
            params = {
                'k': self.API_KEY_V1,
                'q': query
            }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.API_BEATMAP_V1, params=params) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                
                if not data or len(data) == 0:
                    return None
                
                # Группируем по beatmapset_id
                maps = {}
                for b in data:
                    set_id = b.get('beatmapset_id')
                    if set_id not in maps:
                        maps[set_id] = []
                    maps[set_id].append(b)
                
                # Берем первый сет
                first_set_id = list(maps.keys())[0]
                beatmaps = maps[first_set_id]
                first_map = beatmaps[0]
                
                # Статус карты с эмодзи
                status_map = {
                    '-2': 'status_graveyard',
                    '-1': 'status_wip',
                    '0': 'status_pending',
                    '1': 'status_ranked',
                    '2': 'status_approved',
                    '3': 'status_qualified',
                    '4': 'status_loved'
                }
                status_key = status_map.get(first_map.get('approved', '0'), 'status_pending')
                status = self.strings(status_key)
                
                # Видео
                video = self.strings('video_yes') if first_map.get('video') == '1' else self.strings('video_no')
                
                # Сложности с эмодзи
                diffs = []
                mode_emojis = ['🔴', '🥁', '🍏', '🎹']
                
                for b in sorted(beatmaps, key=lambda x: float(x.get('difficultyrating', 0))):
                    mode = int(b.get('mode', 0))
                    stars = float(b.get('difficultyrating', 0))
                    length = int(b.get('total_length', 0))
                    bpm = float(b.get('bpm', 0))
                    
                    # Форматируем длительность
                    minutes = length // 60
                    seconds = length % 60
                    
                    # Эмодзи для сложности в зависимости от звезд
                    if stars < 2:
                        star_emoji = "⭐"
                    elif stars < 3:
                        star_emoji = "🌟🌟"
                    elif stars < 4:
                        star_emoji = "🌟🌟🌟"
                    elif stars < 5:
                        star_emoji = "🌟🌟🌟🌟"
                    elif stars < 6:
                        star_emoji = "🔥🔥🔥"
                    else:
                        star_emoji = "💀💀💀"
                    
                    mode_emoji = mode_emojis[mode] if mode < 4 else '🎵'
                    diffs.append(f"{mode_emoji} {b.get('version', 'N/A')} {star_emoji} {stars:.2f} | ⏱️ {minutes}:{seconds:02d} | 🎵 {bpm:.0f} BPM")
                
                # Общая статистика
                total_plays = sum(int(b.get('playcount', 0)) for b in beatmaps)
                
                return {
                    'artist': first_map.get('artist', 'N/A'),
                    'title': first_map.get('title', 'N/A'),
                    'mapset_id': first_set_id,
                    'creator': first_map.get('creator', 'N/A'),
                    'creator_id': first_map.get('creator_id', '0'),
                    'status': status,
                    'plays': f"{total_plays:,}".replace(',', ' '),
                    'favourites': f"{int(first_map.get('favourite_count', 0)):,}".replace(',', ' '),
                    'video': video,
                    'diff_count': len(beatmaps),
                    'diffs': '\n'.join(diffs[:10])
                }
