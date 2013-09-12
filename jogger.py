
try:

  unicode = unicode

except NameError:

  unicode = str
  basestring = (str, bytes)


def reader(file_name):

    """
    Get a blob of data from somewhere
    """

    with open(file_name, 'r') as f:
        return f.read()


def chunker(blob):

    """
    Chunk a blob of data into an iterable of smaller chunks
    """

    return [chunk for chunk in blob.split('\n') if chunk.strip()]


import json
def parser(chunks):

    """
    Parse a data chunk into a dictionary; catch failures and return suitable
    defaults
    """

    dictionaries = []
    for chunk in chunks:
        try:
            dictionaries.append(json.loads(chunk))
        except:
            dictionaries.append({
                'unparsed': chunk
            })

    return dictionaries


def buncher(line_class, dictionaries):

    """
    Turn an iterable of dictionaries into an iterable of Python objects that
    represent log lines.
    """

    return [line_class(dictionary) for dictionary in dictionaries]


from collections import defaultdict
def inspector(objects):

    api = {
        'attributes': set(),
        'scalars': set(),
        'vectors': set(),
        'defaults': {}
    }

    attributes = defaultdict(set)
    for line in objects:
        for attribute in dir(line):
            if not attribute.startswith('_') and not callable(
                    getattr(line, attribute)
                ):
                kind = type(getattr(line, attribute))
                if kind in (unicode, basestring, bytes) or issubclass(
                    kind, basestring):
                    kind = str
                attributes[attribute].add(kind)

    api['attributes'] = set(attributes.keys())

    for attribute in attributes.keys():
        kinds = set(attributes[attribute])

        if len(kinds) == 1:

            kind = kinds.pop()
            try:
                api['defaults'][attribute] = kind()
            except:
                api['defaults'][attribute] = NoValue

            if not issubclass(kind, collections.Iterable) or kind in (
                str, unicode, basestring, bytes):
                api['scalars'].add(attribute)
            else:
                api['vectors'].add(attribute)
        else:
            # this is a heterogenous attribute! hmm....
            api['defaults'][attribute] = NoValue

            has_scalars = False
            has_vectors = False

            for kind in kinds:

                if not issubclass(kind, collections.Iterable) or kind in (
                    str, unicode, basestring, bytes):
                    has_scalars = True
                else:
                    has_vectors = True

            if has_scalars:
                api['scalars'].add(attribute)
            else:
                api['vectors'].add(attribute)


    return api


def patcher(APIMixin, LogKlass, api):

    """
    Merge the api mixin class with a user Log class and patch in an api; also
    set defaults
    """

    class Log(APIMixin, LogKlass):

        def __init__(self, lines, *args, **kwargs):

            APIMixin.__init__(self, lines, *args, **kwargs)
            LogKlass.__init__(self, lines, *args, **kwargs)

            for a in dir(LogKlass):
                if not a.startswith('_') and not callable(getattr(LogKlass, a)):
                    api['attributes'].add(a)
                    default_value = getattr(LogKlass, a)
                    api['defaults'][a] = default_value
                    kind = type(default_value)
                    if kind in (unicode, basestring, bytes) or issubclass(
                        kind, basestring):
                        kind = str
                    if not issubclass(kind, collections.Iterable) or kind in (
                        str, unicode, basestring):
                        api['scalars'].add(a)
                    else:
                        api['vectors'].add(a)

            self.attributes = sorted(api['attributes'])

            for scalar in api['scalars']:

                value = partial(lambda self, scalar, *args, **kwargs:
                    self._scalar(scalar, *args, **kwargs), self, scalar
                )
                setattr(self, scalar, value)

                value.any = value

                value.all = partial(lambda self, scalar, *args:
                    self._scalar(scalar, *args, mode='all'), self, scalar
                )

                value.none = partial(lambda self, scalar, *args:
                    self._scalar(scalar, *args, mode='none'), self, scalar
                )

                value.only = partial(lambda self, vector, *args:
                    self._scalar(scalar, *args, mode='only'), self, scalar
                )

            for vector in api['vectors']:

                value = partial(lambda self, vector, *args, **kwargs:
                    self._vector(vector, *args, **kwargs), self, vector
                )
                setattr(self, vector, value)

                value.any = value

                value.all = partial(lambda self, vector, *args:
                    self._vector(vector, *args, mode='all'), self, vector
                )

                value.none = partial(lambda self, vector, *args:
                    self._vector(vector, *args, mode='none'), self, vector
                )

                value.only = partial(lambda self, vector, *args:
                    self._vector(vector, *args, mode='only'), self, vector
                )

            for line in self:
                for attribute, default in api['defaults'].items():
                    if not hasattr(line, attribute):
                        try:
                            klass_default = getattr(LogKlass, attribute)
                            setattr(line, attribute, klass_default)
                        except:
                            setattr(line, attribute, default)

    return Log


