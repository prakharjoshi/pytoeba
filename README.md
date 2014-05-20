Pytoeba
=======

Python/Django reimplementation of tatoeba.

Dependencies
------------

See requirements.txt.

Installing Dependencies
----------

Make sure you have gcc, gfortran, python-dev, libblas-dev, liblaplack-dev,
and python-pip. Also you probably will need > 1GB RAM for compiling the
dependencies.

Then in a terminal:
  pip install -r requirements.txt

Configuration
--------------

See the https://github.com/loolmeh/pytoeba-dev repository for a fully
configured project using pytoeba.

Running
-------

In the root directory of the configured project run:

python manage.py syncdb
python manage.py migrate --fake
python manage.py runserver

It should be accessible now on 127.0.0.1:8000
