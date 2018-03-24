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

* ``make pdf`` to make the current protocol specification (``protocol.pdf``);
* ``make sapling`` to make the draft specification for the Overwinter and
  Sapling upgrades (``sapling.pdf``).

By default these use ``latexmk``, which does not work on all systems.
Use ``make nolatexmk-pdf`` or ``make nolatexmk-sapling`` if you run into
problems with ``latexmk``, but that is not the preferred way of building
because it may not run ``pdflatex`` enough times.

There is also support for using the incremental (``-pvc``) mode of
``latexmk`` to automatically rebuild when changes in the source files
are detected: ``make pvcpdf`` or ``make pvcsapling``.
Manual intervention is still needed when there are LaTeX errors.


Optimizing PDF size
-------------------

Optionally, you can use `Péter Szabó <https://github.com/pts>`_'s
``pdfsizeopt`` program to optimize the size of the resulting PDF files.

Run ``make optimized`` to rebuild both PDFs and then optimize them.
This will probably only work on Linux. The first time this is run it
will automatically clone and build the necessary dependencies (pinned
by ``git`` hash) from GitHub.

Alternatively, you can run ``make optimize-pdf`` or ``make optimize-sapling``
to optimize just ``protocol.pdf`` or ``sapling.pdf`` respectively.

This gives a size saving of about 50% for ``protocol.pdf``, and
40% for ``sapling.pdf``.
