MongoDB
===========

Stores input signals in a mongo database. One document will be inserted into the database for each input signal.

Properties
--------------

-   **host**: Mongo server host.
-   **port**: Mongo server port.
-   **database**: Database name.
-   **collection**: Expression property. Collection name. Can be of the form `collection.subcollection.value` to access sub collections
-   **with_type**: If `True`, includes the signal type in the document.

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

----------------

MongoBulkInsert
===========

Exactly the same as MongoDB, except it stores data much faster. This is because it's `collection` property is a String property, not an Expression property. This speeds things up, as it doesn't have to evaluate it for every insert.

Properties
--------------

-   **host**: Mongo server host.
-   **port**: Mongo server port.
-   **database**: Database name.
-   **collection**: String property. Collection name. Can be of the form `collection.subcollection.value` to access sub collections
-   **with_type**: If `True`, includes the signal type in the document.

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
