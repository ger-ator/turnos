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
                    "equipo_8 TEXT, "
                    "normal TEXT) ")

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
