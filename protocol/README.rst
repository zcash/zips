==============================
 Zcash Protocol Specification
==============================

Build dependencies on Debian-based systems include, at least:

.. code::

   apt-get install texlive texlive-science texlive-fonts-extra \
     texlive-generic-recommended texlive-bibtex-extra biber latexmk


Building
--------

Use:

* ``make sapling`` to make the draft specification for the Overwinter and
  Sapling upgrades (``sapling.pdf``);
* ``make sprout`` to make a version of the specification that does not
  include Overwinter or Sapling.

By default these use ``latexmk``, which does not work on all systems.
Use ``make nolatexmk-pdf`` or ``make nolatexmk-sapling`` if you run into
problems with ``latexmk``, but that is not the preferred way of building
because it may not run ``pdflatex`` enough times.

There is also support for using the incremental (``-pvc``) mode of
``latexmk`` to automatically rebuild when changes in the source files
are detected: ``make pvcsapling`` or ``make pvcsprout``.
Manual intervention is still needed when there are LaTeX errors.


Optimizing PDF size
-------------------

Optionally, you can use `Péter Szabó <https://github.com/pts>`_'s
``pdfsizeopt`` program to optimize the size of the resulting PDF files.

Use:

* ``make optsapling`` to make an optimized version of ``sapling.pdf``;
* ``make optsprout`` to make an optimized version of ``sprout.pdf``;
* ``make optimized`` to make both.

This will probably only work on Linux. The first time one of these
targets is run, it will automatically clone and build the necessary
dependencies (pinned by ``git`` hash) from GitHub.

This gives a size saving of about 40-50%.


Converting to HTML
------------------

To convert to HTML you will first need to install ``pdf2htmlEX``. On Debian:

.. code::

   apt-get install pdf2htmlex

Then use ``make html`` (or ``make optimized html``) to convert both PDFs.

The results are placed in the ``html`` directory at ``html/sapling.html``
and ``html/sprout.html``.

See `<https://github.com/zcash/zips/issues/127>`_ for limitations of
this conversion.
