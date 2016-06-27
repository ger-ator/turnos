from PyQt5 import QtSql, QtCore

from enum import Enum

from personal import calendario
from personal import personal
from personal import trabajador

def transaccion(func):
    def func_wrapper(*args):
        QtSql.QSqlDatabase.database().transaction()
        func(*args)
        QtSql.QSqlDatabase.database().commit()
    return func_wrapper

class Bajas(object):
    _dbase = None
    _ids = []
    def __init__(self, dbase=None):
        self.dbase = dbase
        if not Bajas._ids:
            query = QtSql.QSqlQuery()
            query.exec_("SELECT baja_id FROM bajas")
            while query.next():
                Bajas._ids.append(query.value(0))
        self.ids = Bajas._ids

    def iterable(self, lista=None):
        if lista is None:
            return {Baja(self.dbase, index) for index in self.ids}
        else:
            return {Baja(self.dbase, index)
                    for index in self.ids if index in lista}

    @transaccion
    def add(self, sustituido, inicio, final, motivo=""):
        ##Añadir la baja
        query = QtSql.QSqlQuery()
        query.prepare("INSERT INTO bajas "
                      "(sustituido_id, inicio, final, motivo) "
                      "VALUES (?, ?, ?, ?)")
        query.addBindValue(sustituido.rowid())
        query.addBindValue(inicio)
        query.addBindValue(final)
        query.addBindValue(motivo)
        if not query.exec_():
            return False
        baja_insertada = query.lastInsertId()
        Bajas._ids.append(baja_insertada)
        ####
        ##Crear sustituciones asociadas
        mis_sustituciones = Sustituciones()
        cal = calendario.Calendario()
        
        for dia in [inicio.addDays(i)
                    for i in range(inicio.daysTo(final) + 1)]:
            turno = cal.getJornada(sustituido, dia)
            if turno in {personal.Jornada.TM, personal.Jornada.TT,
                         personal.Jornada.TN, personal.Jornada.Ret}:
                mis_sustituciones.add(sustituido, None,
                                             dia, turno, baja_insertada)
        ####

    @transaccion
    def delete(self, baja):
        ##Borra las sustituciones asociadas a la baja
        mis_sustituciones = Sustituciones(self.dbase)
        for sustitucion in mis_sustituciones.iterable(baja):
            mis_sustituciones.delete(sustitucion)
        ####
        ##Borra la baja            
        query = QtSql.QSqlQuery()
        query.prepare("DELETE FROM bajas "
                      "WHERE baja_id = ?")
        query.addBindValue(baja.rowid())
        if not query.exec_():
            return False
        Bajas._ids.remove(baja.rowid())
        return True
        ####

