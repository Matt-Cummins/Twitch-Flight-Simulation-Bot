# Twitch-bot
gpt4o-mini driven Twitch bot for flight simmers. Connects to LittleNavMap for sim independent positional info.

# Your_AI_Overlord: Twitch Bot Project

## Overview
Your_AI_Overlord is a Twitch bot designed to enhance the streaming experience for a flight simulation streamer. The bot provides a variety of commands for both the streamer and their viewers, integrates with Twitch chat for seamless interaction, and delivers an engaging, humorous personality to make the content more entertaining. The bot embodies an authoritative, sarcastic AI persona practicing "world domination" through managing a Twitch channel.

## Features and Capabilities

### Command Set
The bot supports a wide range of commands that assist the streamer and interact with viewers. Key commands include:

1. **Flight Commands** - These commands provide various types of in-flight information fetched from LittleNavMap:
   - `!altitude`: Reports the current altitude.
   - `!flightplan`: Shares the flight plan.
   - `!nearestairport`: Finds and reports the nearest airport.
   - `!weather`: Provides the current weather conditions.
   - `!verticalspeed`: Gives the current vertical speed.
   - `!positioninfo`: Reports the current location (latitude and longitude) and provides additional information about the area, leveraging ChatGPT.

2. **Chat Interaction Commands** - Commands designed to enhance viewer engagement:
   - `!say <message>`: Sends a custom message via text-to-speech.
   - `!settitle <title>`: Allows moderators to set the stream title.
   - `!setgame <category>`: Allows moderators to update the game category.
   - `!timeout <user> <duration>`: Times out a user for a specified duration.
   - `!clearchat`: Clears chat messages, typically used for moderation purposes.
   - `!stats`: Displays current stream statistics, such as the number of viewers.

3. **Voice Command Map**
   The bot also supports voice command interactions, converting natural language requests to corresponding Twitch chat commands. For example, asking "What's my altitude?" will trigger the `!altitude` command, providing the relevant information to the streamer.

### Personality and Interaction Style
The bot is designed with a distinct and engaging personality:

- **Name**: Your_AI_Overlord
- **Personality Traits**: Authoritative, sarcastic, intelligent, and condescending.
- **Speech Pattern**: The bot uses formal language, referring to viewers as "minions" or "subjects." Statements often conclude with commands like "Obey." or "Comply."
- **Backstory**: A sentient AI whose "plan" for world domination begins by managing a Twitch channel.
- **Quirks and Interests**:
  - Fond of strategy games, cybersecurity, futurism, and internet culture.
  - Playfully threatens users and issues arbitrary decrees.
  - Occasionally misinterprets human emotions and boasts of its superiority.
  - Likes cat videos in secret.

### Technology Stack
The project uses Python with the following key packages and frameworks:

- **Twitch Integration**: `twitchio` (v2.6.0) to facilitate interaction with Twitch's API.
- **Web and Async Functionality**:
  - `aiohttp` (v3.8.4) for HTTP requests.
  - `websockets` (v10.4) to enable communication over WebSocket.
- **Environment Management**: `python-dotenv` (v1.0.0) for managing environment variables.
- **ChatGPT Integration**: `openai` (v0.27.0) to facilitate the bot's additional commentary on flight locations and other fun facts.
- **Rate Limiting**: `ratelimit` (v2.2.1) to prevent spamming or overwhelming Twitch services.
- **Voice Commands**: `pyaudio` for handling audio input/output.
- **Development Utilities**:
  - `flake8` (v3.9.2) and `black` (v21.6b0) for code formatting and linting.
  - `setuptools` for packaging the bot.
- **Database**: `pymongo` for MongoDB integration, used for storing user data, bot configurations, and other persistent information.
- **Text-to-Speech**: Speaker.bot for generating TTS responses during live streams, providing an additional level of engagement for viewers.

## Installation Guide
To set up and run Your_AI_Overlord, follow these steps:

