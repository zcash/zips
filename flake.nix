{
  description = "ZIP documentation rendering environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Core dependencies for render.sh
            python3Packages.docutils  # provides rst2html5
            pandoc                    # pandoc markdown renderer
            multimarkdown             # multimarkdown renderer
            perl                      # perl for text processing

            # Build system dependencies
            gnumake                   # make command for building
            git                       # required by Makefile for safe.directory

            # LaTeX dependencies for protocol PDF generation
            (texlive.combine {
              inherit (texlive) scheme-full;
            })

            # Python dependencies for links_and_dests.py
            python3
            python3Packages.beautifulsoup4
            python3Packages.html5lib
            python3Packages.certifi

            # Standard utilities (usually available, but ensuring they're present)
            coreutils                 # sed, grep, cat, basename, wc, diff, cp, rm, mkdir, touch
            bash                      # shell interpreter
            gnused                    # GNU sed
            gnugrep                   # GNU grep
            diffutils                 # diff command
            findutils                 # utilities for finding files
          ];

          shellHook = ''
            echo "ZIP documentation rendering environment"
            echo "Available commands:"
            echo "  make        - Build the entire project"
            echo "  rst2html5   - reStructuredText to HTML converter"
            echo "  pandoc      - Universal document converter"
            echo "  multimarkdown - MultiMarkdown processor"
            echo "  latexmk     - LaTeX build system for PDF generation"
            echo "  pdflatex    - LaTeX engine for PDF generation"
            echo ""
            echo "Usage:"
            echo "  make all-zips    - Build all ZIPs"
            echo "  make all         - Build ZIPs and protocol docs"
            echo "  make linkcheck   - Check links in generated HTML"
            echo "  ./render.sh --rst|--pandoc|--mmd <inputfile> <htmlfile>"
          '';
        };
      }
    );
}