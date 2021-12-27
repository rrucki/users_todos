from django.http import HttpResponse
from django.template import loader
import urllib.request
import json
import csv
import sqlite3


def user_task(request):
    user_url = "http://jsonplaceholder.typicode.com/users"
    todos_url = "http://jsonplaceholder.typicode.com/todos"

    con = sqlite3.connect("users_todos.db")
    cur = con.cursor()

    cur.execute(""" CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY,
                            name, 
                            city
                        );""")

    cur.execute(""" CREATE TABLE IF NOT EXISTS todos (
                            id,
                            title, 
                            completed
                        );""")

    with urllib.request.urlopen(user_url) as user_url:
        user_data = json.loads(user_url.read().decode())

    with urllib.request.urlopen(todos_url) as todos_url:
        todo_data = json.loads(todos_url.read().decode())

    user_db = [(i['name'], i['address']['city']) for i in user_data]
    todo_db = [(i['userId'], i['title'], i['completed']) for i in todo_data]

    cur.executemany(""" INSERT INTO users (
                                name,
                                city
                            ) VALUES (?, ?)""", user_db)

    cur.executemany(""" INSERT INTO todos (
                                id,
                                title,
                                completed
                            ) VALUES (?, ?, ?)""", todo_db)

    cur.execute(""" CREATE VIEW users_todos AS
                            SELECT
                                users.name,
                                users.city,
                                todos.title,
                                todos.completed
                            FROM
                                users
                                LEFT JOIN
                                    todos
                                USING(id)""")

    cur.execute(" SELECT * FROM users_todos")
    combined_data = cur.fetchall()
    con.commit()
    con.close()

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="todos.csv"'},
    )

    with open('user_database.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['name', 'city', 'title', 'completed'])
        writer.writerows(combined_data)

    with open('user_database.csv', 'r') as file:
        reader = csv.reader(file)
        template = loader.get_template('user_task.txt')
        context = {'data': reader}
        response.write(template.render(context))

    return response

