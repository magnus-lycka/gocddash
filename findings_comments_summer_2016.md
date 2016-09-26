# Findings and comments on summer 2016 increment.

Here are some notes as I have looked at changes done to gocddash in the
summer of 2016. The most important aspect of the additions to gocddash
is obviously that they work and add value. Most of the notes below point
out things that could have been made differently or that I've changed,
to make the code simpler, and easier to maintain and extend.

I suspect that the authors have thought about some of these things
already, but didn't get the time to fix it. Maybe there is still a
lesson or two to learn from these notes...

    September 2016
    Magnus Lyckå


# Code quality verification & analysis

Measuring code coverage helps understand to what extent code is getting
tested (or used at all). My initial code coverage measurements showed
about 50% code coverage, which makes it difficult to refactor the code
without adding a substantial amount of extra code. E.g. graphs, email
and claims were entirely untested.

Profiling showed that most of run time is spend waiting for two things:
  - Network queries to the go server.
  - Bokeh.

Solutions for these issues are presented below.

The _inspect code_ function in e.g. PyCharm is very helpful, and
fixing the warnings often reveal actual bugs or bugs waiting to happen,
and it certainly makes the code more consistent and easy to read.
(There are a few inspect bugs for Python 3 in PyCharm though.)

# Source code observations

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
used with pipeline config.) I droppped `create_connection` and
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

# Web application design

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
dependency, but memcached is basically no maintenance.
Just start a server. No schema to maintain. No authentication etc.

# Bokeh

Considering that Bokeh takes a lot of time, I'm considering replacing
it with a client side javascript tool, such as plotly etc. Besides
lowering load on the go-server, it could also enable features such
as zooming and panning in diagrams. (Someone likes bar charts with
500 bars in them...)
