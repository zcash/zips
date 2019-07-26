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


Alternative TeX engines
-----------------------

There is experimental support for building the specification using LuaTeX
or XeTeX; see the comments at the top of the `Makefile`. However, this will
`currently produce poor output <https://github.com/zcash/zips/issues/249>`_.
A warning is included below the Abstract to indicate this.
