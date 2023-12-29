Installation
============


Install from PyPI
-----------------

This approach is recommended for end users and people who want to develop Grapycal extensions.

Prerequisites:

- Python 3.11

.. code-block:: bash

    pip install grapycal grapycal-builtin


Once it's installed, we can go ahead to :doc:`run_grapycal`.

Optionally you can also install existing extensions from PyPI. For example:

.. code-block:: bash

    pip install grapycal-torch


Install from source
-------------------

If you want to contribute to Grapycal itself, you can install it in editable mode from source.

Prerequisites:

- Python 3.11
- npm 9.5.1 or higher (older versions may work, but are not tested)

1. Clone the repository

.. code-block:: bash

    git clone git@github.com:Grapycal/Grapycal.git
    cd Grapycal
    git submodule update --init --recursive
    git checkout dev

2. Install grapycal backend and grapycal-builtin

.. code-block:: bash

    pip install -e backend -e extensions/grapycal_builtin

3. Install pre-commit

.. code-block:: bash

    pip install pre-commit
    pre-commit install --install-hooks

4. Install and build grapycal frontend. The dist folder will be created at ``frontend/dist`` then be copied to
``backend/src/grapycal/webpage``. Grapycal backend will serve the frontend resources from there.

.. code-block:: bash

    cd frontend
    npm install
    npm run build

The development setup is now done. you can make changes to the backend and frontend code.

5. When you pull the latest code in the future, you may need to update the submodules and rebuild the frontend.
Otherwise, Grapycal may fail to run.

.. code-block:: bash

    git pull

    git submodule update --init --recursive

    cd frontend
    npm install
    npm run build
