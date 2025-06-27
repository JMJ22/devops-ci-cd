from setuptools import setup, find_packages

setup(
    name="meuprojeto",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # coloque suas dependências aqui, exemplo:
        # "requests>=2.0"
    ],
    entry_points={
        'console_scripts': [
            # exemplo: 'meuprojeto=meuprojeto.__main__:main'
        ],
    },
)
