class Estudiante:
    def __init__(self, id_estudiante: str, nombre: str, correo: str):
        self.id_estudiante = id_estudiante
        self.nombre = nombre
        self.correo = correo

class Curso:
    def __init__(self, id_curso: str, nombre_curso: str, cupos: int):
        self.id_curso = id_curso
        self.nombre_curso = nombre_curso
        self.cupos = cupos

class Inscripcion:
    def __init__(self, id_inscripcion: str, id_estudiante: str, id_curso: str):
        self.id_inscripcion = id_inscripcion
        self.id_estudiante = id_estudiante
        self.id_curso = id_curso