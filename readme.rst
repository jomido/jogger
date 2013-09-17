.. raw:: html

   <divstyle="float: right;">

.. raw:: html

   </div>

**0.1.1** [*16 Sep 2013*\ ]

Jog, don't slog. Slogging through disparate logs gets tedious. jogger
provides a common API to navigate through different logs. It's an
experiment. I use it.

A Snapshot
----------

.. code:: python

    >>> from jogger import jog
    >>> log = jog('my.log')
    >>> log
    <Log: 1000 lines>

    >>> log.attributes
    ['timestamp', 'level', 'msg']

    >>> log.level()
    ['ERROR', 'INFO', 'DEBUG']

    >>> error_log = log.level('ERROR')
    <Log: 3 lines>

    >>> debug_log = log.level('INFO', 'DEBUG')
    <Log: 997 lines>

But of course there's more.

Installing It
-------------

There's no pip (or PyPI) support yet, but that's in the works. You can
download source and do:

::

    > python setup.py install

In a Nutshell
-------------

Originally designed for exploring JSON logs, jogger is suitable for any
kind of log. Exploring == navigating, filtering, and aggregating,
whether that be via a REPL (human-centric) or a program
(machine-centric).

Unstructured vs. Partly Structured vs. Structured Logs
------------------------------------------------------

When it comes to logging there are three ways of doing it: unstructured,
structured, and everything inbetween.

This is a completely unstructured log line:

::

    Oh, damn, this CrazyException should not have happened.

The nice thing about this log line is that it's easy to read. For a
human. It's also easy to code: you just fire off a print with whatever
message you like. Most logging facilities attempt to minimize this kind
of log line. They enforce some kind of convention, i.e. a bit more
structure.

A partly structured log line:

::

    2013-08-15 00:12:43-0400 my_file.py Oh, damn, this CrazyException should not have happened.

This is still easy to read. For a human. A machine could parse this
easier than the first example, but there's still information hiding in
there that will be hard for it to get at.

A completely structured log line:

