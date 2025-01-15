.. role:: console(code)
   :language: console

Development
===========
This chapter describes how to set up a development environment to run and develop Open Pectus.

.. contents:: Table of Contents
  :local:
  :depth: 3

Ecosystem
---------
.. _Github: https://github.com/Open-Pectus/Open-Pectus/
.. _Github Actions: https://github.com/Open-Pectus/Open-Pectus/tree/main/.github/workflows
.. _Github Container Registry: https://github.com/Open-Pectus/Open-Pectus/pkgs/container/open-pectus
.. _Read the Docs: https://docs.openpectus.org/latest/
.. _Python Packaging Index: https://pypi.org/project/openpectus/

* Source code is managed at Github_
* Issues are tracked at Github_
* Continuous Integration tasks are performed using `Github Actions`_
* Docker images are published to the `Github Container Registry`_
* Documentation is built by `Read the Docs`_
* Python packages are published to the `Python Packaging Index`_

Frontend Setup
--------------
Prerequisites: Node 20 (LTS) must be installed.

Follow the steps below to install packages and build the frontend.

.. code-block:: console

   cd Open-Pectus/openpectus/frontend
   npm ci
   npm run build


Backend Setup
-------------
.. _Download Miniconda: https://docs.conda.io/en/latest/miniconda.html
.. _ANTLR4 grammar syntax support: https://github.com/mike-lischke/vscode-antlr4
.. _Sentry: https://sentry.io

Prerequisites:

* (Optional) A conda installation is highly recommended although it is possible to do without. `Download Miniconda`_.
* (Optional) Java SE SDK is needed for parser generation when updating P-code grammar.
* (Optional) The simplest way to get going using VS Code is this:

   #. Install Java
    
      :console:`conda install -c conda-forge openjdk`
   #. Install VS Code extension `ANTLR4 grammar syntax support`_.
      This should cause the Antlr plugin to automatically regenerate parser code whenever pcode.g4 is modified. 
   #. openjdk-21.0.2 is known to work.


All the following commands can only be run from within the conda prompt, and from the `Open-Pectus` folder.

#. Create a new conda environment and install all dependencies:

   :console:`conda env create --name openpectus --file=environment.yml`

#. Activate the created pectus conda environment:

   :console:`conda activate openpectus`

#. Install open pectus in the environment:

   :console:`pip install -e ".[development]"`

#. (Optional) Set the :console:`SENTRY_DSN` environment variable:

   To enable the Sentry_ logger, the :console:`SENTRY_DSN` environment variable needs to be set.
   Save the value as an environment variable on your developer pc:

   :console:`setx SENTRY_DSN value`


Documentation Setup
-------------------
#. Create a new conda environment and install all dependencies:

   :console:`conda env create --name openpectusdocs --file=environment.yml`

#. Activate the created pectus conda environment:

   :console:`conda activate openpectusdocs`

#. Install open pectus in the environment:

   :console:`pip install -e ".[docs]"`

#. Change directory to the docs directory

   :console:`cd docs`

#. (Optional) Spell check

   :console:`make.bat spelling` on Windows
   
   :console:`make spelling` on Linux

#. Build documentation

   :console:`make.bat html` on Windows
   
   :console:`make html` on Linux

The built documentation is in :console:`docs/html`.

Build status for pull requests and pushes to :console:`main` branch on Github can be monitored at https://app.readthedocs.org/projects/open-pectus/builds/.

Other Commands
--------------

Update conda environment
^^^^^^^^^^^^^^^^^^^^^^^^
To update an existing conda environment with all dependencies (e.g. when :console:`requirements.txt` has changed):

.. code-block:: console

   conda env update -p=./conda --file=environment.yml --prune

Build Distribution
^^^^^^^^^^^^^^^^^^
.. _Github Actions workflow: https://github.com/Open-Pectus/Open-Pectus/blob/main/.github/workflows/combined-workflows.yml

Docker and Pypi builds are normally built via a `Github Actions workflow`_. To build it in the development environment:

.. code-block:: console

   python -m build -o openpectus/dist

.. note::
   To include the frontend in the build, copy the contents of :console:`openpectus/frontend/dist` to :console:`openpectus/aggregator/frontend-dist` before building.

Alembic Database Migrations
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. _SQLAlchemy documentation: https://alembic.sqlalchemy.org/en/latest/autogenerate.html#what-does-autogenerate-detect-and-what-does-it-not-detect
.. _it doesn't support altering a column besides renaming it: https://sqlite.org/lang_altertable.html
.. _"batch" migrations: https://alembic.sqlalchemy.org/en/latest/batch.html
.. _does NOT support transactional DDL: https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#transactional-ddl
.. _only the last change will require cleanup: https://github.com/sqlalchemy/alembic/issues/755#issuecomment-729110204
.. _workaround: https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#serializable-isolation-savepoints-transactional-ddl
.. _it has some severe downsides: https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support

In the following it is described how to create a new migration script.

Change the database model(s) in :console:`openpectus/aggregator/data/models.py` first, then run:

.. code-block:: console

   cd openpectus/aggregator
   alembic revision --autogenerate -m "<migration script name>"


This will create a new migration script in :console:`aggregator/data/alembic/versions/` based on the model changes.  
You **must** check that the changes within are acceptable, and change them if they are not.  
It is a good idea to ensure the downgrade step will leave data as it was.  
See `SQLAlchemy documentation`_ for what autogenerate will and will not detect.

