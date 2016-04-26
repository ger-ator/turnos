from PyQt5 import QtSql

def createConnection():
    db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName('operacion.db')
    if not db.open():
        return False
        
    if 'personal' not in db.tables():
        query = QtSql.QSqlQuery()
        query.exec_("create table personal ("
                    "personal_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                    "siglas TEXT UNIQUE, "
                    "nombre TEXT, "                    
                    "apellido1 TEXT, "
                    "apellido2 TEXT, "
                    "puesto INTEGER, "
                    "unidad INTEGER, "
                    "grupo INTEGER), "
                    "FOREIGN KEY(grupo) REFERENCES grupos(grupo_id), "
                    "FOREIGN KEY(puesto) REFERENCES puestos(puesto_id))")

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

    if 'calendario' not in db.tables():
        query = QtSql.QSqlQuery()
        query.exec_("CREATE TABLE nuevo_calendario ("
                    "calendario_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                    "fecha DATE NOT NULL, "
                    "grupo INTEGER NOT NULL, "
                    "jornada INTEGER NOT NULL, "
                    "FOREIGN KEY(grupo) REFERENCES grupos(grupo_id), "
                    "FOREIGN KEY(jornada) REFERENCES jornadas(jornada_id))")
    return True
