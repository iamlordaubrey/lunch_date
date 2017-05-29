import os
import random
import time
import threading
import asyncio

from dotenv import load_dotenv, find_dotenv
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from celery import Celery
from celery.schedules import crontab

load_dotenv(find_dotenv())

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['broker_url'] = os.environ.get('REDISCLOUD_URL')
app.config['result_backend'] = app.config['broker_url']
# app.config['beat_schedule'] = {
#     'run_task': {
#         'task': 'do_some',
#         'schedule': crontab(hour=10, minute=31, day_of_week='mon-fri')
#     },
# }
# app.config['enable_utc'] = False
app.config['timezone'] = 'Africa/Lagos'

celery = Celery(app.name, broker=app.config['broker_url'])
celery.conf.update(app.config)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # calls test function every 10secs
    sender.add_periodic_task(
        crontab(hour=13, minute=00, day_of_week='mon-fri'),
        test.s("hello there!!!")
    )


@celery.task
def test(arg):
    print(arg)

db = SQLAlchemy(app)

bot_channel = "luncheon"

w = threading.Thread()


# def make_celery(app):
#     app.config['CELERY_BROKER_URL'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
#     app.config['CELERY_RESULT_BACKEND'] = app.config['CELERY_BROKER_URL']
#
#     # create context tasks in celery
#     celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
#     celery.conf.update(app.config)
#     TaskBase = celery.Task
#
#     class ContextTask(TaskBase):
#         abstract = True
#
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return TaskBase.__call__(self, *args, **kwargs)
#
#     celery.Task = ContextTask
#     return celery

# celery = make_celery(app)


@app.route('/task1', methods=["GET"])
def view1():
    background_task.delay(20, 10)

    return 'OK with task1'


# @app.route('/task2', methods=["GET"])
@celery.task(name='do_some')
def some_task():
    background_task.apply_async(args=[25, 15], countdown=10)

    return 'OK with task2'


@app.route('/longtask', methods=['POST'])
def longtask():
    task = long_task.apply_async()
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id)}


@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


@celery.task
def background_task(x, y):
    print('background task called!')
    for i in range(x):
        print('i: ', i)
    for j in range(y):
        print('key: ', j)
        # print('val: ', v)

    return 'finished!!!'


@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}


@app.route("/")
def index():
    return redirect(url_for('oauth_dance'))


@app.route("/install")
def oauth_dance():

    code = request.args.get('code')
    if code:
        from models import get_team_details
        print('code', code)
        team = get_team_details(code)
        print('team: ', team)

        # team_id = team_details['team_id']
        # team_name = team_details['team_name']
        # access_token = team_details['access_token']
        # bot_access_token = team_details['bot']['bot_access_token']
        #
        # print('access_token: ', access_token)
        #
        # team_exists = db.session.query(Bot).filter_by(team_id=team_id).scalar()
        #
        # print('bot_exists: ', team_exists)
        # print('bot methods', dir(team_exists))

        if not team:
            # Team already registered (team is false)
            # ADd some form of 'already exists' message here
            print('team already in db')
            return redirect(url_for('thanks'))

        # new_team = Bot(team_id, team_name, access_token, bot_access_token)
        # add_to_db(new_team)
        # global w
        # w = threading.Thread(name=team.team_name + ' Thread', target=invoke_watcher, args=(team,))
        # w.start()
        start_watchers()

        return redirect(url_for('thanks'))

    from models import oauth
    return render_template("install.html", client_id=oauth["client_id"], scope=oauth["scope"])


@app.route("/thanks", methods=["GET", "POST"])
def thanks():
    # w = Thread(target=invoke_watcher)
    # w.start()

    return render_template("thanks.html")


# def get_team_details(code):
#     sc = SlackClient("")
#     team_details = sc.api_call(
#         "oauth.access",
#         client_id=oauth["client_id"],
#         client_secret=oauth["client_secret"],
#         code=code
#     )
#
#     return team_details


# @app.route("/Vc6htAgefXlrIMuGJfoH", methods=["GET"])
def thread_check():
    # main_thread = threading.main_thread()
    # for t in threading.enumerate():
    #     if t is main_thread:
    #         continue
    print('thread name: ', threading.current_thread().name)

    print('threads: ', threading.active_count())
    print('length: ', threading.active_count())
    if threading.active_count() == 1:
        print('thread == 1. starting watchers')
        start_watchers()
        return render_template("404.html")

    print('threads > 1. not doing nothing')
    return render_template("404.html")


def invoke_watcher(loop, team):
    print('in invoke watcher')
    # while True:
    # from models import get_all_teams
    # print('in while true')
    # print('team in watcher: ', team)
    asyncio.run_coroutine_threadsafe(create_thread_for_team(team), loop)
    print('threads: ', threading.active_count())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        # Canceling pending tasks and stopping the loop
        asyncio.gather(*asyncio.Task.all_tasks()).cancel()
        # Stopping the loop
        loop.stop()
        # Received Ctrl+C
        loop.close()
        # teams = get_all_teams()
        # print('orgs: ', teams)

        # if teams:
        #     for team in teams:
        #         gmt_plus_one = datetime.now() + timedelta(hours=1)
        #         current_time = "{:%H:%M}".format(gmt_plus_one)
        #
        #         print(team.runtime(), current_time)
        #
        #         if str(current_time) == team.runtime():
        #             team.runner()
        # print('thread name: ', threading.current_thread().name)
        #
        # gmt_plus_one = datetime.now() + timedelta(hours=1)
        # current_time = "{:%H:%M}".format(gmt_plus_one)
        #
        # print(team.runtime(), current_time)
        # if str(current_time) == team.runtime():
        #     team.runner()

        # Sleep for a minute without triggering an error
        # time.sleep(20)
        # time.sleep(20)
        # time.sleep(20)

async def create_thread_for_team(team):
    while True:
        print('in while loop')
        print('thread name: ', threading.current_thread().name)

        gmt_plus_one = datetime.now() + timedelta(hours=1)
        current_time = "{:%H:%M}".format(gmt_plus_one)

        print(team.runtime(), current_time)
        if str(current_time) == team.runtime():
            team.runner()

        await asyncio.sleep(30)
        await asyncio.sleep(30)


def start_watchers():
    print('in start watcher. should run once')
    from models import get_all_teams
    teams = get_all_teams()
    print('all teams in db: ', teams)

    for team in teams:
        print('a team from db: ', team)
        # global w
        # w = threading.Thread(name=team.team_name + ' Thread', target=invoke_watcher, args=(team,))
        # w.start()
        worker_loop = asyncio.new_event_loop()

        worker = threading.Thread(name=team.team_name + ' Thread', target=invoke_watcher, args=(worker_loop, team,))
        worker.start()


# def start_server():
#     print('starting server')
#     app.run()


if __name__ == "__main__":
    # start_watchers()

    # s = threading.Thread(target=start_server)
    # s.start()
    app.run()
