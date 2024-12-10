==============================
 Zcash Protocol Specification
==============================

Build dependencies on Debian-based systems include, at least:

.. code::

   apt install python3-pip perl sed cmake \
     texlive texlive-science texlive-fonts-extra texlive-bibtex-extra biber latexmk

Prior to Bullseye you may also need the ``awk`` and ``texlive-generic-recommended``
packages.

For link checking, you will also need the following Python packages:

.. code::

   pip3 install 'docutils==0.21.2' 'rst2html5==2.0.1' certifi PyPDF2


Building
--------

Use:

* ``make nufour`` to make the draft specification for NU4 (``nufour.pdf``);
* ``make heartwood`` to make the specification for Heartwood (``protocol.pdf``);
* ``make blossom`` to make the specification for the Blossom upgrade
  (``blossom.pdf``);
* ``make sapling`` to make the specification for the Overwinter and
  Sapling upgrades (``sapling.pdf``);
* ``make sprout`` to make a version of the specification that does not
  include Overwinter or Sapling (``sprout.pdf``).
* ``make linkcheck`` (in the root of the repo) to build everything and also
  perform link checking. This will access the network.

``make all`` is equivalent to ``make nu5 canopy heartwood blossom sapling``.

By default these use ``latexmk``. If you have trouble getting ``latexmk`` to
work, you can instead use ``make nolatexmk-sapling``, etc. That is not the
preferred way of building because it may not run ``pdflatex`` enough times.

It is also possible to use the incremental (``-pvc``) mode of ``latexmk`` to
automatically rebuild when changes in the source files are detected, by adding
``EXTRAOPT=-pvc`` to the ``make`` command line. In this case the updated PDF
files will be in the ``aux/`` directory. Manual intervention is still needed
when there are LaTeX errors.


Alternative TeX engines
-----------------------

There is experimental support for building the specification using LuaTeX
or XeTeX; see the comments at the top of the `Makefile`. However, this will
`currently produce poor output <https://github.com/zcash/zips/issues/249>`_.
A warning is included below the Abstract to indicate this.
