# Findings and comments on summer 2016 increment.

Here are some notes as I have looked at (and worked with)
additions done to gocddash in the summer of 2016.

The most important aspect of the additions to gocddash is
obviously that they do work and add value. Both of those
conditions are true!

Most of the notes below point out things that could have been
made differently or that I've changed,
to make the code simpler, and easier to maintain and extend.

I suspect that the authors have thought about a lot of these things
already, but didn't get the time to fix it. Maybe there is still a
lesson or two to learn from these notes...

Parts of it was written when I was somewhat grumpy, so if
you have an asbestos suit, you might want to wear that. ;-)



    September 2016
    Magnus Lyckå


# Code quality verification & analysis

Measuring code coverage helps understand to what extent code is getting
tested (or used at all). My initial code coverage measurements showed
about 50% code coverage, which makes it difficult to refactor the code
without adding a substantial amount of extra code. E.g. graphs, email
and claims were untested.

Profiling showed that most of run time is spend waiting for two things:
  - Network queries to the go server.
  - Bokeh.

Solutions for these issues are presented below.

The _inspect code_ function in e.g. PyCharm is very helpful, and
fixing the warnings often reveal actual bugs or bugs waiting to happen,
and it certainly makes the code more consistent and easy to read.
(There are a few inspect bugs for Python 3 in PyCharm though.)


# Source code observations


## Sloppy coding & testing...

Some code was clearly not tested. For instance, running `info` in
the cli tool without stating a pipeline, caused a call of a method
in the data_access module which didn't exist. (Maybe you renamed
a method and didn't have tests...)

    AttributeError: 'SQLConnection' object has no attribute 'get_synced_pipelines'

It's really simple to write generic code in Python, and I think some
of the mistakes in the code was partly due to a lack of understanding
for this. There are many more paths through the program than needed,
presumably because the programmers haven't seen the simple Pythonic
way of writing more generic code.

Also, some diagnostic messages didn't match behaviour:

    2016-10-07 14:48:59.546286 Will synchronize [...] from 39 onwards.
    Requested pipelines = 10 (from 39 to 49)
    Pipeline counter: 39
    Pipeline counter: 38
    [...]
    Pipeline counter: 31
    Pipeline counter: 30


## Global Variables

Don't use global variables, and be very careful when
messing with module global state. I'm sure there are
other programming languages where it's very nifty to
like this, but modules with global variables and
functions are *not* like classes with members and
methods in Python. As a concrete example, there were
unit tests that replaced global objects in modules
with mocks, and didn't clean up after themselves.
This caused spurious errors in completely different
unit tests which used the same modules when using
`python3 -m unittest` to run the tests.

More examples below in the sections about database
code and OOP.


## Connascence

There is a lot of _Connascence of Position_ in the code.
For instance, the functions returning data from an SQL
SELECT statement typically return a tuple, or a list of
tuples, often even the result of a `SELECT * FROM ...`,
which means that A) it's difficult to change the data
model without breaking code, and B) it's time consuming
and error prone to maintain the code, since you might
need to go from a function call you analyse, to the
data_access DB function, to a CREATE VIEW statement, to
a CREATE TABLE statement, to understand what it is you
get back from your function call.

Don't use `SELECT * FROM ...` in production code, and
prefer a row factory etc, which gives you the ability
to access columns by name. E.g. use something like
`conn.cursor(cursor_factory=psycopg2.extras.DictCursor)`
with psycopg2, or `conn.row_factory = sqlite3.Row` with
sqlite3.

For non-SQL code, prefer e.g. instances of a class,
namedtuple, dict and named arguments to tuples and
positional arguments.

__Favour locality!__
The maintenance cost of e.g. _Connascence of Position_
depends a lot on locality. It's no big deal to call a
method with five arguments if it's defined five rows
below in the code.


## Structural confusion

Parts of the code is really much more complex that the actual
problem warrants. There are implicit assumptions which should
be clearly declared once, which are instead assumed in several
different modules. E.g. the idea that we fetch data in chunks
of 10 when we sync pipelines is implicit in at least three
modules, which makes is difficult to change this chunk size.

Another example of structural confusion is the `synchronize()`
function in the `gocddash_sync` script. It's obviously good
that it abstracts away some things, and that e.g. the network
calls to the Go server and the database interactions are
abstracted away, but that's about how much abstraction you
need in this case.

The way it's done, the bulk of the code is in
`analysis.pipeline_fetcher`, but the `gocddash_sync` script
only interacts with it through a thin wrapper in the
`analysis.actions` module. On the other side of
`analysis.pipeline_fetcher`, `analysis.domain` is used as
an abstraction layer over `analysis.data_acces`, which in
turn is an abstraction layer over the SQL database.

