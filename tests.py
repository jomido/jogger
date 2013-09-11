
def static_json_reader():

    return (
    """
        {"line": "what?"}
        {"line": 0}
        bad line
        {"file": "foo.py"}

        {"msg": "Hello"}
        {"tags": ["greetings"]}
        {"tags": ["farewell-ings"]}
        {"tags": ["farewell-ings", "greetings"]}
        {"tags": ["farewell-ings", "greetings", "shazzam"]}
    """)


def test(reader, parser, Klass):

    from jogger import Jogger, NoValue

    jog = Jogger(reader=reader, parser=parser, log=Klass).jog
    log = jog()

    expected_length = 9
    expected_attrs = ['file', 'line', 'msg', 'tags', 'unparsed']
    expected_attrs_length = len(expected_attrs)

    assert len(log) == expected_length
    assert len(log.attributes) == expected_attrs_length
    assert log.attributes == expected_attrs

    for attr in expected_attrs:
        assert(attr in log.attributes)

    # print log.line()
    # return
    assert log.line() == [0, NoValue, 'what?']
    assert log.file() == ['', 'foo.py']
    assert log.msg() == [None, 'Hello']
    assert log.unparsed() == ['', '        bad line']
    assert log.tags() == ['farewell-ings', 'greetings', 'shazzam']

    # value searching by attribute

    assert len(log.line(0)) == 1
    assert len(log.line(NoValue)) == expected_length - 2
    assert len(log.line('what?')) == 1
    assert len(log.line(NoValue, 'what?')) == expected_length - 1
    assert len(log.line(NoValue, 'what?', 0)) == expected_length

    assert len(log.file('foo.py')) == 1
    assert len(log.file('')) == expected_length - 1
    assert len(log.file('foo.py', '')) == expected_length

    assert len(log.msg('Hello')) == 1
    assert len(log.msg(None)) == expected_length - 1
    assert len(log.msg('Hello', None)) == expected_length

    assert len(log.tags('greetings')) == 3
    assert len(log.tags('farewell-ings')) == 3
    assert len(log.tags('farewell-ings').tags('greetings')) == 2

    assert len(log.unparsed('        bad line')) == 1
    assert len(log.unparsed('')) == expected_length - 1
    assert len(log.unparsed('        bad line', '')) == expected_length

    # type searching by attribute

    assert len(log.line(int)) == 1
    assert len(log.line(str)) == 1
    assert len(log.line(str, int)) == 2

    assert len(log.file(str)) == expected_length

    assert len(log.msg(str)) == 1

    assert len(log.tags(list)) == expected_length
    assert len(log.tags(str)) == 0

    assert len(log.unparsed(str)) == expected_length
    assert len(log.unparsed(int)) == 0

    # lambda searching by attribute

    assert len(log.line(lambda line: line == 0)) == 1

    assert len(log.tags(lambda tags: 'greetings' in tags)) == 3

    # mixed searching by attribute

    assert len(log.line(str, 0)) == 2
    assert len(log.line(
        str,
        0,
        lambda line: line == NoValue
    )) == expected_length

    # dictionary searching

    assert len(log({'line': 0})) == 1
    assert len(log({'line': int})) == 1
    assert len(log({'line': lambda line: line == 'what?'})) == 1
    assert len(log({
        'tags': 'greetings',
        'msg': None
    })) == 3
    assert len(log
        ({
            'tags': 'greetings'
        })
        ({
            'msg': None
        })
    ) == 3

    # using all and any on an attribute

    tags = ['farewell-ings', 'greetings']
    assert len(log.tags.any(*tags)) == 4
    assert len(log.tags.all(*tags)) == 2
    assert len(log.tags.none(*tags)) == 5
    assert len(log.tags.only(*tags)) == 1

    # copying

    log2 = log()
    assert log2 == log

    # adding, subtracting, equality

    log2 = log.tags.any('greetings')
    log3 = log.tags.none('greetings')

    assert log2 != log3
    assert log2 != log
    assert log3 != log

    log4 = log2 + log3

    assert log4 == log

    # testing positional mixin

    assert log.current() == log[0]

    try:
        print log.previous()
    except Exception as ex:
        assert isinstance(ex, Klass.OutOfBoundsError)

    log.end()
    assert log.current() == log[-1]

    log.start()
    assert log.current() == log[0]

    assert log.next() == log[1]

    assert log.end().previous() == log[-2]


def run_tests():

    from jogger import PositionalLog, reader, chunker, parser

    class MyLog(PositionalLog):

        msg = None

    test(
        static_json_reader,
        parser,
        MyLog
    )

if __name__ == "__main__":

    run_tests()

