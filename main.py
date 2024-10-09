import os
import asyncio
import json
import logging
from logging.handlers import RotatingFileHandler
import queue
import sys
from typing import List, Optional, Dict, Any
from cachetools import TTLCache

from twitchio.ext import commands
from twitchio.channel import Channel
import aiohttp
import websockets
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from openai import RateLimitError, APIError, APIConnectionError
import speech_recognition as sr
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables from .env file
load_dotenv()

print("Script started")

# Twitch bot configuration
BOT_TOKEN = os.getenv('TWITCH_OAUTH_TOKEN')
CHANNEL_NAME = os.getenv('TWITCH_CHANNEL')
BOT_NAME = os.getenv('BOT_NAME')
BROADCASTER_ID = os.getenv('BROADCASTER_ID')

# Speaker.bot configuration
SPEAKER_BOT_URL = os.getenv('STREAMERBOT_WS_URI')

# OpenAI API configuration
OPENAI_API_KEY = os.getenv('CHATGPT_API_KEY')
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-0613')

# MongoDB configuration
MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')

# Cache for flight data
flight_data_cache = TTLCache(maxsize=100, ttl=60)

def setup_logging(log_file='bot.log', console_level=logging.DEBUG, file_level=logging.DEBUG):
    logger = logging.getLogger('spbot')
    logger.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # File handler
    file_handler = RotatingFileHandler(log_file, maxBytes=10000, backupCount=3)
    file_handler.setLevel(file_level)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

class CustomAlert:
    def __init__(self, name: str, message: str):
        self.name = name
        self.message = message

class AlertManager:
    def __init__(self):
        self.alerts: Dict[str, CustomAlert] = {}

    def add_alert(self, name: str, message: str) -> None:
        self.alerts[name] = CustomAlert(name, message)

    def get_alert(self, name: str) -> Optional[CustomAlert]:
        return self.alerts.get(name)

    def remove_alert(self, name: str) -> None:
        if name in self.alerts:
            del self.alerts[name]

