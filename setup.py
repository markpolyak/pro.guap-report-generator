from setuptools import setup, find_packages

setup(
    name="report_generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn[standard]",
        "python-docx",
        "pydantic",
        "python-dotenv",
        "slowapi",
        "redis",
        "pytest",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "report-generator=report_generator.main:app"
        ]
    },
)
