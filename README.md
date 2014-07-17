MongoDB
===========

Stores input signals in a mongo database. One document will be inserted into the database for each input signal.

Properties
--------------

-   **host**: Mongo server host.
-   **port**: Mongo server port.
-   **database**: Database name.
-   **colleciton**: Expression property. Collection name.
-   **with_type**: If True, includes the signal type in the document.

Dependencies
----------------

-   [pymongo](https://pypi.python.org/pypi/pymongo/)

Commands
----------------
None

Input
-------
One document will be inserted into the database for each input signal.

Output
---------
None
