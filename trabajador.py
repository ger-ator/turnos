from PyQt5.QtSql import *
from PyQt5.QtCore import *

class Trabajador(object):
    def __init__(self, trabajadorid):
        self.trabajadorid = trabajadorid

        query = QSqlQuery()
        query.prepare("SELECT Puesto, Unidad, Equipo FROM personal "
                      "WHERE Id = ?")
        query.addBindValue(trabajadorid)
        query.exec_()
        query.first()
        self.puesto = query.value(0)
        self.unidad = query.value(1)
        self.equipo = query.value(2)

    def getId(self):
        return self.trabajadorid
    
    def getPuesto(self):
        return self.puesto

    def getEquipo(self):
        return self.equipo

    def getUnidad(self):
        return self.unidad
    
    def getTurno(self, fecha):
        query = QSqlQuery()
        query.prepare("SELECT E{0} from calendario "
                      "WHERE Fecha = ?".format(self.equipo))
        query.addBindValue(fecha)
        query.exec_()
        query.first()
        return query.value(0)

class Sustituido(Trabajador):
    def __init__(self, trabajadorid):
        Trabajador.__init__(self, trabajadorid)

    def isPolivalente(self):
        if self.puesto == "Operador Polivalente":
            return True
        else:
            return False

    def isOpReactor(self):
        if self.puesto == "Operador de Reactor":
            return True
        else:
            return False

    def isOpTurbina(self):
        if self.puesto == "Operador de Turbina":
            return True
        else:
            return False

class Candidato(Trabajador):
    def __init__(self, trabajadorid, fecha):
        Trabajador.__init__(self, trabajadorid)
        self.turno_dia_anterior = self.getTurno(fecha.addDays(-1))

    def esta_de_baja(self, fecha):
        query = QSqlQuery()
        query.prepare("SELECT COUNT(trabajadorid) FROM necesidades "
                      "WHERE Fecha = ? AND trabajadorid = ?")
        query.addBindValue(fecha)
        query.addBindValue(self.trabajadorid)
        query.exec_()
        query.first()
        if query.value(0) > 0:
            return True
        else:
            return False

    def esta_sustituyendo(self, fecha):
        query = QSqlQuery()
        query.prepare("SELECT COUNT(Asignado) FROM necesidades "
                      "WHERE Fecha = ? AND Asignado = ?")
        query.addBindValue(fecha)
        query.addBindValue(self.trabajadorid)
        query.exec_()
        query.first()
        if query.value(0) > 0:
            return True
        else:
            return False

    def esta_de_turno(self, fecha):
        query = QSqlQuery()
        query.prepare("SELECT COUNT(E{0}) from calendario "
                      "WHERE Fecha = ? AND (E{0} = 'Mañana' "
                      "OR E{0} = 'Tarde' OR E{0} = 'Noche')".format(self.equipo))
        query.addBindValue(fecha)
        query.exec_()
        query.first()
        if query.value(0) > 0:
            return True
        else:
            return False

    def esta_de_reten(self, fecha):
        query = QSqlQuery()
        query.prepare("SELECT COUNT(E{0}) from calendario "
                      "WHERE Fecha = ? AND E{0} = 'Retén'".format(self.equipo))
        query.addBindValue(fecha)
        query.exec_()
        query.first()
        if query.value(0) > 0:
            return True
        else:
            return False

    def esta_de_descanso(self, fecha):
        query = QSqlQuery()
        query.prepare("SELECT COUNT(E{0}) from calendario "
                      "WHERE Fecha = ? AND E{0} = 'Descanso'".format(self.equipo))
        query.addBindValue(fecha)
        query.exec_()
        query.first()
        if query.value(0) > 0:
            return True
        else:
            return False

    def esta_de_oficina(self, fecha):
        query = QSqlQuery()
        query.prepare("SELECT COUNT(E{0}) from calendario "
                      "WHERE Fecha = ? AND E{0} = 'Oficina'".format(self.equipo))
        query.addBindValue(fecha)
        query.exec_()
        query.first()
        if query.value(0) > 0:
            return True
        else:
            return False

    def esta_de_simulador(self, fecha):
        query = QSqlQuery()
        query.prepare("SELECT COUNT(E{0}) from calendario "
                      "WHERE Fecha = ? AND E{0} = 'Simulador'".format(self.equipo))
        query.addBindValue(fecha)
        query.exec_()
        query.first()
        if query.value(0) > 0:
            return True
        else:
            return False

    def getTurno(self, fecha):
        if self.esta_sustituyendo(fecha):
            query = QSqlQuery()
            query.prepare("SELECT Turno from necesidades "
                          "WHERE Fecha = ? AND Asignado = ?")
            query.addBindValue(fecha)
            query.addBindValue(self.trabajadorid)
            query.exec_()
            query.first()
            return query.value(0)
        else:
            return Trabajador.getTurno(self, fecha)

