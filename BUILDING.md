Developer information - Building
=====================

To package python distribution and upload to test pypi from virtual environment containing wheel and twine:

    pip install -r requirements-build.txt
    rm -R build dist sas_select.egg-info
    python setup.py sdist       # only required for source distribution
    python setup.py bdist_wheel
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*.whl

To install from wheel:

    pip install sas_select-0.0.1-py3-none-any.whl

To install from test pypi:

    pip install --index-url https://test.pypi.org/simple/ sas_select==0.0.1

Developer information - Deploying
============

To deploy to Ubuntu 18.04 using Apache 2.4 and mod_wsgi

    sudo apt install libapache2-mod-wsgi-py3 virtualenv  # install ubuntu packages
    sudo useradd -m -s /bin/bash flasker                 # user which will run the process
    sudo su - flasker                                    # log in as that user for the following commands
    mkdir venvs                                          # create a place for python virtual environment
    mkdir wsgi-scripts                                   # create a place for mod_wsgi script
    virtualenv -p python3 venvs/sas-select               # create a python virtual environment
    source ~/venvs/sas-select/bin/activate               # activate the python virtual environment
    # get copy of wheel created above from dev pc
    pip install sas_select-0.0.1-py3-none-any.whl        # install sas_select web app into virtual environment 
    mkdir -p ~/venvs/sas-select/var/sas_select-instance  # create a place for database 
    # get copy of database from dev pc
    cp db_products.sqlite ~/venvs/sas-select/var/sas_select-instance/   # location of database when running
    
Create file ~flasker/wsgi-scripts/sas-select.wsgi
```
python_home = '/home/flasker/venvs/sas-select'
activate_this = python_home + '/bin/activate_this.py'
with open(activate_this) as file:
    exec(file, dict(__file__=activate_this))
from sas_select import create_app
app = create_app({'SECRET_KEY': 'my actual secret key is different'})
application = app.wsgi_app
```
Create file /etc/apache2/sites-available/sas-select.conf
```
<VirtualHost *:80>
    ServerName sas-select.triptera.com.au
    WSGIDaemonProcess sas-select.triptera.com.au user=flasker group=www-data processes=2 threads=15 python-home=/home/flasker/venvs/sas-select
    WSGIScriptAlias / /home/flasker/wsgi-scripts/sas-select.wsgi
    <Directory /home/flasker/wsgi-scripts>
        Require all granted
    </Directory>
    ErrorLog ${APACHE_LOG_DIR}/error_sas_select.log
    CustomLog ${APACHE_LOG_DIR}/access_sas_select.log combined
    LogLevel info
    LimitRequestBody 1048576
</VirtualHost>
```
Tell apache web server to use new configuration

    sudo a2ensite sas-select.conf  # enable the new site configuration
    sudo apachectl configtest      # test you typed it in correctly
    sudo systemctl reload apache2  # use new configuration


