MongoDBAggregation
==================
A block for finding and grouping multiple documents together.

Properties
----------
- **collection**: Expression property. Collection name. Can be of the form `collection.subcollection.value` to access sub collections.
- **connection**: Configurables for which Mongo Database to connect to.
- **creds**: Mongo username and password needed to connect to database.
- **database**: Database name.
- **enrich**: If true, include original input signal in output signal.
- **pipeline**: The pipelines used to transform the documents into an aggregated result.

Inputs
------

Outputs
-------

Commands
--------

MongoDBBulkInsert
=================
Exactly the same as MongoDB, except it stores data much faster. This is because it's `collection` property is a String property, not an Expression property. This speeds things up, as it doesn't have to evaluate it for every insert.

Properties
----------
- **collection**: Expression property. Collection name. Can be of the form `collection.subcollection.value` to access sub collections.
- **connection**: Configurables for which Mongo Database to connect to.
- **creds**: Mongo username and password needed to connect to database.
- **database**: Database name.
- **enrich**: If true, include original input signal in output signal.
- **with_type**: If `True`, includes the signal type in the document.

Inputs
------

Outputs
-------

Commands
--------

MongoDBCommand
==============
A block for running mongo commands

Properties
----------
- **collection**: Expression property. Collection name. Can be of the form `collection.subcollection.value` to access sub collections.
- **command**: Command to run against database. If command is a string then the command {*command*: 1} will be sent. Otherwise, command must be a dict and will be sent as is.
- **connection**: Configurables for which Mongo Database to connect to.
- **creds**: Mongo username and password needed to connect to database.
- **database**: Database name.
- **enrich**: If true, include original input signal in output signal.

Inputs
------

Outputs
-------

Commands
--------

MongoDBFind
===========
A block for running `find` against a mongodb.

Properties
----------
- **collection**: Expression property. Collection name. Can be of the form `collection.subcollection.value` to access sub collections.
- **condition**: A dictionary form of a find expression. This is an expression property that can evaluate to a dictionary or be a parseable JSON string
- **connection**: Configurables for which Mongo Database to connect to.
- **creds**: Mongo username and password needed to connect to database.
- **database**: Database name.
- **enrich**: If true, include original input signal in output signal.
- **limit**: Max number of documents returned by find query.
- **sort**: Properties to sort the data by.

Inputs
------

Outputs
-------
- **no_results**: Output signal when no results are found.
- **results**: Output signal containing the `find` results from Mongo.

Commands
--------

MongoDBInsert
=============
Stores input signals in a mongo database. One document will be inserted into the database for each input signal.

Properties
----------
- **collection**: Expression property. Collection name. Can be of the form `collection.subcollection.value` to access sub collections.
- **connection**: Configurables for which Mongo Database to connect to.
- **creds**: Mongo username and password needed to connect to database.
- **database**: Database name.
- **enrich**: If true, include original input signal in output signal.
- **with_type**: If `True`, includes the signal type in the document.

Inputs
------

Outputs
-------

Commands
--------

MongoDBRemove
=============
Stores input signals in a mongo database. One document will be removed from the database for each input signal.

Properties
----------
- **collection**: Expression property. Collection name. Can be of the form `collection.subcollection.value` to access sub collections.
- **condition**: 
- **connection**: Configurables for which Mongo Database to connect to.
- **creds**: Mongo username and password needed to connect to database.
- **database**: Database name.
- **enrich**: If true, include original input signal in output signal.
- **only_one**: If true, will only remove one document.

Inputs
------

Outputs
-------

Commands
--------

MongoDBUpdate
=============
Stores input signals in a mongo database. One document will be updated in the database for each input signal.

Properties
----------
- **collection**: Expression property. Collection name. Can be of the form `collection.subcollection.value` to access sub collections.
- **connection**: Configurables for which Mongo Database to connect to.
- **creds**: Mongo username and password needed to connect to database.
- **database**: Database name.
- **document**: Dictionary of what the document should be updated to.
- **enrich**: If true, include original input signal in output signal.
- **multi**: If true update multiple documents.
- **spec**: Document ID to update
- **upsert**: If true, update attempts that can't find the correct document ID will insert a new document.

Inputs
------

Outputs
-------

Commands
--------

