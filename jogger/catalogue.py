
from jogger import Jogger as _Jogger, jog as json_log

from functools import partial
from collections import OrderedDict
import re


def regex_parser(regex, field_map, chunks):

	dictionaries = []

	fields = OrderedDict(field_map)

	for chunk in chunks:

		result = re.match(regex, chunk.strip())

		if result:

			r = result.groups()
			d = {}

			for i, (k, v) in enumerate(fields.items()):

				try:
					value = r[i]
				except IndexError:
					value = None

				d[k] = v(value)

			extra_fields = r[len(field_map):]
			for i, field in enumerate(extra_fields):
				d['field_{}'.format(len(field_map) + i)] = extra_fields[i]

			dictionaries.append(d)

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

	parser = partial(regex_parser, regex, field_map)

	class Log(object):

		address = identifier = userid = request = 'UNPARSED'
		response_code = -1
		# response_size = -1
		timestamp = datetime.datetime(year=datetime.MINYEAR, month=1, day=1)

	def tests():

		test_log = _Jogger(reader=static_reader, parser=parser, log=Log).jog()

		assert len(test_log) == 4
		assert len(test_log(lambda line: line.unparsed)) == 1

		line = test_log[0]
		assert line.address == "127.0.0.1"
		assert line.identifier == 'abc'
		assert line.userid == 'frank'
		assert line.timestamp == datetime.datetime(2000, 10, 10, 13, 55, 36)
		assert line.request == "GET /apache_pb.gif HTTP/1.0"
		assert line.response_code == 404
		assert line.response_size == 82

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

	parser = partial(regex_parser, regex, field_map)

	class Log(object):

		address = identifier = userid = request = referer = user_agent = 'UNPARSED'
		response_code = -1
		response_size = -1
		timestamp = datetime.datetime(year=datetime.MINYEAR, month=1, day=1)

	def tests():

		test_log = _Jogger(reader=static_reader, parser=parser, log=Log).jog()

		assert len(test_log) == 4
		assert len(test_log(lambda line: line.unparsed)) == 1

		line = test_log[0]
		assert line.address == "123.65.150.10"
		assert line.identifier == '-'
		assert line.userid == '-'
		assert line.timestamp == datetime.datetime(2010, 8, 23, 3, 50, 59)
		assert line.request == "POST /wordpress3/wp-admin/admin-ajax.php HTTP/1.1"
		assert line.response_code == 200
		assert line.response_size == 2
		assert line.referer == "http://www.example.com/wordpress3/wp-admin/post-new.php"
		assert line.user_agent == "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_4; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.25 Safari/534.3"

	return (_Jogger(parser=parser, log=Log).jog, tests)


combined_jog, _combined_jog_tests = combined_jog()


def _tests():

	_common_jog_tests()
	_combined_jog_tests()


if __name__ == "__main__":

	_tests()

