"""
Python port of Ruby Nest library (https://github.com/soveran/nest)
Copyright (c) 2012, Exodus Development, Inc.  All Rights Reserved.
https://github.com/inactivist/python-redis-nest/blob/master/LICENSE.txt
"""
__version__ = "0.0.1"

from redis import Redis
import inspect
import types
import pprint

#
# _METHODS is a list of Redis methods we wish to proxy.
_METHODS = ['append', 'blpop', 'brpop', 'brpoplpush', 'decr', 'decrby',
        'del', 'exists', 'expire', 'expireat', 'get', 'getbit', 'getrange', 'getset',
        'hdel', 'hexists', 'hget', 'hgetall', 'hincrby', 'hkeys', 'hlen', 'hmget',
        'hmset', 'hset', 'hsetnx', 'hvals', 'incr', 'incrby', 'lindex', 'linsert',
        'llen', 'lpop', 'lpush', 'lpushx', 'lrange', 'lrem', 'lset', 'ltrim', 'move',
        'persist', 'publish', 'rename', 'renamenx', 'rpop', 'rpoplpush', 'rpush',
        'rpushx', 'sadd', 'scard', 'sdiff', 'sdiffstore', 'set', 'setbit', 'setex',
        'setnx', 'setrange', 'sinter', 'sinterstore', 'sismember', 'smembers',
        'smove', 'sort', 'spop', 'srandmember', 'srem', 'strlen', 'subscribe',
        'sunion', 'sunionstore', 'ttl', 'type', 'unsubscribe', 'watch', 'zadd',
        'zcard', 'zcount', 'zincrby', 'zinterstore', 'zrange', 'zrangebyscore',
        'zrank', 'zrem', 'zremrangebyrank', 'zremrangebyscore', 'zrevrange',
        'zrevrangebyscore', 'zrevrank', 'zscore', 'zunionstore']

# Get a list of Redis methods that take 'name' as the first parameter.
# Is this method efficient?
_method_list = [v for n, v in inspect.getmembers(Redis, inspect.ismethod)
               if v.__name__ in _METHODS]

# Previous list comprehension filters.  Trying to guess at candidate
# Redis methods to be proxied without using _METHODS lookup.
##    if isinstance(v,types.MethodType)
##    and not v.__name__.startswith('__')
##    and len(inspect.getargspec(v)[0]) > 1
##    and not inspect.getargspec(v)[0][1] == 'name'
##    ]


def _redis_func_wrapper(self, f):
    """Function wrapper for redis mapping.  Inserts self, name at front
       of function args list.
    """
    def wrapped_f(*args, **kwargs):
        # We assume that kwargs are never used.  
        assert(len(kwargs) == 0)
        l = list(args)
        l.insert(0, str(self))  # 'name'
        l.insert(0, self.redis) # 'self'
        args = tuple(l)
        return f(*args, **kwargs)

    return wrapped_f

class Nest(str):
    """
       Nested redis keys inspired by Ruby Nest library.
       https://github.com/soveran/nest
    """
    def __new__(cls, s, redis=None):
        return str.__new__(cls, s)

    def __init__(self, s, *args, **kwargs):
        super(Nest, self).__init__(s)
        # Get the redis instance if provided, else create default instance.
        self.redis = kwargs.pop('redis', None)
        if self.redis is None:
            self.redis = Redis()
        # Generate function wrappers/forwarders for all
        # target redis methods.
        # 
        # TODO: Is there a way to do this once for the class rather than
        # per-instance?  (Performance optimization.)
        for m in _method_list:
            setattr(self, m.__name__, _redis_func_wrapper(self, m))

    def __getitem__(self, index):
        return Nest("%s:%s" % (self, index))

    
if __name__ == "__main__" :
    # Simple examples.  Need unit tests.  Get to it!
    x=Nest('event')
    x[3]['attendees'].sadd('Albert')
    x[3]['attendees'].sadd('Robert')
    x[3]['attendees'].smembers()
    print x[3]['attendees'].smembers()

    n = Nest("test")
    n.set(12345)
    n.expire(60)
    print n.get()
    n1 = n['foo']['bar']['baz']
    n1.set(666)
    print n1.get()
    n1.expire(90)

