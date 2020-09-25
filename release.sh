rm dist/*
python setup.py sdist bdist_wheel
twine upload dist/*
echo "now run: git tag <python package version identifier>"
echo "git push"
echo "git push --tags"
