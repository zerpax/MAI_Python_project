from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from tasks import predict  # Импортируем задачу predict
import logging
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Функция, которая вызывает задачу
def schedule_daily_task():
    logger.info("Запуск задачи 'predict'")
    predict.delay()  # Запускаем задачу Celery


# Инициализация планировщика
def start_scheduler():
    scheduler = BackgroundScheduler()

    # Добавление задачи в расписание
    scheduler.add_job(
        schedule_daily_task,
        trigger=CronTrigger(hour=0, minute=0),  # Запуск в полночь каждый день
        id='daily_predict_task',
        replace_existing=True
    )

    # Запуск планировщика
    scheduler.start()
    logger.info("APScheduler запущен")

    try:
        while True:
            time.sleep(1)  # Удерживаем процесс активным
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("APScheduler остановлен")


if __name__ == '__main__':
    start_scheduler()