You can then test your migration with :console:`alembic upgrade head` and :console:`alembic downgrade -1`.  
:console:`alembic upgrade head` is automatically run when aggregator starts, in :console:`openpectus/aggregator/main.py` :console:`main()` function.

Currently, automatic tests touching the database do not use the migration scripts, so you can't trust those to verify the migrations.

SQLite has some severe limitations on what schema changes it supports. e.g. `it doesn't support altering a column besides renaming it`_. 
To alter e.g. a column type, you will need to create a new table, copy the data over, and then drop the old one.
Alembic supports this with `"batch" migrations`_.
The autogenerate feature has been configured to generate with batch migrations as described here https://alembic.sqlalchemy.org/en/latest/batch.html#batch-mode-with-autogenerate

The python driver for SQLite (pysqlite) `does NOT support transactional DDL`_, i.e. running schema changes in a transaction so a failure during a schema change will roll all the changes back. 
Alembic will run each migration separately, so if something fails, `only the last change will require cleanup`_.
There is possibly a `workaround`_ for this but Alembic would likely still not use it correctly as its behavior in :console:`alembic/runtime/migration.py` depends on the :console:`transactional_ddl` flag set to :console:`False` in :console:`alembic/ddl/sqlite.py`.

Even though the autogenerated migrations will include foreign key constraints, they are not enforced by SQLite by default, and while enabling them is possible in SQLAlchemy, `it has some severe downsides`_.

Even though :console:`Mapped[]` Python enum types produce Alembic Enums in the autogenerated migrations, they will not actually be enforced on database level without manually writing some CHECK constraints, or foreign keys to an enum table. It's unclear whether this would be worth the added complexity and management.

Running Open Pectus
-------------------
It is possible to run the aggregator as-is or in a Docker container. The engine can only be run as-is.

Aggregator
^^^^^^^^^^
Run Aggregator to serve frontend from its default build directory. This also starts the WebSocket protocol allowing Engines to connect.

.. code-block:: console

   cd Open-Pectus
   pectus-aggregator -fdd .\openpectus\frontend\dist\

When Aggregator is running, the aggregator services are available, including:

- Frontend:       http://localhost:9800/
- OpenAPI UI:     http://localhost:9800/docs
- OpenAPI spec:   http://localhost:9800/openapi.json

To start aggregator services in Docker, run the following commands:

.. note::
   This depends on the frontend and backend builds being up-to-date.

.. code-block:: console

   cd Open-Pectus/openpectus
   docker compose up --build


pectus-aggregator Command Reference
```````````````````````````````````

.. argparse::
   :filename: ../openpectus/aggregator/main.py
   :func: get_arg_parser
   :prog: pectus-aggregator

Engine
^^^^^^
Run Engine to connect a local engine to the Aggregator above:

.. code-block:: console

   cd Open-Pectus
   pectus-engine --aggregator_host localhost --aggregator_port 9800


When the container is running, the aggregator services are available, including:

- Frontend:       http://localhost:8300/
- OpenAPI UI:     http://localhost:8300/docs
- OpenAPI spec:   http://localhost:8300/openapi.json

.. _pectus_engine_command_reference:

pectus-engine Command Reference
```````````````````````````````

.. argparse::
   :filename: ../openpectus/engine/main.py
   :func: get_arg_parser
   :prog: pectus-engine

Build Validation
----------------
Linting and type checking is configured for Open Pectus.

Linting
^^^^^^^
Open Pectus python code is linted using flake8 which is configured in :console:`openpectus/.flake8`:

.. code-block:: console

   cd Open-Pectus/openpectus
   flake8

Type Checking
^^^^^^^^^^^^^
Python code is type checked using pyright which is configured in :console:`pyproject.toml`:

.. code-block:: console

   cd Open-Pectus/openpectus
   pyright
   # If pyright complains about being out of date:
   # pip install -U pyright

Code generation from API Specification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The frontend generates and uses typescript skeleton interfaces from the aggregator API specification.

To ensure that the implemented backend, the API specification file and the typescript interfaces all match, the flow for modification is as follows:

#. A change is made in the Aggregator API implementation.
#. The script `generate_openapi_spec_and_typescript_interfaces.sh` must be manually invoked. This updates the API spec file and generates updated typescript interfaces from it.
#. The frontend build must be run to check the updated interfaces. If the frontend build fails, the build server build will fail. This indicates an integration error caused by an incompatible API change. This should be fixed before the branch is merged, either by updating the frontend to support the API change or by reworking the API change to be compatible with the frontend.
#. Steps 1-3 must be repeated until both frontend and backend build successfully.
#. All changes must be committed to Git.

To ensure that step 2 is not forgotten, the aggregator test suite contains a test that generates a new API specification file and checks that it matches the specification file last generated by the script. If it doesn't, the test fails and with it the backend build.

Version Numbering
-----------------
Open Pectus adopts the major-minor-patch version number format.
A new package is published to Pypi on each push to :console:`main` with the least significant version digit being the Github Actions run number.
The least significant digit is :console:`dev` in the source code to distinguish from releases.
If relevant, the major and minor digits must be updated manually in the following files:

* :console:`openpectus/__init__.py`
* :console:`openpectus/frontend/src/app/api/core/OpenAPI.ts`
* :console:`openpectus/frontend/openapi.json`
