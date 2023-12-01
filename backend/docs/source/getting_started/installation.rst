Installation
============


Prerequisites:

- Python 3.11 or higher
- npm 9.5.1 or higher (older versions may work, but are not tested)

Install from PyPI
-----------------

This approach is recommended for end users and people who want to develop Grapycal extensions.

.. code-block:: bash

    pip install grapycal grapycal-builtin

Once it's installed, we can go ahead to :doc:`run_grapycal`.

Install from source
-------------------

If you want to contribute to Grapycal itself, you can install it in editable mode from source.

1. Clone the repository

.. code-block:: bash

    git clone git@github.com:eri24816/Grapycal.git
    cd Grapycal
    git submodule update --init --recursive
    git checkout dev

2. Install grapycal backend and grapycal-builtin

.. code-block:: bash

    pip install -e backend -e extensions/grapycal_builtin

3. Install and build grapycal frontend. The dist folder will be created at ``frontend/dist`` then be copied to
``backend/src/grapycal/webpage``. Grapycal backend will serve the frontend resources from there.

.. code-block:: bash

    cd frontend
    npm install
    npm run build

The development setup is now done. you can make changes to the backend and frontend code.

4. When you pull the latest code in the future, you may need to update the submodules and rebuild the frontend.
Otherwise, Grapycal may fail to run.

.. code-block:: bash

    git pull

    git submodule update --init --recursive

    cd frontend
    npm install
    npm run build
