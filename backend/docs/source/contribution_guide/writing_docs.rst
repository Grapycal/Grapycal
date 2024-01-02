Writing Docs
==============

The documentation of the Grapycal project is generated using `Sphinx <https://www.sphinx-doc.org/en/master/>`_.

The API reference is generated from the docstrings of the source code.
The source of the rest of the documentation is in reStructuredText (`.rst`) files located in `backend/docs/source`.

To build the documentation locally, run the following command from the `backend/docs` directory:

.. code-block::

    make clean
    make html

Open `backend/docs/build/html/index.html` in a browser to view the documentation.

Local builds of the documentation are ignored by git. To publish changes to the documentation, push the sources to
``git@github.com:Grapycal/Grapycal.git`` and the documentation will be automatically built and published to https://docs.grapycal.org/.

.. note::

    A good example of how to write sphinx documentation and write docstrings for autoapi is the `Pytorch documentation <https://pytorch.org/docs/stable/index.html>`_.

Generate documentation for an extension
---------------------------------------
.. code-block::

    python extension_docgen/gen.py -e <extension_name> -o <output_file>

For the builtin nodes, run:

.. code-block::

    python extension_docgen/gen.py -e grapycal_builtin -o source/user_manual/grapycal_builtin.rst
