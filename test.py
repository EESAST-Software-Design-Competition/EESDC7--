import json
import os
import time
import uuid
import atexit

from flask import Flask, redirect, url_for, render_template, request, session, send_from_directory

from mysql import Mysql
from flask_apscheduler import APScheduler
import datetime
import fcntlock as fcntl


class MyFlask(Flask):
    sqlite = Mysql()

    def __init__(self, *args, **kwargs):
        os.makedirs("./data", exist_ok=True)
        os.makedirs("./db", exist_ok=True)
        super(MyFlask, self).__init__(*args, **kwargs)

    def run(self, host=None, port=None, debug=None, load_dotenv=True, clear=False, **options):
        self.sqlite.new_table(clear=clear)
        super(MyFlask, self).run(host, port, debug, load_dotenv, **options)


class Config(object):
    SCHEDULER_API_ENABLED = True


scheduler = APScheduler()
app = MyFlask(__name__)
app.config["SECRET_KEY"] = "fwou4pj49qaJFSLIjflkq"


@app.route("/")
def home():
    return redirect(url_for('create'))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/help")
def help():
    return render_template("help.html")

@app.route("/create/", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        name = request.form["name"]
        author = request.form["author"]
        url = MyFlask.sqlite.create_board(name, author)
        if 'id' not in session:
            session['id'] = str(uuid.uuid1())
        session[url] = author
        return redirect(url_for('room', url=url))
    return render_template("create.html")


@app.route("/room/<url>")
def room(url):
    if not os.path.exists(f"./data/{url}/information.json"):
        return redirect(url_for('create', status=404))
    if 'id' not in session or url not in session:
        return redirect(url_for('login', url=url))
    information = json.load(open(f"./data/{url}/information.json"))
    app.sqlite.open_board(url)
    app.sqlite.update_users(url, {"name": session[url], "id": str(session["id"])})
    return render_template("index.html", url=url, user=session["id"], name=information["name"], author=information["author"], client=session[url])


@app.route("/room/<url>/view")
def guest(url):
    if not os.path.exists(f"./data/{url}/information.json"):
        return redirect(url_for('create', status=404))
    information = json.load(open(f"./data/{url}/information.json"))
    app.sqlite.open_board(url)
    return render_template("guest.html", url=url, name=information["name"], author=information["author"])


@app.route("/room/<url>/login", methods=["GET", "POST"])
def login(url):
    if not os.path.exists(f"./data/{url}/information.json"):
        return redirect(url_for('create', status=404))
    if 'id' in session and url in session:
        return redirect(url_for('room', url=url))
    if request.method == "POST":
        if 'id' not in session:
            session['id'] = str(uuid.uuid1())
        session[url] = request.form["name"]
        return redirect(url_for('room', url=url))
    information = json.load(open(f"./data/{url}/information.json"))
    return render_template("login.html", url=url, name=information["name"], author=information["author"])


@app.route('/api/<room>/create', methods=["POST"])
def update_namef(room):
    if not os.path.exists(f"./data/{room}/namef.json"):
        return {"status": 404, "message": "Room Not Found"}
    app.sqlite.open_board(room)
    if "id" not in session:
        return {"status": 403, "message": "Forbidden"}
    for user1 in app.sqlite.get_users(room):
        if str(session["id"]) == user1["id"]:
            break
    else:
        return {"status": 403, "message": "Forbidden"}
    formular_id = str(uuid.uuid1())
    formular_name = request.form["name"]
    app.sqlite.update_namef(room, {"id": formular_id, "name": formular_name, "status": 0})
    app.sqlite.set_time_last_oper(room)
    return {"status": 200, "message": "OK", "id": formular_id, "name": formular_name}


@app.route('/api/<room>/entries')
def get_entries(room):
    if not os.path.exists(f"./data/{room}/entry.json"):
        return {"status": 404, "message": "Room Not Found"}
    app.sqlite.open_board(room)
    app.sqlite.set_time_last_oper(room)
    return json.dumps(app.sqlite.get_entry(room))


@app.route('/api/<room>/users')
def get_users(room):
    if not os.path.exists(f"./data/{room}/users.json"):
        return {"status": 404, "message": "Room Not Found"}
    app.sqlite.open_board(room)
    app.sqlite.set_time_last_oper(room)
    return json.dumps(app.sqlite.get_users(room))


@app.route('/api/<room>/drafts')
def get_drafts(room):
    if not os.path.exists(f"./data/{room}/draft.json"):
        return {"status": 404, "message": "Room Not Found"}
    app.sqlite.open_board(room)
    app.sqlite.set_time_last_oper(room)
    return json.dumps(app.sqlite.get_draft(room))


@app.route('/api/<room>/names')
def get_namef(room):
    if not os.path.exists(f"./data/{room}/namef.json"):
        return {"status": 404, "message": "Room Not Found"}
    app.sqlite.open_board(room)
    app.sqlite.set_time_last_oper(room)
    return json.dumps(app.sqlite.get_namef(room))


@app.route('/api/<room>/<user>/<formula>', methods=["POST", "DELETE"])
def edit_draft(room,user,formula):
    if not os.path.exists(f"./data/{room}/namef.json"):
        return {"status": 404, "message": "Room Not Found"}
    app.sqlite.open_board(room)
    if "id" not in session or str(session["id"]) != user:
        return {"status": 403, "message": "Forbidden"}
    if room not in session:
        return redirect(url_for('login', url=room), code=403)
    for user1 in app.sqlite.get_users(room):
        if user == user1["id"]:
            break
    else:
        return {"status": 403, "message": "Forbidden"}
    for formular1 in app.sqlite.get_namef(room):
        if formula == formular1["id"]:
            break
    else:
        return {"status": 404, "message": "Formular Not Found"}
    app.sqlite.set_time_last_oper(room)
    if request.method == "DELETE":
        app.sqlite.delete_draft(room, user, formula)
        return {"status": 200, "message": "OK"}
    text = request.form["text"]
    name = request.form["name"]
    app.sqlite.update_namef(room, {"id": formula, "name": name,"status":0})
    app.sqlite.update_draft(room, user, formula, {"name":name, "text": text, "time": time.time()})
    return {"status": 200, "message": "OK"}


@app.route('/api/<room>/<user>/<formular>/submit', methods=["POST"])
def update_entry(room,user,formular):
    if not os.path.exists(f"./data/{room}/entry.json"):
        return {"status": 404, "message": "Room Not Found"}
    app.sqlite.open_board(room)
    if "id" not in session or str(session["id"]) != user:
        return {"status": 403, "message": "Forbidden"}
    if room not in session:
        return redirect(url_for('login', url=room), code=403)
    for user1 in app.sqlite.get_users(room):
        if user == user1["id"]:
            break
    else:
        return {"status": 403, "message": "Forbidden"}
    for formular1 in app.sqlite.get_namef(room):
        if formular == formular1["id"]:
            break
    else:
        return {"status": 404, "message": "Formular Not Found"}
    #formular_text = request.form["text"]
    formular_time = time.time()
    draft = app.sqlite.get_draft_by_id(room, user, formular)
    app.sqlite.set_namef_submitted(room, formular)
    app.sqlite.update_entry(room, {"id": formular, "name":draft["name"], "text": draft["text"], "editor": user, "time": formular_time})
    app.sqlite.delete_draft(room, user, formular)
    app.sqlite.set_time_last_oper(room)
    #app.sqlite.update_draft(room, user, formular, {"text": formular_text, "time": formular_time})
    return {"status": 200, "message": "OK"}


@scheduler.task('interval', id='save', seconds=61, misfire_grace_time=900)
def job1():
    app.sqlite.save_all()
    print(str(datetime.datetime.now()) + ' save executed')


@scheduler.task('interval', id='close', seconds=10, misfire_grace_time=1000)
def job2():
    #print(app.sqlite.id_now)
    for url in list(app.sqlite.Time_last_oper.keys()):
        # print(url, app.sqlite.Time_last_oper[url])
        if app.sqlite.test_time_last_oper(url):
            app.sqlite.close_board(url)
            print(str(datetime.datetime.now()) + url + ' close executed')
    print(str(datetime.datetime.now()) + ' no close executed')


def create_apscheduler(scheduler):
    f = open("./aps.lock", "wb")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        apscheduler = scheduler
        apscheduler.api_enabled = True
        apscheduler.init_app(app)
        apscheduler.start()
    except:
        pass

    def unlock():
        try:
            fcntl.flock(f, fcntl.LOCK_UN)
        except:
            pass
        f.close()

    atexit.register(unlock)


@atexit.register
def exit_handler():
    MyFlask.sqlite.close_all()

if __name__ == '__main__':
    # scheduler.api_enabled = True
    # scheduler.init_app(app)
    # scheduler.start()
    create_apscheduler(scheduler)
    app.run(host="127.0.0.1", port=5000, debug=False, clear=False)
