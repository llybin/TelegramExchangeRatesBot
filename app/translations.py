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


def get_translations(language_code: str) -> gettext:
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


def transform_locale(locale: str) -> str:
    """ Transform format locale
    See available formats: site-packages/babel/locale-data
    """
    locale_parts = locale.split('-')
    len_parts = len(locale_parts)

    if len_parts == 1:
        # zh
        return locale_parts[0]

    elif len_parts == 2:
        len_second = len(locale_parts[1])
        if len_second == 2:
            # br-pt -> br_PT
            return f'{locale_parts[0].lower()}_{locale_parts[1].upper()}'
        elif len_second > 2:
            # zh-hans -> zh_Hans
            return f'{locale_parts[0].lower()}_{locale_parts[1].capitalize()}'

    elif len_parts == 3:
        # zh-hans-sg -> zh_Hans_SG
        return f'{locale_parts[0].lower()}_{locale_parts[1].capitalize()}_{locale_parts[2].upper()}'

    logging.error('Unknown format locale: %s', locale)
    return settings.LANGUAGE_CODE