class MetaNoValue(type):
    def __bool__(cls):
        return False
    def __nonzero__(cls):
        return False
    def __getattr__(cls, attr):
        return cls

class NoValue(object):
    __metaclass__ = MetaNoValue


class Line(object):

    """
    The default user-defined "bunch" class, for lines in a log
    """

    def __init__(self, dictionary):

        for k, v in dictionary.items():
            if isinstance(v, collections.Mapping):
                dictionary[k] = self.__class__(v)
        self.__dict__.update(dictionary)


class Log(object):

    """
    The default user-defined log class

    def __init__(self, lines, *args, **kwargs):
        pass

    """


import re
PATTERN_TYPE = type(re.compile('a'))


class APIMixin(list):

    """
    The base API we're striving for on the Log instance goes here
    """

    def __init__(self, lines, *args, **kwargs):

        self.extend(lines)
        self._args = args
        self._kwargs = kwargs

    def _where(self, *comparators, **comparator):

        def by_schema(self, schema):

            log = self[:]
            to_remove = set()

            for line in log:

                if not isinstance(line, collections.Mapping):
                    try:
                        d = line.__dict__
                    except AttributeError:
                        continue
                else:
                    d = line

                for k, t in schema.items():

                    if k.startswith('~'):
                        notted = True
                        k = k[1:]
                    else:
                        notted = False

                    if k not in d:
                        to_remove.add(line)
                    else:

                        v = d[k]

                        if isinstance(v, collections.Iterable) and not isinstance(v, (str, unicode)):
                            method = self._vector_match
                        else:
                            method = self._scalar_match

                        if notted:
                            if method(v, t):
                                to_remove.add(line)
                        else:
                            if not method(v, t):
                                to_remove.add(line)

            for line in to_remove:
                log.remove(line)

            return log

        log = self.__class__(self)
        if comparator:
            comparators += (comparator,)

        for comparator in comparators:

            if isinstance(comparator, collections.Mapping):
                log = by_schema(log, comparator)
                continue

            if callable(comparator):
                log = self.__class__([line for line in log if comparator(line)])
                continue

            raise TypeError("Invalid comparator")

        return log

    def _vector(self, name, *selection, **kwargs):

        if not selection:
            vector = set()
            for line in self:
                [vector.add(t) for t in getattr(line, name)]

            return sorted(vector, key=self._get_sort_key)

        mode = kwargs.pop('mode', 'any')

        selection = set(selection)
        lines = []

        for i, line in enumerate(self):
            passes = []
            value = getattr(line, name)
            for select in selection:

                # if self._vector_match(value, select):
                #     lines.append(line)

                if passes and mode == 'any' and any(passes):
                    break

                if self._vector_match(value, select):
                    passes.append(True)
                else:
                    passes.append(False)

            if passes and mode == 'any' and any(passes):
                lines.append(line)
            elif passes and mode == 'all' and all(passes):
                lines.append(line)
            elif mode == 'none' and (not passes or not any(passes)):
                lines.append(line)
            elif mode == 'only' and passes and all(passes) and len(passes) == len(value):
                lines.append(line)

        return self.__class__(set(lines))

    def _get_sort_key(self, obj):

        return str(obj)

    def _scalar(self, name, *selection, **kwargs):

        if not selection:
            return sorted(set([getattr(line, name) for line in self]), key=self._get_sort_key)

        mode = kwargs.pop('mode', 'any')

        selection = set(selection)
        lines = []

        for line in self:
            passes = []
            value = getattr(line, name)
            for select in selection:

                # if self._scalar_match(value, select):
                #     lines.append(line)

                if passes and mode == 'any' and any(passes):
                    break

                if self._scalar_match(value, select):
                    passes.append(True)
                else:
                    passes.append(False)

            if passes and mode == 'any' and any(passes):
                lines.append(line)
            elif passes and mode == 'all' and all(passes):
                lines.append(line)
            elif mode == 'none' and (not passes or not any(passes)):
                lines.append(line)
            elif mode == 'only' and passes and all(passes) and len(passes) == len(value):
                lines.append(line)

        return self.__class__(set(lines))

    def _vector_match(self, value, select):

        invalid = (types.ClassType, types.TypeType, MetaNoValue)
        if type(select) not in invalid:
            if callable(select):
                if select(value):
                    return True
            else:
                for elem in value:
                    if self._scalar_match(elem, select):
                        return True
        else:
            if select in (str, unicode, basestring, bytes) or issubclass(
                select, basestring):
                select = str
            if type(value) in (str, unicode, basestring, bytes) or issubclass(
                type(value), basestring):
                value = str(value)
            if isinstance(value, select):
                return True

    def _scalar_match(self, value, select):

        if select == value:
            return True
        else:
            invalid = (types.ClassType, types.TypeType, MetaNoValue)
            if type(select) not in invalid:
                if type(select) == PATTERN_TYPE:
                    if select.match(value):
                        return True
                elif callable(select):
                    if select(value):
                        return True
            else:
                if select in (str, unicode, basestring, bytes) or issubclass(
                    select, basestring):
                    select = str
                if type(value) in (str, unicode, basestring, bytes) or issubclass(
                    type(value), basestring):
                    value = str(value)
                if isinstance(value, select):
                    return True

    def __call__(self, *comparators, **comparator):

        return self._where(*comparators, **comparator)

    def __getslice__(self, i, j):

        # this special method is gone in py 3.x; detect a slice object in
        # __getitem__ for py 3 instead (py 2.x code will still call this
        # special method)

        return self.__class__(
            list.__getslice__(self, i, j),
                *self._args,
                **self._kwargs
            )

    def __getitem__(self, item):

        if type(item) in (unicode, str, bytes) or issubclass(
            type(item), basestring):
            return getattr(self, item)

        if type(item) == slice:
            return self.__class__(
                list.__getitem__(self, item),
                    *self._args,
                    **self._kwargs
                )

        return list.__getitem__(self, item)

    def __setitem__(self, item, value):

        if type(item) in (unicode, str, bytes) or issubclass(
            type(item), basestring):
            setattr(self, item, value)
            return

        list.__setitem__(self, item, value)

    def __sub__(self, other):

        lines = [line for line in self if line not in other]
        return self.__class__(lines)

    def __isub__(self, other):

        lines = [line for line in self if line not in other]
        return self.__class__(lines)

    def __add__(self, other):

        return self.__class__(set(list(self) + list(other)))

    def __iadd__(self, other):

        return self.__class__(set(list(self) + list(other)))

    def __eq__(self, other):

        return (
            set([hash(line) for line in self]) ==
            set([hash(line) for line in other])
        )

    def __repr__(self):

        return "<Log: {} lines>".format(len(self))


