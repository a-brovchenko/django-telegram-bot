# django-telegram-bot

This is a simple news aggregator that provides the latest news based on selected tags. The bot offers several functions:

- Sends the latest global news.
- Sends the latest news related to a chosen tag.
- Allows users to subscribe to newsletters for specific tags.
- Generates an API token for subscribed users.

### To run a project using Docker 
Create an .env file in the app folder and specify the following variables:
```env
BOT_TOKEN='Your bot token'
DJANGO_TOKEN='Your Django project token'
```
Then navigate to the folder with the Docker Compose file and run it through the terminal:
```
docker-compose up -d
```

### Running the Bot Locally
Create an .env file in the app folder and specify the variables:
```
BOT_TOKEN='Your bot token'
DJANGO_TOKEN='Your django project token'
```
In the project settings in the cache, replace
```
'LOCATION': 'redis://redis:6379/0'
```
with
```
'LOCATION': 'redis://127.0.0.1:6379/0'
```
Start the redis container
```
docker run -d -p 6379:6379 redis
```
Start the Django server:
```
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```
After running, your server is accessible at
```
http://localhost:8000/
```
## API 
API endpoints are available at the following links:
- Get all news from the database:

```
http://host_name:port/api/news/
```
- Get all tags from the database:

```
http://host_name:port/api/tags/
```

To retrieve data, follow these steps in the Telegram bot:

- Go to "My subscriptions"
- Click "Subscribe" if not subscribed and enter the tag
- Click "Show Token"
- If no token exists, click "Generate it"

Now you have access to the bot API, and you can use it, for example, in your code:

```
import requests

url = 'http://host_name:port/api/news/'
token = 'your token'

headers = {
    'Authorization': f'Token {token}',
}

response = requests.get(url, headers=headers)
print(response.json())
```