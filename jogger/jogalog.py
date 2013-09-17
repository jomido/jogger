
from jogger import Jogger as _Jogger, jog as json_log
from functools import partial, wraps


def apply(*args, **kwargs):

    """
    This function allows you to lock in none, some or all of the positional
    arguments or keyword arguments of another function via decoration. a.k.a.
    partial application.
    """

    def wrapper(fn):

        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return partial(wrapper, *args, **kwargs)

    return wrapper


from collections import OrderedDict
import re


def regex_parser(regex, field_map, chunks):

	dictionaries = []

	fields = OrderedDict(field_map)

	for chunk in chunks:

		result = re.match(regex, chunk.strip())
		if result:
			r = result.groups()
			dictionaries.append(
				{k: v(r[i]) for i, (k, v) in enumerate(fields.items())}
			)
		else:
			dictionaries.append({
				'unparsed': chunk
			})

	return dictionaries


def common_jog():

	"""
	Common Log Format
	"""

	def static_reader():

		return """

			127.0.0.1 abc frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 404 82

			asdasd
			127.0.0.1 abc susie [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326
			127.0.0.2 ghi frank [12/Oct/2000:13:55:36 -0700] "GET /apache_pb.jpg HTTP/1.0" 200 1326

		"""

	import datetime

	regex = '([(\d\.)]+) (.*) (.*) \[(.*?)\] "(.*?)" (\d+) (\d+)'
	strptime = datetime.datetime.strptime
	value = lambda x: x
	int_value = lambda x: int(x)
	date_value = lambda x: strptime(x.split(' ')[0], '%d/%b/%Y:%H:%M:%S')

	field_map = [
		('address', 	  value),
		('identifier', 	  value),
		('userid', 		  value),
		('timestamp', 	  date_value),
		('request', 	  value),
		('response_code', int_value),
		('response_size', int_value)
	]

	parser = apply(regex, field_map)(regex_parser)

	class Log(object):

		address = identifier = userid = request = 'UNPARSED'
		response_code = -1
		response_size = -1
		timestamp = datetime.datetime(year=datetime.MINYEAR, month=1, day=1)

	def tests():

		test_log = _Jogger(reader=static_reader, parser=parser, log=Log).jog()

		print test_log
		print test_log.attributes
		print test_log.address()

		import pprint
		pprint.pprint(test_log[0].__dict__)
		assert len(test_log) == 4
		#assert len(test_log(lambda line: line.unparsed)) == 1

	return (_Jogger(parser=parser, log=Log).jog, tests)


common_jog, _common_jog_tests = common_jog()


def combined_jog():

	"""
	Combined Log Format
	"""

	def static_reader():

		return """

			123.65.150.10 - - [23/Aug/2010:03:50:59 +0000] "POST /wordpress3/wp-admin/admin-ajax.php HTTP/1.1" 200 2 "http://www.example.com/wordpress3/wp-admin/post-new.php" "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.25 Safari/534.3"

			asdasd
			123.65.150.10 - - [23/Aug/2010:03:50:59 +0000] "POST /wordpress3/wp-admin/admin-ajax.php HTTP/1.1" 200 2 "http://www.example.com/wordpress3/wp-admin/post-new.php" "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.25 Safari/534.3"
			123.65.150.10 - - [23/Aug/2010:03:50:59 +0000] "POST /wordpress3/wp-admin/admin-ajax.php HTTP/1.1" 200 2 "http://www.example.com/wordpress3/wp-admin/post-new.php" "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.25 Safari/534.3"

		"""

	import datetime

	regex = '([(\d\.)]+) (.*) (.*) \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)"'
	strptime = datetime.datetime.strptime
	value = lambda x: x
	int_value = lambda x: int(x)
	date_value = lambda x: strptime(x.split(' ')[0], '%d/%b/%Y:%H:%M:%S')

	field_map = [
		('address', 	  value),
		('identifier', 	  value),
		('userid', 		  value),
		('timestamp', 	  date_value),
		('request', 	  value),
		('response_code', int_value),
		('response_size', int_value),
		('referer', 	  value),
		('user_agent', 	  value),
	]

	parser = apply(regex, field_map)(regex_parser)

	class Log(object):

		address = identifier = userid = request = referer = user_agent = 'UNPARSED'
		response_code = -1
		response_size = -1
		timestamp = datetime.datetime(year=datetime.MINYEAR, month=1, day=1)

	def tests():

		test_log = _Jogger(reader=static_reader, parser=parser, log=Log).jog()

		assert len(test_log) == 4
		assert len(test_log(lambda line: line.unparsed)) == 1
		import pprint
		pprint.pprint(test_log[0].__dict__)

	return (_Jogger(parser=parser, log=Log).jog, tests)


combined_jog, _combined_jog_tests = combined_jog()


def _run_tests():

	_common_jog_tests()
	_combined_jog_tests()


if __name__ == "__main__":

	_run_tests()

