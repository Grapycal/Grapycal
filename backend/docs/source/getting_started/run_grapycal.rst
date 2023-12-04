Run Grapycal
==================

The basic command to run Grapycal is:

.. code-block:: bash

    python -m grapycal

. It should then be avaliable at http://localhost:9001/. 

To specify the workspace file to load from and save to, pass a positional argument to the command:

.. code-block:: bash

    python -m grapycal my_workspace

To specify the port of http server, use the ``--http-port`` option:

.. code-block:: bash

    python -m grapycal --http-port 9002 # the default port is 9001

Next, head over to :doc:`basic_usage`.

Further details
---------------

By default, the Grapycal server includes a HTTP server at http://localhost:9001/ that serves the webpage and a WebSocket server at ws://localhost:8765/ that
handles the interaction between the webpage and the Grapycal server. Once you make changes to the frontend code,
you need to run ``npm run build`` to rebuild the frontend code and refresh the webpage.

Alternatively, you can run the Grapycal server without the HTTP server by passing the ``--no-serve-webpage`` option,
and instead serve the webpage using the webpack dev server. This is useful if you want to develop the frontend code.

.. code-block:: bash

    python -m grapycal --no-serve-webpage

.. code-block:: bash

    cd frontend
    npm run app