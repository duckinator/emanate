Configuration
=============

Emanate is configured by `emanate.json` in the source directory. The source
directory defaults to the directory it was executed from.

You can override the source directory with `--source`, and specify a
configuration file at a different location using `--config`.

`emanate.json` contains one object, with the keys `"confirm"`, `"destination"`,
and `"ignore"`.

They control Emanate's behavior in the following ways:

* ``"confirm"``: A boolean value (default: ``true``); if true, ask the user for confirmation before overwriting a file.
* ``"destination"``: A string, specfiying the location to write symlinks to (default: the value of ``Path.home()``).
* ``"ignore"``: A list of file patterns to ignore. This is *appended* to the defaults, which includes things like ``*~`` (temporary files), ``emanate.json`` (to avoid copying the config file to the destination), ``.git/`` (to avoid copying the git repository your dotfiles are in into your home directory), etc.

See `emanate/config.py`_ for the exact default values for ``"ignore"``.

An example configuration file, only adding more things to ignore, may look like:

.. code-block::

      {
        "ignore": ["README.md", "emanate.pyz", "emanate-*.pyz"]
      }

.. _emanate/config.py: https://github.com/duckinator/emanate/blob/main/emanate/config.py
