spikedev.button
===============
A module to interact with the ``left``, ``right``, ``center`` and ``connect`` buttons on the SPIKE hub

Example
-------

.. code:: python

    from spikedev.button import ButtonCenter

    button = ButtonCenter()
    button.wait_for_bump()
    print("center button was bumped")

Classes
-------
.. automodule:: spikedev.button
    :members:
    :undoc-members:
    :show-inheritance: