from PyQt5 import QtSql, QtCore

import trabajador

class Baja(object):
    def __init__(self, *args):
        ##Si proporciono un solo argumento supongo que se
        ##quiere cargar datos del ID de la base de datos
        if len(args) == 1:
            query = QtSql.QSqlQuery()
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
                self.sustituido = trabajador.Sustituido(query.value(0))
                self.inicio = QtCore.QDate.fromString(query.value(1),
                                                      QtCore.Qt.ISODate)
                self.final = QtCore.QDate.fromString(query.value(2),
                                                     QtCore.Qt.ISODate)
                self.motivo = query.value(3)
                self.sustituciones = self.cargaSustituciones()
            else:
                raise ValueError
        ##Si proporciono 4 argumentos supongo que quiero crear una entrada
        ##en la base de datos, *args=(sustituido_id, inicio, final, motivo)
        elif len(args) == 4:
            query = QtSql.QSqlQuery()
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
            self.sustituido = trabajador.Sustituido(args[0])
            self.inicio = args[1]
            self.final = args[2]
            self.motivo = args[3]
            self.sustituciones = self.creaSustituciones()
        else:
            raise RuntimeError("Error en numero de argumentos de Baja(*args).")

    def creaSustituciones(self):
        query = QtSql.QSqlQuery()
        sustituciones = []
        for turno in [trabajador.Turno.manana, trabajador.Turno.tarde,
                      trabajador.Turno.noche, trabajador.Turno.reten]:
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
                tmp = trabajador.Sustitucion(self.sustituido.getId(),
                                             query.value(0),
                                             turno,
                                             self.bajaid)
                sustituciones.append(tmp)
        else:
            return sustituciones

    def cargaSustituciones(self):
        query = QtSql.QSqlQuery()
        sustituciones = []
        query.prepare("SELECT sustitucion_id FROM sustituciones "
                      "WHERE baja_id = ?")
        query.addBindValue(self.bajaid)
        if not query.exec_():
            print("Error al cargar sustituciones.")
            print(query.lastError().text())

        while query.next():
            tmp = trabajador.Sustitucion(query.value(0))
            sustituciones.append(tmp)
        else:
            return sustituciones

    def setInicio(self, fecha):
        query = QtSql.QSqlQuery()
        query.prepare("UPDATE bajas "
                      "SET inicio = ? "
                      "WHERE baja_id = ?")
        query.addBindValue(fecha)
        query.addBindValue(self.bajaid)
        query.exec_()
        self.inicio = fecha

    def setFinal(self, fecha):
        query = QtSql.QSqlQuery()
        query.prepare("UPDATE bajas "
                      "SET final = ? "
                      "WHERE baja_id = ?")
        query.addBindValue(fecha)
        query.addBindValue(self.bajaid)
        query.exec_()
        self.final = fecha

    def modificaSustituciones(self, inicio, final):
        query = QtSql.QSqlQuery()

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
            for turno in [trabajador.Turno.manana, trabajador.Turno.tarde,
                          trabajador.Turno.noche, trabajador.Turno.reten]:
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
                    tmp = trabajador.Sustitucion(self.sustituido.getId(),
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
            for turno in [trabajador.Turno.manana, trabajador.Turno.tarde,
                          trabajador.Turno.noche, trabajador.Turno.reten]:
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
                    tmp = trabajador.Sustitucion(self.sustituido.getId(),
                                                 query.value(0),
                                                 turno,
                                                 self.bajaid)
                    ##A partir de aqui ya no tengo ordenadas las sustituciones.
                    ##Ver si me afecta en algo
                    self.sustituciones.append(tmp)
            self.setFinal(final)            
