from PyQt5.QtSql import *
from PyQt5.QtCore import *
from trabajador import *

class Baja(object):
    def __init__(self, *args):
        ##Si proporciono un solo argumento supongo que se
        ##quiere cargar datos del ID de la base de datos
        if len(args) == 1:
            query = QSqlQuery()
            query.prepare("SELECT sustituido_id, inicio, final, motivo "
                          "FROM bajas "
                          "WHERE baja_id = ?")
            query.addBindValue(args[0])
            if not query.exec_():
                print("Error al cargar datos de baja.")
                print(query.lastError().text())
            query.first()
            if query.isValid():
                self.bajaid = args[0]
                self.sustituido = Sustituido(query.value(0))
                self.inicio = QDate.fromString(query.value(1), Qt.ISODate)
                self.final = QDate.fromString(query.value(2), Qt.ISODate)
                self.motivo = query.value(3)
                self.sustituciones = self.cargaSustituciones()
            else:
                raise ValueError
        ##Si proporciono 4 argumentos supongo que quiero crear una entrada
        ##en la base de datos, *args=(sustituido_id, inicio, final, motivo)
        elif len(args) == 4:
            query = QSqlQuery()
            query.prepare("INSERT INTO bajas "
                          "(sustituido_id, inicio, final, motivo) "
                          "VALUES (?, ?, ?, ?)")
            query.addBindValue(args[0])##sustituido_id
            query.addBindValue(args[1])##inicio
            query.addBindValue(args[2])##final
            query.addBindValue(args[3])##motivo
            if not query.exec_():
                print("Error al crear sustitucion.")
                print(query.lastError().text())
                raise ValueError("Alguno de los argumentos no "
                                 "es valido para la base de datos.")            
            self.bajaid = query.lastInsertId()
            self.sustituido = Sustituido(args[0])
            self.inicio = args[1]
            self.final = args[2]
            self.motivo = args[3]
            self.sustituciones = self.creaSustituciones()
        else:
            raise RuntimeError("Error en numero de argumentos de Baja(*args).")

    def creaSustituciones(self):
        query = QSqlQuery()
        sustituciones = []
        for turno in [Turno.manana, Turno.tarde, Turno.noche, Turno.reten]:
            query.prepare("SELECT fecha FROM calendario "
                          "WHERE ( fecha BETWEEN date(:inicio) AND date(:final) ) "
                          "AND ( {0} = :equipo ) "
                          "ORDER BY fecha ASC".format(turno.name))
            query.bindValue(":inicio", self.inicio)
            query.bindValue(":final", self.final)
            query.bindValue(":equipo", self.sustituido.getEquipo())
            query.exec_()

            ##Inserto las necesidades de personal generadas por la baja
            while query.next():
                tmp = Sustitucion(self.sustituido.getId(),
                                  query.value(0),
                                  turno,
                                  self.bajaid)
                sustituciones.append(tmp)
        else:
            return sustituciones

    def cargaSustituciones(self):
        query = QSqlQuery()
        sustituciones = []
        query.prepare("SELECT sustitucion_id FROM sustituciones "
                      "WHERE baja_id = ?")
        query.addBindValue(self.bajaid)
        if not query.exec_():
            print("Error al cargar sustituciones.")
            print(query.lastError().text())

        while query.next():
            tmp = Sustitucion(query.value(0))
            sustituciones.append(tmp)
        else:
            return sustituciones
