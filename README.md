"Nested" Redis keys for Python (redis-nest)
======

Nested, or "Object Oriented" keys for [Redis](http://redis.io).  Inspired by [Ruby Nest](https://github.com/soveran/nest). 

**Please visit the [project wiki](https://github.com/inactivist/python-redis-nest/wiki) pages for more information.**

Status:
------
* Tested with Python 2.7 and redis 2.4.9.
* redis-nest is currently in an early alpha release.  There's more work to be done, but the basic model is not expected to change.

Description
-----------

*(Much of this section is based on the Ruby Nest [README](https://github.com/soveran/nest/blob/master/README.md) file.)*

*`redis-nest`* is a simple wrapper around the Python's [redis](http://pypi.python.org/pypi/redis) package.  It allows you to create and operate on *namespaced* keys when using Redis.

For example, if you are operating on Redis keys like these:

    >>> import redis
    >>> r = redis.Redis()
    >>> r.sadd("event:3:attendees", "Robert")
    1
    >>> r.sadd("event:3:attendees", "Albert")
    1
    >>> r.smembers("event:3:attendees")
    set(['Robert', 'Albert'])

You can use `redis-nest` to operate on keys in a more natural and consistent way:

    >>> x=Nest('event')
    >>> x[3]['attendees'].sadd('Albert')
    1
    >>> x[3]['attendees'].sadd('Robert')
    1
    >>> x[3]['attendees'].smembers()
    set(['Robert', 'Albert'])
    
Usage
-----

Redis Nest is modeled after the [Ruby Nest](https://github.com/soveran/nest) library, and it's easy to 
use.  You create a 'namespace' which is used as the base Redis key,
then you can add subkeys under that namespace, which are represented
as a concatenation of colon-separated subkeys based on the array path.

To create a new namespace named 'foo':

    >>> ns = Nest("foo")
    >>> ns
    'foo'
    
You can then invoke public Redis instance methods on the namespace:

    >>> ns.set(1)
    True
    >>> ns.get()
    '1'

Which is equivalent to the following Redis methods:

    >>> import redis
    >>> r = redis.Redis()
    >>> r.set('foo', 1)
    True
    >>> r.get('foo')
    '1'    
    
To create a nested sub-key 'bar' inside the namespace 'foo':
 
    >>> ns["bar"]
    'foo:bar'
    
You can nest as deeply as you wish:

    >>> ns["bar"]["baz"]["qux"]
    'foo:bar:baz:qux'

You can use other objects as a key, as long the object's string 
representation is a valid Redis key string:

    >>> ns["bar"][42]
    "foo:bar:42"

You can specify your own Redis library instance:

    import redis
    >>> r = redis.Redis(host="192.168.0.101") 
    >>> x = redis_nest.Nest("foo", redis=r)
 
Installation
------------

Requires the [redis](https://github.com/inactivist/python-redis-nest/blob/master/README.md) python library.

For now, just checkout the repo and add it to your PYTHONPATH.  
A PyPi installable package is forthcoming.

More to come...
