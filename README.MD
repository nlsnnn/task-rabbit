# Task Queue Service

Асинхронный сервис обработки задач на FastAPI с использованием RabbitMQ и PostgreSQL.

## Быстрый старт

1. Клонируйте репозиторий:

```bash
git clone https://github.com/nlsnnn/task-rabbit.git
cd task-rabbit
```

2. Создайте `.env` файл из примера:

```bash
cp .env.example .env
```

3. Запустите все сервисы:

```bash
docker-compose up --build
```

### Доступные сервисы

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (только в debug режиме)
- **RabbitMQ Management UI**: http://localhost:15672 (guest/guest)
- **PostgreSQL**: localhost:5432

## Архитектура

Система состоит из четырёх основных компонентов:

1. **API (FastAPI)** - принимает HTTP-запросы, сохраняет задачи в БД, публикует в очередь
2. **Worker** - забирает задачи из очереди, обрабатывает, обновляет статусы в БД
3. **PostgreSQL** - хранит задачи и их статусы
4. **RabbitMQ** - очередь сообщений для асинхронной обработки

### Почему выбран RabbitMQ, а не Kafka?

- Простота настройки и эксплуатации. RabbitMQ из коробки готов к работе, не требует сложной конфигурации как Kafka.
- Kafka избыточен для простой очереди задач.
- Management UI. Удобный веб-интерфейс для мониторинга и отладки из коробки.
- Docker-образ легче, стартует быстрее.

### Как масштабировать решение

#### Горизонтальное:

**Воркеры:**

```bash
docker-compose up --scale worker=5  # 5 параллельных воркеров
```

Несколько воркеров будут параллельно забирать задачи из очереди. Каждый воркер независим.

**API:**

```bash
docker-compose up --scale backend=3  # 3 инстанса FastAPI
```

Несколько инстансов API за load balancer (nginx/traefik). Каждый публикует в одну очередь.

#### Вертикальное:

- **PostgreSQL**: увеличить CPU/RAM, настроить connection pooling (PgBouncer), добавить read replicas для чтения статусов
- **RabbitMQ**: увеличить ресурсы, настроить кластер (3-5 нод) для высокой доступности

### Точки отказа

1. **Единая точка отказа везде**
   - Один PostgreSQL, падение = полная остановка системы
   - Один RabbitMQ, падение = задачи не обрабатываются
   - Если API упадёт во время публикации в очередь (после сохранения в БД), задача зависнет в pending

2. **Network split**
   - Worker может потерять соединение с RabbitMQ/Postgres во время обработки
   - Задача останется в processing, хотя воркер умер

3. **Race conditions**
   - Если два воркера обработают одно сообщение
   - Решается идемпотентностью или блокировкой во время запроса

#### Решения

**Высокая доступность:**

- PostgreSQL: master-slave репликация или Patroni
- RabbitMQ: кластер из 3-5 нод
- API/Worker: несколько инстансов, перезапуск при падении

**Мониторинг:**

- Dead letter queue для проблемных задач
- Алерты на зависшие задачи (processing > 10 минут)
- Метрики: queue size, processing time, error rate

### Что улучшить для продакшена

1. **Graceful shutdown** - воркер должен доработать текущую задачу перед остановкой
2. **Retry policy** - автоматический retry для failed задач
3. **Логирование** - структурированные логи (JSON), отправка в ELK/Loki
4. **Monitoring & Observability** - Prometheus метрики, Grafana дашборды, алерты
5. **Health checks** - `/health` endpoint для мониторинга состояния API
6. **Rate limiting** - защита от DDoS и перегрузки
7. **Тесты** - unit/integration тесты (pytest), CI/CD


## Технологии

- **Python 3.12**
- **FastAPI**
- **SQLAlchemy** - async ORM
- **Alembic** - миграции БД
- **aio-pika** - async клиент для RabbitMQ
- **asyncpg** - async драйвер для PostgreSQL
- **PostgreSQL 16**
- **RabbitMQ 4.2**