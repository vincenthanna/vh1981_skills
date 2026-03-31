---

CCC — Claude's C Compiler

A fully self-contained C compiler written in Rust by Claude Opus 4.6 — 100% AI-authored with no human code contributions. Targets x86-64, i686, AArch64, and RISC-V 64. Includes its own frontend, SSA-based IR, optimizer, code generator, assembler, linker, and DWARF debug info.

## Installation

```bash
git clone https://github.com/anthropics/claudes-c-compiler.git
cd claudes-c-compiler
cargo build --release
```

Produces 5 binaries: `ccc`, `ccc-x86`, `ccc-arm`, `ccc-riscv`, `ccc-i686`.

## Usage

```bash
# Compile and run
./target/release/ccc -o hello hello.c
./hello

# With optimizations and debug info
./target/release/ccc -O2 -g -o program program.c

# Cross-compile to ARM
./target/release/ccc-arm --sysroot=/path/to/aarch64-sysroot -o program program.c
```

Supports GCC-compatible flags (`-O2`, `-g`, `-S`, `-c`, `-E`, `-fPIC`, `-shared`, etc.) and can serve as a drop-in GCC replacement for build systems (make, CMake, configure).

## Proven Builds

Can compile real-world projects including:
- Linux kernel (bootable)
- PostgreSQL (all 237 tests pass)
- SQLite, Redis, CPython, FFmpeg, QEMU
- 150+ additional projects

## Requirements

- Rust (stable, 2021 edition)
- Linux host with glibc or musl headers
- Cross-compilation sysroots for ARM/RISC-V/i686 targets

## License

CC0-1.0 (Public Domain)

## Links

- GitHub: https://github.com/anthropics/claudes-c-compiler
