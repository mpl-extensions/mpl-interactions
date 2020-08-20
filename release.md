Because I always forget how to do this:

1. remove the `dev` in `_version.py`
2.
```bash
rm dist/*
python setup.py sdist bdist_wheel
twine upload dist/*
```
3. bump version to next `dev` version in `_version.py`