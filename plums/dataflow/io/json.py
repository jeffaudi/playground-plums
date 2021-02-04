# JSON backends import
import json

try:
    import rapidjson
    _HAS_RAPIDJSON = True
except ImportError:
    _HAS_RAPIDJSON = False

try:
    import simplejson
    _HAS_SIMPLEJSON = True
except ImportError:
    _HAS_SIMPLEJSON = False
try:
    import orjson
    _HAS_ORJSON = True
except ImportError:
    _HAS_ORJSON = False


# JSON IO operation
def load(filepath):
    """Open a JSON file on disk as a Python structure.

    Args:
        filepath (|Path|): The path to the image file on disk.

    Returns:
        Any: The parsed Python structure.

    """
    # Backend selection (Fastest to slowest).
    if _HAS_ORJSON:
        with open(str(filepath), 'rb') as f:
            return orjson.loads(f.read())

    if _HAS_RAPIDJSON:
        with open(str(filepath), 'rb') as f:
            return rapidjson.load(f, number_mode=rapidjson.NM_NATIVE)

    with open(str(filepath), 'r') as f:
        if _HAS_SIMPLEJSON:
            return simplejson.load(f)
        else:
            return json.load(f)


def dump(data, filepath):
    """Save a Python structure as a JSON file on disk.

    Args:
        filepath (|Path|): The path to the image file on disk.
        data (Any): The Python structure to save a JSON object.

    """
    # Backend selection (Fastest to slowest).
    if _HAS_ORJSON:
        with open(str(filepath), 'wb') as f:
            f.write(orjson.dumps(data))
            return

    if _HAS_RAPIDJSON:
        with open(str(filepath), 'wb') as f:
            rapidjson.dump(data, f, number_mode=rapidjson.NM_NATIVE)
            return

    with open(str(filepath), 'w') as f:
        if _HAS_SIMPLEJSON:
            simplejson.dump(data, f)
        else:
            json.dump(data, f)
