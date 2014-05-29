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

```
pip install -r requirements.txt
```

Configuration
--------------

See the [pytoeba](https://github.com/loolmeh/pytoeba-dev) repository for a fully
configured project using pytoeba.

Running
-------

In the root directory of the configured project run:

```
python manage.py syncdb --migrate
python manage.py runserver
```

It should be accessible now on 127.0.0.1:8000

Tests and coverage
-------

To run the test suite:

```
py.test
```

To see the coverage report:

```
coverage run --source pytoeba -m py.test
coverage report
```

To generate an html report:

```
coverage run --source pytoeba -m py.test
coverage html
```

Then check htmlcov/index.html in your browser for a line by line
coverage report per module
