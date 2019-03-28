import gettext
import logging

from suite.conf import settings

_ = gettext.gettext

translations = dict()


def init_translations():
    for l in settings.LANGUAGES:
        # zh_Hans to zh-hans
        key = l.lower().replace('_', '-')
        translations[key] = gettext.translation(
            'messages',
            localedir='locale',
            languages=[l]
        )


def get_translations(language_code: str):
    if language_code in translations:
        return translations[language_code].gettext

    elif language_code[:2] in translations:
        # en-us
        return translations[language_code[:2]].gettext

    elif language_code[:7] in translations:
        # zh-hans-sg
        return translations[language_code[:7]].gettext

    else:
        logging.info('No translations for language: %s', language_code)
        return gettext.gettext