class LittleNavmapClient:
    def __init__(self, base_url: str = "http://localhost:8965/api"):
        self.base_url = base_url
        self.logger = logging.getLogger('LittleNavmapClient')
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug("LittleNavmapClient initialized with base_url: %s", self.base_url)

    async def get_airport_info(self, ident: str):
        return await self._get_data(f'/airport/info?ident={ident}')

    async def get_sim_info(self):
        return await self._get_data('/sim/info')

    async def _get_data(self, endpoint: str):
        self.logger.debug(f"Attempting to retrieve data from endpoint: {endpoint}")
        url = f"{self.base_url}{endpoint}"
        self.logger.debug(f"Full URL: {url}")
        headers = {
            'User-Agent': 'TwitchBot/1.0',
            'Accept': 'application/json'
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    self.logger.debug(f"Response status: {response.status}")
                    self.logger.debug(f"Response headers: {response.headers}")
                    content = await response.text()
                    self.logger.debug(f"Response content: {content}")
                    if response.status == 200:
                        data = await response.json()
                        self.logger.info(f"Successfully retrieved data from {endpoint}")
                        return data
                    else:
                        self.logger.error(f"Failed to retrieve data from {endpoint}. Status code: {response.status}. Content: {content}")
                        return None
        except aiohttp.ClientError as e:
            self.logger.error(f"Connection error while accessing {url}: {str(e)}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {str(e)}")
        return None

class Bot(commands.Bot):
    def __init__(self, openai_client_instance: AsyncOpenAI, cli_mode: bool = False):
        super().__init__(token=BOT_TOKEN, prefix="!", initial_channels=[CHANNEL_NAME])
        self.loop = asyncio.get_event_loop()
        self.openai_client: AsyncOpenAI = openai_client_instance
        self.speaker_bot_ws: Optional[websockets.WebSocketClientProtocol] = None
        self.bot_active: bool = True
        self.bot_personality: str = "You are a helpful Twitch chat assistant."
        self.text_prefix: str = "!"
        self.voice_prefix: str = "hey bot"
        self.bot_trigger_words: List[str] = [
            "ok overlord", "hey overlord", "your ai overlord", "@your ai overlord"
        ]
        self.verbose: bool = False
        self.cli_mode: bool = cli_mode

        self.logger = setup_logging()
        self.logger.info("Bot instance created")

        self.voice_command_queue: queue.Queue[str] = queue.Queue()

        self.alert_manager = AlertManager()

        self.tts_voice = "default"
        self.tts_speed = 1.2
        self.tts_volume = 1.0

        self.mongo_client = AsyncIOMotorClient(MONGO_URI, io_loop=self.loop)
        self.db = self.mongo_client[MONGO_DB_NAME]
        self.conversation_collection = self.db["conversations"]

        self.littlenavmap_client = LittleNavmapClient()

        self.loop.run_until_complete(self.ensure_indexes())

    async def ensure_indexes(self):
        await self.conversation_collection.create_index([('timestamp', -1)])
        await self.conversation_collection.create_index([('user', 1), ('timestamp', -1)])
        self.logger.info("Indexes created on conversation collection.")

    async def periodic_flight_info_update(self):
        last_altitude = None
        last_position = None
        while True:
            try:
                sim_info = await self.littlenavmap_client.get_sim_info()
                if sim_info:
                    current_altitude = sim_info.get('indicated_altitude')
                    current_position = sim_info.get('position')
                    
                    if last_altitude is None or abs(current_altitude - last_altitude) > 1000:
                        self.logger.info(f"Significant altitude change: {current_altitude} feet")
                        last_altitude = current_altitude
                    
                    if last_position is None or (
                        abs(current_position['lat'] - last_position['lat']) > 0.1 or
                        abs(current_position['lon'] - last_position['lon']) > 0.1
                    ):
                        self.logger.info(f"Significant position change: Lat {current_position['lat']}, Lon {current_position['lon']}")
                        last_position = current_position
                    
                    self.logger.debug(f"[Periodic Update] Sim Info: {sim_info}")
                else:
                    self.logger.warning("Unable to retrieve sim info")
            except Exception as e:
                self.logger.error(f"Error during periodic flight info update: {e}")
            await asyncio.sleep(60)

    @commands.command(name='flightstatus')
    async def flight_status_command(self, ctx):
        sim_info = await self.littlenavmap_client.get_sim_info()
        if sim_info:
            altitude = round(sim_info.get('indicated_altitude', 0), 2)
            ground_speed = round(sim_info.get('ground_speed', 0) * 3600, 2)  # Convert to km/h
            heading = round(sim_info.get('heading', 0), 1)
            lat = round(sim_info.get('position', {}).get('lat', 0), 4)
            lon = round(sim_info.get('position', {}).get('lon', 0), 4)
            wind_direction = round(sim_info.get('wind_direction', 0), 1)
            wind_speed = round(sim_info.get('wind_speed', 0) * 3.6, 1)  # Convert to km/h

            status_message = (
                f"Current flight status: Altitude: {altitude} feet, "
                f"Ground Speed: {ground_speed} km/h, Heading: {heading}°, "
                f"Position: {lat}, {lon}. "
                f"Wind: {wind_direction}° at {wind_speed} km/h. Comply."
            )
            await ctx.send(status_message)
            await self.send_to_speaker_bot(status_message)
        else:
            await ctx.send("I am unable to retrieve flight data at this time. Patience, minion.")

    @commands.command(name='airport')
    async def airport_info_command(self, ctx, ident: str):
        airport_info = await self.littlenavmap_client.get_airport_info(ident)
        if airport_info:
            # Extract relevant information from airport_info
            # This will depend on the actual structure of the AirportInfoResponse
            # You may need to adjust this based on the actual response
            name = airport_info.get('name', 'Unknown')
            elevation = airport_info.get('elevation', 'Unknown')
            await ctx.send(f"Airport {ident}: {name}, Elevation: {elevation} feet. Obey.")
        else:
            await ctx.send(f"No information available for airport {ident}. Obey.")

    async def cli_interface(self):
        while True:
            command = input("Enter command (status/toggle/quit): ").strip().lower()
            if command == "status":
                self.logger.info(f"Bot status: {'active' if self.bot_active else 'inactive'}")
                self.logger.info(f"Verbose mode: {'enabled' if self.verbose else 'disabled'}")
            elif command == "toggle":
                self.bot_active = not self.bot_active
                self.logger.info(f"Bot {'activated' if self.bot_active else 'deactivated'}")
            elif command == "quit":
                self.logger.info("Shutting down bot...")
                break
            else:
                self.logger.info("Invalid command. Available commands: status, toggle, quit")

    async def handle_bot_mention(self, message: Any) -> None:
        self.logger.info(f"Handling bot mention: {message.content}")
        self.logger.debug(f"Bot trigger words: {self.bot_trigger_words}")
        try:
            response = await self.generate_chatgpt_response(message.content)
            self.logger.debug(f"Generated response: {response}")
            if self.speaker_bot_ws and self.speaker_bot_ws.open:
                await self.send_to_speaker_bot(response)
            else:
                self.logger.warning("Speaker.bot connection is not available. Skipping TTS.")
            await message.channel.send(response)
        except Exception as e:
            self.logger.error(f"Error handling bot mention: {e}", exc_info=True)
            await message.channel.send("I'm sorry, I encountered an error while processing your request. Please try again later.")

    async def update_tts_settings(self) -> None:
        command = {
            'command': 'UpdateTTSSettings',
            'voice': self.tts_voice,
            'speed': self.tts_speed,
            'volume': self.tts_volume
        }
        await self.speaker_bot_ws.send(json.dumps(command))

    async def listen_for_voice_commands(self) -> None:
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            recognizer.adjust_for_ambient_noise(source)

        def callback(recognizer, audio):
            try:
                text = recognizer.recognize_google(audio)
                self.logger.info("Recognized voice command: %s", text)
                if text.lower().startswith(self.voice_prefix):
                    command = text[len(self.voice_prefix):].strip()
                    self.voice_command_queue.put(command)
            except sr.UnknownValueError:
                self.logger.info("Speech not understood")
            except sr.RequestError as e:
                self.logger.error("Could not request results from Google Speech Recognition service; %s", e)
            except Exception as e:
                self.logger.error("An unexpected error occurred during voice recognition: %s", e)

        self.logger.info("Listening for voice commands...")
        stop_listening = recognizer.listen_in_background(mic, callback)

        while self.bot_active:
            await asyncio.sleep(0.1)

        stop_listening(wait_for_stop=False)

    async def process_voice_command(self, command: str) -> None:
        self.logger.info(f"Processing voice command: {command}")
        if any(word in command.lower() for word in self.bot_trigger_words):
            response = await self.generate_chatgpt_response(command)
            await self.send_to_speaker_bot(response)
            self.logger.info(f"Voice command response: {response}")
        else:
            self.logger.debug(f"Ignoring voice command: {command}")

    async def event_ready(self) -> None:
        self.logger.info('Bot is ready. Logged in as | %s', self.nick)
        try:
            await self.connect_to_speaker_bot()
            self.loop.create_task(self.listen_for_voice_commands())
            self.loop.create_task(self.periodic_flight_info_update())
            
            sim_info = await self.littlenavmap_client.get_sim_info()
            if sim_info:
                active = sim_info.get('active', False)
                status = sim_info.get('simconnect_status', 'Unknown')
                self.logger.info(f"Connected to simulator. Active: {active}, Status: {status}")
            else:
                self.logger.error("Failed to retrieve simulator information")
            
            self.logger.debug("All initial tasks created successfully")
        except Exception as e:
            self.logger.error(f"Error during bot initialization: {e}", exc_info=True)

    async def connect_to_speaker_bot(self) -> None:
        max_retries = 5
        retry_delay = 5

        if self.speaker_bot_ws and self.speaker_bot_ws.open:
            self.logger.info("WebSocket connection to Speaker.bot already established.")
            return

        for attempt in range(max_retries):
            try:
                self.logger.info(f"Attempting to connect to Speaker.bot at {SPEAKER_BOT_URL}, attempt {attempt + 1}")
                self.speaker_bot_ws = await websockets.connect(SPEAKER_BOT_URL)
                self.logger.info("Successfully connected to Speaker.bot")
                return
            except Exception as e:
                self.logger.error(f"Failed to connect to Speaker.bot: {e}")

            if attempt < max_retries - 1:
                self.logger.info(f"Retrying connection in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)

        self.logger.error("Failed to connect to Speaker.bot after multiple attempts.")

    async def event_message(self, message) -> None:
        try:
            content = message.content.lower()

            if any(word in content for word in self.bot_trigger_words) or f"@{self.nick.lower()}" in content:
                self.logger.debug(f"Handling bot mention: {content}")
                await self.handle_bot_mention(message)
            elif content.startswith(self.text_prefix):
                self.logger.debug(f"Handling command: {content}")
                await self.handle_command(message, is_voice=False)
            elif message.author.name.lower() == CHANNEL_NAME.lower():
                self.logger.debug(f"Handling streamer command: {content}")
                await self.handle_streamer_command(message)
            else:
                self.logger.debug(f"Regular chat message: {content}")

        except Exception as e:
            self.logger.error(f"Unexpected error in event_message: {e}", exc_info=True)

    async def handle_command(self, message: Any, is_voice: bool = False) -> None:
        self.logger.info(
            f"Handling command: {'voice command' if is_voice else message.content}"
        )
        try:
            content = message if is_voice else message.content[len(self.text_prefix):]
            parts = content.lower().split()
            command = parts[0]
            args = parts[1:]

            self.logger.info(f"Parsed command: {command}, args: {args}")

            command_handlers = {
                'tts': self.handle_tts_command,
                'addalert': self.handle_add_alert,
                'alert': self.handle_alert,
                'say': self.handle_say_command,
                'flightstatus': self.flight_status_command,
                'airport': self.airport_info_command
            }

            handler = command_handlers.get(command)
            if handler:
                self.logger.info(f"Attempting to execute command: {command}")
                result = await handler(*([message.channel] + args))
                if result:
                    self.logger.info(f"Command result: {result}")
                    await self.send_to_speaker_bot(result)
                else:
                    self.logger.info("Command executed with no result")
            else:
                self.logger.info(f"Unknown command: {command}")
                await self.send_to_speaker_bot(f"Unknown command: {command}")
        except Exception as e:
            self.logger.error(f"Error in handle_command: {e}")

    async def handle_say_command(self, *args) -> str:
        message = ' '.join(args)
        self.logger.info(f"Executing 'say' command with message: {message}")
        await self.send_to_speaker_bot(message)
        return f"Said: {message}"

    async def handle_tts_command(self, *args) -> None:
        if args[0] == 'voice':
            self.tts_voice = args[1]
        elif args[0] == 'speed':
            self.tts_speed = float(args[1])
        elif args[0] == 'volume':
            self.tts_volume = float(args[1])
        await self.update_tts_settings()

    async def handle_add_alert(self, *args) -> str:
        if len(args) >= 2:
            self.alert_manager.add_alert(args[0], ' '.join(args[1:]))
            return f"Alert {args[0]} added."
        return "Invalid alert format."

    async def handle_alert(self, *args) -> str:
        if len(args) >= 1:
            alert = self.alert_manager.get_alert(args[0])
            if alert:
                return alert.message
            else:
                return f"Alert {args[0]} not found."
        return "No alert specified."

    async def generate_chatgpt_response(self, message: str) -> str:
        try:
            self.logger.info(f"Generating ChatGPT response for: {message}")
            
            history = await self.get_conversation_history()
            
            messages = [{"role": "system", "content": self.bot_personality}]
            for entry in history:
                messages.append({"role": "user", "content": entry['user']})
                messages.append({"role": "assistant", "content": entry['bot']})
            messages.append({"role": "user", "content": message})

            input_length = len(message.split())
            history_length = len(history)
            max_tokens = min(500, max(100 + (input_length // 5), history_length * 10))
            
            self.logger.info(f"Using max_tokens: {max_tokens}")

            response: ChatCompletion = await self.openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                max_tokens=max_tokens
            )
            bot_response = response.choices[0].message.content.strip()

            await self.save_conversation(message, bot_response)

            self.logger.info(f"Generated ChatGPT response: {bot_response}")
            return bot_response
        except Exception as e:
            self.logger.error(f"Error generating ChatGPT response: {e}", exc_info=True)
            return "I'm sorry, I encountered an error while processing your request. Please try again later."

    async def get_conversation_history(self) -> List[Dict[str, str]]:
        cursor = self.conversation_collection.find().sort('timestamp', -1).limit(5)
        history = await cursor.to_list(length=5)
        return list(reversed(history))

    async def save_conversation(self, user_message: str, bot_response: str) -> None:
        await self.conversation_collection.insert_one({
            'user': user_message,
            'bot': bot_response,
            'timestamp': asyncio.get_event_loop().time()
        })

    async def send_to_speaker_bot(self, text: str) -> None:
        if self.speaker_bot_ws is None:
            self.logger.error("WebSocket connection not established.")
            raise ConnectionError("WebSocket connection not established")

        self.logger.info(f"Sending to Speaker.bot: {text}")

        command = {
            'command': 'Overlord',
            'text': text,
            'voice': self.tts_voice,
            'speed': self.tts_speed,
            'volume': self.tts_volume
        }

        try:
            await self.speaker_bot_ws.send(json.dumps(command))
            if self.verbose:
                self.logger.debug(f"Sent command to Speaker.bot: {command}")
        except websockets.exceptions.ConnectionClosed as e:
            self.logger.error("WebSocket connection closed: %s", e)
            await self.connect_to_speaker_bot()
            raise ConnectionError("WebSocket connection closed unexpectedly") from e
        except websockets.exceptions.WebSocketException as e:
            self.logger.error("WebSocket error: %s", e)
            raise

    async def event_error(self, error: Exception, data: Optional[Dict[str, Any]] = None) -> None:
        self.logger.error("An error occurred: %s", error)
        if isinstance(error, (commands.errors.CommandNotFound, commands.errors.CheckFailure)):
            pass
        elif isinstance(error, aiohttp.ClientError):
            self.logger.warning("Network error occurred. Attempting to reconnect...")
            await self.connect_to_speaker_bot()
        else:
            self.logger.error("Unexpected error: %s", error)

    async def handle_streamer_command(self, message: Any) -> None:
        if message.content.startswith('!botconfig'):
            await message.channel.send("Bot configuration command received.")
        elif message.content.startswith('!botstatus'):
            status = "active" if self.bot_active else "inactive"
            await message.channel.send(f"Bot is currently {status}.")
        elif message.content.startswith('!botclear'):
            await self.conversation_collection.delete_many({})
            await message.channel.send("Conversation history cleared.")
        elif message.content.startswith('!botpersonality'):
            _, personality = message.content.split(' ', 1)
            self.bot_personality = personality
            await message.channel.send(f"Bot personality changed to: {personality}")
        elif message.content.startswith('!bottoggle'):
            self.bot_active = not self.bot_active
            status = "activated" if self.bot_active else "deactivated"
            await message.channel.send(f"Bot has been {status}.")
        elif message.content.startswith('!botvoiceprefix'):
            _, prefix = message.content.split(' ', 1)
            self.voice_prefix = prefix
            await message.channel.send(f"Voice command prefix changed to: {prefix}")
        elif message.content.startswith('!bottextprefix'):
            _, prefix = message.content.split(' ', 1)
            self.text_prefix = prefix
            await message.channel.send(f"Text command prefix changed to: {prefix}")
        elif message.content.startswith('!botverbose'):
            self.verbose = not self.verbose
            await message.channel.send(
                f"Verbose mode {'enabled' if self.verbose else 'disabled'}."
            )

    async def event_loop(self):
        while True:
            try:
                command = self.voice_command_queue.get_nowait()
                self.logger.info(f"Processing voice command from queue: {command}")
                await self.process_voice_command(command)
            except queue.Empty:
                await asyncio.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error processing voice command: {e}", exc_info=True)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Twitch Bot with AI integration")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    args = parser.parse_args()

    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    bot = Bot(openai_client, cli_mode=args.cli)

    try:
        if args.cli:
            asyncio.run(bot.cli_interface())
        else:
            bot.run()
    except KeyboardInterrupt:
        print("Bot is shutting down...")
    except Exception as e:
        logging.error(f"Bot crashed: {e}", exc_info=True)
    finally:
        # Perform any cleanup if necessary
        pass