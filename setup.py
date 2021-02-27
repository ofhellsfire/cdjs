from setuptools import setup
from setuptools_rust import Binding, RustExtension

setup(
    name="cdjs",
    version="0.1.0",
    rust_extensions=[RustExtension("cdjs.cdjs", binding=Binding.PyO3)],
    packages=["cdjs"],
    # rust extensions are not zip safe, just like C-extensions.
    zip_safe=False,
)

