exe:
	wine ~/.wine/drive_c/Python34/Scripts/pyinstaller.exe --onefile --windowed main.py
clean:
	rm -rf build
	rm -rf dist
