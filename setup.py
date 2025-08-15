from setuptools import setup

setup(
    name='DailyTodoApp',
    version='1.0',
    py_modules=['app'],
    install_requires=[
        'flask',
        'pyinstaller'
    ],
)