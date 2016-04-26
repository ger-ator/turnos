from PyQt5 import QtSql, QtCore

from enum import Enum

from personal import calendario
from personal import personal

class Trabajadores(object):
    _dbase = None
    _ids = []
    def __init__(self, dbase=None):
        self.dbase = dbase
        if not Trabajadores._ids:
            query = QtSql.QSqlQuery()
            query.exec_("SELECT personal_id FROM personal")
            while query.next():
                Trabajadores._ids.append(query.value(0))
        self.ids = Trabajadores._ids

    def iterable(self):
        return [Trabajador(self.dbase, index) for index in self.ids]

class Trabajador(object):
    __BASE_PERSONAL = {"trabajador_id":0,
                       "siglas":1,
                       "nombre":2,
                       "apellido1":3,
                       "apellido2":4,
                       "puesto":5,
                       "unidad":6,
                       "grupo":7}
    _cache = {}
    
    def __init__(self, dbase, personal_id):
        self.dbase = dbase
        self.personal_id = str(personal_id)
        ##Añadir trabajador a cache
        if not self.personal_id in Trabajador._cache:
            query = QtSql.QSqlQuery()
            query.prepare("SELECT * FROM personal "
                          "WHERE personal_id = ?")
            query.addBindValue(personal_id)
            if not query.exec_():
                print(query.lastError().text())
                raise ValueError
            query.first()
            if query.isValid():
                Trabajador._cache[self.personal_id] = {}
                for key, value in Trabajador.__BASE_PERSONAL.items():
                    Trabajador._cache[self.personal_id][key] = query.value(value)
        ####
        ##Tomar datos del trabajador
        self.datos = Trabajador._cache[self.personal_id]
        ####

    def getColumn(self, column):
        try:
            return self.datos[column]
        except KeyError:
            print("Trabajador.getColumn: No se ha encontrado {0} "
                  "para {1}".format(column, self.personal_id))
            return None

    def rowid(self):
        return self.getColumn("trabajador_id")

    def siglas(self):
        return self.getColumn("siglas")

    def nombre(self):
        return self.getColumn("nombre")

    def apellido1(self):
        return self.getColumn("apellido1")
    
    def apellido2(self):
        return self.getColumn("apellido2")

    def puesto(self):
        return personal.Puesto(self.getColumn("puesto"))

    def unidad(self):
        return personal.Unidad(self.getColumn("unidad"))

    def grupo(self):
        return personal.Grupo(self.getColumn("grupo")) 
