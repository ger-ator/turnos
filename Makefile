exe:
	wine ~/.wine/drive_c/Python34/Scripts/pyinstaller.exe --onedir --windowed main.py
clean:
	rm -rf build
	rm -rf dist
	rm main.spec
