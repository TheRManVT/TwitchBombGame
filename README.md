# 💣 Twitch Bomb Bot

A Twitch chat bot that runs a secret-word bomb game. After a random number of messages a bomb arms, chat has a limited number of messages to say the secret word to defuse it — or the `!bomb` command fires and triggers to whatever you have set it.

---

## How It Works

The game has two phases:

**Phase 1 — Waiting**
The bot silently counts chat messages. After a random number of messages (between `MIN_MESSAGES` and `MAX_MESSAGES`) the bomb arms and Phase 2 begins.

**Phase 2 — Armed**
A secret word is chosen at random from the word list. The bot announces that the bomb is armed and tells chat how many messages they have left. If **anyone** says the secret word (case-insensitive, anywhere in their message) the bomb is defused and the game resets to Phase 1. If the word is **not** said within the countdown, `!bomb` fires and the secret word is revealed.

---

## Chat Messages

| Event | Message |
|---|---|
| Bomb arms | `💣 A bomb has been planted and armed! Find the secret word within X message(s) or face the consequences... 🔴` |
| Bomb defused | `✅ @username defused the bomb by saying the secret word: 'word'! Chat is safe... for now. 😅` |
| Bomb detonates | `💥 Sorry... but you didn't find the word in time... The secret word was 'word'!` then `!bomb` |

---

## Commands

| Command | Description |
|---|---|
| `!bombstats` | Shows current state and messages remaining (mod-friendly) |
| `!currrentword` | Shows the possible secret words in the list (capped at 21 words, can be changed with changing `before` and `after`|

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/twitch-bomb-bot.git
cd twitch-bomb-bot
```

### 2. Create your `.env` file
```bash
cp .env.example .env
```
Fill in your Twitch credentials and adjust the message range values if desired.

### 3. Get a Twitch OAuth token
Go to [https://twitchtokengenerator.com/](https://twitchtokengenerator.com/) and generate a token for your bot account. Paste it (including the `oauth:` prefix) into `.env`.

### 4. Customize the bot

**Word list** — edit `self.word_list` in `bot.py`:
```python
self.word_list = [
    "apple",
    "banana",
    # add your own words here (lowercase only)
]
```

**Ignored users** — edit `self.ignored_users` in `bot.py`:
```python
self.ignored_users = {
    "nightbot",
    "streamelements",
    "yourbotusername",
}
```

### 5. Run with Docker
```bash
docker compose up -d
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `TWITCH_OAUTH_TOKEN` | — | Bot account OAuth token (required) |
| `TWITCH_USERNAME` | — | Bot account username (required) |
| `TWITCH_CHANNEL` | — | Channel to monitor (required) |
| `MIN_MESSAGES` | `5` | Minimum messages before bomb arms |
| `MAX_MESSAGES` | `30` | Maximum messages before bomb arms |
| `MIN_ARMED_MESSAGES` | `3` | Minimum messages in armed phase |
| `MAX_ARMED_MESSAGES` | `15` | Maximum messages in armed phase |

---

## Project Structure

```
twitch-bomb-bot/
├── bot/
│   └── bot.py             # Main bot script
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment variables
└── README.md
```

---

## Notes
- Words in `word_list` must be **lowercase** — chat messages are automatically lowercased before matching so `Apple`, `APPLE`, and `apple` all count.
- Ignored users' messages are completely invisible to the bot — they don't count toward any trigger and their messages are never checked for the secret word.
- The `!bombstats` command is intended for mods/the streamer. It does not reveal the secret word to chat.
- This was made with the Claude Sonnet 4.6
