==============================
 Zcash Protocol Specification
==============================

Build dependencies on Debian-based systems include, at least:

.. code::

   apt-get install texlive texlive-science texlive-fonts-extra \
     texlive-generic-recommended texlive-bibtex-extra biber latexmk perl

To use the targets described under "Optimizing PDF size", you will also
need the `ghostscript`, `extractpdfmark`, and `awk` packages.


Building
--------

Use:

* ``make sapling`` to make the specification for the Overwinter and
  Sapling upgrades (``protocol.pdf``);
* ``make blossom`` to make the draft specification for the Blossom upgrade
  (``blossom.pdf``);
* ``make sprout`` to make a version of the specification that does not
  include Overwinter or Sapling.

By default these use ``latexmk``, which does not work on all systems.
Use ``make nolatexmk-sapling`` or ``make nolatexmk-sprout`` if you run into
problems with ``latexmk``, but that is not the preferred way of building
because it may not run ``pdflatex`` enough times.

There is also support for using the incremental (``-pvc``) mode of
``latexmk`` to automatically rebuild when changes in the source files are
detected: ``make pvcsapling``, ``make pvcblossom``, or ``make pvcsprout``.
Manual intervention is still needed when there are LaTeX errors.


Optimizing PDF size
-------------------

Optionally, you can use Ghostscript to optimize the size of the resulting
PDF files.

Use:

* ``make optsapling`` to make an optimized version of ``protocol.pdf``;
* ``make optblossom`` to make an optimized version of ``blossom.pdf``;
* ``make optsprout`` to make an optimized version of ``sprout.pdf``;
* ``make optimized`` to make all optimized PDFs.


Alternative TeX engines
-----------------------

There is experimental support for building the specification using LuaTeX
or XeTeX; see the comments at the top of the `Makefile`. However, this will
`currently produce poor output <https://github.com/zcash/zips/issues/249>`_.
A warning is included below the Abstract to indicate this.


Converting to HTML
------------------

To convert to HTML you will first need to install ``pdf2htmlEX``. On Debian:

.. code::

   apt-get install pdf2htmlex

Then use ``make html`` (or ``make optimized html``) to convert all PDFs.

The results are placed in the ``html`` directory at ``html/sapling.html``,
``html/blossom.html``, and ``html/sprout.html``.

See `<https://github.com/zcash/zips/issues/127>`_ for limitations of
this conversion. In particular, the resulting files are very large (over
7 MiB for the Sapling spec), and external linking into the document does
not work correctly.
