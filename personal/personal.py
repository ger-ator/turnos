from enum import Enum

from PyQt5 import QtSql

class Jornada(Enum):
    TM = 1
    TT = 2
    TN = 3
    Ret = 4
    Ofi = 5
    Des = 6
    Vac = 7
    Sim = 8
    For = 9

    def __str__(self):
        query = QtSql.QSqlQuery()
        query.prepare("SELECT turno FROM jornadas WHERE turno_id = ?")
        query.addBindValue(self.value)
        query.exec_()
        query.first()
        return query.value(0)

class Grupo(Enum):
    SC1 = 1
    SC2 = 2
    SC3 = 3
    SC4 = 4
    SC5 = 5
    SC6 = 6
    SC7 = 7
    SC8 = 8
    PL1 = 9
    PL2 = 10
    PL3 = 11
    PL4 = 12
    PL5 = 13
    PL6 = 14
    PL7 = 15
    OFI = 16

class Puesto(Enum):
    JdTurno = 1
    Supervisor = 2
    OpReactor =  3
    OpTurbina = 4
    OpPolivalente = 5
    Capataz = 6
    AuxTurbina = 7
    AuxAuxiliar = 8
    AuxSalvaguardias = 9
    AuxExteriores = 10
    AuxTratamiento = 11

class Unidad(Enum):
    U1 = 1
    U2 = 2
    UX = 3
