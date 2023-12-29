.. Grapycal documentation master file, created by
   sphinx-quickstart on Wed Jun 28 07:16:11 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. figure:: https://i.imgur.com/aU1ZUZ7.png
    :align: center
    :width: 100%

Welcome to Grapycal
====================================

Grapycal is a graphical and interactive programming language. It allows users to manipulate and assemble programs by dragging and clicking blocks or graphs representing various built-in and custom Python functions.

`Installation <getting_started/installation.html>`_

`Run Grapycal <getting_started/run_grapycal.html>`_

`Contribution Guide <contribution_guide/contribution.html>`_


`Website <https://www.grapycal.org>`_ | `GitHub Repository <https://github.com/eri24816/Grapycal>`_ | `PyPI <https://pypi.org/project/grapycal/>`_ | `Discord <https://discord.gg/adNQcS42CT>`_



   In our daily lives, countless ideas emerge in our minds, only to be dismissed because the perceived cost of realizing them is too high. Over time, sadly, we tend to forget our inherent creativity.

   The mission of Grapycal is to push more ideas over the line to be worthy of trying out.

.. `Grapycal v0.2.0 whats new <https://github.com/eri24816/Grapycal/blob/main/docs/v0.2.0.md>`_

.. toctree::
   :caption: Getting Started
   :hidden:

   getting_started/installation
   getting_started/run_grapycal
   getting_started/basic_usage
   getting_started/extension

.. toctree::
   :caption:  User Manual
   :hidden:

   .. user_manual/overview

   user_manual/node
   user_manual/grapycal_builtin

   .. user_manual/execution_of_graph

.. toctree::
   :caption: Contribution Guide
   :hidden:

   contribution_guide/contribution
   contribution_guide/project_overview
   contribution_guide/define_a_node
   contribution_guide/examples_of_node_definition
   
   .. developer_guide/attribute
   .. developer_guide/port
   .. developer_guide/controls

   developer_guide/writing_docs

.. This is a caption separating guide and API
   Nothing is inside this because AutoAPI will be inserted into TOC automatically
   The generated API docs will appeared to have a caption "API"
   This is a bit tricky but I think it looks good
.. toctree::
   :caption: API
   :hidden: