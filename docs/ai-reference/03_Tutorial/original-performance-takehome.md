---

Anthropic's Original Performance Take-Home

Anthropic's original performance engineering take-home challenge, open-sourced after Claude Opus 4.5 surpassed human performance on it. A CPU cycle optimization challenge on a simulated machine.

## Overview

This challenge tasks participants with optimizing code to minimize CPU cycles on a simulated machine. It was originally used for Anthropic's hiring process and was released publicly after AI performance exceeded human baselines.

## Usage

```bash
git clone https://github.com/anthropics/original_performance_takehome.git
cd original_performance_takehome
python tests/submission_tests.py
```

## Performance Benchmarks

| Model / Baseline | Cycles |
|-----------------|--------|
| Unoptimized | ~3000+ |
| Claude Opus 4 | 2164 |
| Human expert | ~1500 |
| Claude Opus 4.5 | 1363 |

> Anyone who beats 1487 cycles is invited to email Anthropic for recruiting consideration.

## Requirements

- Python (for test runner)

## Links

- GitHub: https://github.com/anthropics/original_performance_takehome
