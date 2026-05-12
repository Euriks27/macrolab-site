from setuptools import setup, find_packages

setup(
    name='macrolab',
    version='7.0.0',
    description='Framework de Inteligência Macroeconômica e Risco Soberano',
    author='Éuriks Souza Davalo',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'scikit-learn',
        'matplotlib',
        'seaborn',
        'statsmodels',
        'flask',
        'requests'
    ],
    python_requires='>=3.8',
)