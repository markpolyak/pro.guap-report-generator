from setuptools import setup, find_packages

setup(
    name='app-example',
    version='0.0.1',
    author='Michael S',
    author_email='orenconbrio@gmail.com',
    description='FastAPI app',
    packages=find_packages(),
    install_requires=[
        'fastapi==0.78.0',
        'uvicorn==0.18.2',
        'pydantic==1.9.1',
        'aioredis==1.3.1',
        'docx==0.2.4',
        'fastapi-limiter==0.1.4',
        'starlette~=0.19.1',
        'python-docx~=0.8.11',
        'lxml~=4.9.1',
        'document~=1.0',
        'pip~=22.1.2',
        'wheel~=0.37.1',
        'Pillow~=9.2.0',
        'setuptools~=60.2.0',
    ],
    scipts=['main.py']
)