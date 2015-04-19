import os
from datetime import datetime
from flask import *
from peewee import *

app = Flask("journal")
db = SqliteDatabase(os.path.join(os.getcwd(), "journal.db"))

class Entry(Model):
    """
    The object representation of a journal entry
    """
    created = DateTimeField()
    text = TextField()

    class Meta: 
        database = db
        db_table = 'entries'
        order_by = ('-created',)

class Migration(Model):
    index = IntegerField(unique=True)
    
    class Meta:
        database = db
        db_table = 'migrations'

def migrate(db):
    Migration.create_table(fail_silently=True)
    
    directory = os.path.join(os.getcwd(), 'migrations')
    migrations = os.listdir(directory)
    migrations = map(lambda entry: os.path.join(directory, entry), migrations)
    migrations = filter(os.path.isdir, migrations)
    for migration in migrations:
        index = os.path.basename(migration)
        try:
            Migration.get(Migration.index == int(index))
        except Migration.DoesNotExist:
            module = {}
            path = os.path.join(migration, 'up.sql')
            db.execute_sql(open(path).read())
            Migration.create(index = int(index))

@app.template_filter('strftime')
def strftime(date):
    return date.strftime('%b %d, %Y')

@app.route("/", methods=["GET"])
def index():
    query = Entry.select(Entry.id, Entry.created)
    entries = list(query)
    return render_template("index.html", entries=entries)

@app.route("/new", methods=["GET"])
def new():
    return render_template("new.html")

@app.route("/", methods=["POST"])
def create():
    
    entry = Entry.create(
            text = request.form['text'], 
            created=datetime.now()
    )
    
    return redirect(url_for('show', id=entry.id))

@app.route('/<int:id>')
def show(id):
    entry = Entry.get(id=id)
    return render_template("show.html", entry=entry)

if __name__ == "__main__":
    db.connect()
    migrate(db)
    app.debug = True
    app.run()