This kinds of layered architecture, but typically three
layers rather than five, was popular in large projects in
the 1990's, before agile methodologies and test driven
development became popular. The plan was to isolate the
details in the different layers from each other, so that
they could be developed independently without creating a
mess when several dozen developers were developing the
same application. It's debatable whether this is a good
idea at all, and it's certainly overkill in this case.
It's not consistently used here anyway. For instance, the
`gocddash_sync` script makes calls directly to the bottom
`analysis.data_acces` layer, completely short-circuiting
the layered approach.

Someone once said that there is no problem you can't solve by
adding another layer of abstraction except the problem of having
too many layers of abstraction. I'd say we ran into this problem
here...

First of all, we don't need all the layers of abstraction seen
here. It's a bit as if you've thought
_"hey, let's add another module"_,
when you ought to have thought
_"is there a simpler way of solving this problem?"_

One reason for structural confusion could be collaboration
problems. It might be easier to  add or change in "my module"
even if I know it really belongs in "his module". The way to
get around this is to integrate continuously. Work with small
chunks in the same branch (preferably master) and make sure
to push well tested code after each little chunk, and to pull
the collaborators changes as soon as they pushed.

I also think the solutions would have been simpler if there had
been more of object-oriented design.
Classes and instances are good at organizing data and operations
on that data in a good way if done right.
I didn't really appreciate the inter-modular roller coaster I
had to go through to follow some of the code flow...

If we use an approach of abstractions / layers, it's important
to understand what belongs where, and how we actually add entropy
to code.

For instance, text strings should typically be created
close to where they are displayed in the code structure. Data
passed between layers is better passed as data structures with
descriptively labeled pristine values.
See Connascense of Position above. If it seems important to declare
string formatting where the data is constructed rather than
consumed, use classes and the `__str__` method, instead of just
passing a string. Another day someone who uses the function
wants to use that number you embedded in the string...


## Dead code

There were a number of functions and code sections that only returned
an empty string, or never got any value (e.g. finished_pipelines).
Work in progress adds no value, but does add a significant cost in
maintenance and for understanding the code.

Please refrain from adding any code which "might come in handy
later", and make sure to do one thing at a time, and only that
thing until that thing works.
If code falls out of use, remove it entirely, even if you might
want it again later. It's in the git history...


## Explicit call of superclass methods

Use super(), e.g. `super().__init__(args)` to call `__init__` of
appropriate parent class. E.g:

    class TestFailure(StageFailure):
        def __init__(self, stage, failure_signature, test_names):
            super().__init__(stage)
            ...

instead of

    class TestFailure(StageFailure):
        def __init__(self, stage, failure_signature, test_names):
            StageFailure.__init__(self, stage)
            ...

A common motivation for super is to get correct method resolution
order in case of multiple inheritance, but as I see it, the main
advantage, besides being less cluttered, is that it reduces the
risk of mistakes as the code evolves and we change the inheritance
structure or copy and paste code.


## Database code details

A cursor *must* not be used beyond a single database transaction.
(Marc-André Lemburg, author of PEP 249, the DB-API 2.0 spec, was very
clear about this when he commented my "Database Programming with
Python" tutorial at EuroPython 2004...) Behaviour is undefined.
This might have caused the odd bug you saw with psycopg2 queries.

Why the explicit `create_connection` followed by `get_connection`
and a global connection object? (Same pattern is
used with pipeline config.) I dropped `create_connection` and
the global object, and made `SQLConnection` a Borg. That reduces
`get_connection()` to just `return SQLConnection()`.


## Object-oriented programming

There seems to be a reluctance to use objects and methods
implemented in other modules. E.g. the go_client module has two
classes with the same interface, and then the same interface is
repeated in it's entirety as functions, instead of simply using
a factory function which returned an instance of the appropriate
variant of the interface.

There are a number of classes which are just used as plain C
structs (e.g. in `analysis.domain`).
They have an `__init__` method which simply sets members, and basically
no more methods; but instead module global functions using these
objects as values. Having methods on classes is not a bad idea,
but if a non-OO approach is preferred, there are better containers
in the Python 3 library than anorectic classes.
`collections.namedtuple` for instance.

One important aspect of this is that the life cycles for
instances and modules are completely different in Python.
When you create an object, you get an new instance, which is
not shared outside your control, and is garbage collected
when there are no more references to it. An imported module
stays alive during the whole execution of the process, and
its state is shared.


## Parsing through splitting

There is a lot of this kind of stuff:
    some_log = some_log.split('Some peculiar text')[1]
    some_log = some_log.split('Some other interesting text')[0]
    ...

This is not a very robust way of parsing text files. The errors
we'll get when the file doesn't look like we expected will give
the impression that there is a bug in the code rather than something
wrong with the file, and I kind of agree... ;-)

