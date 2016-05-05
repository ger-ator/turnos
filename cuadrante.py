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

        primer_dia = self.encabezado[0]
        tabla_mensual = []
        tabla_temporal = []

        for dia in self.encabezado:
            if dia.month() == primer_dia.month():
                tabla_temporal.append(dia)
            else:
                tabla_mensual.append(tabla_temporal)
                primer_dia = dia
                tabla_temporal = [dia]
        else:
            tabla_mensual.append(tabla_temporal)
            

        for mes in tabla_mensual:
            ##Insertar tabla
            tabla = cursor.insertTable(len(self.filas) + 1,
                                       len(mes) + 1)
            ####
            ##Preparar el encabezado con los dias
            cursor.insertText(mes[0].toString("MMMM-yyyy"))
            cursor.movePosition(QtGui.QTextCursor.NextCell)
            for fecha in mes:
                cursor.insertText("{0:02d}".format(fecha.day()))
                cursor.movePosition(QtGui.QTextCursor.NextCell)
            ####
            ##Añadir fila del sustituido
            sustituido = trabajador.Trabajador(None, self.filas["sustituido"]["id"])
            cursor.insertText(" ".join([sustituido.nombre(),
                                        sustituido.apellido1(),
                                        sustituido.apellido2()]))
            cursor.movePosition(QtGui.QTextCursor.NextCell)
            for fecha in mes:
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
                for fecha in mes:
                    try:
                        cursor.insertText(str(fila[fecha])[0])
                        cursor.movePosition(QtGui.QTextCursor.NextCell)
                    except KeyError:
                        cursor.movePosition(QtGui.QTextCursor.NextCell)
            ####
            ##Sale de la tabla
            cursor.movePosition(QtGui.QTextCursor.NextBlock)
            cursor.insertText(" ")
            ####
        return documento

