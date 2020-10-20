from celery import Celery
from celery.result import AsyncResult

app = Celery('tasks_example',
             broker='redis://127.0.0.1:6379/1',
             backend='redis://127.0.0.1:6379/2')


@app.task  # Task
def add(x, y):
    print(f'{x} + {y}')
    return x + y


app.conf.beat_schedule = {
    'add-every-10-seconds': {
        'task': 'tasks_example.add',
        'schedule': 10.0,
        'args': (3, 4)
    }
}

if __name__ == '__main__':
    ret: AsyncResult = add.delay(1, 2)
    print(ret.id)
    print(ret.get())
