all: anadir_ui.py asignar_ui.py mainwindow_ui.py baja_ui.py personal_ui.py
personal_ui.py : personal.ui
	pyuic5 personal.ui -o personal_ui.py
anadir_ui.py : anadir.ui
	pyuic5 anadir.ui -o anadir_ui.py
asignar_ui.py : asignar.ui
	pyuic5 asignar.ui -o asignar_ui.py
mainwindow_ui.py : mainwindow.ui
	pyuic5 mainwindow.ui -o mainwindow_ui.py
baja_ui.py : baja.ui
	pyuic5 baja.ui -o baja_ui.py
clean:
	rm *_ui.py