class Baja(object):
    __BASE_BAJAS = {"baja_id":0,
                    "sustituido_id":1,
                    "inicio":2,
                    "final":3,
                    "motivo":4}
    _cache = {}
    
    def __init__(self, dbase, baja_id):
        self.dbase = dbase
        self.baja_id = str(baja_id)
        ##Añadir baja a cache
        if not self.baja_id in Baja._cache:
            query = QtSql.QSqlQuery()
            query.prepare("SELECT * FROM bajas "
                          "WHERE baja_id = ?")
            query.addBindValue(baja_id)
            if not query.exec_():
                print(query.lastError().text())
                raise ValueError
            query.first()
            if query.isValid():
                Baja._cache[self.baja_id] = {}
                for key, value in Baja.__BASE_BAJAS.items():
                    if query.isNull(value):
                        Baja._cache[self.baja_id][key] = None
                    else:
                        Baja._cache[self.baja_id][key] = query.value(value)
        ####
        ##Tomar datos de la baja
        self.datos = Baja._cache[self.baja_id]
        ####

    def __eq__(self, other):
        if other is None:
            return self is None
        else:
            return self.rowid() == other.rowid()

    def __ne__(self, other):
        if other is None:
            return self is not None
        else:
            return self.rowid() != other.rowid()
        
    def __key(self):
        return (self.datos["baja_id"], self.datos["sustituido_id"])

    def __hash__(self):
        return hash(self.__key()) 

    def getColumn(self, column):
        try:
            return self.datos[column]
        except KeyError:
            print("Baja.getColumn: No se ha encontrado {0} "
                  "para {1}".format(column, self.baja_id))
            return None

    def setColumn(self, column, value):
        try:
            query = QtSql.QSqlQuery()
            query.prepare("UPDATE bajas "
                          "SET {0} = ? "
                          "WHERE baja_id = ?".format(column))
            query.addBindValue(value)
            query.addBindValue(self.datos["baja_id"])
            if not query.exec_():
                print(query.lastError().text())
                raise ValueError
            Baja._cache[self.baja_id][column] = value
        except KeyError:
            print("Baja.setColumn: No se ha encontrado {0} "
                  "para {1}".format(column, self.baja_id))

    def rowid(self):
        return self.getColumn("baja_id")

    def sustituido(self):
        sustituido = self.getColumn("sustituido_id")
        if sustituido is None:
            return None
        else:
            return trabajador.Trabajador(self.dbase, sustituido)

    def inicio(self):
        return QtCore.QDate.fromString(self.getColumn("inicio"),
                                       QtCore.Qt.ISODate)

    def final(self):
        return QtCore.QDate.fromString(self.getColumn("final"),
                                       QtCore.Qt.ISODate)

    def motivo(self):
        return self.getColumn("motivo")

    def setInicio(self, fecha):
        if fecha == self.inicio():
            return
        elif fecha > self.inicio():
            mis_sustituciones = Sustituciones(self.dbase)
            for sustitucion in mis_sustituciones.iterable(self):
                if sustitucion.fecha() < fecha:
                    mis_sustituciones.delete(sustitucion)
        elif fecha < self.inicio():
            mis_sustituciones = Sustituciones(self.dbase)
            cal = calendario.Calendario()
            
            for dia in [fecha.addDays(i)
                        for i in range(fecha.daysTo(self.inicio()))]:
                turno = cal.getJornada(self.sustituido(), dia)
                if turno in {personal.Jornada.TM, personal.Jornada.TT,
                             personal.Jornada.TN, personal.Jornada.Ret}:
                    mis_sustituciones.add(self.sustituido(), None,
                                          dia, turno, self.rowid())
        self.setColumn("inicio", fecha.toString(QtCore.Qt.ISODate))
        
    def setFinal(self, fecha):
        if fecha == self.final():
            return
        elif fecha < self.final():
            mis_sustituciones = Sustituciones(self.dbase)
            for sustitucion in mis_sustituciones.iterable(self):
                if sustitucion.fecha() > fecha:
                    mis_sustituciones.delete(sustitucion)
        elif fecha > self.final():
            mis_sustituciones = Sustituciones(self.dbase)
            cal = calendario.Calendario()
            
            for dia in [fecha.addDays(i)
                        for i in range(fecha.daysTo(self.final()), 0)]:
                turno = cal.getJornada(self.sustituido(), dia)
                if turno in {personal.Jornada.TM, personal.Jornada.TT,
                             personal.Jornada.TN, personal.Jornada.Ret}:
                    mis_sustituciones.add(self.sustituido(), None,
                                          dia, turno, self.rowid())
        self.setColumn("final", fecha.toString(QtCore.Qt.ISODate))

