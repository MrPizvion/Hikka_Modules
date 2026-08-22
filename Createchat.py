# meta developer: @Edu_kak_xochu
# meta pic: https://img.icons8.com/color/48/000000/chat.png
# meta banner: https://via.placeholder.com/300x100.png?text=Chat+Manager

from telethon.tl.types import Message
from telethon.tl.functions.messages import CreateChatRequest

from .. import loader, utils

@loader.tds
class ChatManagerMod(loader.Module):
    """Создание и управление чатами для модулей"""
    
    strings = {
        "name": "ChatManager",
        "creating": "🔄 <b>Создание чатов...</b>",
        "created": "✅ <b>Чаты созданы!</b>\n\n🎮 Развлечения: <code>{ent}</code>\n🔧 Технический: <code>{tech}</code>\n🤖 AI: <code>{ai}</code>",
        "exists": "✅ <b>Чаты уже созданы!</b>\n\n🎮 Развлечения: <code>{ent}</code>\n🔧 Технический: <code>{tech}</code>\n🤖 AI: <code>{ai}</code>",
        "error": "❌ <b>Ошибка:</b> {error}",
        "help": "📖 <b>Команды ChatManager:</b>\n\n<b>.createchats</b> - создать чаты\n<b>.chatinfo</b> - информация о чатах",
    }
    
    strings_ru = {
        "creating": "🔄 <b>Создание чатов...</b>",
        "created": "✅ <b>Чаты созданы!</b>\n\n🎮 Развлечения: <code>{ent}</code>\n🔧 Технический: <code>{tech}</code>\n🤖 AI: <code>{ai}</code>",
        "exists": "✅ <b>Чаты уже созданы!</b>\n\n🎮 Развлечения: <code>{ent}</code>\n🔧 Технический: <code>{tech}</code>\n🤖 AI: <code>{ai}</code>",
        "error": "❌ <b>Ошибка:</b> {error}",
        "help": "📖 <b>Команды ChatManager:</b>\n\n<b>.createchats</b> - создать чаты\n<b>.chatinfo</b> - информация о чатах",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "entertainment_chat_id",
                "",
                "ID чата развлечений",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "tech_chat_id",
                "",
                "ID технического чата",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "ai_chat_id",
                "",
                "ID AI чата",
                validator=loader.validators.String(),
            ),
        )
        self.chats_created = False

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self._me = await client.get_me()
        
        # Проверяем, созданы ли чаты
        if all([
            self.config["entertainment_chat_id"],
            self.config["tech_chat_id"],
            self.config["ai_chat_id"]
        ]):
            self.chats_created = True

    @loader.command()
    async def createchatscmd(self, message: Message):
        """Создать все чаты"""
        if self.chats_created:
            await utils.answer(
                message, 
                self.strings("exists").format(
                    ent=self.config["entertainment_chat_id"],
                    tech=self.config["tech_chat_id"],
                    ai=self.config["ai_chat_id"]
                )
            )
            return
        
        await utils.answer(message, self.strings("creating"))
        
        try:
            # Создаем чат развлечений
            ent_result = await self.client(CreateChatRequest(
                users=[self._me.id],
                title="🎮 Развлечения"
            ))
            ent_chat_id = str(ent_result.chats[0].id)
            self.config["entertainment_chat_id"] = ent_chat_id
            
            # Создаем технический чат
            tech_result = await self.client(CreateChatRequest(
                users=[self._me.id],
                title="🔧 Технический"
            ))
            tech_chat_id = str(tech_result.chats[0].id)
            self.config["tech_chat_id"] = tech_chat_id
            
            # Создаем AI чат
            ai_result = await self.client(CreateChatRequest(
                users=[self._me.id],
                title="🤖 AI Модули"
            ))
            ai_chat_id = str(ai_result.chats[0].id)
            self.config["ai_chat_id"] = ai_chat_id
            
            self.chats_created = True
            
            await utils.answer(
                message, 
                self.strings("created").format(
                    ent=ent_chat_id,
                    tech=tech_chat_id,
                    ai=ai_chat_id
                )
            )
            
        except Exception as e:
            await utils.answer(message, self.strings("error").format(error=str(e)))

    @loader.command()
    async def chatinfocmd(self, message: Message):
        """Показать информацию о чатах"""
        if not self.chats_created:
            await utils.answer(
                message,
                "⚠️ <b>Чаты не созданы!</b>\n\nСоздайте их командой <code>.createchats</code>"
            )
            return
        
        await utils.answer(
            message,
            self.strings("exists").format(
                ent=self.config["entertainment_chat_id"],
                tech=self.config["tech_chat_id"],
                ai=self.config["ai_chat_id"]
            )
        )

    @loader.command()
    async def chathelpcmd(self, message: Message):
        """Показать справку"""
        await utils.answer(message, self.strings("help"))
