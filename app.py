from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import desc

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(ZoneInfo("America/New_York")))
    color = db.Column(db.String(200), default = "lightblue", nullable=False)
    deadline = db.Column(db.DateTime)
    status = db.Column(db.String(50), nullable=False)


    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content'].strip()
        dt = datetime.fromisoformat(request.form['when'])
        if dt <= datetime.now():
            return "Date must be in the future", 400
        if not task_content:
            return "Task content cannot be empty", 400
        new_task = Todo(content = task_content, deadline = dt, status = "todo")

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue adding your task"
    else:
        tasks = Todo.query.filter_by(status='todo').order_by(desc(Todo.date_created)).all()
        return render_template('index.html', tasks = tasks)

@app.route('/complete/<int:id>', methods = ['POST'])
def complete(id):
    task_to_complete= Todo.query.get_or_404(id)
    task_to_complete.status = 'done'
    task_to_complete.date_created = datetime.now(ZoneInfo("America/New_York"))

    try:
        db.session.commit()
        return redirect('/')
    except:
        "There was a problem completing your task"


@app.route('/delete/<int:id>', methods = ['POST'])
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        "There was a problem deleting your task"

@app.route('/update/<int:id>', methods = ['GET', 'POST'])
def update(id):
    task_to_update = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task_to_update.content = request.form['content']

        try:
            db.session.commit()
            return redirect('/')
        except:
            "There was a problem updating your task"
    else:
        return render_template("update.html", task = task_to_update)

@app.route('/change-color/<int:id>', methods = ['GET', 'POST'])
def change_color(id):
    task_to_update = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task_to_update.color = request.form['color-' + str(id)]

        try:
            db.session.commit()
            return redirect('/')
        except:
            "Please pick a valid color"
    else:
        return render_template("color.html", task = task_to_update)

@app.route('/view-completed')
def completed():
    tasks = Todo.query.filter_by(status='done').order_by(desc(Todo.date_created)).all()
    return render_template('completed.html', tasks = tasks)

def due_soon(dt, days=1):
    now = datetime.now()
    return now < dt <= now + timedelta(days=days)

app.jinja_env.filters['due_soon'] = due_soon

if __name__ == "__main__":
    app.run(debug=True)