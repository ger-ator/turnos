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

    def setInicio(self, fecha):
        query = QSqlQuery()
        query.prepare("UPDATE bajas "
                      "SET inicio = ? "
                      "WHERE baja_id = ?")
        query.addBindValue(fecha)
        query.addBindValue(self.bajaid)
        query.exec_()
        self.inicio = fecha

    def setFinal(self, fecha):
        query = QSqlQuery()
        query.prepare("UPDATE bajas "
                      "SET final = ? "
                      "WHERE baja_id = ?")
        query.addBindValue(fecha)
        query.addBindValue(self.bajaid)
        query.exec_()
        self.final = fecha

    def modificaSustituciones(self, inicio, final):
        query = QSqlQuery()

        if inicio > self.inicio:
            query.prepare("DELETE FROM sustituciones "
                          "WHERE ( fecha BETWEEN date(:inicio) AND date(:nuevo_inicio) ) "
                          "AND baja_id = :bajaid")
            query.bindValue(":inicio", self.inicio)
            query.bindValue(":nuevo_inicio", inicio.addDays(-1))
            query.bindValue(":bajaid", self.bajaid)
            query.exec_()
            self.setInicio(inicio)            
        elif inicio < self.inicio:
            for turno in [Turno.manana, Turno.tarde, Turno.noche, Turno.reten]:
                query.prepare("SELECT fecha FROM calendario "
                              "WHERE ( fecha BETWEEN date(:nuevo_inicio) AND date(:inicio) ) "
                              "AND ( {0} = :equipo ) "
                              "ORDER BY fecha ASC".format(turno.name))
                query.bindValue(":nuevo_inicio", inicio)
                query.bindValue(":inicio", self.inicio.addDays(-1))
                query.bindValue(":equipo", self.sustituido.getEquipo())
                query.exec_()
                ##Inserto las necesidades de personal generadas por la baja
                while query.next():
                    tmp = Sustitucion(self.sustituido.getId(),
                                      query.value(0),
                                      turno,
                                      self.bajaid)
                    ##A partir de aqui ya no tengo ordenadas las sustituciones.
                    ##Ver si me afecta en algo
                    self.sustituciones.append(tmp)
            self.setInicio(inicio)

        if final < self.final:
            query.prepare("DELETE FROM sustituciones "
                          "WHERE ( fecha BETWEEN date(:nuevo_final) AND date(:final) ) "
                          "AND baja_id = :bajaid")
            query.bindValue(":nuevo_final", final.addDays(1))
            query.bindValue(":final", self.final)
            query.bindValue(":bajaid", self.bajaid)
            query.exec_()
            self.setFinal(final)            
        elif final > self.final:
            for turno in [Turno.manana, Turno.tarde, Turno.noche, Turno.reten]:
                query.prepare("SELECT fecha FROM calendario "
                              "WHERE ( fecha BETWEEN date(:final) AND date(:nuevo_final) ) "
                              "AND ( {0} = :equipo ) "
                              "ORDER BY fecha ASC".format(turno.name))
                query.bindValue(":final", self.final.addDays(1))
                query.bindValue(":nuevo_final", final)
                query.bindValue(":equipo", self.sustituido.getEquipo())
                query.exec_()
                ##Inserto las necesidades de personal generadas por la baja
                while query.next():
                    tmp = Sustitucion(self.sustituido.getId(),
                                      query.value(0),
                                      turno,
                                      self.bajaid)
                    ##A partir de aqui ya no tengo ordenadas las sustituciones.
                    ##Ver si me afecta en algo
                    self.sustituciones.append(tmp)
            self.setFinal(final)            
