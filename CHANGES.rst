2011-05-31 version 0.3.9:

  * Added initial support for G0-1 charsets (mappings taken from ``tty``
    kernel driver) and SI, SO escape sequences.
  * Changed ``ByteStream`` to support fallback encodings -- it nows
    takes a list of ``(encoding, errors)`` pairs and traverses it
    left to right on ``feed()``.
  * Switched to ``unicode_literals`` -- one step closer to Python3.


2011-05-23 version 0.3.8:

  * Major rewrite of ``Screen`` internals -- highlights: inherits from
    ``list``; each character is represented by ``namedtuple`` which
    also holds SGR data.
  * Numerous bugfixes, especialy in methods, dealing with manipulating
    character attributes.


2011-05-16 version 0.3.7:

  * Added support for ANSI color codes, as listed in
    ``man console_codes``. Not implemnted yet: setting alternate font,
    setting and resetting mappings, blinking text.
  * Added a couple of trivial usage examples in the `examples/` dir.
