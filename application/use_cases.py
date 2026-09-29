from domain.entities import Estudiante, Curso, Inscripcion

class RegistrarEstudianteUseCase:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def ejecutar(self, id_estudiante: str, nombre: str, correo: str):
        if self.repositorio.obtener_estudiante(id_estudiante):
            raise ValueError("El estudiante con este ID ya está registrado.")
        
        estudiante = Estudiante(id_estudiante, nombre, correo)
        self.repositorio.guardar_estudiante(estudiante)
        return estudiante

class CrearCursoUseCase:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def ejecutar(self, id_curso: str, nombre_curso: str, cupos: int):
        if self.repositorio.obtener_curso(id_curso):
            raise ValueError("El curso con este ID ya existe.")
        
        curso = Curso(id_curso, nombre_curso, cupos)
        self.repositorio.guardar_curso(curso)
        return curso

class InscribirEstudianteUseCase:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def ejecutar(self, id_inscripcion: str, id_estudiante: str, id_curso: str):
        # Validar que existan el estudiante y el curso
        estudiante = self.repositorio.obtener_estudiante(id_estudiante)
        if not estudiante:
            raise ValueError("El estudiante no se encuentra registrado.")
            
        curso = self.repositorio.obtener_curso(id_curso)
        if not curso:
            raise ValueError("El curso no existe.")

        # Validar si ya está inscrito
        inscripciones_existentes = self.repositorio.obtener_inscripciones_por_estudiante(id_estudiante)
        for ins in inscripciones_existentes:
            if ins.id_curso == id_curso:
                raise ValueError("El estudiante ya está inscrito en este curso.")

        inscripcion = Inscripcion(id_inscripcion, id_estudiante, id_curso)
        self.repositorio.guardar_inscripcion(inscripcion)
        return inscripcion

class ConsultarCursosInscritosUseCase:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def ejecutar(self, id_estudiante: str):
        estudiante = self.repositorio.obtener_estudiante(id_estudiante)
        if not estudiante:
            raise ValueError("El estudiante no existe.")

        inscripciones = self.repositorio.obtener_inscripciones_por_estudiante(id_estudiante)
        cursos_inscritos = []
        for ins in inscripciones:
            curso = self.repositorio.obtener_curso(ins.id_curso)
            if curso:
                cursos_inscritos.append(curso)
        return cursos_inscritos