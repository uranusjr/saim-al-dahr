Beam us up, Scotty!
===================

.. testsetup:: *

    import json
    captain_list_json = '["Kirk", "Picard", "Sisko", "Janeway", "Archer"]'

A simple test:

.. doctest::

    >>> 1 + 1
    2

A variable:

.. doctest::

    >>> resistance = 'futile'

And now we can use it:

.. doctest::

    >>> print(resistance)
    futile

This is fine, too:

.. testcode::

    print(resistance)

.. testoutput::

    futile

Testing ``testsetup``:

.. doctest::

    >>> captain_list = json.loads(captain_list_json)
    >>> for captain in captain_list:
    ...     print(captain)
    ...
    Kirk
    Picard
    Sisko
    Janeway
    Archer

A function:

.. doctest::

    >>> def get_ship(name='Enterprise', prefix='', suffix=''):
    ...     comps = [name]
    ...     if prefix:
    ...         comps.insert(0, prefix)
    ...     if suffix:
    ...         comps.append(suffix)
    ...     return ' '.join(comps)
    ...

Using a previously-defined function:

.. doctest::

    >>> print(get_ship(prefix='USS', suffix='(NCC-1701)'))
    USS Enterprise (NCC-1701)

To boldly go where no-one has gone before:

.. doctest::

    >>> def get_captains(captains=None):
    ...     if captains is None:
    ...         captains = captain_list
    ...     return captains[:]
    ...

Let's use it.

.. testcode::

    for captain in get_captains(['Spock', 'Sulu', 'Riker']):
        print(captain)

.. testoutput::

    Spock
    Sulu
    Riker

Of course, ``doctest`` block also works.

.. doctest::

    >>> for captain in get_captains():
    ...     print(captain)
    ...
    Kirk
    Picard
    Sisko
    Janeway
    Archer

Another function, this one using both user-defined global variable *and* a builtin global:

.. testcode::

    def count_captains(captains=None):
        if captains is None:
            captains = captain_list
        return len(captains)

.. doctest::

    >>> count_captains(['Sulu'])
    1

.. testcode::

    print(count_captains())

.. testoutput::

    5
