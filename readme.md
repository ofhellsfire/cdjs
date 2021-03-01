# CDJS (Custom Datetime JSON Serializer)

`cdjs` is an extension for [orjson](https://github.com/ijl/orjson) to serialize datetime in a custom way.

By default [orjson](https://github.com/ijl/orjson) serializes datetime according to RFC 3339 format which sometimes may not suit. 
[orjson](https://github.com/ijl/orjson) provides a mean to process datetime using custom serializer (via `OPT_PASSTHROUGH_DATETIME` flag and via `default=custom_datetime_serializer`). 
Serializers implemented in Python are usually not fast enough, that's the reason behind implementation of the custom datetime serializer written in Rust to gain optimal speed.

## Example

```
import datetime
import orjson
from cdjs import serialize_date

mydate = datetime.datetime(2021, 1, 1, hour=0, minute=4, second=36, microsecond=123000)
orjson.dumps(mydate, option=orjson.OPT_PASSTHROUGH_DATETIME, default=serialize_date)
```

## Benchmarks

TODO

## Installation

```
pip install cdjs
```

## Building

### To make a develop build

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

