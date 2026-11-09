# Windows device filename aliases

Export filename repair must reserve COM/LPT followed by ASCII digits 1 through 9
and the Windows aliases U+00B9, U+00B2 and U+00B3. This applies before an extension,
including multi-dot names, and is case-insensitive. Prefix repaired names with an
underscore; reject them in the backend bare-filename validator. Keep the backend
and Electron rules aligned without normalizing unrelated Unicode names.

Reference: https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file

Dependency-free regression commands from the repository root:

    node --test tests/frontend/portableFilename.test.mjs
    python -B tests/test_windows_device_aliases.py

The Node command requires a Node version with native TypeScript stripping
(validated with Node 26). Both tests exercise pure string helpers only. The Python
test loads the module directly to avoid application and pytest fixture startup.
They do not write device paths or access user data, sockets, models or processes.
These targeted tests do not replace the full release or cross-platform UI gates.
