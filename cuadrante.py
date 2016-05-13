#!/usr/bin/python
# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui

from personal import bajas, trabajador, personal

class Cuadrante(object):
    def __init__(self, baja, inicio, final):
        mis_sustituciones = bajas.Sustituciones()        
        self.sustituido = baja.sustituido()        
        self.encabezado = [inicio.addDays(i)
                           for i in range(inicio.daysTo(final) + 1)]
        self.filas = {self.sustituido:{}}
    
        for sust in mis_sustituciones.iterable(baja):
            if sust.fecha() in self.encabezado:
                self.filas[self.sustituido][sust.fecha()] = sust.turno()
                sustituto = sust.sustituto()
                if sustituto is not None:
                    if sustituto not in self.filas:
                        self.filas[sustituto] = {}
                    self.filas[sustituto][sust.fecha()] = sust.turno()

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
            cursor.insertText(str(self.sustituido))
            cursor.movePosition(QtGui.QTextCursor.NextCell)
            for fecha in mes:
                try:
                    cursor.insertText(str(self.filas[self.sustituido][fecha])[0])
                    cursor.movePosition(QtGui.QTextCursor.NextCell)
                except KeyError:
                    cursor.movePosition(QtGui.QTextCursor.NextCell)
            ####
            ##Añadir filas de los sustitutos
            for sustituto, calendario in self.filas.items():
                if sustituto == self.sustituido:
                    continue
                cursor.insertText(str(sustituto))
                cursor.movePosition(QtGui.QTextCursor.NextCell)
                for fecha in mes:
                    try:
                        cursor.insertText(str(calendario[fecha])[0])
                        cursor.movePosition(QtGui.QTextCursor.NextCell)
                    except KeyError:
                        cursor.movePosition(QtGui.QTextCursor.NextCell)
            ####
            ##Sale de la tabla
            cursor.movePosition(QtGui.QTextCursor.NextBlock)
            cursor.insertText(" ")
            ####
        return documento

