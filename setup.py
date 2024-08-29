from setuptools import setup,find_packages
from setuptools.command.install import install
import os
import json

class setupconfig(install):

    def run(self):
        install.run(self)
        self.create_cnf_file()
        self.create_dependencies()

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

    def create_dependencies(self):
        flag = False

        path = os.path.join(self.install_lib, "Attendbot")
        logs_dir = os.path.join(path,"logs")
        if not os.path.exists(logs_dir):
            os.mkdir(logs_dir)
            flag = True
        print("\033[32m Find logs at:",logs_dir,"\033[37m")

        current_attendance = os.path.join(path,"current_attendance")
        if not os.path.exists(current_attendance):
            os.mkdir(current_attendance)
            flag = True
        # print("Find attendance reports at:",current_attendance)

        completed = os.path.join(path,"completed")
        if not os.path.exists(current_attendance):
            os.mkdir(current_attendance)
            flag = True
        print("\033[36m Find attendance reports at:",completed,"\033[37m \n")

        if flag:
            config_file = os.path.join(self.install_lib, "Attendbot", "config.json")
            with open(config_file, 'r+') as cfg:
                config_content = json.load(cfg)
                config_content['completed'] = completed
                config_content['logs_dir'] = logs_dir
                config_content['current_attendance'] = current_attendance
                json.dump(config_content,cfg)
        else:
            pass

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