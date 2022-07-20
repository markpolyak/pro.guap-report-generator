from setuptools import setup

setup(
    name='practice',
    version='0.1',
    author='V. Sokolov',
    install_requires=[
        'fastapi==0.78.0',
        'uvicorn==0.15.0',
        'redis==3.5.3',
        'pytest==7.1.2',
        'requests==2.28.1',
        'pydantic==1.9.1',
        'beautifulsoup4==4.11.1',
        'starlette==0.19.1',
        'slowapi==0.1.5'
    ],
    scripts=['app/main.py']
)
