import sqlite3
import hashlib
from domain.entities import Estudiante, Curso, Inscripcion

class DatabaseConnection:
    def __init__(self, db_name="colegio.db"):
        self.db_name = db_name
        self._crear_tablas()

    def _conectar(self):
        return sqlite3.connect(self.db_name)

    def _crear_tablas(self):
        with self._conectar() as conn:
            cursor = conn.cursor()
            # Tabla de Usuarios (Autenticación)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT,
                    correo TEXT UNIQUE,
                    password TEXT
                )
            """)
            # Tabla Estudiantes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS estudiantes (
                    id TEXT PRIMARY KEY,
                    nombre TEXT,
                    correo TEXT
                )
            """)
            # Tabla Cursos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cursos (
                    id TEXT PRIMARY KEY,
                    nombre TEXT,
                    cupos INTEGER
                )
            """)
            # Tabla Inscripciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inscripciones (
                    id TEXT PRIMARY KEY,
                    id_estudiante TEXT,
                    id_curso TEXT,
                    FOREIGN KEY(id_estudiante) REFERENCES estudiantes(id),
                    FOREIGN KEY(id_curso) REFERENCES cursos(id)
                )
            """)
            conn.commit()

class SQLiteRepository:
    def __init__(self, db_conn: DatabaseConnection):
        self.db_conn = db_conn

    # --- USUARIOS / AUTENTICACIÓN ---
    def registrar_usuario(self, nombre: str, correo: str, password_plana: str):
        # Encriptar contraseña por seguridad básica
        password_hash = hashlib.sha256(password_plana.encode()).hexdigest()
        with self.db_conn._conectar() as conn:
            try:
                conn.execute("INSERT INTO usuarios (nombre, correo, password) VALUES (?, ?, ?)",
                             (nombre, correo, password_hash))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False # El correo ya está registrado

    def validar_usuario(self, correo: str, password_plana: str):
        password_hash = hashlib.sha256(password_plana.encode()).hexdigest()
        with self.db_conn._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM usuarios WHERE correo = ? AND password = ?", (correo, password_hash))
            return cursor.fetchone()

    # --- ESTUDIANTES ---
    def obtener_estudiante(self, id_estudiante: str):
        with self.db_conn._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, correo FROM estudiantes WHERE id = ?", (id_estudiante,))
            fila = cursor.fetchone()
        if fila is None:
            return None
        return Estudiante(*fila)

    def guardar_estudiante(self, estudiante: Estudiante):
        with self.db_conn._conectar() as conn:
            conn.execute("INSERT OR REPLACE INTO estudiantes (id, nombre, correo) VALUES (?, ?, ?)",
                         (estudiante.id_estudiante, estudiante.nombre, estudiante.correo))
            conn.commit()

    def eliminar_estudiante(self, id_estudiante: str):
        with self.db_conn._conectar() as conn:
            conn.execute("DELETE FROM estudiantes WHERE id = ?", (id_estudiante,))
            conn.commit()

    # --- CURSOS ---
    def obtener_curso(self, id_curso: str):
        with self.db_conn._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, cupos FROM cursos WHERE id = ?", (id_curso,))
            fila = cursor.fetchone()
        if fila is None:
            return None
        return Curso(*fila)

    def guardar_curso(self, curso: Curso):
        with self.db_conn._conectar() as conn:
            conn.execute("INSERT OR REPLACE INTO cursos (id, nombre, cupos) VALUES (?, ?, ?)",
                         (curso.id_curso, curso.nombre_curso, curso.cupos))
            conn.commit()

    def eliminar_curso(self, id_curso: str):
        with self.db_conn._conectar() as conn:
            conn.execute("DELETE FROM cursos WHERE id = ?", (id_curso,))
            conn.commit()

    # --- INSCRIPCIONES ---
    def obtener_inscripciones_por_estudiante(self, id_estudiante: str):
        with self.db_conn._conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, id_estudiante, id_curso FROM inscripciones WHERE id_estudiante = ?",
                (id_estudiante,),
            )
            filas = cursor.fetchall()
        return [Inscripcion(*fila) for fila in filas]

    def guardar_inscripcion(self, inscripcion: Inscripcion):
        with self.db_conn._conectar() as conn:
            conn.execute("INSERT OR IGNORE INTO inscripciones (id, id_estudiante, id_curso) VALUES (?, ?, ?)",
                         (inscripcion.id_inscripcion, inscripcion.id_estudiante, inscripcion.id_curso))
            conn.commit()

    def eliminar_inscripcion(self, id_inscripcion: str):
        with self.db_conn._conectar() as conn:
            conn.execute("DELETE FROM inscripciones WHERE id = ?", (id_inscripcion,))
            conn.commit()