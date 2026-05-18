---

Anthropic's Original Performance Take-Home

Anthropic의 원본 performance engineering take-home 챌린지. Claude Opus 4.5가 이 챌린지에서 사람의 성능을 능가한 이후 오픈소스화되었다. 시뮬레이션된 머신에서의 CPU 사이클 최적화 챌린지.

## Overview

이 챌린지는 참가자에게 시뮬레이션된 머신에서 CPU 사이클을 최소화하도록 코드를 최적화하는 과제를 부여한다. 원래는 Anthropic의 채용 과정에서 사용되었으며, AI 성능이 사람의 베이스라인을 초과한 이후 공개되었다.

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

> 1487 사이클을 넘어서는 사람은 누구나 채용 검토를 위해 Anthropic에 email을 보낼 수 있다.

## Requirements

- Python (테스트 러너용)

## Links

- GitHub: https://github.com/anthropics/original_performance_takehome
