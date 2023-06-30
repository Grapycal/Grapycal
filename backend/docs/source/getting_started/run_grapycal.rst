Run Grapycal
==============



Run the Grapycal App
------------------

The Grapycal python package has been installed in the previous step. Now, we can navigate to an abitrary folder where
we wish to run Grapycal. In this example:

.. code-block:: bash

    mkdir working_dir
    cd working_dir

Then, simply run the Grapycal App by:

.. code-block:: bash

    python -m grapycal

.. note:: If you are using a virtual environment, make sure it is activated before running the above command.
    If you used poetry in the installation step, you can activate the virtual environment by running `poetry shell` in the Grapycal/backend folder.

Run the Web Server
------------------------

.. code-block:: bash

    cd frontend
    npm run app

The web interface is now avaliable at http://localhost:9001/.
Open it in your browser to access Grapycal.