I know regular expressions aren't a lot of fun, but I still think
they'd be a better fit here. You'd end up with not getting the
data you expected when the file is broken, and acting based on
that, rather than getting an unexpected IndexError all of a sudden.

A maybe better option could be <https://pypi.python.org/pypi/parse>


## Import hacking

    sys.path.append(str(Path(abspath(getsourcefile(lambda: 0))).parents[1]))

It's probably better to install the package in the `virtualenv` with
setup.py, or possibly to set `PYTHONPATH` in advance of running the
program.


## Error handling

`except Exception as error` Ouch! In Python this means that we
e.g. catch `NameError` and `AttributeError`, which are almost
certainly programming errors!


# Flask & Web application design


## Blueprints

`Flask Blueprints` are a good way of partitioning `Flask` apps.
It might be better to e.g. have the `insights` and `graph`
parts of `app.py` as separate `Blueprints`, or in a common
`pipeline` `Blueprint`.


## URLs and business modeling

Related to _data modeling_ mentioned below, it might be better to
have URLs focused on the central resources. E.g.
`http://go/dash/pipelines/old-system-tests/insights`
instead of `http://go/dash/insights/old-system-tests`,
`http://go/dash/pipelines/old-system-tests/graphs`
instead of `http://go/dash/graphs/old-system-tests`, and
`http://go/dash/pipelines/old-system-tests/counter/123/claim`
instead of `http://go/dash/claim` and all substance in the
POST data.
The web server logs are certainly more useful with more
explicit URLs, and I think testing gets easier too.


## Flask decorators

Decorators such as `@app.before_first_request` helps you
run things at the right time, without having to run them
when the module is imported (which might cause a mess for
testing etc).


# Persistence & caching solution


## Data modeling

We can certainly model our business objects in different ways, and there
is no strict right and wrong, but depending on how we twist and turn
things, we might turn out with solutions that are fairly straight forward,
or very complex, to use. Concretely:
* Is a `claim` best modeled as an enity which has a `pipeline instance`
  as a property, or as a couple of properties of a `pipeline instance`?
* Is a `final stage` an entity, or is it simply a property of a `stage`.

I think five or so of the database tables are better modeled as
additional columns in the `pipeline_instance` or `stage` tables.

If I use an RDBMS for persistence or objects in an object oriented
application, I'd certainly use abstract keys, but in the current
situation, where the natural keys are derived from the go-server
REST API, why not simply use these? In this case, abstract keys
just seem like an awkward detour which forces us to join table
much more than we really need.

I haven't fully gotten my head around the views yet, but it seems
to me that you're using the database for some things that might
be easier and quicker to do in Python, particularly with your
overly complex data model and lack of indices.


## Choice of technical solutions

We use the database for two simple tasks:
 * Caching some things we learn from the go server REST API.
 * Bookkeeping of small amounts of non-critical data:
   - claims: name and comment
   - whether email has been sent

Using a full blown SQL server, such as PostgreSQL for this seems
like overkill. Adding a migration tool (yoyo) to the mix when
there are no requirements on persistence also seems extravagant.

As a start, I'm ditching PostgreSQL and yoyo, and replacing psycopg2
with the builtin sqlite3 module, which is sufficient for this task.
This way, we drop 3rd party dependencies (docker-py as well) and
remove configuration work.

I'm also adding memcached through `werkzeug.contrib.cache.MemcachedCache`,
to cache all network calls to the go-server
(in `go_client.GoSource.base_request`). This does add an extra
dependency, but memcached is basically no maintenance:
Just start a server. No schema to maintain. No authentication etc.


# Bokeh

Considering that Bokeh takes a lot of time, (both CPU time and
network time) I'm considering replacing
it with a client side javascript tool, such as plotly etc. Besides
lowering load on the go-server, it could also enable features such
as zooming and panning in diagrams. (Someone likes bar charts with
500 bars in them...)

UPDATE: I replaced Bokeh with plotly.js. This reduced both
installation time (no numpy, pandas or bokeh) and runtime
(both server side CPU time, network transfering 2 MB png
and client side rendering time) a lot, and allowed for zooming
and panning etc in the chart.

