from hashlib import sha256

from appdirs import user_cache_dir

from plums.commons.path import Path
from .path import PathResolver
from ..io.json import load, dump


class NotInCacheError(Exception):
    """Exception raised by the |DatasetCache| if a requested entry is not in the cache.

    Args:
        prefix (str): The cache prefix where the entry was looked-up.
        key (str): The cache index which was not found.

    """

    def __init__(self, prefix, key):
        self.prefix = str(prefix)
        self.key = key
        super(NotInCacheError, self).__init__('Dataset {}-{} was not found in cache.'.format(prefix, key))


class DatasetCache(object):
    """A wrapper class around a dataset cache folder.

    Args:
        prefix (str): A cache prefix to cluster all related entry together and avoid eventual collisions.

    """

    def __init__(self, prefix):
        # Store parameters
        self._path = Path(user_cache_dir(appname='plums')) / prefix
        self._resolver = PathResolver('{key}.json')

        # Create prefix if it does not exist
        self._path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def hash(*keys):
        """Compute a SHA256 hash string from a tuple of strings.

        Args:
            *keys (str): String keys to hash.

        Returns:
            str: A SHA256 digest of the provided string keys.

        """
        return sha256((''.join(keys)).encode('utf8')).hexdigest()

    def retrieve(self, *keys):
        """Retrieve a JSON-stored dataset from the cache prefixed folder.

        Args:
            *keys (str): The requested dataset string keys.

        Returns:
            Any: The deserialized JSON-stored dataset object corresponding to the provided keys.

        Raises:
            NotInCacheError: If the provided keys does not match any entry in the cache prefixed folder.

        """
        key = self.hash(*keys)
        index = {path.match['key']: path for path in self._resolver.find(self._path)}

        if key not in index:
            raise NotInCacheError(self._path[-1], key)

        return load(index[key])

    def cache(self, data, *keys):
        """Store a JSON-stored dataset in the cache prefixed folder.

        Args:
            data (Any): A JSON-serializable object to store in the cache.
            *keys (str): The requested dataset string keys.

        """
        # Dump cache
        dump(data, self._path / '{}.json'.format(self.hash(*keys)))
