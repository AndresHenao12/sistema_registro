from flask import Flask, render_template, request, redirect, url_for, session, flash
from infrastructure.database import DatabaseConnection, SQLiteRepository
from application.use_cases import (
    RegistrarEstudianteUseCase,
    CrearCursoUseCase,
    InscribirEstudianteUseCase
)

app = Flask(__name__)
app.secret_key = 'clave_secreta_uniremington_segura' # Necesario para las sesiones de usuario

db_conn = DatabaseConnection("colegio.db")
repo = SQLiteRepository(db_conn)

registrar_est_uc = RegistrarEstudianteUseCase(repo)
crear_curso_uc = CrearCursoUseCase(repo)
inscribir_uc = InscribirEstudianteUseCase(repo)

# --- RUTAS DE AUTENTICACIÓN ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        password = request.form['password']
        usuario = repo.validar_usuario(correo, password)
        if usuario:
            session['user_id'] = usuario[0]
            session['user_name'] = usuario[1]
            return redirect(url_for('index'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']
        exito = repo.registrar_usuario(nombre, correo, password)
        if exito:
            flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        else:
            flash('El correo ya está registrado.', 'danger')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- RUTAS PRINCIPALES (Protegidas) ---
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/estudiantes')
def estudiantes():
    if 'user_id' not in session: return redirect(url_for('login'))
    with db_conn._conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM estudiantes")
        lista = cursor.fetchall()
    return render_template('estudiantes.html', estudiantes=lista)

@app.route('/registrar_estudiante', methods=['POST'])
def registrar_estudiante():
    if 'user_id' not in session: return redirect(url_for('login'))
    try:
        registrar_est_uc.ejecutar(request.form['id'], request.form['nombre'], request.form['correo'])
    except Exception as e:
        print(f"Error: {e}")
    return redirect(url_for('estudiantes'))

@app.route('/eliminar_estudiante/<id>')
def eliminar_estudiante(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    repo.eliminar_estudiante(id)
    return redirect(url_for('estudiantes'))

@app.route('/cursos')
def cursos():
    if 'user_id' not in session: return redirect(url_for('login'))
    with db_conn._conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cursos")
        lista = cursor.fetchall()
    return render_template('cursos.html', cursos=lista)

@app.route('/crear_curso', methods=['POST'])
def crear_curso():
    if 'user_id' not in session: return redirect(url_for('login'))
    try:
        crear_curso_uc.ejecutar(request.form['id_curso'], request.form['nombre_curso'], int(request.form['cupos']))
    except Exception as e:
        print(f"Error: {e}")
    return redirect(url_for('cursos'))

@app.route('/eliminar_curso/<id>')
def eliminar_curso(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    repo.eliminar_curso(id)
    return redirect(url_for('cursos'))

@app.route('/inscripciones')
def inscripciones():
    if 'user_id' not in session: return redirect(url_for('login'))
    with db_conn._conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM estudiantes")
        estudiantes = cursor.fetchall()
        cursor.execute("SELECT * FROM cursos")
        cursos = cursor.fetchall()
        cursor.execute("""
            SELECT i.id, e.nombre, c.nombre 
            FROM inscripciones i
            JOIN estudiantes e ON i.id_estudiante = e.id
            JOIN cursos c ON i.id_curso = c.id
        """)
        lista = cursor.fetchall()
    return render_template('inscripciones.html', estudiantes=estudiantes, cursos=cursos, inscripciones=lista)

@app.route('/inscribir', methods=['POST'])
def inscribir():
    if 'user_id' not in session: return redirect(url_for('login'))
    try:
        inscribir_uc.ejecutar(request.form['id_inscripcion'], request.form['id_estudiante'], request.form['id_curso'])
    except Exception as e:
        print(f"Error: {e}")
    return redirect(url_for('inscripciones'))

@app.route('/eliminar_inscripcion/<id>')
def eliminar_inscripcion(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    repo.eliminar_inscripcion(id)
    return redirect(url_for('inscripciones'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)