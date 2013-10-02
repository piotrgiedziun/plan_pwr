from celery import task

@task()
def create(login, password, session_id):
    return 2