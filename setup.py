from setuptools import setup,find_packages

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
)