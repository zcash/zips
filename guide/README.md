# Zcash Design Guide

This folder contains an mdbook instance of design-related toipcs for Zcash that are outside the scope of the protocol specification or ZIPs.

## Rendering

This folder is an [mdbook](https://rust-lang.github.io/mdBook/) project.

### Requirements

The standard means of rendering this folder is to install `mdbook` via `cargo`.

1. To install `cargo`, we recommend using [rustup](https://rustup.rs) for your platform.
1. With cargo installed, run `cargo install mdbook`.
1. In the ZIPs root, run `make design`, or in this folder run `mdbook build`.
1. The rendered output is in `design/book`.

### Integration into ZIPs Repo

This folder has a target in the root `/Makefile` to provie a `make design` target for rendering. This make target is part of the `all` target.

The rendered directory is `design/book` and this path is in `.gitignore`. This deviates from the approach with ZIPs and protocol spec where the rendered output is tracked in `git`.