class PositionalLog(object):

    class OutOfBoundsError(Exception): pass

    def __init__(self, lines, *args, **kwargs):

        super(PositionalLog, self).__init__(lines, *args, **kwargs)
        self._position = 0

    def current(self):

        if self._position == len(self) or self._position == -1:
            raise PositionalLog.OutOfBoundsError

        return self[self._position]

    def next(self):

        self._position += 1
        if self._position > len(self):
            self._position == len(self)

        return self.current()

    def previous(self):

        self._position -= 1
        if self._position < -1:
            self._position == -1

        return self.current()

    def start(self):

        self._position = 0

        return self

    def end(self):

        self._position = len(self) - 1

        return self

    def position(self, position=None):

        if position:
            self._position = position
            return self

        return self._position


from functools import partial
import collections
import types

try:
    types.ClassType = types.ClassType
    types.TypeType = types.TypeType
except AttributeError:
    types.ClassType = type
    types.TypeType = type

class Jogger(object):

    def __init__(self, reader=reader, chunker=chunker, parser=parser,
                 buncher=buncher, inspector=inspector, patcher=patcher,
                 line=Line, log=Log, api=APIMixin):

        self.read       = reader
        self.chunk      = chunker
        self.parse      = parser
        self.bunch      = partial(buncher, line)
        self.inspect    = inspector
        self.klass      = log
        self.patch      = partial(patcher, api, log)

    def jog(self, *args, **kwargs):

        """
        This method returns an instance of a patched-together Log class
        """

        blob    = self.read(*args, **kwargs)
        chunks  = self.chunk(blob) if self.chunk else blob
        dicts   = self.parse(chunks) if self.parse else chunks
        objects = self.bunch(dicts) if self.bunch else dicts
        api     = self.inspect(objects)
        klass   = self.patch(api)
        log     = klass(objects, *args, **kwargs)

        return log

"""
A default jogger implementation (a json-based one)
"""

jogger = Jogger()
jog = jogger.jog


if __name__ == "__main__":

    pass