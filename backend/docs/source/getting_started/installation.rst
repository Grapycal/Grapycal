Installation
============

1. Clone the repository

.. code-block:: bash

    git clone git@github.com:eri24816/Grapycal.git
    cd Grapycal

2. Install backend dependencies...

a. via pip (recommended)

.. code-block:: bash

    cd backend
    pip install -e .

b. via poetry

.. code-block:: bash

    cd backend
    poetry install

    

3. Install frontend dependencies

.. code-block:: bash

    cd ../frontend
    rm package-lock.json # I don't know why but it doesn't work with it
    npm install

