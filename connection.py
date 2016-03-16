from PyQt5 import QtSql

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
                    "Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                    "Siglas TEXT UNIQUE, "
                    "Nombre TEXT, "                    
                    "Apellido1 TEXT, "
                    "Apellido2 TEXT, "
                    "Puesto TEXT, "
                    "Unidad TEXT, "
                    "Equipo INTEGER)")

    if 'calendario' not in db.tables():
        query = QtSql.QSqlQuery()
        query.exec_("create table calendario ("
                    "Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                    "Fecha DATE UNIQUE, "
                    "E1 TEXT, "                    
                    "E2 TEXT, "
                    "E3 TEXT, "
                    "E4 TEXT, "
                    "E5 TEXT, "
                    "E6 TEXT, "
                    "E7 TEXT, "
                    "E8 TEXT)")

    if 'bajas' not in db.tables():
        query = QtSql.QSqlQuery()
        query.exec_("""PRAGMA foreign_keys = ON""")
        query.clear()
        query.exec_("create table bajas ("
                    "Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                    "trabajadorid INTEGER, "
                    "Inicio DATE, "
                    "Final DATE, "
                    "FOREIGN KEY(trabajadorid) REFERENCES personal(Id))")
        
    if 'necesidades' not in db.tables():
        query = QtSql.QSqlQuery()
        query.exec_("""PRAGMA foreign_keys = ON""")
        query.clear()
        query.exec_("create table necesidades ("
                    "Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "
                    "trabajadorid INTEGER, "                    
                    "Fecha DATE, "
                    "Turno TEXT, "
                    "Motivo TEXT, "
                    "Asignado INTEGER, "
                    "bajaid INTEGER, "
                    "FOREIGN KEY(trabajadorid) REFERENCES personal(Id), "
                    "FOREIGN KEY(bajaid) REFERENCES bajas(Id))")
        
    return True

def insertBaja(trabajadorid, inicio, final):
    ##Creo registro de baja
    query = QtSql.QSqlQuery()
    query.prepare("INSERT INTO bajas (trabajadorid, Inicio, Final) "
                  "VALUES (?, ?, ?)")
    query.addBindValue(trabajadorid)
    query.addBindValue(inicio)
    query.addBindValue(final)
    query.exec_()

    ##Obtengo datos del equipo    
    bajaid = query.lastInsertId()    
    query.prepare("SELECT Equipo FROM personal WHERE Id = ?")
    query.addBindValue(trabajadorid)
    query.exec_()
    query.first()
    
    equipo = query.value(0)
    
    query.prepare("SELECT Fecha, E{0} FROM calendario "
                  "WHERE (Fecha BETWEEN date(?) AND date(?)) AND "
                  "(E{0} = 'Mañana' OR E{0} = 'Tarde' "
                  "OR E{0} = 'Noche' OR E{0} = 'Retén') "
                  "ORDER BY Fecha ASC".format(equipo))
    query.addBindValue(inicio)
    query.addBindValue(final)
    query.exec_()

    ##Inserto las necesidades de personal generadas por la baja
    while query.next():
        subquery = QtSql.QSqlQuery()
        subquery.prepare("INSERT INTO necesidades (trabajadorid, Fecha, Turno, Motivo, bajaid) "
                         "VALUES (?, ?, ?, ?, ?)")
        subquery.addBindValue(trabajadorid)
        subquery.addBindValue(query.value(0)) ##FECHA
        subquery.addBindValue(query.value(1)) ##TURNO
        subquery.addBindValue("B")
        subquery.addBindValue(bajaid)
        subquery.exec_()
