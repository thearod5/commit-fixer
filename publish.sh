mypy && pytest && echo "Tests Are Passing!" && python3 -m build && python3 -m twine upload --repository pypi dist/* && rm -rf dist