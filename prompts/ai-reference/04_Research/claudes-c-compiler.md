---

CCC — Claude's C Compiler

Rust로 작성된 완전 자체 완결형(C) 컴파일러로, Claude Opus 4.6이 작성했다 — 100% AI가 작성했으며 사람의 코드 기여는 없다. x86-64, i686, AArch64, RISC-V 64를 타깃으로 한다. 자체 frontend, SSA 기반 IR, optimizer, code generator, assembler, linker, 그리고 DWARF 디버그 정보를 포함한다.

## Installation

```bash
git clone https://github.com/anthropics/claudes-c-compiler.git
cd claudes-c-compiler
cargo build --release
```

5개의 바이너리를 생성한다: `ccc`, `ccc-x86`, `ccc-arm`, `ccc-riscv`, `ccc-i686`.

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

GCC 호환 플래그(`-O2`, `-g`, `-S`, `-c`, `-E`, `-fPIC`, `-shared` 등)를 지원하며, 빌드 시스템(make, CMake, configure)에서 GCC를 그대로 대체하는 drop-in replacement로 사용할 수 있다.

## Proven Builds

다음과 같은 실제 프로젝트를 컴파일할 수 있다:
- Linux kernel (부팅 가능)
- PostgreSQL (237개 테스트 전부 통과)
- SQLite, Redis, CPython, FFmpeg, QEMU
- 그 외 150개 이상의 프로젝트

## Requirements

- Rust (stable, 2021 edition)
- glibc 또는 musl 헤더를 갖춘 Linux 호스트
- ARM/RISC-V/i686 타깃을 위한 cross-compilation sysroot

## License

CC0-1.0 (Public Domain)

## Links

- GitHub: https://github.com/anthropics/claudes-c-compiler
