Developer Guide
===============

Welcome to the QFinance Developer Guide! This page provides instructions on how to contribute to the development of QFinance, including setting up your environment, code standards, and submitting pull requests.

Getting Started
---------------
1. **Clone the repository:**

   .. code-block:: bash

       git clone https://github.com/BlueVT/QFinance
       cd qfinance

2. **Create a virtual environment:**

   .. code-block:: bash

       python -m venv env
       source env/bin/activate  # On Windows use: env\Scripts\activate

3. **Install dependencies:**

   .. code-block:: bash

       pip install -e .

Development Workflow
--------------------
- Follow the existing coding style outlined in the repository.
- Write comprehensive docstrings for all new classes and functions.
- Run existing tests or add new tests in the `tests/` directory.
- Use `pytest` or your preferred testing framework.

Contributing
------------
- Fork the repository.
- Create a new feature branch:

  .. code-block:: bash

       git checkout -b feature/your-feature-name

- Make your changes, commit with clear messages.
- Push your branch and create a pull request on GitHub.

Code Standards
--------------
- Follow PEP 8 styling.
- Use docstrings to document functions and classes.
- Write tests for new features or bug fixes.

Reporting Issues
----------------
- Use GitHub Issues to report bugs or request features.
- Provide clear steps to reproduce issues and relevant logs.

Thank you for contributing to QFinance!