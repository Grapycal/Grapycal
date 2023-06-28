.. Grapycal documentation master file, created by
   sphinx-quickstart on Wed Jun 28 07:16:11 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Grapycal's documentation!
====================================

Pages
-----
- :doc:`First page <usage>`
- :doc:`Second page <guide>`

.. toctree::
   :caption: Guide
   :hidden:

   usage
   guide
   layer

.. This is a caption separating guide and API
   Nothing is inside this because AutoAPI will be inserted into TOC automatically
   The generated API docs will appeared to have a caption "API"
   This is a bit tricky but I think it looks good
.. toctree::
   :caption: API
   :hidden:
