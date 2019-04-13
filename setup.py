from setuptools import setup, find_packages

setup(
    name             = 'wecolib',
    version          = '1.0',
    description      = 'Quantitative trading tools for our economic liberty',
    author           = 'Onew',
    author_email     = 'seunghwan0216@gmail.com',
    url              = 'https://github.com/onewquant/wecolib',
    download_url     = 'https://github.com/Onewquant/wecolib/archive/master.zip',
    install_requires = ['PyAutoGUI<=0.9.39','PyQt5','SQLAlchemy','XlsxWriter','beautifulsoup4','bs4','certifi','idna','lxml','matplotlib','numpy','openpyxl','pandas<=0.22.0','pyodbc','pywin32','pywinauto','requests','scipy','seaborn','selenium','urllib3','xlrd' ],
    packages         = find_packages(exclude = ['docs', 'tests*']),
    keywords         = ['liquibase', 'db migration'],
    python_requires  = '>=3',
    package_data     =  {
        'wecolib' : [
            'configs.txt',
            'requirements.txt'
    ]},
    zip_safe=False,
    classifiers      = [
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)