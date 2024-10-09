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



