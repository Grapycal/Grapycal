Installation
============

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

2. Install grapycal 

.. code-block:: bash

    cd backend
    pip install -e .

3. Install grapycal-builtin

.. code-block:: bash

    cd grapycal_builtin
    pip install -e .

4. Install frontend dependencies

This step is optional. If you do not intend to modify the frontend, you can skip this step
and use the pre-built frontend content include in the grapycal python package.

.. code-block:: bash

    cd ../frontend
    rm package-lock.json # I don't know why but it doesn't work with it
    npm install