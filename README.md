Pytoeba
=======

Python/Django reimplementation of tatoeba.

Dependencies
------------

See requirements.txt.

Installing Dependencies
----------

You can choose your graphing backend to either be pure python (networkx)
or C (scipy). The python backend should work readily with any flavor of
python. The C one might not but is insanely fast on CPython. To install
the C backend make sure you have gcc, gfortran, python-dev, libblas-dev,
liblaplack-dev, and python-pip. Also you probably will need > 1GB RAM for
compiling the dependencies.

You can also choose and configure a search engine backend for haystack.
Consult [haystack's docs](http://django-haystack.readthedocs.org/en/latest/tutorial.html#configuration) for more information.
The template project provides a configuration for xapian. The dependencies
is basically the header files libxapian-dev and the python bindings
python-xapian. To install it inside a virtualenv install libxapian-dev
on your system and then run the provided xapianvenv.sh script from within
the virtualenv.

Then in a terminal:

```
pip install -r requirements.txt
```

For the graphing backend:

```
pip install -r scipy\_backend\_requirements.txt
```

or

```
pip install -r networkx\_backend\_requirements.txt
```

For the xapian search backend:

```
pip install -r xapian\_backend\_requirements.txt
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
