==============================
 Zcash Protocol Specification
==============================

Build dependencies on Debian-based systems include, at least:

.. code::

   apt-get install texlive texlive-science texlive-fonts-extra \
     texlive-generic-recommended texlive-bibtex-extra biber latexmk perl


Building
--------

Use:

* ``make sapling`` to make the specification for the Overwinter and
  Sapling upgrades (``protocol.pdf``);
* ``make blossom`` to make the draft specification for the Blossom upgrade
  (``blossom.pdf``);
* ``make sprout`` to make a version of the specification that does not
  include Overwinter or Sapling.

``make all`` is equivalent to ``make sapling blossom sprout``.

By default these use ``latexmk``. If you have trouble getting ``latexmk`` to
work, you can instead use ``make nolatexmk-sapling``, etc. That is not the
preferred way of building because it may not run ``pdflatex`` enough times.

There is also support for using the incremental (``-pvc``) mode of
``latexmk`` to automatically rebuild when changes in the source files are
detected: ``make pvcsapling``, ``make pvcblossom``, or ``make pvcsprout``.
Manual intervention is still needed when there are LaTeX errors.


Optimizing PDF size
-------------------

Optionally, you can use Ghostscript to attempt to optimize the size of the
resulting PDF files. Note that this is not recommended with recent versions
of TeXLive that produce smaller PDFs in any case, since then it may increase
the size. (Debian Buster includes TeXLive 2019.)

For this option you will need to ensure the `ghostscript`, `extractpdfmark`,
and `awk` packages are installed. Then use:

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
