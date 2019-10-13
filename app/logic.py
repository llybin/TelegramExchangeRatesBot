from app.helpers import import_module
from app.keyboard import KeyboardSimpleClever
from app.models import Chat
from app.parsers.base import PriceRequest
from app.parsers.exceptions import ValidationException
from app.queries import get_last_request
from suite.conf import settings
from suite.database import Session


def get_keyboard(chat_id: int, symbol="") -> list or None:
    if chat_id < 0:
        return None

    chat = Session.query(Chat).filter_by(id=chat_id).first()

    if not chat.is_show_keyboard:
        return None

    else:
        last_requests = get_last_request(chat_id)

        if last_requests:
            last_reqs_list = [
                f"{symbol}{x.from_currency.code} {x.to_currency.code}"
                for x in last_requests
            ]
            width = int(chat.keyboard_size.split("x")[0])
            return KeyboardSimpleClever(last_reqs_list, width).show()

        return None


PARSERS = [import_module(parser_path) for parser_path in settings.BOT_PARSERS]


def start_parse(
    text: str,
    chat_id: int,
    locale: str,
    default_currency: str,
    default_currency_position: bool,
) -> PriceRequest:
    for parser in PARSERS:
        try:
            return parser(
                text, chat_id, locale, default_currency, default_currency_position
            ).parse()
        except ValidationException:
            pass

    raise ValidationException
