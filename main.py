from app import config
from app.models import engine


if __name__ == "__main__":
    print(config['app']['sqlalchemy.url'])
