from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

#Configuramos la conexion a la db con SQLALCHEMY
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:azul_1234@localhost/flaskmysql'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

#Definimos las variables de la db y marshmallow
db = SQLAlchemy(app)
#Incluimos Marshmellow para la Serializacion (Codificar a formato JSON)
ma = Marshmallow(app)

#Creamos la clase modelo de la db (Esto crea las columnas en nuestra base de datos)
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(70), unique=True)
    description = db.Column(db.String(100))

    def __init__(self, title, description):
        self.title = title
        self.description = description

db.create_all()

class TaskSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'description')

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)

#Ruta para crear una nueva task
@app.route('/tasks', methods=['POST'])
def create_task():
    #Ponemos en variables los valores que nos pasaron con los request
    title = request.json['title']
    description = request.json['description']

    #Instanciamos una tarea con los valores previamente guardados en variables
    new_task = Task(title, description)

    #Añadimos la tarea a la db
    db.session.add(new_task)
    #Guardamos la db
    db.session.commit()

    #Devolvemos la nueva tarea en forma de JSON
    return task_schema.jsonify(new_task)

#Ruta para ver todas las tareas
@app.route('/tasks', methods=['GET'])
def get_tasks():
    #Pedimos a la db una query que pase todas las tareas
    all_tasks = Task.query.all()
    #Serializamos y guardamos todas las tareas en una variable llamada result
    result= tasks_schema.dump(all_tasks)

    #Devolvemos un json con el resultado.
    return jsonify(result)

#Ruta para conseguir una sola tarea
@app.route('/tasks/<id>', methods=['GET'])
#Como la ruta pide un id, se lo agregamos como parametro a la funcion
def get_task(id):
    #Pedimos a la db un query basado en su id y lo almacenamos en una variable
    task = Task.query.get(id)
    #Serializamos y devolvemos la variable task en forma de JSON
    return task_schema.jsonify(task)

#Ruta para modificar una tarea
@app.route('/tasks/<id>', methods=['PUT'])
def update_task(id):
    #Hacemos un query a la db basado en la id y almacenamos el valor devuelto
    task = Task.query.get(id)

    #Aca almacenamos los valores de los request en variables
    title = request.json['title']
    description = request.json['description']

    #Ya que task es una instancia del query, cambiamos sus valores
    task.title= title
    task.description = description

    #Hacemos un commit de la db
    db.session.commit()
    #Devolvemos con una serializacion en forma de JSON el task despues de ser modificado.
    return task_schema.jsonify(task)


#Ruta para eliminar una tarea
@app.route('/tasks/<id>', methods=['DELETE'])
def delete_task(id):
    #Hacemos un query a la db basado en la id y almacenamos su valor
    task = Task.query.get(id)
    #Desde la db, usamos la funcion delete pasandole como parametro la variable task
    db.session.delete(task)
    #Hacemos commit de la db
    db.session.commit()

    #Devolvemos con una serializacion en forma de json el task que eliminamos.
    return task_schema.jsonify(task)


if __name__ == '__main__':
    app.run(debug=True)