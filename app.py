# from os import abort
import sys
from flask import Flask, jsonify, redirect, render_template, request, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:!pass4sure@localhost:5432/todo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

migrate = Migrate(app, db)


class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    list_id = db.Column(db.Integer, db.ForeignKey(
        'todolists.id'), nullable=False)

    def __repr__(self):
        return f'<Todo {self.id} name: {self.description} completed: {self.completed}>'


class TodoList(db.Model):
    __tablename__ = 'todolists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    todos = db.relationship('Todo', backref='list', lazy=True)

    def __repr__(self):
      return f'<TodoList {self.id} {self.name} {self.todos} {self.completed}>'

# db.create_all()


# @app.route('/')
# def hello_world():
#     return 'Hello Everyone!'

@app.route('/todos/create', methods=['POST'])
def create_todo():
    body = {}
    error = False
    try:
        description = request.get_json()['description']
        list_id = request.get_json()['list_id']
        todo = Todo(description=description, completed=False, list_id=list_id)
        # body['description'] = todo.description
        active_list = TodoList.query.get(list_id)
        todo.list = active_list
        db.session.add(todo)
        db.session.commit()
        # body['id'] = todo.id
        # body['completed'] = todo.completed
        body['description'] = todo.description
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error == True:
        abort(400)
    else:
        return jsonify(body)


@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_completed_todo(todo_id):
    try:
        completed = request.get_json()['completed']
        print('completed', completed)
        todo = Todo.query.get(todo_id)
        todo.completed = completed
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        return redirect(url_for('index'))


@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    try:
        todo = Todo.query.get(todo_id)
        db.session.delete(todo)
        # Todo.query.filter_by(id=todo_id).delete()
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    return jsonify({'success': True})


@app.route('/lists/create', methods=['POST'])
def create_todo_list():
    body = {}
    error = False
    try:
        name = request.get_json()['name']
        todoList = TodoList(name=name, completed=False)
        db.session.add(todoList)
        db.session.commit()
        body['name'] = todoList.name
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error == True:
        abort(400)
    else:
        return jsonify(body)


@app.route('/lists/<list_id>')
def get_list_todos(list_id):
  return render_template('index.html',
  lists=TodoList.query.all(),
  active_list=TodoList.query.get(list_id),
  data=Todo.query.filter_by(list_id=list_id).order_by('id').all()
)


@app.route('/lists/<list_id>/set-completed', methods=['POST'])
def set_completed_list(list_id):
    error = False
    try:
        completed = request.get_json()['completed']
        print('completed', completed)
        list = TodoList.query.get(list_id)
        list.completed = completed
        for todo in list.todos:
            todo.completed = True
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return '', 200


@app.route('/')
def index():
  return redirect(url_for('get_list_todos', list_id=1))


# always include this at the bottom of your code
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)
