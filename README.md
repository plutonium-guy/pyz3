# pyz3 - Python Extensions in Zig

<p align="center">
    <em>Write Python extensions in Zig. Fast builds, automatic type conversion, zero hassle.</em>
</p>
<p align="center">
    <em>Like <a href="https://pyo3.rs">PyO3</a> for Rust, but for Zig.</em>
</p>

<p align="center">
<a href="https://pypi.org/project/pyz3" target="_blank">
    <img src="https://img.shields.io/pypi/v/pyz3" alt="Package version">
</a>
<a href="https://docs.python.org/3/whatsnew/3.11.html" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/pyz3" alt="Python version">
</a>
<a href="https://github.com/amiyamandal-dev/pyz3/blob/main/LICENSE" target="_blank">
    <img src="https://img.shields.io/github/license/amiyamandal-dev/pyz3" alt="License">
</a>
</p>

---

## Get Started in 60 Seconds

```bash
pip install pyz3
pyz3 new myproject
cd myproject
pip install -e ".[dev]"
pyz3 develop
pytest
```

That's it. You now have a working Python extension written in Zig.

Try it:

```python
>>> from myproject import _lib
>>> _lib.add(2, 3)
5
>>> _lib.hello("pyz3")
'Hello, pyz3!'
```

## What You Get

```
myproject/
  src/myproject.zig      # Your Zig code (auto-converts to Python module)
  myproject/__init__.py   # Python package
  test/test_myproject.py  # Tests that work with pytest
  pyproject.toml          # Standard Python packaging (hatchling)
  build.zig.zon           # Zig package manifest
```

## Write Zig, Call from Python

### Functions

```zig
const py = @import("pyz3");

/// Exposed as a Python function with automatic type conversion.
pub fn add(args: struct { a: i64, b: i64 }) i64 {
    return args.a + args.b;
}

comptime {
    py.rootmodule(@This());
}
```

```python
>>> import mymodule
>>> mymodule.add(a=2, b=3)  # keyword args work too
5
```

### Classes

```zig
pub const Counter = py.class(struct {
    pub const __doc__ = "A simple counter.";
    const Self = @This();

    value: i64,

    pub fn __init__(self: *Self, args: struct { start: i64 = 0 }) void {
        self.value = args.start;
    }

    pub fn increment(self: *Self) void {
        self.value += 1;
    }

    pub fn get(self: *const Self) i64 {
        return self.value;
    }
});
```

```python
>>> c = mymodule.Counter(start=10)
>>> c.increment()
>>> c.get()
11
```

### Error Handling

```zig
pub fn divide(args: struct { a: i64, b: i64 }) !i64 {
    if (args.b == 0) {
        return py.ZeroDivisionError(root).raise("division by zero");
    }
    return @divTrunc(args.a, args.b);
}
```

### NumPy Integration

```zig
pub fn array_stats() !py.PyObject {
    const np = try py.numpy.getModule(@This());
    defer np.decref();

    const arange_method = try np.getAttribute("arange");
    defer arange_method.decref();
    const arr = try py.call(root, py.PyObject, arange_method, .{ 1, 11 }, .{});
    defer arr.decref();

    const mean_method = try arr.getAttribute("mean");
    defer mean_method.decref();
    return try py.call(root, py.PyObject, mean_method, .{}, .{});
}
```

## Type Conversion

Automatic conversion between Python and Zig types:

| Zig Type | Python Type |
|----------|-------------|
| `bool` | `bool` |
| `i32`, `i64`, `u64` | `int` |
| `f32`, `f64` | `float` |
| `[]const u8` | `str` |
| `struct {...}` | keyword args / `dict` |
| `py.PyObject` | any Python object |
| `!T` | raises Python exception on error |

## CLI Commands

```bash
pyz3 new <name>         # Create new project
pyz3 develop            # Build + install in dev mode
pyz3 run -c "expr"      # Build + run a Python expression
pyz3 run script.py      # Build + run a script
pyz3 watch              # Hot-reload on file changes
pyz3 build-wheel        # Build distribution wheel
pyz3 deploy             # Publish to PyPI
pyz3 bench <module>     # Run benchmarks
pyz3 stubs <module>     # Generate .pyi type stubs
pyz3 memcheck script.py # Memory leak detection
```

## Compatibility

- **Zig**: 0.15.x
- **Python**: 3.11, 3.12, 3.13 (CPython)
- **Platforms**: Linux (x86_64, aarch64), macOS (x86_64, arm64), Windows (x64)

## Installation

```bash
pip install pyz3
```

With distribution extras:

```bash
pip install pyz3[dist]
```

## Cross-Platform Distribution

```bash
# Build for all platforms
pyz3 build-wheel --all-platforms

# Or target specific platforms
ZIG_TARGET=x86_64-linux-gnu pyz3 build-wheel
ZIG_TARGET=aarch64-macos pyz3 build-wheel
```

## Why pyz3?

- **Fast builds** — Zig compiles faster than Rust, comparable to C
- **Zero-cost abstractions** — No runtime overhead from the bridge
- **Cross-compile everything** — Zig's cross-compilation makes multi-platform wheels trivial
- **Small binaries** — Smaller than equivalent Rust/PyO3 extensions
- **SIMD for free** — Zig's auto-vectorization and explicit SIMD support
- **C interop included** — Import any C library with `@cImport`

## Acknowledgments

Hard fork of [ziggy-pydust](https://github.com/fulcrum-so/ziggy-pydust) by [Fulcrum](https://fulcrum.so). Major additions: NumPy integration, enhanced CLI, cross-compilation, improved docs.

## License

Apache License 2.0

## Links

- [ziggy-pydust](https://github.com/fulcrum-so/ziggy-pydust) (original project)
- [Zig](https://ziglang.org) | [NumPy](https://numpy.org) | [PyO3](https://pyo3.rs) (inspiration)