class Sustituciones(object):
    _dbase = None
    _ids = []
    def __init__(self, dbase=None):
        self.dbase = dbase
        if not Sustituciones._ids:
            query = QtSql.QSqlQuery()
            query.exec_("SELECT sustitucion_id FROM sustituciones")
            while query.next():
                Sustituciones._ids.append(query.value(0))
        self.ids = Sustituciones._ids

    def iterable(self, baja=None):
        if baja is None:
            return {Sustitucion(self.dbase, index) for index in self.ids}
        else:
            return {Sustitucion(self.dbase, index)
                    for index in self.ids
                    if Sustitucion(self.dbase, index).baja() == baja}

    def add(self, sustituido, sustituto, fecha, turno, baja_id):
        query = QtSql.QSqlQuery()
        query.prepare("INSERT INTO sustituciones "
                      "(sustituido_id, sustituto_id, fecha, turno, baja_id) "
                      "VALUES (?, ?, ?, ?, ?)")
        query.addBindValue(sustituido.rowid())
        if sustituto is None:
           query.addBindValue(None)
        else:
           query.addBindValue(sustituto.rowid())
        query.addBindValue(fecha)
        query.addBindValue(turno.value)
        query.addBindValue(baja_id)
        if not query.exec_():
            raise ValueError("Alguno de los argumentos no "
                             "es valido para la base de datos.")        
        Sustituciones._ids.append(query.lastInsertId())

    def delete(self, sustitucion):
        query = QtSql.QSqlQuery()
        query.prepare("DELETE FROM sustituciones "
                      "WHERE sustitucion_id = ?")
        query.addBindValue(sustitucion.rowid())
        if not query.exec_():
            return False
        Sustituciones._ids.remove(sustitucion.rowid())
        return True
    ##ME FALTA DARE UNA VUELTA A COMO ELIMINO DE LA CACHE DE class Sustitucion
    ##DE MOMENTO DEJO LA CACHE SUCIA YA QUE LOS IDS SON UNICOS

