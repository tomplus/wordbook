Wordbook
========

DICT Python Client

.. image:: https://img.shields.io/pypi/v/wordbook.svg
    :target: https://pypi.python.org/pypi/wordbook
.. image:: https://img.shields.io/pypi/pyversions/wordbook.svg
    :target: https://pypi.python.org/pypi/wordbook
.. image:: https://img.shields.io/pypi/l/wordbook.svg
    :target: https://pypi.python.org/pypi/wordbook
.. image:: https://travis-ci.org/tomplus/wordbook.svg?branch=master
    :target: https://travis-ci.org/tomplus/wordbook
.. image:: https://coveralls.io/repos/github/tomplus/wordbook/badge.svg?branch=master
    :target: https://coveralls.io/github/tomplus/wordbook?branch=master


More details
-----------

Wordbook is a Python asynchronous library to query Dict servers. It implements the main parts of DICT protocol (`RFC 2229 <https://tools.ietf.org/html/rfc2229>`_)

The library consists two classes:

* **DictBase**: which implements commands from RFC2229.
* **Wordbook**: which exposes more abstract methods to find a definition within dictionaries.

Both classes are asynchronous and require Python 3.5+.


Installation
------------

To install from pypi

.. code-block:: bash

   $ sudo pip install wordbook

or from source:

.. code-block:: bash

    $ sudo python setup.py install


Examples
--------

Getting information from a server using the *DictBase* class:

.. code-block:: pycon

   import asyncio
   import wordbook


   async def main():
       dictb = wordbook.DictBase()
       await dictb.connect()
       await dictb.client('wordbook/server-status.py')
       info = await dictb.show_server()
       for line in info:
           print(line)


   if __name__ == "__main__":
       loop = asyncio.get_event_loop()
       loop.run_until_complete(main())
       loop.close()

Output:

.. code-block::

   dictd 1.12.1/rf on Linux 4.10.0-30-generic
   On LT19758: up 07:55:45, 5 forks (0.6/hour)

   Database      Headwords         Index          Data  Uncompressed
   gcide              203645       3859 kB         12 MB         38 MB
   wn                 147311       3002 kB       9247 kB         29 MB
   moby-thesaurus      30263        528 kB         10 MB         28 MB


Getting definition of word *mock* using the *WordBookDatabase* class: 

.. code-block:: pycon

   import asyncio
   import wordbook

   async def main():
       wb = wordbook.WordBookDatabase('wn')
       await wb.connect()
       lines = await wb.define('mock')
       for line in lines:
           print(line)
        
   if __name__ == "__main__":
       loop = asyncio.get_event_loop()
       loop.run_until_complete(main())
       loop.close()

Output:

.. code-block::

   ["mock" wn "WordNet (r) 3.0 (2006)"]
   mock
       adj 1: constituting a copy or imitation of something; "boys in
              mock battle"
       n 1: the act of mocking or ridiculing; "they made a mock of him"
       v 1: treat with contempt; "The new constitution mocks all
            democratic principles" [syn: {mock}, {bemock}]
       2: imitate with mockery and derision; "The children mocked their
          handicapped classmate"

You can find more examples in directory *example/*.


Resources
---------

* The DICT Development Group - http://www.dict.org/
* RFC 2229: https://tools.ietf.org/html/rfc2229
