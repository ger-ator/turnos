from PyQt5 import QtSql, QtCore

from personal import personal

class Calendario(object):
    
    _cache = {}
    
    def __init__(self):
        if not Calendario._cache:
            for grupo in personal.Grupo:
                self.populate(grupo)
        self.cal = Calendario._cache

    def populate(self, grupo):
        Calendario._cache[grupo] = {}
        query = QtSql.QSqlQuery()
        query.prepare("SELECT fecha, jornada FROM calendario "
                      "WHERE grupo=?")
        query.addBindValue(grupo.value)
        if not query.exec_():
            print("Error al construir calendario.")
            print(query.lastError().text())
        while query.next():
            try:
                fecha = QtCore.QDate.fromString(query.value(0), QtCore.Qt.ISODate)
                Calendario._cache[grupo][fecha] = personal.Jornada(query.value(1))
            except ValueError:
                Calendario._cache[grupo][fecha] = None
            except KeyError:
                print("Error al cargar calendario.")
                    
    def getCalendario(self, grupo):
        try:
            return self.cal[grupo]
        except KeyError:
            return None
        
    def getJornada(self, trabajador, fecha):
        try:
            return self.cal[trabajador.grupo()][fecha]
        except KeyError:
            return None
