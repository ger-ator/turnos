from PyQt5.QtSql import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from connection import *

class Trabajador(object):
    def __init__(self, trabajadorid):
        if isinstance(trabajadorid, int):
            query = QSqlQuery()
            query.prepare("SELECT nombre, apellido1, apellido2, "
                          "puesto, unidad, equipo FROM personal "
                          "WHERE personal_id = ?")
            query.addBindValue(trabajadorid)
            if not query.exec_():
                print("Error al crear trabajador")
                print(query.lastError().text())
            query.first()
            if query.isValid():
                self.trabajadorid = trabajadorid
                self.nombre = query.value(0)
                self.apellido1 = query.value(1)
                self.apellido2 = query.value(2)
                self.puesto = Puesto(query.value(3))
                self.unidad = Unidad(query.value(4))
                self.equipo = Equipo(query.value(5))
            else:
                print("No hay ningun trabajador con ese ID en la base de datos.")
                raise ValueError
        else:
            raise TypeError

    def getNombre(self):
        return self.nombre

    def getApellido1(self):
        return self.apellido1

    def getApellido2(self):
        return self.apellido1

    def __str__(self):
        return " ".join([self.nombre, self.apellido1, self.apellido2])

    def getId(self):
        return self.trabajadorid
    
    def getPuesto(self):
        return self.puesto.value

    def getEquipo(self):
        return self.equipo.value

    def getUnidad(self):
        return self.unidad.value
    
    def getTurno(self, fecha):
        query = QSqlQuery()
        query.prepare("SELECT {0} from calendario "
                      "WHERE fecha = ?".format(self.equipo.name))
        query.addBindValue(fecha)
        if not query.exec_():
            print("Error al extraer el turno.")
            print(query.lastError().text())
        query.first()
        if query.isValid():
            return Turno(query.value(0))
        else:
            return Turno.sin_asignar

class Sustituido(Trabajador):
    def __init__(self, trabajadorid):
        Trabajador.__init__(self, trabajadorid)

    def isPolivalente(self):
        if self.puesto == Puesto.OpPolivalente:
            return True
        else:
            return False

    def isOpReactor(self):
        if self.puesto == Puesto.OpReactor:
            return True
        else:
            return False

    def isOpTurbina(self):
        if self.puesto == Puesto.OpTurbina:
            return True
        else:
            return False

class Candidato(Trabajador):
    def __init__(self, trabajadorid):
        Trabajador.__init__(self, trabajadorid)

    def esta_de_baja(self, fecha):
        query = QSqlQuery()
        query.prepare("SELECT sustituido_id FROM bajas "
                      "WHERE ( inicio <= date(:fecha) AND final >= date(:fecha) ) "
                      "AND sustituido_id = :sustituido_id")
        query.bindValue(":fecha", fecha)
        query.bindValue(":sustituido_id", self.trabajadorid)
        if not query.exec_():
            print("Error verificar si el trabajador esta de baja.")
            print(query.lastError().text())
        query.first()        
        if query.isValid():
            return True
        else:
            return False

    def esta_sustituyendo(self, fecha):
        query = QSqlQuery()
        query.prepare("SELECT sustituto_id FROM sustituciones "
                      "WHERE fecha = ? AND sustituto_id = ?")
        query.addBindValue(fecha)
        query.addBindValue(self.trabajadorid)
        if not query.exec_():
            print("Error verificar si el trabajador esta sustituyendo.")
            print(query.lastError().text())
        query.first()
        if query.isValid():
            return True
        else:
            return False

    def esta_de_turno(self, fecha):
        if self.getTurno(fecha) in [Turno.manana, Turno.tarde, Turno.noche]:
            return True
        else:
            return False

    def esta_de_reten(self, fecha):
        if self.getTurno(fecha) == Turno.reten:
            return True
        else:
            return False

    def esta_de_descanso(self, fecha):
        if self.getTurno(fecha) == Turno.descanso:
            return True
        else:
            return False

    def esta_de_oficina(self, fecha):
        if self.getTurno(fecha) == Turno.oficina:
            return True
        else:
            return False

    def esta_de_simulador(self, fecha):
        if self.getTurno(fecha) == Turno.simulador:
            return True
        else:
            return False

    def getTurno(self, fecha):
        if self.esta_sustituyendo(fecha):
            query = QSqlQuery()
            query.prepare("SELECT turno from sustituciones "
                          "WHERE fecha = ? AND sustituto_id = ?")
            query.addBindValue(fecha)
            query.addBindValue(self.trabajadorid)
            if not query.exec_():
                print("Error al extraer el turno.")
                print(query.lastError().text())
            query.first()
            return Turno(query.value(0))
        else:
            return Trabajador.getTurno(self, fecha)     

