clean:
	python3 -c "import pathlib; [p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]"
	python3 -c "import pathlib; import shutil; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('__pycache__')]"
	python3 -c "import pathlib; import shutil; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('.pytest_cache')]"
	python3 -c "import pathlib; import shutil; [shutil.rmtree(p, ignore_errors=True) for p in pathlib.Path('.').rglob('tmp')]"
