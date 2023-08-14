broker_url = 'pyamqp://guest@rabbitmq//'
result_backend = 'redis://redis:6379/0'

imports = ('app.celery_worker',)

beat_schedule = {
    'add-menu-every-20-seconds': {
        'task': 'app.celery_worker.add_menu',
        'schedule': 15.0
    },
}
