from copy import deepcopy
from collections import defaultdict
from suite.conf import settings

import redis

from telegram.ext.basepersistence import BasePersistence

STORAGE_TTL = 60 * 60 * 24 * 30
CHAT_DATA_KEY = 'chat_data'
USER_DATA_KEY = 'user_data'
CONVERSATIONS_KEY = 'conversations'


class RedisPersistence(BasePersistence):
    redis: redis

    chat_data: defaultdict or None
    user_data: defaultdict or None
    conversations: dict or None

    def __init__(self, store_user_data=True, store_chat_data=True):
        super().__init__(store_user_data, store_chat_data)
        self.redis = redis.StrictRedis.from_url(settings.BOT_PERSISTENCE_URL)
        self.user_data = None
        self.chat_data = None
        self.conversations = None

    def get_user_data(self) -> defaultdict:
        if self.user_data is None:
            data = self.redis.get(USER_DATA_KEY)
            if data:
                self.user_data = defaultdict(dict, data)
            else:
                self.user_data = defaultdict(dict)

        return deepcopy(self.user_data)

    def get_chat_data(self) -> defaultdict:
        if self.chat_data is None:
            data = self.redis.get(CHAT_DATA_KEY)
            if data:
                self.chat_data = defaultdict(dict, data)
            else:
                self.chat_data = defaultdict(dict)

        return deepcopy(self.chat_data)

    def get_conversations(self, name: str) -> dict:
        if self.conversations is None:
            data = self.redis.get(CONVERSATIONS_KEY)
            if data:
                self.conversations = data
            else:
                self.conversations = {}

        return self.conversations.get(name, {}).copy()

    def update_conversation(self, name, key, new_state) -> None:
        if self.conversations.setdefault(name, {}).get(key) == new_state:
            return
        self.conversations[name][key] = new_state
        self.redis.setex(CONVERSATIONS_KEY, STORAGE_TTL, self.conversations)

    def update_user_data(self, user_id, data) -> None:
        if self.user_data.get(user_id) == data:
            return
        self.user_data[user_id] = data
        self.redis.setex(USER_DATA_KEY, STORAGE_TTL, self.user_data)

    def update_chat_data(self, chat_id, data) -> None:
        if self.chat_data.get(chat_id) == data:
            return
        self.chat_data[chat_id] = data
        self.redis.setex(CHAT_DATA_KEY, STORAGE_TTL, self.chat_data)

    def flush(self) -> None:
        if self.user_data:
            self.redis.setex(USER_DATA_KEY, STORAGE_TTL, self.user_data)
        if self.chat_data:
            self.redis.setex(CHAT_DATA_KEY, STORAGE_TTL, self.chat_data)
        if self.conversations:
            self.redis.setex(CONVERSATIONS_KEY, STORAGE_TTL, self.conversations)
