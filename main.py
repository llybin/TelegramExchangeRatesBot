from app.models import engine
from suite.conf import settings


if __name__ == "__main__":
    # import os
    # os.environ.setdefault('SETTINGS_MODULE', 'app.settings')

    print(settings.SQLALCHEMY['url'])
