The first time you run, you should execute something like the following:

.. code-block:: bash

    python run.py -u 'http://export.arxiv.org/api/query?search_query=cat:astro-ph&max_results=2000&sortBy=lastUpdatedDate&sortOrder=descending'

After that, you can just do the following every day:

.. code-block:: bash

    python run.py
