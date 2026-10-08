from flask import Flask, render_template, request, redirect, url_for, session, flash
from infrastructure.database import DatabaseConnection, SQLiteRepository
from application.use_cases import (
    BuscarEstudiantesUseCase,
    RegistrarEstudianteUseCase,
    CrearCursoUseCase,
    InscribirEstudianteUseCase
)

app = Flask(__name__)
app.secret_key = 'clave_secreta_uniremington_segura'

db_conn = DatabaseConnection("colegio.db")
repo = SQLiteRepository(db_conn)

buscar_estudiantes_uc = BuscarEstudiantesUseCase(repo)
registrar_est_uc = RegistrarEstudianteUseCase(repo)
crear_curso_uc = CrearCursoUseCase(repo)
inscribir_uc = InscribirEstudianteUseCase(repo)


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


@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/estudiantes')
def estudiantes():
    if 'user_id' not in session: return redirect(url_for('login'))
    busqueda = request.args.get('q', '').strip()
    lista = buscar_estudiantes_uc.ejecutar(busqueda)
    return render_template('estudiantes.html', estudiantes=lista, busqueda=busqueda)

@app.route('/registrar_estudiante', methods=['POST'])
def registrar_estudiante():
    if 'user_id' not in session: return redirect(url_for('login'))
    try:
        registrar_est_uc.ejecutar(request.form['id'], request.form['nombre'], request.form['correo'])
        flash('Estudiante registrado correctamente.', 'success')
    except Exception as e:
        print(f"Error: {e}")
        flash(f'Error al registrar estudiante: {e}', 'danger')
    return redirect(url_for('estudiantes'))

@app.route('/eliminar_estudiante/<id>')
def eliminar_estudiante(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    repo.eliminar_estudiante(id)
    flash('Estudiante eliminado.', 'info')
    return redirect(url_for('estudiantes'))

@app.route('/editar_estudiante/<id>', methods=['GET', 'POST'])
def editar_estudiante(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    estudiante = repo.obtener_estudiante(id)
    if not estudiante:
        flash('No se encontró el estudiante.', 'danger')
        return redirect(url_for('estudiantes'))
    if request.method == 'POST':
        repo.actualizar_estudiante(id, request.form['nombre'], request.form['correo'])
        flash('Estudiante actualizado correctamente.', 'success')
        return redirect(url_for('estudiantes'))
    return render_template('editar.html', tipo='estudiante', registro=estudiante)

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
        flash('Curso creado correctamente.', 'success')
    except Exception as e:
        print(f"Error: {e}")
        flash(f'Error al crear curso: {e}', 'danger')
    return redirect(url_for('cursos'))

@app.route('/eliminar_curso/<id>')
def eliminar_curso(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    repo.eliminar_curso(id)
    flash('Curso eliminado.', 'info')
    return redirect(url_for('cursos'))

@app.route('/editar_curso/<id>', methods=['GET', 'POST'])
def editar_curso(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    curso = repo.obtener_curso(id)
    if not curso:
        flash('No se encontró el curso.', 'danger')
        return redirect(url_for('cursos'))
    if request.method == 'POST':
        try:
            cupos = int(request.form['cupos'])
            if cupos < 0:
                raise ValueError
        except ValueError:
            flash('Los cupos deben ser un número igual o mayor que cero.', 'danger')
            return render_template('editar.html', tipo='curso', registro=curso)
        repo.actualizar_curso(id, request.form['nombre_curso'], cupos)
        flash('Curso actualizado correctamente.', 'success')
        return redirect(url_for('cursos'))
    return render_template('editar.html', tipo='curso', registro=curso)

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
        flash('Inscripción realizada correctamente.', 'success')
    except Exception as e:
        print(f"Error: {e}")
        flash(f'Error al inscribir: {e}', 'danger')
    return redirect(url_for('inscripciones'))

@app.route('/eliminar_inscripcion/<id>')
def eliminar_inscripcion(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    repo.eliminar_inscripcion(id)
    flash('Inscripción eliminada.', 'info')
    return redirect(url_for('inscripciones'))

@app.route('/editar_inscripcion/<id>', methods=['GET', 'POST'])
def editar_inscripcion(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    inscripcion = repo.obtener_inscripcion(id)
    if not inscripcion:
        flash('No se encontró la inscripción.', 'danger')
        return redirect(url_for('inscripciones'))
    with db_conn._conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM estudiantes")
        estudiantes = cursor.fetchall()
        cursor.execute("SELECT id, nombre FROM cursos")
        cursos = cursor.fetchall()
    if request.method == 'POST':
        id_estudiante = request.form['id_estudiante']
        id_curso = request.form['id_curso']
        if not repo.obtener_estudiante(id_estudiante) or not repo.obtener_curso(id_curso):
            flash('Selecciona un estudiante y un curso válidos.', 'danger')
            return render_template('editar.html', tipo='inscripcion', registro=inscripcion,
                                   estudiantes=estudiantes, cursos=cursos)
        duplicada = any(
            existente.id_inscripcion != id and existente.id_curso == id_curso
            for existente in repo.obtener_inscripciones_por_estudiante(id_estudiante)
        )
        if duplicada:
            flash('El estudiante ya está inscrito en este curso.', 'danger')
            return render_template('editar.html', tipo='inscripcion', registro=inscripcion,
                                   estudiantes=estudiantes, cursos=cursos)
        repo.actualizar_inscripcion(id, id_estudiante, id_curso)
        flash('Inscripción actualizada correctamente.', 'success')
        return redirect(url_for('inscripciones'))
    return render_template('editar.html', tipo='inscripcion', registro=inscripcion,
                           estudiantes=estudiantes, cursos=cursos)

@app.route('/redes')
def redes():
    if 'user_id' not in session: return redirect(url_for('login'))
    return render_template('redes.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)