class ListaCandidatos(object):
    def __init__(self, sustituido, fecha):
        
        self.candidatos = []
        
        query = QSqlQuery()
        if sustituido.isPolivalente():
            query.prepare("SELECT Id "
                          "FROM personal "
                          "WHERE NOT Equipo = ? AND "
                          "(Puesto = ? OR "
                          "Puesto = 'Operador de Turbina' OR "
                          "Puesto = 'Operador de Reactor')")
        elif sustituido.isOpReactor():
            query.prepare("SELECT Id "
                          "FROM personal "
                          "WHERE NOT Equipo = ? AND "
                          "(Puesto = 'Operador Polivalente' OR "
                          "Puesto = ?)")
        elif sustituido.isOpTurbina():
            query.prepare("SELECT Id "
                          "FROM personal "
                          "WHERE NOT Equipo = ? AND "
                          "(Puesto = 'Operador Polivalente' OR "
                          "Puesto = ?)")
        else:
            query.prepare("SELECT Id "
                          "FROM personal "
                          "WHERE NOT Equipo = ? AND Puesto = ?")
        ##ESTA FORMA DE ELEGIR CANDIDATOS HACE QUE NO SE ESCOJA AL RETEN
        ##DE LA UNIDAD CONTRARIA PARA SUSTITUIR AL RETEN, COMO DEBE SER.
        ##PERO QUEDA ENMASCARADO PORQUE SE DEBE A QUE AL GENERAR NECESIDADES
        ##SOLO SE TIENE EN CUENTA TURNOS Y RETEN, Y NUNCA BUSCO CANDIDATOS
        ##DEL EQUIPO DEL INDIVIDUO QUE GENERA LA NECESIDAD
	
	##OJO!!!CUANDO QUIERA METER NECESIDADES QUE PROVENGAN DE GENTE DE OFICINA
	##ESTO ME VA A DAR PROBLEMAS
        query.addBindValue(sustituido.getEquipo())
        query.addBindValue(sustituido.getPuesto())
        query.exec_()

        reten = []
        reten_Ucontraria = []
        oficina = []
        oficina_Ucontraria = []
        descanso = []
        descanso_Ucontraria = []

        while query.next():
            pringao = Candidato(query.value(0), fecha)
            if pringao.esta_de_turno(fecha):
                continue
            elif pringao.esta_sustituyendo(fecha) or pringao.esta_de_baja(fecha):
                continue
            elif pringao.esta_de_reten(fecha):
                if pringao.getUnidad() == sustituido.getUnidad():
                    reten.append(pringao)
                else:
                    reten_Ucontraria.append(pringao)
            elif pringao.esta_de_oficina(fecha):
                if pringao.getUnidad() == sustituido.getUnidad():
                    oficina.append(pringao)
                else:
                    oficina_Ucontraria.append(pringao)
            elif pringao.esta_de_descanso(fecha):
                if pringao.getUnidad() == sustituido.getUnidad():
                    descanso.append(pringao)
                else:
                    descanso_Ucontraria.append(pringao)
            else:
                continue
        self.candidatos = (reten + reten_Ucontraria + oficina +
                           oficina_Ucontraria + descanso + descanso_Ucontraria)

    def getCandidatos(self):
        return self.candidatos

    def getCandidato(self, trabajadorid):
        for i in self.candidatos:
            if i.getId() == trabajadorid:
                return i
            else:
                continue
        return None

class Necesidad(object):
    def __init__(self, necesidadid):
        self.necesidadid = necesidadid
        
        query = QSqlQuery()
        query.prepare("SELECT Fecha, trabajadorid, bajaid FROM necesidades "
                      "WHERE Id = ?")
        query.addBindValue(self.necesidadid)
        query.exec_()
        query.first()
        
        self.fecha = QDate.fromString(query.value(0), "yyyy-MM-dd")
        self.sustituido = Sustituido(query.value(1))
        self.bajaid = query.value(2)
        self.candidatos = ListaCandidatos(self.sustituido, self.fecha)

    def getId(self):
        return self.necesidadid

    def getSustituido(self):
        return self.sustituido

    def getFecha(self):
        return self.fecha
    
    def getListaIds(self):
        return tuple(i.getId() for i in self.candidatos.getCandidatos())

    def getCandidatos(self):
        return self.candidatos.getCandidatos()

    def asignaCandidato(self, trabajadorid):
##        candidato = self.candidatos.getCandidato(trabajadorid)
##        turno_dia_anterior = candidato.turno_dia_anterior
##        turno_del_sustituido = self.sustituido.getTurno(self.getFecha())
##        if (turno_del_sustituido == "Mañana" and
##            turno_dia_anterior == "Noche"):
##            query = QSqlQuery()
##            ###BUSCAR TRABAJADOR QUE ESTA DE TARDE
##            query.prepare("SELECT * FROM calendario")
##            ###
##            query.prepare("INSERT INTO necesidades "
##                          "(trabajadorid, Fecha, Turno, Motivo, bajaid, Asignado) "
##                          "VALUES (?, ?, ?, ?, ?, ?)")
##            query.addBindValue(trabajadorid)
##            query.addBindValue(self.getFecha()) ##FECHA
##            query.addBindValue(self.sustituto.getTurno()) ##TURNO
##            query.addBindValue("Cambio a peticion de empresa")
##            query.addBindValue(self.bajaid)
##            query.addBindValue(trabadorid_TTarde)
##            query.exec_()
##            ##CAMBIA AL DE TARDE A MAÑANA Y ASIGNA TARDE
##        else:
##            query = QSqlQuery()
##            query.prepare("UPDATE necesidades SET Asignado = ? WHERE Id = ?")
##            query.addBindValue(trabajadorid)
##            query.addBindValue(self.getId())
##            query.exec_()

        query = QSqlQuery()
        query.prepare("UPDATE necesidades SET Asignado = ? WHERE Id = ?")
        query.addBindValue(trabajadorid)
        query.addBindValue(self.getId())
        query.exec_()
        
