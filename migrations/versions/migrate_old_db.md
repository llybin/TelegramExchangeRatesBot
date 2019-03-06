pg_dump --data-only tg_exchange_bot -t chats > data_chats.sql
pg_dump --data-only tg_exchange_bot -t chat_rates > data_chat_rates.sql
pg_dump --data-only tg_exchange_bot -t messages > data_messages.sql

python manage.py db migrate --migration_name 8b7deeb35c6c

psql -h127.0.0.1 -Upostgres postgres < data_chats.sql
psql -h127.0.0.1 -Upostgres postgres < data_chat_rates.sql
psql -h127.0.0.1 -Upostgres postgres < data_messages.sql

python manage.py db migrate