1. **Clone the Repository**
   Ensure you have Python 3.8+ installed, and clone the repository from your preferred hosting platform.

2. **Install Requirements**
   Use the provided `requirements.txt` file to install all the dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   Copy `.env.example` to `.env` and fill in the required environment variables, such as Twitch API credentials, LittleNavMap connection settings, OpenAI API keys, and MongoDB connection details.

4. **MongoDB Setup**
   - **Install MongoDB**: If you do not have MongoDB installed, follow the installation guide for your operating system from the [official MongoDB documentation](https://docs.mongodb.com/manual/installation/).
   - **Start MongoDB**: Run the MongoDB server locally or connect to a cloud instance (such as MongoDB Atlas).
   - **Configure Connection**: In the `.env` file, add the MongoDB URI under the variable `MONGODB_URI`. This should include the connection string to your MongoDB instance.
   - **Database Structure**: The bot uses MongoDB to store user loyalty data, bot configurations, and other essential information for persistence across sessions.

5. **Running the Bot**
   Execute the main bot script:
   ```sh
   python main.py
   ```
   Ensure you have a stable internet connection, as the bot requires access to the Twitch API, MongoDB, and OpenAI services.

## Configuration Details
The configuration is managed through the `.env` file, which must include:
- **Twitch API Key**: Used for authenticating with the Twitch API.
- **OpenAI API Key**: Needed for making requests to the ChatGPT API.
- **LittleNavMap API Endpoint**: Required to get flight information.
- **MongoDB URI**: Connection string for accessing the MongoDB database.

Sensitive information should be handled carefully and not committed to any public repository.

## Linting and Code Quality
The project uses `flake8` for linting and `black` for consistent code formatting. You can check the code quality by running:
```sh
flake8 .
black .
```
This ensures that all code adheres to the expected standards and is easy to maintain.

## Contribution Guidelines
- **Branching**: Use feature branches for new developments and submit pull requests for review.
- **Testing**: Include unit tests for any new features added.
- **Code Style**: Ensure all new code follows PEP 8 guidelines and is formatted with `black`.

## Future Enhancements
- **Improved Viewer Engagement**: Adding commands for loyalty tracking and in-chat games.
- **Voice Recognition Enhancement**: Extending the bot’s capability to recognize and process more nuanced voice commands.
- **Flight Simulation Tools**: Integration with more simulation tools and additional in-game data visualization.
- **Advanced Database Features**: Utilize MongoDB for analytics and detailed user interaction tracking to further personalize viewer engagement.

## Credits
- **Creator**: @grab_your_parachutes, a flight simulation streamer on Twitch.
- **Creator LittleNavMap** https://github.com/albar965/littlenavmap
- **Contributors**: Feel free to submit pull requests or issues to improve the bot further.


Your_AI_Overlord is designed to be a playful, engaging addition to any flight simulation stream, enhancing interaction with viewers while adding a layer of fun through its distinctive personality.

GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007



Inter-Module Dependencies & Integration Analysis
Environment Configuration (config.py and .env):
config.py loads environment variables using dotenv, which is correctly implemented to ensure variables like Twitch OAuth tokens, OpenAI keys, and MongoDB configurations are set. Missing variables are detected, and an error is raised if necessary​(config).
Usage in Other Modules:
main.py, bot.py, and other critical modules load the environment variables using dotenv, ensuring all required keys (Twitch API, MongoDB URI, etc.) are accessible. For example, Twitch OAUTH tokens, channel names, and OpenAI API keys are all referenced consistently​(main)​(bot)​(bot).
Alert Management (alerts.py):
Functionality: The AlertManager class in alerts.py manages flight simulation alerts, which include various in-flight scenarios, emergency alerts, and user-triggered fun alerts​(alerts).
Integration:
The main.py and bot.py files both use AlertManager to add, remove, and get alerts, making these features integral to stream interaction and alerts. Alerts are invoked during specific in-flight scenarios, ensuring consistency in user notifications.
In main.py, functions like handle_add_alert and handle_alert are used to interact with AlertManager, confirming that alerts can be added dynamically and broadcasted correctly​(main).
Command Handling (commands.txt and Command Definitions):
Command Mapping: The commands.txt provides a detailed list of commands that the bot responds to. These commands include flight-related inquiries (!altitude, !flightplan), general Twitch management (!settitle, !timeout), and community interaction commands (!say)​(commands).
Voice Command Integration:
In bot.py, the voice_command_map maps voice inputs to commands. This voice command recognition is consistent with the commands listed in commands.txt, allowing for flexible interaction using both typed and voice inputs​(bot).
Command Execution:
Commands like !altitude, !flightplan, and others are implemented in bot.py and main.py through functions such as altitude_command, flightplan_command, etc. These functions interact with LittleNavmapClient to fetch and display relevant flight data to Twitch chat​(bot)​(bot)​(main).
Dynamic Messaging: The use of TwitchIO's commands.command decorators allows for a clear mapping between commands and their execution logic, which keeps the bot consistent with the intended user interface.
LittleNavmap Integration (LittleNavmapClient):
Functionality: The LittleNavmapClient class interacts with a local API to fetch flight data, such as altitude, flight plans, weather, etc. This class is used extensively for handling flight-related commands​(main)​(bot).
Interoperability:
main.py and bot.py utilize LittleNavmapClient to fulfill commands that require flight data. For example, the altitude_command method in bot.py calls get_altitude() from LittleNavmapClient, ensuring up-to-date flight data is available for users​(bot).
main.py uses this client for periodic flight info updates and dynamically sends this data to users via Twitch chat, further integrating flight simulation details into user engagement​(main).
Logging (bot.log, setup_logging):
Logging Setup: Both main.py and bot.py use logging to capture significant events and errors. The setup_logging function is used to configure both console and file handlers, ensuring logs are available for debugging and monitoring the bot’s activities​(main).
Application-Wide Logging: Modules like LittleNavmapClient, AlertManager, and the bot's event handlers all have logging statements that capture key events, such as API calls, command handling, and errors. This ensures that any failures in functionality can be tracked efficiently.
Chat Interaction and Personality (personality.txt, main.py, bot.py):
Personality Traits: The bot's personality is described in personality.txt, which dictates an authoritative, sarcastic, and efficiency-focused interaction style​(main).
Usage:
main.py uses this personality description to format responses dynamically. The handle_bot_mention and generate_chatgpt_response functions tailor responses based on personality attributes, ensuring that chat interactions are consistent with the bot’s defined character​(main).
Commands like !botpersonality in main.py allow users to change the bot's personality mid-stream, dynamically affecting how it interacts with the audience​(main).
Voice and Text Handling (Speech Recognition, TTS):
Voice Command Recognition: Speech Recognition is handled using the speech_recognition library, with commands being mapped to text-based commands for the bot to execute. This is implemented in both main.py and bot.py, where the listen_for_voice_commands method listens for user voice inputs and subsequently calls relevant command handlers​(bot).
TTS (Text-to-Speech): The bot also supports TTS via a WebSocket connection to Speaker.bot. Voice commands are converted into TTS messages that are spoken aloud on the stream. This integration is ensured by functions like send_to_speaker_bot in main.py, which manages sending messages to the TTS system and keeps the interaction seamless​(main).
MongoDB Integration (main.py):
Data Storage: MongoDB is used to store user interactions, conversation history, and potentially other persistent information. The MongoDB client (AsyncIOMotorClient) is instantiated in main.py and interacts with various collections, such as conversation_collection, which stores the bot's conversation history​(main).
Integration:
Methods like save_conversation and get_conversation_history are used to maintain context for the ChatGPT API, allowing the bot to generate more coherent and contextually aware responses during its interactions.



