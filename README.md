# Animebot

Animebot is a Telegram bot that provides users with access to a large database of anime, movies, and TV series. It allows users to search for content, view details, and watch videos directly through the bot.

## Features

-   Search for anime, movies, and TV series by title
-   Browse content by ratings (IMDb, Kinopoisk, Shikimori)
-   Search by external links (IMDb, Kinopoisk, Shikimori)
-   View detailed information about each title
-   Watch content directly through embedded video players
-   Add titles to favorites
-   Dark/light theme switcher for the web interface

## Docker Usage

To run Animebot using Docker, follow these steps:

1. Ensure you have Docker installed on your system.

2. Clone the repository:

    ```
    git clone https://github.com/w1sq/animebot.git
    cd animebot
    ```

3. Create a `.env` file in the root directory with the following variables:

    ```
    API_KEY=your_telegram_bot_token
    SECRET_KEY=your_flask_secret_key
    CONN_STR=your_postgresql_connection_string
    ```

4. Build the Docker images:

    ```
    docker build -f Dockerfile.bot -t animebot-bot .
    docker build -f Dockerfile.web -t animebot-web .
    ```

5. Run the containers:

    ```
    docker run -d --env-file .env --name animebot-bot animebot-bot
    docker run -d --env-file .env -p 5000:5000 --name animebot-web animebot-web
    ```

    The web server will be accessible at `http://localhost:5000`.

6. To stop the containers:

    ```
    docker stop animebot-bot animebot-web
    ```

7. To remove the containers:

    ```
    docker rm animebot-bot animebot-web
    ```

## Commands

-   `/start` - Initialize the bot and display the main menu
-   `/help` - Display help information and FAQ
-   Use inline queries to search for content (e.g., `@YourBotUsername #anime Naruto`)

## Project Structure

-   `bot/` - Contains the Telegram bot code
-   `web/` - Contains the Flask web server code
-   `Dockerfile.bot` - Dockerfile for the Telegram bot
-   `Dockerfile.web` - Dockerfile for the web server

## Database

The project uses PostgreSQL as its database. The main models are:

-   `Users` - Stores user information and preferences
-   `Anime` - Stores information about anime titles

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

-   [aiogram](https://github.com/aiogram/aiogram) - Telegram Bot framework
-   [Flask](https://flask.palletsprojects.com/) - Web framework
-   [SQLAlchemy](https://www.sqlalchemy.org/) - ORM for database operations

---

For more information on how to use the bot and frequently asked questions, visit our [FAQ page](https://telegra.ph/Otvety-na-chasto-zadavaemye-voprosy-03-18-3).
