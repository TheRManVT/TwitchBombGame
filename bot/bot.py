import os
import random
import logging
from twitchio.ext import commands

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- BOMB GAME STATES ---
STATE_WAITING = "waiting"   # Counting up to first trigger
STATE_ARMED   = "armed"     # Word selected, counting down to !bomb

class PhraseBot(commands.Bot):
    def __init__(self):
        # Get environment variables
        token   = os.getenv('TWITCH_OAUTH_TOKEN')
        channel = os.getenv('TWITCH_CHANNEL')

        # Message counting config
        self.min_messages = int(os.getenv('MIN_MESSAGES', 5))
        self.max_messages = int(os.getenv('MAX_MESSAGES', 30))

        # ----------------------------------------------------------------
        # BOMB GAME CONFIG
        # ----------------------------------------------------------------
        self.word_list = [
            "apple",
            "banana",
            "shadow",
            "rocket",
            "forest",
            "mirror",
            "castle",
            "thunder",
            "pillow",
            "lantern",
            # Add or replace words here
        ]

        # How many messages (without the secret word) must pass before !bomb fires
        self.min_armed_messages = int(os.getenv('MIN_ARMED_MESSAGES', 3))
        self.max_armed_messages = int(os.getenv('MAX_ARMED_MESSAGES', 15))

        # ----------------------------------------------------------------
        # IGNORED USERS
        # ----------------------------------------------------------------
        self.ignored_users = {
            "nightbot",
            "streamelements",
            "<insert bot username here>",
            # Add more usernames to ignore here (lowercase)
        }

        # ----------------------------------------------------------------
        # BOMB STATE
        # ----------------------------------------------------------------
        self.bomb_state    = STATE_WAITING
        self.secret_word   = None
        self.message_count = 0
        self.next_trigger  = random.randint(self.min_messages, self.max_messages)
        self.armed_count   = 0
        self.armed_trigger = 0

        super().__init__(
            token=token,
            prefix='!',
            initial_channels=[channel]
        )

        logger.info(f"Bot initialized for channel: {channel}")
        logger.info(f"[BOMB] STATE_WAITING — first trigger in {self.next_trigger} messages.")

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _full_reset(self):
        """Reset everything back to the very beginning (STATE_WAITING)."""
        self.bomb_state    = STATE_WAITING
        self.secret_word   = None
        self.message_count = 0
        self.armed_count   = 0
        self.armed_trigger = 0
        self.next_trigger  = random.randint(self.min_messages, self.max_messages)
        logger.info(f"[BOMB] Full reset → STATE_WAITING. Next arm in {self.next_trigger} messages.")



    # ------------------------------------------------------------------
    # EVENTS
    # ------------------------------------------------------------------

    async def event_ready(self):
        logger.info(f'Logged in as | {self.nick}')
        logger.info(f'User id is   | {self.user_id}')
        logger.info(f'Monitoring   | {self.connected_channels[0].name}')
        logger.info("Bot is ready and listening for messages!")

    async def event_message(self, message):
        # Ignore echoes
        if message.echo:
            return

        # Ignore specific users
        username_lower = message.author.name.lower()
        if username_lower in self.ignored_users:
            logger.debug(f"Ignoring message from {message.author.name}")
            return

        logger.debug(f"[{message.author.name}]: {message.content}")

        # Ignore commands
        if message.content.startswith('!'):
            await self.handle_commands(message)
            return

        # ------------------------------------------------------------------
        # BOMB GAME LOGIC
        # ------------------------------------------------------------------
        content_lower = message.content.lower()

        if self.bomb_state == STATE_WAITING:
            self.message_count += 1
            logger.info(f"[BOMB][WAITING] {self.message_count}/{self.next_trigger}")

            if self.message_count >= self.next_trigger:
                await self._arm_bomb(message.channel)

        elif self.bomb_state == STATE_ARMED:
            # Check if the secret word appears anywhere in the message
            if self.secret_word in content_lower:
                logger.info(
                    f"[BOMB] Secret word '{self.secret_word}' found in message by "
                    f"{message.author.name} — full reset!"
                )
                await self._disarm(message)
                return

            # Word not found — increment armed counter
            self.armed_count += 1
            logger.info(f"[BOMB][ARMED] {self.armed_count}/{self.armed_trigger} (word not said)")

            if self.armed_count >= self.armed_trigger:
                await self._detonate(message.channel)

    async def _arm_bomb(self, channel):
        """Move from STATE_WAITING → STATE_ARMED and announce to chat."""
        self.bomb_state    = STATE_ARMED
        self.secret_word   = random.choice(self.word_list)
        self.armed_count   = 0
        self.armed_trigger = random.randint(self.min_armed_messages, self.max_armed_messages)

        logger.info(
            f"[BOMB] STATE_ARMED — secret word: '{self.secret_word}' | "
            f"detonates in {self.armed_trigger} clean messages."
        )

        await channel.send(
            f"💣 A bomb has been planted and armed! "
            f"Find the secret word within {self.armed_trigger} message(s) or face the consequences... 🔴"
        )

    async def _disarm(self, message):
        """Secret word was said — announce who saved chat and fully reset."""
        await message.channel.send(
            f"✅ @{message.author.name} defused the bomb by saying the secret word: "
            f"'{self.secret_word}'! Chat is safe... for now. 😅"
        )
        self._full_reset()

    async def _detonate(self, channel):
        """Nobody said the word in time — announce, fire !bomb, and reset."""
        logger.info("[BOMB] DETONATING — sending !bomb")
        await channel.send(f"💥 Sorry... but you didn't find the word in time... The secret word was '{self.secret_word}'!")
        await channel.send("!bomb")
        self._full_reset()

    # ------------------------------------------------------------------
    # COMMANDS
    # ------------------------------------------------------------------

    @commands.command(name='bombstats')
    async def bomb_stats(self, ctx):
        """Shows the current bomb game state (mod-friendly debug command)."""
        if self.bomb_state == STATE_WAITING:
            remaining = self.next_trigger - self.message_count
            await ctx.send(f"[BOMB] Waiting — arms in {remaining} more message(s).")
        elif self.bomb_state == STATE_ARMED:
            remaining = self.armed_trigger - self.armed_count
            await ctx.send(
                f"[BOMB] ARMED — detonates in {remaining} more clean message(s). "
                f"(Secret word is hidden 🤫)"
            )


if __name__ == "__main__":
    bot = PhraseBot()
    bot.run()
