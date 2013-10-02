from tasks import create

def add_task(request):
    create.delay(1,1,1)