# pro.guap-report-generator

В данной ветке реализован Telegram-бот для работы с шаблонами отчётов в 
личном кабинете ГУАП. (см. 
[Issue #5](https://github.com/markpolyak/pro.guap-report-generator/issues/5)).

## Сборка

```shell
docker build --tag report-bot ./telegram_bot/
docker build --tag report-mock-backend ./mock_backend/
docker build --tag report-register ./register_server/
```

## Запуск

Перед запуском необходимо создать мост между ботом и бэкендом:

```shell
docker network create report-bot
```

Запуск:

```shell
docker run --rm --net report-net --name bot -d report-bot
docker run --rm --net report-net --name backend -d report-backend
docker run --rm --name register -d --publish 8080:5000 report-register
```