::

    {"timestamp": "2013-08-15 00:12:43-0400", "file": "foo.py", "exception": "CrazyException", msg": "Oh, damn, this CrazyException should not have happened."}

This is easy to read. For a machine. All the information is readily
parseable and is not hiding anywhere. For a human, though, this is
awful.

It is easier to move data from a structured format to an unstructured
format than it is to do the reverse. I could probably tie this to
entropy, and give you a proof, but I'm neither smart nor inclined
enough. Knowing this fact, however, and promising yourself forever and
ever to only log structured data does not change these other facts:

1. there are old logs that are unstructured, partly or in whole
2. there are other programmers who have different views than you

   a. and you have to deal with this civilly

3. there are paths of least resistance - existing logging tools that do
   not emit fully structured data
4. there are fractured log formats - all the tools emit something
   different
5. you use print statements/calls at least once in blue moon, and even
   forget to remove them
6. you're lazy

Some reading:

-  `+1 for structured
   logging <http://gregoryszorc.com/blog/2012/12/06/thoughts-on-logging---part-1---structured-logging/>`__
-  `-1 for structured
   logging <http://carolina.mff.cuni.cz/~trmac/blog/2011/structured-logging/>`__

Disparate ways of logging are here to stay. Some people will dump
structured data, others unstructured, and others a mixture of both.
Sometimes the logs are in a database, and sometimes they're in plain
files.

Jogging: What Is It?
--------------------

Jogging is just getting data bundled up into a nice, common API, as
shown in "Snapshot" above.

To achieve this, jogger follows these steps, each with an appropriate
hook:

    | read
    | chunk
    | parse
    | bunch
    | inspect
    | patch

By specifying code for zero or more of those, jogger builds you a custom
jogger object to jog your data with. These build steps are there for
transforming data, so here's a data-centric view of them:

    | *step : data*
    | read : return a blob
    | chunk : accept a blob and return an iterable of smaller blobs (log
    lines)
    | parse : accept an iterable of blobs and return an iterable of
    Python dictionaries
    | bunch : accept an iterable of Python dictionaries and return an
    iterable of Line instances
    | inspect : --
    | patch : accept an iterable of Line instances and log mixins and
    return a Log instance

Each operation passes what it gets to the next operation below, with the
exception of inspect. The inspect and patch operations are what give you
back a nice API.

These operations exist for the crudest case: unstructured text.
Sometimes logs are stored in databases where the data is already chunked
(rows from a SQL db), or maybe already parsed (documents from a NoSQL
db). In these cases the irrelevant build operations can be skipped.

A JSON Example
~~~~~~~~~~~~~~

JSON logs are the easiest to jog, because you don't have to provide any
code to get started. Just grab the default jog method, which is both
JSON and line-based:

.. code:: python

    >>> from jogger import jog

Here is the contents of a line-based JSON log (test.log):

.. code:: javascript

    {"line": 11, "file": "foo.py", "msg": "Hello"}
    {"line": 11, "file": "bar.py", "msg": "World"}
    This is an errant print statement, an unstructured (bad) log line entry

    Here's another plain text one, preceded by a blank line
    {"line": 12, "file": "bar.py", "msg": "Pizza", "tags": ["food"]}
    {"line": 13, "file": "bar.py", "msg": "Avocado", "tags": ["food"]}
    {"line": 14, "file": "bar.py", "msg": "Cheese", "tags": ["food"]}
    {"line": 15, "file": "bar.py", "msg": "Whiskey", "tags": ["drink"]}
    {"line": 11, "file": "foo.py", "msg": "Hello"}
    {"line": 11, "file": "bar.py", "msg": "World"}
    {"line": 22, "file": "foo.py", "msg": "Liver", "tags": ["warn", "food"]}
    {"line": 43, "file": "bar.py", "msg": "Onions", "tags": ["err", "food"]}
    {"line": "woops","file": "foo.py", "msg": "Bazinga"}
    {"msg": "All is well."}

It's kind of a mess.

Here is what you can do with it when you jog it from the REPL:

.. code:: python

    >>> log = jog('test.log')
    >>> log
    <Log: 14 lines>

    # it's an iterable
    >>> log[0]
    <jogger.Line object at 0x000000000263DDD8>

    # see all of the attributes (keys) for the lines in the log:
    >>> log.attributes
    >>> ['file', 'line', 'msg', 'tags', 'unparsed']

A key thing to note here is that *every* log line now has all of these
attributes, even if that log line did not originally specify it. For
instance, the last log line only defined a "msg" key. When we inspect
it, however, it will not only have a "msg" attribute, but also all of
the attributes specified by any other log line in the entire log.

    *jogger homogenizes all the log lines in a given log*

In the case where a log line is given attributes that it originally did
not have, jogger attempts to infer a default value.

.. code:: python

    >>> log[-1].file
    ''

Since all of the "file" keys in the log lines were strings, the default
value for the "file" attribute is a call to str(), which produces ''.
Similarly for tags, all of the values were lists, so:

.. code:: python

    >>> log[-1].tags
    []

Sometimes jogger can't infer a default value because a key contains more
than one type of value across all the log lines. The second last log
line has a string ("woops") for its "line" key, whereas all other log
lines that specify the same key have an integer.

.. code:: python

    >>> log[-1].line
    <class 'jogger.NoValue'>

    >>> bool(log[-1].line)
    False

If jogger can't infer a default value, it will insert a special
placeholder value: jogger.NoValue. This is an empty class that is
false-y.

You can override these default values by supplying your own Log
definition. The default Log definition is just this!:

.. code:: python

    class Log(object): pass

If you want to specify a default value for the "line" key, you can do so
by setting a class attribute for that key on your own Log definition:

.. code:: python

    class Log(object):

        line = 0

Then create a new jogger with jogger.Jogger:

.. code:: python

    >>> from jogger import Jogger
    >>> jogger = Jogger(log=Log)
    >>> log = jogger.jog('test.log')
    >>> log[-1].line
    0

When you create this log it will be an instance of the custom Log class
that you passed in to Jogger. It will also be an instance of
jogger.APIMixin, granting it other capabilities. Let's look at what some
of those are.

Attribute Methods (or Key Methods, Column Methods, Field Methods, etc.)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each key in all the log lines of your log has become a method on the log
object. Calling such a method without arguments returns all the possible
values in the log for that attribute as an iterable. Using "file" as an
example:

.. code:: python

    >>> log.file()
    ['', 'bar.py', 'foo.py']

This returns a list of all the possible values for "file" in all the log
lines.

Sometimes a *machine* might not know which attributes are available
until it inspects them. As a shortcut, the machine can access the
attributes of log lines by specifying a string key on the log object,
dictionary-style:

.. code:: python

    >>> log['file']()
    ['', 'bar.py', 'foo.py']

    >>> log['file'] == log.file
    True

Querying with Attribute Methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's get all the log lines that come from bar.py:

.. code:: python

    >>> log.file('bar.py')
    <Log: 7 lines>

Calling the "file" attribute method with arguments returns a new log
object with the relevant lines. Querying a log in any fashion returns a
new log. This is handy because:

-  the object returned from a query has the same API, making queries
   chainable
-  subsets of logs are easily created, passed around, combined, and
   compared

Here's all the log lines from line 11 of bar.py:

.. code:: python

    >>> log.file('bar.py').line(11)
    <Log: 2 lines>

Each attribute method call can accept 0 or more arguments. Here's all
the log lines that come from either foo.py or bar.py:

.. code:: python

    >>> log.file('bar.py', 'foo.py')
    <Log: 11 lines>

However, we know there are more lines than that:

.. code:: python

    >>> log
    <Log: 14 lines>

There's three missing. What other ones were there again?:

.. code:: python

    >>> log.file()
    ['', 'bar.py', 'foo.py']

Oh, some are empty.

.. code:: python

    >>> log.file('')
    <Log: 3 lines>

There they are. Another way to get at those three missing lines is this:

.. code:: python

    >>> log.file.none('foo.py', 'bar.py')
    <Log: 3 lines>

Each attribute method call can also be dot-suffixed with a mode. Here's
what each means:

-  any: get the log lines where any of the arguments equal the
   attribute, if the attribute is a single value (a scalar). If the
   attribute is an iterable (a vector), get the log lines where any of
   the arguments are in the attribute.

-  none: get the log lines where none of the arguments equal the scalar
   attribute. Get the log lines where none of the arguments are in the
   vector attribute.

-  all: get the log lines where all of the arguments are in the vector
   attribute.

-  only: get the log lines where all of the arguments are in the vector
   attribute, and the vector attribute *only* has those arguments.

The last two modes only make sense for attributes that are iterables (or
vectors). The "tags" key in test.log is an iterable (a list):

.. code:: python

    >>> log.tags()
    ['drink', 'err', 'food', 'warn']

    >>> log.tags('food')
    <Log: 5 lines>
    >>> log.tags('food', 'drink')
    <Log: 6 lines>

    >>> log.tags.all('food', 'warn')
    <Log: 1 lines>
    >>> log.tags.none('food', 'warn')
    <Log: 9 lines>
    >>> log.tags.only('food', 'warn')
    <Log: 1 lines>
    >>> log.tags.any('food', 'warn')
    <Log: 5 lines>

That is a *human-friendly* way to query the log. A machine might only
know attribute names and modes as strings. Let's be kind to machines
(these are equivalent to the previous four):

.. code:: python

    >>> log['tags']('food', 'warn', mode='all')
    >>> log['tags']('food', 'warn', mode='none')
    >>> log['tags']('food', 'warn', mode='only')
    >>> log['tags']('food', 'warn', mode='any')

Querying with Types, Functions, and Regexes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The searching shown so far has used values. But you can also use types,
functions, and regexes (in any combination) for searching.

Querying with Types
^^^^^^^^^^^^^^^^^^^

Get all the log lines where the "line" key was an integer:

.. code:: python

    >>> log.line(int)
    <Log: 10 lines>

Oh, four missing. What was the value "line" in those, then?

.. code:: python

    >>> log.line.none(int)
    <Log: 4 lines>

    >>> log.line.none(int).line()
    [<class 'jogger.NoValue'>, u'woops']

The four that had non-integer line numbers had NoValue and 'woops'
instead. Which one's had 'woops'?

.. code:: python

    >>> log.line(str)
    <Log: 1 lines>

Querying with Functions
^^^^^^^^^^^^^^^^^^^^^^^

You can use functions for querying too. These must be predicates
(functions that return a truth-y or false-y value). They accept the
attribute you're querying for as a single parameter. Here's all the log
lines that had the letter "l" in the "msg" key:

.. code:: python

    >>> log.msg(lambda msg: 'l' in msg)
    <Log: 5 lines>

So what were those messages?:

.. code:: python

    >>> log.msg(lambda msg: 'l' in msg).msg()
    ['All is well.', 'Hello', 'World']

Querying with Regexes
^^^^^^^^^^^^^^^^^^^^^

You can use compiled regexes to search as well:

.. code:: python

    >>> import re
    >>> r1 = re.compile('f')
    >>> log.file(r1)
    <Log: 4 lines>

    >>> r2 = re.compile('b')
    >>> log.file(r, r2)
    <Log: 11 lines>

Querying via Calling the Log Instance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A different way to query is by calling a log instance with arguments. A
log instance will accept keyword arguments mapping to the attributes of
your log lines, as well as dictionaries and lambdas.

Calling with No Arguments (Copying)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To get a copy of the current log, you can just call the log with no
arguments:

.. code:: python

    >>> log2 = log()
    >>> log2
    <Log: 14 lines>

    >>> log2 == log
    True

    >>> log2 is log
    False

Calling with Keywords
^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    >>> log(file='foo.py')
    <Log: 4 lines>

    >>> log(file=lambda file: file == 'foo.py')
    <Log: 4 lines>

    >>> log(file=str)
    <Log: 14 lines>

    >>> log(file=re.compile('f'))
    <Log: 4 lines>

Calling with Dictionaries
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    >>> log({'tags': 'food', 'line': int})
    <Log: 5 lines>

These dictionary support "notting" the keywords by prefixing them with a
"~". To get all the log lines that did not have "food" as a tag, but
whose "line" key was an integer:

.. code:: python

    >>> log({'~tags': 'food', 'line': int})
    <Log: 5 lines>

For dictionary searching, all of the items specified must be True for a
log line to match (i.e. dictionary searching is ANDy in nature). The
dictionary is a specification to which the log line must conform.

You can use types, predicate functions, and compiled regexes in
dictionary searches:

.. code:: python

    >>> log({
    ...   'tags': lambda tags: 'food' in tags or 'warn' in tags
    ...   'line': int,
    ...   'file': re.compile('b')
    ... })
    <Log: 5 lines>

Calling with Predicate Function
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can pass a predicate function to a log. The predicate accepts a line
as a single argument:

.. code:: python

    >>> log(lambda line: line.file == 'foo.py')
    <Log: 4 lines>

You can pass as many dictionaries and predicate functions to log() as
you like:

.. code:: python

    log({'tags': 'food'}, {'tags': 'warn'})
    <Log: 1 lines>

    >>> log({'tags': 'food'}, lambda line: line.line == 12)
    <Log: 1 lines>

Adding and Subtracting Logs
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can add, subtract, and equate logs:

.. code:: python

    >>> log
    <Log: 14 lines>

    # get all the log lines from foo.py and bar.py
    >>> log2 = log.file('foo.py', 'bar.py')
    >>> log2
    >>> <Log: 11 lines>

    # get another log that is the initial log minus all the log lines from
    # foo.py and bar.py
    >>> log3 = log - log2
    >>> log3
    <Log: 3 lines>

    # or more succinctly
    >>> log - log.file('foo.py', 'bar.py')
    <Log: 3 lines>

    >>> log2 + log3
    <Log: 14 lines>

    >>> log2 + log3 == log
    True

Dealing with Unstructured Data
------------------------------

The real world is hardly structured. There are lots of logs out there
with no structure. Sometimes you have to abide by conventions. Sometimes
there is inertia or paths of least resistance.

Let's suppose that your logs are *mostly* JSON, but they are prefixed
with a timestamp that you need to parse out first. They look like this:

::

    ...
    2013-08-15 00:12:43-0400 {"line": 11, "file": "foo.py", "msg": "Hello"}
    ...

You want to put that timestamp into a 'date' key for each log line. To
create a custom jog method that can do this we just need to override the
parse step. The parse step is where you turn an iterable of blobs (log
lines) into an iterable of dictionaries. Let's do that:

.. code:: python

    def parser(chunks):

        dictionaries = []

        for chunk in chunks:

            try:
                parts = chunk.split('{')
                json_data = '{' + '{'.join(parts[1:])
                d = JSON.loads(json_data)
                d['date'] = parts[0].strip()
                dictionaries.append(d)
            except Exception as ex:
                dictionaries.append({
                    'unparsed': chunk
                })

        return dictionaries

To create the jogger, use the Jogger class:

.. code:: python

    from jogger import Jogger
    jogger = Jogger(parser=parser).jog
    log = jog('my.log')

If you want to see log lines that were unparse-able:

.. code:: python

    unparsed = log(unparsed=str)

To check if there were any unparsed lines at all:

.. code:: python

    were_there_unparsed_lines = 'unparsed' in log.attributes

If that's False then there were no log lines that had an 'unparsed' key.

Homogeneity
~~~~~~~~~~~

Jogger homogenizes all the log lines so that they all have the same set
of keys/attributes. It will attempt to infer a default value if you
didn't explicitly offer one. If it can't infer a default then a key will
be given the special value jogger.NoValue (an empty class).

To provide default values, just create a new Log definition (a class)
and specify class attributes:

.. code:: python

    class MyLog(object):

        line = 0
        file = 'unknown'
        func = 'unknown'
        tags = []

When you create a jog method, pass this class in:

.. code:: python

    jog = Jogger(parser=parser, log=MyLog).jog

How jogger Works
----------------

Log parsing and navigating is (somewhat) easy in Python. jogger is
essentially just a light tool that encapsulates everyday, normal,
you-should-be-able-to-figure-this-out Python programming. The tool aims
to give you one thing: a human and machine-friendly interface into log
data.

Let's reiterate a bit.

jogger provides function hooks to create any kind of jogger. You do so
via the Jogger object:

.. code:: python

    from jog import Jogger

jogger uses the following data operations, one at a time, in a pipeline:

    read -> chunk -> parse -> bunch -> inspect -> patch

As an end user, the first three operations are the ones most likely to
be supplied by you. You are also likely to create your own Line and Log
classes.

The default jog method (from jogger import jog) is from the default
jogger (from jogger import jogger), which is a file-and-new-line-based
JSON jogger (as you've seen). It assumes that:

-  logs are on file on disk
-  log lines are separated by new lines
-  log lines are most likely in JSON format

In source you will see that jogger.jogger is constructed like this:

.. code:: python

    jogger = Jogger()

The \_\_init\_\_ method for Jogger has defaults like this:

.. code:: python

    def __init__(self, reader=reader,
                       chunker=chunker,
                       parser=parser,
                       buncher=buncher,
                       inspector=inspector,
                       patcher=patcher,
                       line=Line,
                       log=Log,
                       api=APIMixin):

All of those defaults are functions in jogger.py, with the exception of
the last three, which are classes. Most of the functions are simple
one-or-two liners. This structure allows you to replace any of the steps
required in building a jogger. You can replace the read operation, the
chunking, the parsing, or all three. Here's the default reader function:

.. code:: python

    def reader(file_name):

        with open(file_name, 'r') as f:
            return f.read()

That's just basic Python 101. There isn't even any error checking. (I've
left that to user code.) Here's the default chunker function:

.. code:: python

    def chunker(blob):

        return [chunk for chunk in blob.split('\n') if chunk.strip()]

Again, rather boring Python code (good!). The default parser function:

.. code:: python

    def parser(chunks):

        dictionaries = []
        for chunk in chunks:
            try:
                dictionaries.append(JSON.loads(chunk))
            except:
                dictionaries.append({
                    'unparsed': chunk
                })

        return dictionaries

Pretty simple. The default buncher:

.. code:: python

    def buncher(line_class, dictionaries):

        return [line_class(dictionary) for dictionary in dictionaries]

For a note on what a "bunch" class is, and why I'm using this term, see:

    `The Bunch
    Class <http://pydanny.blogspot.ca/2011/11/loving-bunch-class.html>`__

The code for the inspect and patch operations is less simple, but you
shouldn't have to worry about those.

A Python DB API Database Jogger
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sometimes logs are stored in databases. Here is an example of a database
jog method (in this case, Oracle):

.. code:: python

    def reader(cursor, sql, params):

        """
        Get data from somewhere
        """

        cursor.execute(sql, params)
        return (
            [desc[0].lower() for desc in cursor.description],
            cursor.fetchall()
        )

    def parser(chunks):

        """
        Turn the chunked log lines into dictionaries
        """

        columns, rows = chunks
        return [{columns[i]: v for i, v in enumerate(row)} for row in rows]

    from jogger import Jogger

    # The chunking step is not necessary because the database already
    # returns chunked data (aka rows), so we set the chunker to None
    jog = Jogger(reader=reader, chunker=None, parser=parser).jog

    import cx_Oracle
    conn = cx_Oracle.Connection('some_user/some_password@some_db')
    sql = """
        SELECT code, type, ship_date
        FROM order_log
        WHERE employee = :employee_name
        AND ship_date >= sysdate - 100
    """
    params = {'employee_name': 'jon.dobson'}

    log = jog(conn.cursor(), sql, params)

    print (log)
    # <Log: 9 lines>

    print (log.attributes)
    # ['code', 'type', 'ship_date']

    print (log.type())
    # ['book', 'magazine', 'gift card']

    print (log.type('book'))
    # <Log: 4 lines>

Example Enhancement: Positional Navigation
------------------------------------------

Included in source is a PositionalLog class definition. You can use this
to enhance your jogger like so:

.. code:: python

    >>> from jogger import PositionalLog
    >>> jog= Jogger(log=PositionalLog).jog
    >>> log = jog('test.log')

Your log now contains a positional marker that is set to 0 when the log
is created. The marker endows the log with a "current log line". You can
get the current log line like so:

.. code:: python

    >>> log.current()
    <jogger.Line object at 0x000000000233E080>

    >>> log.current() == log[0]
    True

    >>> log.position() == 0
    True

You can move the marker forward:

.. code:: python

    >>> log.next()
    <jogger.Line object at 0x000000000233EF60>

    >>> log.current() == log[1]
    True

    >>> log.position() == 1
    True

Similarly, you can move the marker backward:

.. code:: python

    >>> log.previous()
    <jogger.Line object at 0x000000000233E080>

    >>> log.current() == log[0]
    True

    >>> log.position() == 0
    True

If you move backward or forward too far, you will get an error:

.. code:: python

    >>> log.previous()
    Traceback (most recent call last):
      ...
    jogger.OutOfBoundsError

You can go to the start and end of a log like so:

.. code:: python

    >>> log.end().current() == log[-1]
    True

    >>> log.start().current() == log[0]
    True

You can manually set the position:

.. code:: python

    >>> log.position(2).current() == log[2]
    True

Object Querying
---------------

The object querying in jogger is done in one of two ways. Either by
calling attributes derived from keys (attribute methods), or by calling
the log with dictionaries, predicate functions, and keywords. What this
amounts to is a small query language for objects. The functionality is
minimal, and could be expanded. Rather than do this myself I defer to
the explorations of others:

    `quibble <http://writeonly.wordpress.com/2009/12/24/quibble-a-damn-small-query-langauge-dsql-using-python/>`__

If you want to expand on the object querying capabilities of your jog
method, you can modify the Log definition like so:

.. code:: python

    class MyLog(object):

        def __init__(self, lines, *args, **kwargs):

            # some extra initialization
            pass

        def some_extra_functionality(self):

            for line in self:
                print (line)

    jog = Jogger(log=MyLog).jog
    log = jog('test.log')
    log.some_extra_functionality()

Cataloging
----------

If you've got lots of different kinds of logs to explore, you'll have a
bunch of different parser functions stored somewhere. Some of the log
parsing tools out there rely on regex repositories for different log
types. You can do this too. It might be handy to keep a set of common
log parser functions included with the jogger project. An attempt to do
that may [edit: *has*] happen(ed).

A jog catalogue (a jogalog?) is now available at jogger.catalogue. Two
joggers have been added to it. One for the `Common Log
Format <http://en.wikipedia.org/wiki/Common_Log_Format>`__ as used by
popular web servers (Apache, nginx, etc.) and another for the `Combined
Log Format <http://httpd.apache.org/docs/2.4/logs.html>`__.
(jogger.catalogue.common\_jog and jogger.catalogue.combined\_jog
respectively.) Additionally, the json-based jogger demonstrated
throughout this document is available as jogger.catalogue.json\_jogger.

.. code:: python

    >>> from jogger.catalogue import common_jog as jog
    >>> log = jog('my_common_log.log')
    >>> log
    <Log: 14566 lines>

    >>> from jogger.catalogue import combined_jog as jog
    >>> log = jog('my_combined_log.log')
    >>> log
    <Log: 4988 lines>

Both of these joggers have been built on a regex parser that you can use
on your own (knowledge of regexes required, of course). Assuming a
simple log with lines like this:

    [10/Oct/2000:13:55:36 -0700] "user foo logged in"

...one could use the regex parser like so:

.. code:: python

    >>> from jogger import Jogger
    >>> from jogger.catalogue import regex_parser
    >>> regex = '[(.*?)\] "(.*?)"'
    >>> field_map = [
            ('timestamp', lambda x: datetime.strptime(x.split(' ')[0], '%d/%b/%Y:%H:%M:%S')),
            ('message', lambda x: x)
        ]
    >>> parser = partial(regex_parser, regex, field_map)
    >>> jog = Jogger(parser=parser).jog
    >>> log = jog('my_simple_log.log')
    >>> log.attributes
    ['timestamp', 'message']
    >>> log[0].timestamp
    datetime.datetime(2000, 10, 10, 13, 55, 36)
    >>> log[0].message
    user foo logged in

There are more "advanced" concepts involved in this example - such as
`functools.partial <http://doughellmann.com/2008/04/pymotw-functools.html>`__
and
`regexes <http://www.marksanborn.net/howto/learning-regular-expressions-for-beginners-the-basics/>`__
- but that's what the Internet is for!

Other Thoughts
--------------

Half-ORM-ish
~~~~~~~~~~~~

jogger as it stands is kind of half a micro-ORM. It's the read half. It
reads in data and translates it into objects - it has no facility to
write or save changes. Generically the default Line class == an Object
and the default Log class == a Collection. I imagine you could make it
more ORMy by implementing your own custom Log definition.

Nested Structures
~~~~~~~~~~~~~~~~~

Although it can handle nested data, it seems like the best way to log is
flat - i.e. one level deep. None of the examples showed logs with nested
structures. jogger currently handles this by recursively turning all
collections.Mapping objects (that includes dicts) into Line instances.
If you have nested structures then your log lines will contain lines
themselves.