class Sustitucion(object):
    __BASE_SUSTITUCIONES = {"sustitucion_id":0,
                            "sustituido_id":1,
                            "sustituto_id":2,
                            "fecha":3,
                            "turno":4,
                            "baja_id":5}
    _cache = {}
    
    def __init__(self, dbase, sustitucion_id):
        self.dbase = dbase
        self.sustitucion_id = str(sustitucion_id)
        ##Añadir sustitucion a cache
        if not self.sustitucion_id in Sustitucion._cache:
            query = QtSql.QSqlQuery()
            query.prepare("SELECT * FROM sustituciones "
                          "WHERE sustitucion_id = ?")
            query.addBindValue(sustitucion_id)
            if not query.exec_():
                print(query.lastError().text())
                raise ValueError
            query.first()
            if query.isValid():
                Sustitucion._cache[self.sustitucion_id] = {}
                for key, value in Sustitucion.__BASE_SUSTITUCIONES.items():
                    if query.isNull(value):
                        Sustitucion._cache[self.sustitucion_id][key] = None
                    else:
                        Sustitucion._cache[self.sustitucion_id][key] = query.value(value)
        ####
        ##Tomar datos de la sustitucion
        self.datos = Sustitucion._cache[self.sustitucion_id]
        ####

    def __eq__(self, other):
        if other is None:
            return self is None
        else:
            return self.rowid() == other.rowid()

    def __ne__(self, other):
        if other is None:
            return self is not None
        else:
            return self.rowid() != other.rowid()

    def __key(self):
        return (self.datos["sustitucion_id"], self.datos["sustituido_id"],
                self.datos["fecha"], self.datos["turno"])

    def __hash__(self):
        return hash(self.__key()) 

    def getColumn(self, column):
        try:
            return self.datos[column]
        except KeyError:
            print("Sustitucion.getColumn: No se ha encontrado {0} "
                  "para {1}".format(column, self.sustitucion_id))
            return None

    def setColumn(self, column, value):
        try:
            query = QtSql.QSqlQuery()
            query.prepare("UPDATE sustituciones "
                          "SET {0} = ? "
                          "WHERE sustitucion_id = ?".format(column))
            query.addBindValue(value)
            query.addBindValue(self.datos["sustitucion_id"])
            if not query.exec_():
                print(query.lastError().text())
                raise ValueError
            Sustitucion._cache[self.sustitucion_id][column] = value
        except KeyError:
            print("Sustitucion.setColumn: No se ha encontrado {0} "
                  "para {1}".format(column, self.baja_id))

    def rowid(self):
        return self.getColumn("sustitucion_id")

    def sustituido(self):
        sustituido = self.getColumn("sustituido_id")
        if sustituido is None:
            return None
        else:
            return trabajador.Trabajador(self.dbase, sustituido)

    def sustituto(self):
        sustituto = self.getColumn("sustituto_id")
        if sustituto is None:
            return None
        else:
            return trabajador.Trabajador(self.dbase, sustituto)

    def fecha(self):
        return QtCore.QDate.fromString(self.getColumn("fecha"),
                                       QtCore.Qt.ISODate)

    def turno(self):
        return personal.Jornada(self.getColumn("turno"))                                       

    def baja(self):
        return Baja(self.dbase, self.getColumn("baja_id"))

    def setSustituto(self, sustituto):
        if isinstance(sustituto, trabajador.Trabajador):
            self.setColumn("sustituto_id", sustituto.rowid())
        else:
            self.setColumn("sustituto_id", None)        

    def sustitutos(self):
        trabajadores = trabajador.Trabajadores(self.dbase)
        sustituido = self.sustituido()
        mis_sustituciones = Sustituciones(self.dbase)
        mis_bajas = Bajas(self.dbase)
        cal = calendario.Calendario()
        candidatos = set()
        no_validos = set()
        puestos = {sustituido.puesto()}
        
        if personal.Puesto.OpPolivalente in puestos:
            puestos.update({personal.Puesto.OpReactor,
                            personal.Puesto.OpTurbina})
        elif (personal.Puesto.OpReactor in puestos or
              personal.Puesto.OpTurbina in puestos):
            puestos.add(personal.Puesto.OpPolivalente)
        ##Buscar trabajadores de otros equipos en jornada de Ofi, Des, Ret        
        for candidato in trabajadores.iterable():
            if (candidato.puesto() in puestos and
                candidato.grupo() != sustituido.grupo() and
                cal.getJornada(candidato, self.fecha()) in {personal.Jornada.Des,
                                                            personal.Jornada.Ret,
                                                            personal.Jornada.Ofi}):
                candidatos.add(candidato)
        ####
        ##Filtrar trabajadores que estan de baja o sustituyendo
        for sustitucion in mis_sustituciones.iterable():
            if sustitucion.fecha() == self.fecha():
                no_validos.add(sustitucion.sustituto())                                         
        for baja in mis_bajas.iterable():
            if baja.inicio() <= self.fecha() and baja.final() >= self.fecha():
                no_validos.add(baja.sustituido())
        ####
        ##Filtrar trabajadores con TN programado o debido a sustitucion
        ##para evitar empalmar dos turno seguidos
        if self.turno() is personal.Jornada.TM:
            for candidato in candidatos:
                if cal.getJornada(candidato,
                                  self.fecha().addDays(-1)) is personal.Jornada.TN:
                    no_validos.add(candidato)
            for sustitucion in mis_sustituciones.iterable():
                if (sustitucion.fecha() == self.fecha().addDays(-1) and
                    sustitucion.turno() is personal.Jornada.TN):
                    no_validos.add(sustitucion.sustituto())
        return (candidatos - no_validos)

    def orderedSustitutos(self):
        candidatos = self.sustitutos()      
        cal = calendario.Calendario()
        
        lista_ordenada = [(i,
                           cal.getJornada(i, self.fecha())) for i in candidatos]
        if self.sustituido().unidad() is personal.Unidad.U1:
            lista_ordenada.sort(key=lambda trabajador: trabajador[0].datos["unidad"])
        else:
            lista_ordenada.sort(key=lambda trabajador: trabajador[0].datos["unidad"], reverse=True)
        lista_ordenada.sort(key=lambda trabajador: trabajador[1].value)

        return [i[0] for i in lista_ordenada]        
    
