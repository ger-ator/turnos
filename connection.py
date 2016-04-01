from PyQt5 import QtSql
from enum import Enum

class Turno(Enum):
    manana = "Mañana"
    tarde = "Tarde"
    noche = "Noche"
    reten = "Retén"
    oficina = "Oficina"
    descanso = "Descanso"
    vacaciones = "Vacaciones"
    simulador = "Simulador"
    sin_asignar = ""

    def __sub__(self, turno):
        if self is Turno.manana and turno is Turno.noche:
            return 0
        elif self is Turno.tarde and turno is Turno.manana:
            return 0
        elif self is Turno.noche and turno is Turno.tarde:
            return 0
        else:
            return 8            

class Puesto(Enum):
    JTurno = "Jefe de Turno"
    Supervisor = "Supervisor"
    OpReactor =  "Operador de Reactor"
    OpTurbina = "Operador de Turbina"
    OpPolivalente = "Operador Polivalente"
    Capataz = "Capataz"
    AuxTurbina = "Auxiliar de Turbinas"
    AuxAuxiliar = "Auxiliar de Auxiliar"
    AuxSalvaguardias = "Auxiliar de Salvaguardias"
    AuxExteriores = "Auxiliar de Exteriores"
    AuxTratamiento = "Auxiliar de Tratamiento"

class Unidad(Enum):
    U1 = "1"
    U2 = "2"
    UX = "X"

class Equipo(Enum):
    equipo_1 = 1
    equipo_2 = 2
    equipo_3 = 3
    equipo_4 = 4
    equipo_5 = 5
    equipo_6 = 6
    equipo_7 = 7
    equipo_8 = 8
    
if __name__ == '__main__':
    asdf = Turno("Mañana")
    print(asdf.name)

def createConnection():
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('operacion.db')
    if not db.open():
        QtGui.QMessageBox.critical(None, QtGui.qApp.tr("No se pudo abrir la base de datos."),
                QtGui.qApp.tr("Imposible establecer conexion.\n"
                              "Pulsa Cancelar para salir."),
                QtGui.QMessageBox.Cancel)
        return False
        
    if 'personal' not in db.tables():
        query = QtSql.QSqlQuery()
        query.exec_("create table personal ("
                    "personal_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                    "siglas TEXT UNIQUE, "
                    "nombre TEXT, "                    
                    "apellido1 TEXT, "
                    "apellido2 TEXT, "
                    "puesto TEXT, "
                    "unidad TEXT, "
                    "equipo INTEGER)")

    if 'calendario' not in db.tables():
        query = QtSql.QSqlQuery()
        query.exec_("CREATE TABLE calendario ( "
                    "calendario_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                    "fecha DATE UNIQUE NOT NULL, "
                    "manana TEXT NOT NULL, "
                    "tarde TEXT NOT NULL, "
                    "noche TEXT NOT NULL, "
                    "reten TEXT NOT NULL, "
                    "oficina TEXT, "
                    "simulador TEXT, "
                    "descanso TEXT, "
                    "vacaciones TEXT, "
                    "equipo_1 TEXT, "
                    "equipo_2 TEXT, "
                    "equipo_3 TEXT, "
                    "equipo_4 TEXT, "
                    "equipo_5 TEXT, "
                    "equipo_6 TEXT, "
                    "equipo_7 TEXT, "
                    "equipo_8 TEXT) ")

    if 'bajas' not in db.tables():
        query = QtSql.QSqlQuery()
        query.exec_("""PRAGMA foreign_keys = ON""")
        query.clear()
        query.exec_("create table bajas ("
                    "baja_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                    "sustituido_id INTEGER, "
                    "inicio DATE, "
                    "final DATE, "
                    "motivo TEXT, "
                    "FOREIGN KEY(sustituido_id) REFERENCES personal(personal_id))")
        
    if 'sustituciones' not in db.tables():
        query = QtSql.QSqlQuery()
        query.exec_("""PRAGMA foreign_keys = ON""")
        query.clear()
        query.exec_("create table sustituciones ("
                    "sustitucion_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                    "sustituido_id INTEGER, "
                    "sustituto_id INTEGER, "
                    "fecha DATE, "
                    "turno TEXT, "
                    "baja_id INTEGER, "
                    "FOREIGN KEY(sustituido_id) REFERENCES personal(personal_id), "
                    "FOREIGN KEY(sustituto_id) REFERENCES personal(personal_id), "
                    "FOREIGN KEY(baja_id) REFERENCES bajas(baja_id))")

    if 'candidatos' not in db.tables():
        query = QtSql.QSqlQuery()
        query.exec_("""PRAGMA foreign_keys = ON""")
        query.clear()
        query.exec_("CREATE TABLE candidatos ("
                    "candidatos_id INTEGER PRIMARY KEY AUTOINCREMENT, "
                    "sustituto_id INTEGER, "
                    "turno TEXT, "
                    "FOREIGN KEY(sustituto_id) REFERENCES personal(personal_id))")        
    return True
