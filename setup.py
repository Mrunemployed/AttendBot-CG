from setuptools import setup,find_packages
from setuptools.command.install import install
import os
import json

class setupconfig(install):

    def run(self):

        install.run(self)

        config_file = os.path.join(os.path.curdir,"config.json")

        config_content = {
            "git_repo": config_file
        }

        with open(config_file) as cfg:
            json.dump(config_content,cfg)
        
        print(f"config added at {config_file}")

setup(
    name='Attendbot',
    version='1.5',
    author='Rudradip Khan',
    description='A bot that uses Beautiful Soup along with Selenium to effortlessly put your shift claim manual attendence in the Capgemini portal',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'selenium',
        'bs4',
        'logging',
        'gitpython',
        'lxml'
    ],
    entry_points={
        'console_scripts':[
            'mark = Attendbot.mark:main'
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    scripts=['Attendbot/mark.py','Attendbot/DataIn.py'],
    # data_files=[('logs')]
    cmdclass={
        'install':setupconfig,
    },
)