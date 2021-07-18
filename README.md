# stylechecker
A very simple and minimalistic stylechecker for C++/CMake projects

The type of the file is determined by a regular expression.
Based on that type, a number of checks are performed.

Basic checks:
 - No trailing whitespace
 - No tabs
 - No \r\n linebreaks
 - single blank line at EoF

C++-checks:
 - No bad C++ patterns (configurable)
 - Limit line length (configurable soft and hard limit)

The basic checks are performed on `*.cpp`, `*.h`, `CMakeLists.txt`, `*.in`, `*.yml`, `*.sh`, `*.md`, `*.qss`, `*.py` files.
The C++-checks are performed on `*.cpp` and `*.h` files only.

The `main.py` script has a convenient command line interface and exists with `0` if all files comply and `1` if one or more files don't comply.
The line length limit and bad C++ patterns can be configured with a JSON file.


Example usage: `stylechecker/main.py --root src --options stylechecker-options.json`
