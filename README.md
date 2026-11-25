# Twitch API

REST API developed with **FastAPI** to manage users and their favourite Twitch streamers. The application uses **MySQL** to store data and the **official Twitch API** to retrieve streamer profiles and live streaming information.

## Features

- Create, retrieve, update and delete users.
- Add streamers to each user's favourites list.
- Retrieve and remove favourite streamers.
- Retrieve information about individual Twitch streamers.
- Check the live status of a user's favourite streamers.
- Validate incoming data and handle errors using HTTP status codes.

## Technologies Used

- Python
- FastAPI
- MySQL
- Pydantic
- Requests
- Twitch API

## Project Structure

```text
twitch-api/
├── configuration/
├── models/
├── routers/
├── services/
├── sql-scripts/
├── main.py
├── .env
├── .env.template
├── .gitignore
├── requirements.txt
└── README.md
```

## Prerequisites

To run this project, the following software and credentials are required:

- Python 3.10 or higher.
- MySQL Server.
- Git.
- Credentials for an application registered on the Twitch Developer Console.

## Installation and Configuration

### 1. Clone the repository

```bash
git clone <REPOSITORY_URL>
cd twitch-api
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate the virtual environment:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file based on `.env.template` and provide the required credentials:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=twitch_api

TWITCH_CLIENT_ID=your_client_id
TWITCH_CLIENT_SECRET=your_client_secret
```

### 5. Configure the database

Create the MySQL database and execute the SQL scripts located in the `sql-scripts/` directory to create the required tables.

### 6. Run the application

From the project root directory, execute:

```bash
uvicorn main:app --reload
```

## Main Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Welcome message |
| `POST` | `/users` | Create a user |
| `GET` | `/users` | Retrieve all users |
| `GET` | `/users/{user_id}` | Retrieve a specific user |
| `PATCH` | `/users/{user_id}` | Update a user |
| `DELETE` | `/users/{user_id}` | Delete a user |
| `POST` | `/users/{user_id}/favorites` | Add a favourite streamer |
| `GET` | `/users/{user_id}/favorites` | Retrieve a user's favourite streamers |
| `DELETE` | `/users/{user_id}/favorites/{twitch_login}` | Remove a favourite streamer |
| `GET` | `/twitch/streamers/{login}` | Retrieve information about a streamer |
| `GET` | `/twitch/users/{user_id}/favorites` | Retrieve information and live status of a user's favourite streamers |

## Project Documentation

Detailed documentation covering the development process, project structure, testing and observations is available in:

`Twitch_API_Documentation.md`

## Author

Alba Bigarella Martínez

Master's Degree in Web Application Development

Academic Year 2026–2027
