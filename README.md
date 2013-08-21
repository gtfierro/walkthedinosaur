walkthedinosaur
===============

On-demand ORM for SQL database

A wrapper around SQLAlchemy Core queries that aims to provide much of the
functionality gained by using SQLAlchemy's ORM, but without all the loss of
performance!

## Upcoming Features

* flexible query interface, similar (or perhaps equivalent) to SQLAlchemy's ORM
  queries
* return Python objects from queries
* fast! fast fast fast!
    * with benchmarks
* support for concurrent access to databases (readonly, of course), mayhaps
  with some sort of callback structure
