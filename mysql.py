import json
import os
import random
import time

from sqlalchemy import create_engine, text


class Mysql:
    id_now = 0
    Entry = {}  # {url:[{"id":x, "name":u, "text":y, "editor":z, "time":w}]}
    Users = {}  # {url:[{"id":x, "name":y}]}
    Draft = {}  # {url:{(formular_id, user_id):{"name":u, "text":x, "time":y}}}
    Namef = {}  # {url:[{"id":x, "name":y, "status":z}]} z:0:未提交 1:已提交
    Time_last_oper = {}  # {url:time}

    def __init__(self):
        self.__engine = create_engine("sqlite:///./db/test.db", echo=True, future=True)

    def new_table(self, clear=False):
        with self.__engine.connect() as sqldb:
            if clear:   # 清空表
                sqldb.execute(text("drop table if exists info"))
                self.id_now = 0
            sqldb.execute(text(f"create table if not exists info(id integer PRIMARY KEY, name text, rand_url char(4), "
                               f"author text, status int, create_time int)"))
            # 获取最大主键
            result = sqldb.execute(text("select max(id) from info"))
            for row in result:
                self.id_now = row[0] + 1 if row[0] is not None else 0
                return

    def create_board(self, name, author):
        random_url = random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=4)
        random_url = str(self.id_now)+"".join(random_url)   # 生成随机url
        create_time = int(time.time())
        # 插入数据
        with self.__engine.connect() as sqldb:
            sqldb.execute(text(f"insert into info (id, name, rand_url, author, status, create_time) "
                               f"values({self.id_now}, '{name}', '{random_url}', '{author}', 0, {create_time})"))
            sqldb.commit()
        # 建立对应资源文件夹
        os.makedirs(f"./data/{random_url}")
        with open(f"./data/{random_url}/information.json", "w") as fp:
            json.dump({'id': self.id_now, 'name': name, 'url': random_url, 'author': author, 'status': 0, 'create_time': create_time}, fp)
        with open(f"./data/{random_url}/entry.json", "w") as fp:
            json.dump([], fp)
        with open(f"./data/{random_url}/users.json", "w") as fp:
            json.dump([], fp)
        with open(f"./data/{random_url}/draft.json", "w") as fp:
            json.dump([], fp)
        with open(f"./data/{random_url}/namef.json", "w") as fp:
            json.dump([], fp)
        self.id_now += 1
        return random_url

    def open_board(self, url):
        if url in self.Entry.keys():
            return
        with open(f"./data/{url}/entry.json", "r") as fp:
            self.Entry[url] = json.load(fp)
        with open(f"./data/{url}/users.json", "r") as fp:
            self.Users[url] = json.load(fp)
        with open(f"./data/{url}/draft.json", "r") as fp:
            temp = json.load(fp)
            self.Draft[url] = {(x["id"], x["editor"]):{"name":x["name"], "text":x["text"], "time":x["time"]} for x in temp}
        with open(f"./data/{url}/namef.json", "r") as fp:
            self.Namef[url] = json.load(fp)
        self.Time_last_oper[url] = int(time.time())

    def save_board(self, url):
        if url not in self.Entry.keys():
            return
        with open(f"./data/{url}/entry.json", "w") as fp:
            json.dump(self.Entry[url], fp)
        with open(f"./data/{url}/users.json", "w") as fp:
            json.dump(self.Users[url], fp)
        with open(f"./data/{url}/draft.json", "w") as fp:
            json.dump([{"id": key[0], "name":self.Draft[url][key]['name'], "editor":key[1], "text":self.Draft[url][key]['text'], "time":self.Draft[url][key]["time"]} for key in self.Draft[url].keys()], fp)
        with open(f"./data/{url}/namef.json", "w") as fp:
            json.dump(self.Namef[url], fp)

    def save_all(self):
        for url in self.Entry.keys():
            self.save_board(url)

    def close_board(self, url):
        if url not in self.Entry.keys():
            return
        self.save_board(url)
        self.Entry.pop(url)
        self.Users.pop(url)
        self.Draft.pop(url)
        self.Namef.pop(url)
        self.Time_last_oper.pop(url)

    def set_time_last_oper(self, url):
        self.Time_last_oper[url] = int(time.time())
        #print(self.Time_last_oper)
    
    def test_time_last_oper(self, url):
        return time.time() - self.Time_last_oper[url] > 20

    def update_entry(self, url, data):
        self.Entry[url].append(data)

    def get_entry(self, url):
        return self.Entry[url]

    def get_users(self, url):
        return self.Users[url]

    def update_users(self, url, data):
        for user in self.Users[url]:
            if user["id"] == data["id"]:
                return
        self.Users[url].append(data)

    def get_draft(self, url):
        return [{"id": key[0], "name":self.Draft[url][key]['name'], "editor":key[1], "text":self.Draft[url][key]['text'], "time":self.Draft[url][key]["time"]} for key in self.Draft[url].keys()]

    def get_draft_by_id(self, url, user_id, formular_id):
        return self.Draft[url][(formular_id, user_id)]
    
    def update_draft(self, url, user_id,formular_id, data):
        self.Draft[url][(formular_id, user_id)] = data
    
    def delete_draft(self, url, user_id, formular_id):
        self.Draft[url].pop((formular_id, user_id), None)

    def get_namef(self, url):
        return self.Namef[url]

    def update_namef(self, url, data):
        for formular in self.Namef[url]:
            if formular["id"] == data["id"]:
                formular["name"] = data["name"]
                return
        self.Namef[url].append(data)

    def delete_namef(self, url, formular_id):
        for formular in self.Namef[url]:
            if formular["id"] == formular_id:
                self.Namef[url].remove(formular)
                return
            
    def set_namef_submitted(self, url, formular_id):
        for formular in self.Namef[url]:
            if formular["id"] == formular_id:
                formular["status"] = 1
                return
    
    def check_namef_submitted(self, url, formular_id):
        for formular in self.Namef[url]:
            if formular["id"] == formular_id:
                return formular["status"] == 1
        return False
            
    def close_all(self):
        self.save_all()
        self.Entry.clear()
        self.Users.clear()
        self.Draft.clear()
        self.Namef.clear()
        


    # def get_engine(self):
    #     return self.__engine


if __name__ == "__main__":
    mysql = Mysql()
    # engine = mysql.get_engine()
    mysql.new_table()
    print(mysql.create_board("test", "admin"))
    print(mysql.create_board("test2", "admin"))
    mysql.open_board("0test")
    mysql.update_entry("0test", {"id": 0, "text":"E=mc^2", "editor": "admin", "time": 0})
    print(mysql.get_users("0test"))
    mysql.update_users("0test", {"id": 0, "name": "admin"})
    print(mysql.get_draft("0test"))
    mysql.update_draft("0test", 0, 0, {"text": "test", "time": 0})
    mysql.update_draft("0test", 0, 1, {"text": "test1", "time": 1})
    mysql.update_draft("0test", 1, 0, {"text": "test2", "time": 2})
    mysql.update_draft("0test", 0, 0, {"text": "test3", "time": 3})
    print(mysql.get_namef("0test"))
    mysql.update_namef("0test", {"id": 0, "name": "formular0"})
    mysql.close_board("0test")
    # x= {(0, 0):{"text": "test", "time": 0}, (0, 1):{"text": "test1", "time": 1}, (1, 0):{"text": "test2", "time": 2}, (1, 1):{"text": "test3", "time": 3}}
    # print([{"id": key[0], "editor":key[1], "text":x[key]['text'], "time":x[key]["time"]} for key in x.keys()])
