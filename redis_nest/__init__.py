"""
Python port of Ruby Nest library (https://github.com/soveran/nest)
Copyright (c) 2012, Exodus Development, Inc.  All Rights Reserved.
https://github.com/inactivist/python-redis-nest/blob/master/LICENSE.txt
"""
__version__ = "0.0.4"

from redis import Redis
import inspect
import types
import pprint

#
# _METHODS is a list of Redis public methods we wish to proxy by inserting key value as
# first parameter.
_METHODS_ADD_SELF = ['append', 'brpoplpush', 'decr', 'decrby', 'exists',
        'expire', 'expireat', 'get', 'getbit', 'getrange', 'getset',
        'hdel', 'hexists', 'hget', 'hgetall', 'hincrby', 'hkeys', 'hlen', 'hmget',
        'hmset', 'hset', 'hsetnx', 'hvals', 'incr', 'incrby', 'lindex', 'linsert',
        'llen', 'lpop', 'lpush', 'lpushx', 'lrange', 'lrem', 'lset', 'ltrim', 'move',
        'persist', 'rename', 'renamenx', 'rpop', 'rpoplpush', 'rpush',
        'rpushx', 'sadd', 'scard', 'sdiffstore', 'set', 'setbit', 'setex',
        'setnx', 'setrange', 'sismember', 'smembers',
        'smove', 'sort', 'spop', 'srandmember', 'srem', 'strlen', 
        'ttl', 'type', 'zadd',
        'zcard', 'zcount', 'zincrby', 'zrange', 'zrangebyscore',
        'zrank', 'zrem', 'zremrangebyrank', 'zremrangebyscore', 'zrevrange',
        'zrevrangebyscore', 'zrevrank', 'zscore']

# List of methods that need to be proxied without adding key name as first parameter.
_METHODS_AS_IS = [
    'blpop', 'brpop', 'keys', 'mget', 'mset', 'msetnx', 'publish', 'psubscribe', 
    'punsubscribe',
    'randomkey', 'sdiff', 
    'sinter', 'sinterstore', 'subscribe', 'sunion', 'sunionstore', 'unsubscribe', 
    'watch', 'zinterstore', 'zunionstore'
    ]

# Generate method lookup dictionaries.  
# TODO: Is there a more efficient way to search the method name lists?

# Get a list of Redis methods that take 'name' as the first parameter.
_redis_methods_add_self_and_name = dict((name, func) 
    for name, func in inspect.getmembers(Redis, inspect.ismethod)
        if name in _METHODS_ADD_SELF)

# Get a list of Redis methods to be proxied as-is.
_redis_methods_as_is = dict((name, func) 
    for name, func in inspect.getmembers(Redis, inspect.ismethod)
        if name in _METHODS_AS_IS)

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

    def __getattr__(self, name):
        # Monkeypatch function wrappers/forwarders for target redis methods.
        # __getattr__ is only called when attribute isn't found elsewhere. 

        # Methods that take self and this item's key name as first parameter.
        m = _redis_methods_add_self_and_name.get(name)
        if m:
            #print '%s(%d): Adding SELF,NAME method "%s": %s' % (self, id(self), name, m)
            setattr(self, name, _redis_func_wrapper(self, m))
        else:
            m = _redis_methods_as_is.get(name)
            if m:
                #print '%s(%d): Adding AS-IS method "%s": %s' % (self, id(self), name, m)
                setattr(self, name, types.MethodType(m, self.redis, self.redis.__class__))
        return super(Nest, self).__getattribute__(name)

    def __getslice__(self, i, j):
        """Slices are not supported at this time."""
        raise TypeError("Nest indices must be integers, not slices.")
    
    def __setslice__(self, i, j, sequence):
        """Slices are not supported at this time."""
        raise TypeError("Nest indices must be integers, not slices.")
    
    def __getitem__(self, index):
        if index is Ellipsis:
            raise TypeError("Nest indices must be integers, not ellipsis.")
        return Nest("%s:%s" % (self, index))

    #
    # Define redis methods aren't automatically handled in __getattr__().
    def delete(self):
        """Simple delete.  Forward to redis instance with self as string."""
        return self.redis.delete(str(self))
        
        
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

