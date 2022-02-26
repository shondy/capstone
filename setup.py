from setuptools import setup
# https://flask.palletsprojects.com/en/2.0.x/patterns/packages/

setup(
    name='capstone',
    packages=['capstone'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)