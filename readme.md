# CDJS (Custom Datetime JSON Serializer)

`cdjs` is an extension for [orjson](https://github.com/ijl/orjson) to serialize datetime (and other types) in a fast custom way.

By default [orjson](https://github.com/ijl/orjson) serializes datetime according to RFC 3339 format which sometimes may not suit. 
[orjson](https://github.com/ijl/orjson) provides a mean to process datetime using custom serializer (via `OPT_PASSTHROUGH_DATETIME` flag and via `default=custom_datetime_serializer`). 
Serializers implemented in Python are usually not fast enough, that's the reason behind implementation of the custom datetime serializer written in Rust to gain optimal speed.

Aside from datetimes, `cdjs` is an attempt to port `bson.json_util.default()` and to use with `orjson` as a default handler.

At the moment serialization of the following types are supported:

- `datetime`
- `bson.ObjectId`

## Example

```
import datetime
import hashlib

from bson import ObjectId
from cdjs import serialize
import orjson

mydata = {
    '_id': ObjectId(hashlib.md5(b'test').hexdigest()[:24]),
    'date': datetime.datetime(2021, 1, 1, hour=0, minute=4, second=36, microsecond=123000)
}
orjson.dumps(mydata, option=orjson.OPT_PASSTHROUGH_DATETIME, default=serialize)

# b'{"_id":{"$oid":"098f6bcd4621d373cade4e83"},"date":{"$date":"2021-01-01T00:04:36.123Z"}}'
```

## Benchmarks

To run benchmark:

```
pip install -r bench-requirements.txt
python tests/benchmark.py --help
python tests/benchmark.py --scenario utc_dates
```

![UTC Dates Only Benchmark](https://github.com/ofhellsfire/cdjs/blob/master/assets/images/orjson_plus_cdjs_benchmark.png)

## Installation

```
pip install cdjs
```

## Building

### To make a develop build

**NOTE:** Develop build doesn't enable optimizations, hence the result may work slow.

```
python ./setup.py develop
```

### To make a release build

Pre-requisites

```
# switch to nightly channel
RUSTUP_USE_CURL=1 rustup default nightly-2021-01-31
pip install maturin
```

To compile, package and publish to PyPI

```
maturin build --no-sdist --release --strip --manylinux off
maturin publish
```

## Testing

To run tests

```
python -m unittest -v tests.test_serialization
```

## Python/OS Version Support

- Python 3.6 (tested)
- Python 3.7+ (not tested)
- Linux (with GLib 2.17+)

