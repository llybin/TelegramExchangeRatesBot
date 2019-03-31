# Telegram ExchangeRatesBot

[![Build Status](https://travis-ci.com/llybin/TelegramExchangeRatesBot.svg?branch=master)](https://travis-ci.com/llybin/TelegramExchangeRatesBot)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/ddb58369590944a69a53737837c8dd3b)](https://www.codacy.com/app/llybin/TelegramExchangeRatesBot?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=llybin/TelegramExchangeRatesBot&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/ddb58369590944a69a53737837c8dd3b)](https://www.codacy.com/app/llybin/TelegramExchangeRatesBot?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=llybin/TelegramExchangeRatesBot&amp;utm_campaign=Badge_Coverage)
[![GPLv3](https://img.shields.io/badge/license-GPLv3-blue.svg)](LICENSE)

Telegram bot actual exchange rates for travel, work and daily life.

Online from 01 July 2015.

[https://telegram.me/ExchangeRatesBot]()

## Translations

Don't have your localization? Any translation errors? Help fix it.

👉 [PoEditor.com](https://poeditor.com/join/project/LLu8AztSPb)

## How to run

`cp .env.default .env`

Configure your .env:

BOT_TOKEN - set up

`docker-compose up`

## Development

### See manage commands

`docker-compose run service ./manage.py`

### How to run tests

`docker-compose run service ./manage.py test`