class Sustitucion(object):
    def __init__(self, *args):
        ##Si proporciono un solo argumento supongo que se
        ##quiere cargar datos del ID de la base de datos
        if len(args) == 1:
            ##Obtener datos de la sustitucion de la base de datos.
            query = QSqlQuery()
            query.prepare("SELECT sustituido_id, fecha, turno, baja_id "
                          "FROM sustituciones "
                          "WHERE sustitucion_id = ?")
            query.addBindValue(args[0])
            if not query.exec_():
                print("Error al cargar datos de sustitucion.")
                print(query.lastError().text())
            query.first()
            if query.isValid():
                self.sustitucionid = args[0]
                self.sustituido = Sustituido(query.value(0))
                self.fecha = QDate.fromString(query.value(1), "yyyy-MM-dd")
                self.turno = Turno(query.value(2))
                self.bajaid = query.value(3)
            else:
                raise ValueError("No hay ninguna sustitucion con ese ID.")
        ##Si proporciono 4 argumentos supongo que quiero crear una entrada
        ##en la base de datos, *args=(sustituido_id, fecha, turno, baja_id)
        elif len(args) == 4:
            query = QSqlQuery()
            query.prepare("INSERT INTO sustituciones "
                          "(sustituido_id, fecha, turno, baja_id) "
                          "VALUES (?, ?, ?, ?)")
            query.addBindValue(args[0])##sustituido_id
            query.addBindValue(args[1])##fecha
            query.addBindValue(args[2].value)##turno
            query.addBindValue(args[3])##baja_id
            if not query.exec_():
                print("Error al crear sustitucion.")
                print(query.lastError().text())
                raise ValueError("Alguno de los argumentos no "
                                 "es valido para la base de datos.")
            self.sustitucionid = query.lastInsertId()
            self.sustituido = Sustituido(args[0])
            self.fecha = args[1]
            self.turno = args[2]
            self.bajaid = args[3]
        else:
            raise RuntimeError("Error en numero de argumentos de Sustitucion(*args).")

    def getListaCandidatos(self):       
        query = QSqlQuery()
        if self.sustituido.isPolivalente():
            query.prepare("SELECT personal_id "
                          "FROM personal "
                          "WHERE NOT equipo = ? AND "
                          "(puesto = ? OR "
                          "puesto = 'Operador de Turbina' OR "
                          "puesto = 'Operador de Reactor')")
        elif self.sustituido.isOpReactor():
            query.prepare("SELECT personal_id "
                          "FROM personal "
                          "WHERE NOT equipo = ? AND "
                          "(puesto = 'Operador Polivalente' OR "
                          "puesto = ?)")
        elif self.sustituido.isOpTurbina():
            query.prepare("SELECT personal_id "
                          "FROM personal "
                          "WHERE NOT equipo = ? AND "
                          "(puesto = 'Operador Polivalente' OR "
                          "puesto = ?)")
        else:
            query.prepare("SELECT personal_id "
                          "FROM personal "
                          "WHERE NOT equipo = ? AND puesto = ?")

        query.addBindValue(self.sustituido.getEquipo())
        query.addBindValue(self.sustituido.getPuesto())
        if not query.exec_():
            print("Error buscar candidatos.")
            print(query.lastError().text())
            return []

        reten = []
        reten_Ucontraria = []
        oficina = []
        oficina_Ucontraria = []
        descanso = []
        descanso_Ucontraria = []

        while query.next():
            pringao = Candidato(query.value(0))
            if (pringao.esta_de_turno(self.fecha)
                or pringao.esta_sustituyendo(self.fecha)
                or pringao.esta_de_baja(self.fecha)):
                continue
            elif pringao.esta_de_reten(self.fecha):
                if pringao.unidad == self.sustituido.unidad:
                    reten.append(pringao)
                else:
                    reten_Ucontraria.append(pringao)
            elif pringao.esta_de_oficina(self.fecha):
                if pringao.unidad == self.sustituido.unidad:
                    oficina.append(pringao)
                else:
                    oficina_Ucontraria.append(pringao)
            elif pringao.esta_de_descanso(self.fecha):
                if pringao.unidad == self.sustituido.unidad:
                    descanso.append(pringao)
                else:
                    descanso_Ucontraria.append(pringao)
            else:
                continue
        return (reten + reten_Ucontraria + oficina +
                oficina_Ucontraria + descanso + descanso_Ucontraria)
    
    def getListaCandidatosIds(self):
        return tuple(i.getId() for i in self.getListaCandidatos())

    def getId(self):
        return self.sustitucionid

    def getSustituido(self):
        return self.sustituido

    def getFecha(self):
        return self.fecha
    
    def asignaCandidato(self, trabajadorid):
        candidato = Candidato(trabajadorid)
        turno_ayer = candidato.getTurno(self.fecha.addDays(-1))
        ##Solo se contempla hacer una sustitucion diaria, luego solo
        ##hay que comprobar si va de mañana y el dia anterior de noche.
        turno_sustitucion = self.sustituido.getTurno(self.fecha)
        ##Si no hay descanso entre turnos
        if turno_ayer is Turno.noche and turno_sustitucion is Turno.manana:
            print("no descansa 8h, tengo que cambiar al de tarde a manana")
            ##Conseguir el ID del trabajador de tarde
            ##cambio = Baja(id del trabajador de tarde, self.fecha, self.fecha, "Cambio Turno")
            ##for i in cambio.sustituciones:
            ##  i.asignaCandidato(trabajadorid)
            ##query = QSqlQuery()
            ##query.prepare("UPDATE sustituciones "
            ##              "SET sustituto_id = ? "
            ##              "WHERE sustitucion_id = ?")
            ##query.addBindValue(ID del trabajador de tarde)
            ##query.addBindValue(self.getId())
            ##query.exec_()            
        ##Si descansa 8 horas entre turnos
        else:
            query = QSqlQuery()
            query.prepare("UPDATE sustituciones "
                          "SET sustituto_id = ? "
                          "WHERE sustitucion_id = ?")
            query.addBindValue(trabajadorid)
            query.addBindValue(self.getId())
            query.exec_()        

#######################################################################################
if __name__ == '__main__':
    app = QApplication([])
    if not createConnection():
        sys.exit(1)

    Turno.manana - Turno.manana    
    ##Sustitucion(1)
    Candidato(1)
##    Sustitucion(1, QDate(2016, 3, 23), Turno.manana, 7)
    
##    gmb = Trabajador(1)


##    gmb = Candidato(1, QDate(2016, 3, 22))
##    print (gmb.esta_de_baja(QDate(2016, 3, 22)))
##
##    sustitucion = Necesidad(1)
    
    
    app.exec_()
##    if dlg.exec_():
##        print(dlg.getData())

        
