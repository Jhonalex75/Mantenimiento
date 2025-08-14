from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mantenimiento",
    version="0.1.0",
    author="Jhonalex75",
    author_email="tu@email.com",
    description="Sistema de Gestión de Mantenimiento",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Jhonalex75/mantenimiento",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={
        "mantenimiento": ["templates/*", "static/*"],
    },
    install_requires=[
        'Flask>=2.0.1',
        'python-dotenv>=0.19.0',
        'Werkzeug>=2.0.1',
        'pandas>=1.3.0',
    ],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'mantenimiento=mantenimiento.__main__:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
