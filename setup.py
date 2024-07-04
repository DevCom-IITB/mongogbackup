from setuptools import find_packages, setup

setup(
    name = 'mongogbackup',
    packages=find_packages(include=['mongogbackup']),
    version = '0.1.0',
    description='Securely Backup MongoDB to Google Drive',
    author='DevCom, IIT Bombay',
    install_requires=[]
)


#How to create python library instruction
#https://medium.com/analytics-vidhya/how-to-create-a-python-library-7d5aea80cc3f
