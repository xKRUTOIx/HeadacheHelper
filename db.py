import redis
from collections import defaultdict

_redis_connection = defaultdict(lambda: None)


def get_redis_connection(decode_responses=True):
    """
    Get Redis connection object. Reuse the previous connection if it is available.

    :rtype: redis.StrictRedis
    """

    global _redis_connection

    if _redis_connection[decode_responses] is None:
        _redis_connection[decode_responses] = redis.StrictRedis(host='localhost', port=6379, db=3,
                                                                decode_responses=decode_responses)

    return _redis_connection[decode_responses]
