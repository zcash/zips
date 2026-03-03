{
  description = "ZIP documentation rendering environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    multimarkdown6 = {
      url = "github:zcash/MultiMarkdown-6/543434c9df78b6be9e8125ff19a5e6934dc8ba82";
      inputs.nixpkgs.follows = "nixpkgs";
      inputs.flake-utils.follows = "flake-utils";
    };
  };

  outputs = { self, nixpkgs, flake-utils, multimarkdown6 }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        mmd = multimarkdown6.packages.${system}.default;
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            # Core dependencies for render.sh
            pkgs.python3Packages.docutils  # provides rst2html5
            pkgs.pandoc                    # pandoc markdown renderer
            mmd                            # multimarkdown renderer (zcash fork)
            pkgs.perl                      # perl for text processing

            # Build system dependencies
            pkgs.gnumake                   # make command for building
            pkgs.git                       # required by Makefile for safe.directory

            # LaTeX dependencies for protocol PDF generation
            (pkgs.texlive.combine {
              inherit (pkgs.texlive) scheme-full;
            })

            # Python dependencies for links_and_dests.py
            pkgs.python3
            pkgs.python3Packages.beautifulsoup4
            pkgs.python3Packages.html5lib
            pkgs.python3Packages.certifi

            # Standard utilities (usually available, but ensuring they're present)
            pkgs.coreutils
            pkgs.bash
            pkgs.gnused
            pkgs.gnugrep
            pkgs.diffutils
            pkgs.findutils
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
