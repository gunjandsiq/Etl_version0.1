from app import celery 
from celery import chain  # type: ignore


@celery.task
def add(x, y):
    return x + y

@celery.task
def mul(x, y):
    return x * y





