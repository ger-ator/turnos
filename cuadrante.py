#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui

from personal import bajas, trabajador, personal

class Cuadrante(object):
    def __init__(self, baja_id, inicio, final):
        self.baja = bajas.Baja(None, baja_id)
        self.mis_sustituciones = bajas.Sustituciones()
        self.encabezado = [inicio.addDays(i)
                           for i in range(inicio.daysTo(final) + 1)]
        self.filas = {"sustituido":{"id":self.baja.sustituido()}}
    
        for sust in self.mis_sustituciones.iterable(baja_id):
            if sust.fecha() in self.encabezado:
                self.filas["sustituido"][sust.fecha()] = sust.turno()
                if sust.sustituto() != "":
                    if not str(sust.sustituto()) in self.filas:
                        self.filas[str(sust.sustituto())]={"id":sust.sustituto()}
                    self.filas[str(sust.sustituto())][sust.fecha()] = sust.turno()

    def toTextDoc(self):
        documento = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(documento)

        tabla = cursor.insertTable(len(self.filas) + 1,
                                   len(self.encabezado) + 1)
        ##Preparar el encabezado con los dias
        cursor.movePosition(QtGui.QTextCursor.NextCell)
        for fecha in self.encabezado:
            cursor.insertText(str(fecha.day()))
            cursor.movePosition(QtGui.QTextCursor.NextCell)
        ####
        ##Añadir fila del sustituido
        sustituido = trabajador.Trabajador(None, self.filas["sustituido"]["id"])
        cursor.insertText(" ".join([sustituido.nombre(),
                                    sustituido.apellido1(),
                                    sustituido.apellido2()]))
        cursor.movePosition(QtGui.QTextCursor.NextCell)
        for fecha in self.encabezado:
            try:
                cursor.insertText(str(self.filas["sustituido"][fecha])[0])
                cursor.movePosition(QtGui.QTextCursor.NextCell)
            except KeyError:
                cursor.movePosition(QtGui.QTextCursor.NextCell)
        ####
        ##Añadir filas de los sustitutos
        for fila in self.filas.values():
            if fila is self.filas["sustituido"]:
                continue
            sustituto = trabajador.Trabajador(None, fila["id"])
            cursor.insertText(" ".join([sustituto.nombre(),
                                        sustituto.apellido1(),
                                        sustituto.apellido2()]))
            cursor.movePosition(QtGui.QTextCursor.NextCell)
            for fecha in self.encabezado:
                try:
                    cursor.insertText(str(fila[fecha])[0])
                    cursor.movePosition(QtGui.QTextCursor.NextCell)
                except KeyError:
                    cursor.movePosition(QtGui.QTextCursor.NextCell)
        ####
        return documento


if __name__ == '__main__':
    import connection
    if not connection.createConnection():
        import sys
        sys.exit(1)
    prueba = Cuadrante(1, QtCore.QDate(2016,4,3), QtCore.QDate(2016,5, 1))
    print(prueba.filas)
