from celery import Celery

celery = Celery("tasks",backend = f'db+postgresql://postgres:238956@localhost:5432/postgres',broker ='redis://:JUSTWIN12@localhost:6379/0')

@celery.task
def add(x, y):
    return x + y