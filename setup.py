from setuptools import setup,find_packages
from setuptools.command.install import install
import os
import json

class setupconfig(install):

    def run(self):
        install.run(self)
        self.create_cnf_file()
        # self.create_dependencies()

    def create_cnf_file(self):
        git_path = os.path.join(os.path.abspath(os.path.curdir))
        cnf_dir = os.path.join(self.install_lib, "Attendbot")
        if "config.json" in os.listdir(cnf_dir):
            pass
        else:
            config_file = os.path.join(self.install_lib, "Attendbot", "config.json")
            config_content = dict()
            config_content['git_repo'] = git_path

            with open(config_file, 'w') as cfg:
                json.dump(config_content,cfg)
                cfg.close()


setup(
    name='Attendbot',
    version='2.0',
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