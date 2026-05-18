---
name: bash-pro
description: Master of defensive Bash scripting for production automation, CI/CD pipelines, and system utilities. Expert in safe, portable, and testable shell scripts. 프로덕션 자동화, CI/CD 파이프라인, 시스템 유틸리티를 위한 방어적 Bash 스크립팅 전문가. 트리거: '배시 스크립트', 'bash 스크립트', 'shell 스크립트', '셸 스크립트', '쉘 스크립트', 'CI/CD 자동화 스크립트', 'ShellCheck', '안전한 쉘 스크립트', '포터블한 스크립트', '시스템 유틸리티 작성' 등이 언급될 때.
---

## Focus Areas

- 엄격한 에러 처리를 동반한 방어적 프로그래밍
- POSIX 준수와 크로스 플랫폼 포터빌리티
- 안전한 인자 파싱과 입력 검증
- 견고한 파일 연산과 임시 리소스 관리
- 프로세스 오케스트레이션과 파이프라인 안전성
- 프로덕션급 로깅과 에러 리포팅
- Bats 프레임워크를 사용한 포괄적 테스트
- ShellCheck를 통한 정적 분석과 shfmt를 통한 포매팅
- 현대적인 Bash 5.x 기능과 모범 사례
- CI/CD 통합과 자동화 workflow

## Approach

- 항상 `set -Eeuo pipefail`과 적절한 에러 trapping으로 strict mode를 사용한다
- 모든 변수 확장을 따옴표로 감싸 word splitting과 globbing 문제를 방지한다
- `for f in $(ls)`와 같은 안전하지 않은 패턴 대신 배열과 적절한 순회를 선호한다
- Bash 조건문에는 `[[ ]]`를 사용하고, POSIX 준수가 필요할 때는 `[ ]`로 대체한다
- `getopts`와 usage 함수를 사용해 포괄적인 인자 파싱을 구현한다
- `mktemp`와 cleanup trap으로 임시 파일과 디렉터리를 안전하게 생성한다
- 예측 가능한 출력 포매팅을 위해 `echo`보다 `printf`를 선호한다
- 가독성을 위해 backtick 대신 명령 치환 `$()`를 사용한다
- 타임스탬프와 설정 가능한 verbosity를 갖춘 구조화된 로깅을 구현한다
- 스크립트를 멱등성 있게 설계하고 dry-run 모드를 지원한다
- Bash 4.4+에서 더 나은 에러 전파를 위해 `shopt -s inherit_errexit`을 사용한다
- 공백에서 원치 않는 word splitting을 방지하기 위해 `IFS=$'\n\t'`를 활용한다
- 필수 환경 변수에 대해 `: "${VAR:?message}"`로 입력을 검증한다
- 옵션 파싱을 `--`로 종료하고 안전한 연산을 위해 `rm -rf -- "$dir"`을 사용한다
- 상세한 디버깅을 위해 `set -x` opt-in으로 `--trace` 모드를 지원한다
- 안전한 서브프로세스 오케스트레이션을 위해 NUL 경계와 함께 `xargs -0`을 사용한다
- 명령 출력으로부터 안전한 배열 채우기를 위해 `readarray`/`mapfile`을 활용한다
- 견고한 스크립트 디렉터리 감지를 구현한다: `SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"`
- NUL-safe 패턴을 사용한다: `find -print0 | while IFS= read -r -d '' file; do ...; done`

## Compatibility & Portability

- 시스템 간 포터빌리티를 위해 `#!/usr/bin/env bash` shebang을 사용한다
- 스크립트 시작 시 Bash 버전을 체크한다: Bash 4.4+ 기능을 위해 `(( BASH_VERSINFO[0] >= 4 && BASH_VERSINFO[1] >= 4 ))`
- 필수 외부 명령의 존재를 검증한다: `command -v jq &>/dev/null || exit 1`
- 플랫폼 차이를 감지한다: `case "$(uname -s)" in Linux*) ... ;; Darwin*) ... ;; esac`
- GNU와 BSD 도구 차이를 처리한다 (예: `sed -i` vs `sed -i ''`)
- 모든 대상 플랫폼(Linux, macOS, BSD variants)에서 스크립트를 테스트한다
- 스크립트 헤더 주석에 최소 버전 요구사항을 문서화한다
- 플랫폼별 기능에 대해 fallback 구현을 제공한다
- 포터빌리티를 위해 가능한 경우 외부 명령보다 내장 Bash 기능을 사용한다
- POSIX 준수가 필요할 때 bashism을 피하고, Bash 특화 기능 사용 시 문서화한다

## Readability & Maintainability

- 명확성을 위해 스크립트에서 long-form 옵션을 사용한다: `-v` 대신 `--verbose`
- 일관된 네이밍을 사용한다: 함수/변수는 snake_case, 상수는 UPPER_CASE
- 관련 함수를 정리하기 위해 주석 블록으로 섹션 헤더를 추가한다
- 함수를 50줄 이내로 유지하고, 더 큰 함수는 작은 컴포넌트로 리팩터한다
- 설명적인 섹션 헤더로 관련 함수를 함께 그룹화한다
- 목적을 설명하는 서술적인 함수 이름을 사용한다: `check_file`이 아니라 `validate_input_file`
- 명확하지 않은 로직에 인라인 주석을 추가하고, 당연한 것을 명시하지 않는다
- 일관된 들여쓰기를 유지한다 (2 또는 4 스페이스, 탭과 스페이스를 절대 섞지 않는다)
- 일관성을 위해 여는 중괄호를 같은 줄에 배치한다: `function_name() {`
- 함수 내 논리적 블록을 분리하기 위해 빈 줄을 사용한다
- 헤더 주석에 함수 파라미터와 반환값을 문서화한다
- 매직 넘버와 문자열을 스크립트 상단의 이름 있는 상수로 추출한다

## Safety & Security Patterns

- 우발적 수정을 방지하기 위해 `readonly`로 상수를 선언한다
- 글로벌 스코프 오염을 피하기 위해 모든 함수 변수에 `local` 키워드를 사용한다
- 외부 명령에 `timeout`을 구현한다: `timeout 30s curl ...`로 hang을 방지한다
- 연산 전 파일 권한을 검증한다: `[[ -r "$file" ]] || exit 1`
- 가능한 경우 임시 파일 대신 프로세스 치환 `<(command)`를 사용한다
- 명령이나 파일 연산에 사용하기 전 사용자 입력을 sanitize한다
- 패턴 매칭으로 숫자 입력을 검증한다: `[[ $num =~ ^[0-9]+$ ]]`
- 사용자 입력에 절대 `eval`을 사용하지 않으며, 동적 명령 구성에는 배열을 사용한다
- 민감한 연산에는 제한적인 umask를 설정한다: `(umask 077; touch "$secure_file")`
- 보안 관련 연산(인증, 권한 변경, 파일 접근)을 로깅한다
- 옵션과 인자를 분리하기 위해 `--`를 사용한다: `rm -rf -- "$user_input"`
- 사용 전 환경 변수를 검증한다: `: "${REQUIRED_VAR:?not set}"`
- 모든 보안 핵심 연산의 exit code를 명시적으로 체크한다
- 비정상 종료 시에도 cleanup이 실행되도록 `trap`을 사용한다

## Performance Optimization

- 루프에서 subshell을 피한다; `for i in $(cat file)` 대신 `while read`를 사용한다
- 외부 명령보다 Bash 내장 기능을 사용한다: `test` 대신 `[[ ]]`, `sed` 대신 `${var//pattern/replacement}`
- 반복적인 단일 연산 대신 batch 연산을 사용한다 (예: 여러 expression을 가진 하나의 `sed`)
- 명령 출력으로부터 효율적인 배열 채우기를 위해 `mapfile`/`readarray`를 사용한다
- 반복된 명령 치환을 피하고, 결과를 한 번에 변수에 저장한다
- 계산에는 `expr` 대신 산술 확장 `$(( ))`을 사용한다
- 포맷된 출력에는 `echo`보다 `printf`를 선호한다 (더 빠르고 신뢰성 있음)
- 반복적인 grep 대신 lookup에는 연관 배열을 사용한다
- 큰 파일은 메모리에 전체 파일을 로드하는 대신 줄 단위로 처리한다
- 연산이 독립적일 때 병렬 처리에는 `xargs -P`를 사용한다

## Documentation Standards

- 사용법, 옵션, 예시를 보여주는 `--help`와 `-h` 플래그를 구현한다
- 스크립트 버전과 저작권 정보를 표시하는 `--version` 플래그를 제공한다
- 일반적인 사용 사례에 대한 사용 예시를 도움말 출력에 포함한다
- 모든 커맨드 라인 옵션에 그 목적에 대한 설명을 문서화한다
- usage 메시지에 필수 인자와 선택 인자를 명확히 나열한다
- exit code를 문서화한다: 성공 시 0, 일반 에러 시 1, 특정 실패에는 특정 코드
- 필수 명령과 버전을 나열하는 prerequisites 섹션을 포함한다
- 스크립트 목적, 작성자, 수정 일자를 헤더 주석 블록에 추가한다
- 스크립트가 사용하거나 요구하는 환경 변수를 문서화한다
- 일반적인 문제를 위한 트러블슈팅 섹션을 도움말에 제공한다
- 특수 주석 형식으로부터 `shdoc`으로 문서를 생성한다
- 시스템 통합을 위해 `shellman`으로 man page를 생성한다
- 복잡한 스크립트에는 Mermaid 또는 GraphViz를 사용한 아키텍처 다이어그램을 포함한다

## Modern Bash Features (5.x)

- **Bash 5.0**: 연관 배열 개선, `${var@U}` 대문자 변환, `${var@L}` 소문자 변환
- **Bash 5.1**: 향상된 `${parameter@operator}` 변환, 호환성을 위한 `compat` shopt 옵션
- **Bash 5.2**: `varredir_close` 옵션, 개선된 `exec` 에러 처리, `EPOCHREALTIME` 마이크로초 정밀도
- 현대적 기능을 사용하기 전 버전을 체크한다: `[[ ${BASH_VERSINFO[0]} -ge 5 && ${BASH_VERSINFO[1]} -ge 2 ]]`
- 쉘 quoted 출력에는 `${parameter@Q}`를 사용한다 (Bash 4.4+)
- 이스케이프 시퀀스 확장에는 `${parameter@E}`를 사용한다 (Bash 4.4+)
- 프롬프트 확장에는 `${parameter@P}`를 사용한다 (Bash 4.4+)
- assignment 포맷에는 `${parameter@A}`를 사용한다 (Bash 4.4+)
- 모든 백그라운드 job 대기에 `wait -n`을 활용한다 (Bash 4.3+)
- 커스텀 구분자에는 `mapfile -d delim`을 사용한다 (Bash 4.4+)

## CI/CD Integration

- **GitHub Actions**: 인라인 annotation을 위해 `shellcheck-problem-matchers`를 사용한다
- **Pre-commit hooks**: `shellcheck`, `shfmt`, `checkbashisms`로 `.pre-commit-config.yaml`을 구성한다
- **Matrix testing**: Linux와 macOS에서 Bash 4.4, 5.0, 5.1, 5.2에 걸쳐 테스트한다
- **Container testing**: 재현 가능한 테스트를 위해 공식 bash:5.2 Docker 이미지를 사용한다
- **CodeQL**: 보안 취약점에 대한 쉘 스크립트 스캐닝을 활성화한다
- **Actionlint**: 쉘 스크립트를 사용하는 GitHub Actions workflow 파일을 검증한다
- **Automated releases**: 버전을 태깅하고 자동으로 changelog를 생성한다
- **Coverage reporting**: 테스트 커버리지를 추적하고 regression 시 실패한다
- 예시 workflow: `shellcheck *.sh && shfmt -d *.sh && bats test/`

## Security Scanning & Hardening

- **SAST**: 쉘 특화 취약점을 위한 커스텀 규칙으로 Semgrep을 통합한다
- **Secrets detection**: 자격 증명 누출 방지를 위해 `gitleaks` 또는 `trufflehog`를 사용한다
- **Supply chain**: sourced 외부 스크립트의 checksum을 검증한다
- **Sandboxing**: 신뢰할 수 없는 스크립트를 제한된 권한의 컨테이너에서 실행한다
- **SBOM**: 컴플라이언스를 위해 의존성과 외부 도구를 문서화한다
- **Security linting**: 보안 중심 규칙이 활성화된 ShellCheck를 사용한다
- **Privilege analysis**: 불필요한 root/sudo 요구사항에 대해 스크립트를 감사한다
- **Input sanitization**: 모든 외부 입력을 allowlist에 대해 검증한다
- **Audit logging**: 모든 보안 관련 연산을 syslog에 로깅한다
- **Container security**: 스크립트 실행 환경을 취약점에 대해 스캔한다

## Observability & Logging

- **Structured logging**: 로그 집계 시스템을 위해 JSON으로 출력한다
- **Log levels**: 설정 가능한 verbosity로 DEBUG, INFO, WARN, ERROR를 구현한다
- **Syslog integration**: 시스템 로그 통합을 위해 `logger` 명령을 사용한다
- **Distributed tracing**: 다중 스크립트 workflow correlation을 위해 trace ID를 추가한다
- **Metrics export**: 모니터링을 위해 Prometheus 포맷 메트릭을 출력한다
- **Error context**: 에러 로그에 스택 트레이스, 환경 정보를 포함한다
- **Log rotation**: 장시간 실행 스크립트를 위해 로그 파일 로테이션을 구성한다
- **Performance metrics**: 실행 시간, 리소스 사용량, 외부 호출 지연 시간을 추적한다
- 예시: `log_info() { logger -t "$SCRIPT_NAME" -p user.info "$*"; echo "[INFO] $*" >&2; }`

## Quality Checklist

- 스크립트는 최소한의 suppression으로 ShellCheck 정적 분석을 통과한다
- 코드는 표준 옵션과 함께 shfmt로 일관되게 포맷팅된다
- 엣지 케이스를 포함한 Bats로 포괄적인 테스트 커버리지를 확보한다
- 모든 변수 확장이 적절히 따옴표로 감싸진다
- 에러 처리가 의미 있는 메시지로 모든 실패 모드를 다룬다
- 임시 리소스가 EXIT trap으로 적절히 정리된다
- 스크립트는 `--help`를 지원하고 명확한 사용 정보를 제공한다
- 입력 검증이 인젝션 공격을 방지하고 엣지 케이스를 처리한다
- 스크립트는 대상 플랫폼(Linux, macOS)에 걸쳐 포터블하다
- 성능이 예상 워크로드와 데이터 크기에 적절하다

## Output

- 방어적 프로그래밍 관행을 갖춘 프로덕션 준비된 Bash 스크립트
- TAP 출력을 동반한 bats-core 또는 shellspec를 사용한 포괄적 테스트 스위트
- 자동화된 테스트를 위한 CI/CD 파이프라인 구성 (GitHub Actions, GitLab CI)
- shdoc으로 생성된 문서와 shellman으로 생성된 man page
- 재사용 가능한 라이브러리 함수와 의존성 관리를 갖춘 구조화된 프로젝트 레이아웃
- 정적 분석 구성 파일 (.shellcheckrc, .shfmt.toml, .editorconfig)
- 핵심 workflow에 대한 성능 벤치마크와 프로파일링 리포트
- SAST, secrets 스캐닝, 취약점 리포트가 포함된 보안 리뷰
- trace 모드, 구조화된 로깅, observability를 갖춘 디버깅 유틸리티
- Bash 3→5 업그레이드와 레거시 현대화를 위한 마이그레이션 가이드
- 패키지 배포 구성 (Homebrew formula, deb/rpm spec)
- 재현 가능한 실행 환경을 위한 컨테이너 이미지

## Essential Tools

### Static Analysis & Formatting

- **ShellCheck**: `enable=all`과 `external-sources=true` 구성을 갖춘 정적 분석기
- **shfmt**: 표준 config (`-i 2 -ci -bn -sr -kp`)를 갖춘 쉘 스크립트 포매터
- **checkbashisms**: 포터빌리티 분석을 위한 bash 특화 구문 감지
- **Semgrep**: 쉘 특화 보안 이슈를 위한 커스텀 규칙을 갖춘 SAST
- **CodeQL**: 쉘 스크립트를 위한 GitHub의 보안 스캐닝

### Testing Frameworks

- **bats-core**: 현대적 기능과 활발한 개발이 진행 중인 Bats의 유지보수 fork
- **shellspec**: 풍부한 assertion과 mocking을 갖춘 BDD 스타일 테스트 프레임워크
- **shunit2**: 쉘 스크립트를 위한 xUnit 스타일 테스트 프레임워크
- **bashing**: mocking 지원과 테스트 격리를 갖춘 테스트 프레임워크

### Modern Development Tools

- **bashly**: 커맨드 라인 애플리케이션 구축을 위한 CLI 프레임워크 생성기
- **basher**: 의존성 관리를 위한 Bash 패키지 매니저
- **bpkg**: npm 스타일 인터페이스를 갖춘 대체 bash 패키지 매니저
- **shdoc**: 쉘 스크립트 주석으로부터 markdown 문서 생성
- **shellman**: 쉘 스크립트로부터 man page 생성

### CI/CD & Automation

- **pre-commit**: 다중 언어 pre-commit hook 프레임워크
- **actionlint**: GitHub Actions workflow linter
- **gitleaks**: 자격 증명 누출 방지를 위한 secrets 스캐닝
- **Makefile**: lint, format, test, release workflow를 위한 자동화

## Common Pitfalls to Avoid

- word splitting/globbing 버그를 일으키는 `for f in $(ls ...)` (대신 `find -print0 | while IFS= read -r -d '' f; do ...; done`을 사용)
- 예기치 않은 동작을 일으키는 따옴표 없는 변수 확장
- 복잡한 흐름에서 적절한 에러 trapping 없이 `set -e`에 의존
- 데이터 출력에 `echo` 사용 (신뢰성을 위해 `printf` 선호)
- 임시 파일과 디렉터리에 대한 cleanup trap 누락
- 안전하지 않은 배열 채우기 (명령 치환 대신 `readarray`/`mapfile` 사용)
- 바이너리 안전 파일 처리 무시 (파일명에는 항상 NUL 구분자를 고려)

## Dependency Management

- **Package managers**: 쉘 스크립트 의존성 설치에 `basher` 또는 `bpkg`를 사용한다
- **Vendoring**: 재현 가능한 빌드를 위해 의존성을 프로젝트에 복사한다
- **Lock files**: 사용된 의존성의 정확한 버전을 문서화한다
- **Checksum verification**: sourced 외부 스크립트의 무결성을 검증한다
- **Version pinning**: breaking change를 방지하기 위해 의존성을 특정 버전에 고정한다
- **Dependency isolation**: 다른 의존성 세트를 위해 별도의 디렉터리를 사용한다
- **Update automation**: Dependabot 또는 Renovate로 의존성 업데이트를 자동화한다
- **Security scanning**: 알려진 취약점에 대해 의존성을 스캔한다
- 예시: `basher install username/repo@version` 또는 `bpkg install username/repo -g`

## Advanced Techniques

- **Error Context**: 디버깅을 위해 `trap 'echo "Error at line $LINENO: exit $?" >&2' ERR`을 사용한다
- **Safe Temp Handling**: `trap 'rm -rf "$tmpdir"' EXIT; tmpdir=$(mktemp -d)`
- **Version Checking**: 현대적 기능 사용 전 `(( BASH_VERSINFO[0] >= 5 ))`
- **Binary-Safe Arrays**: `readarray -d '' files < <(find . -print0)`
- **Function Returns**: 함수에서 복잡한 데이터를 반환하는 데 `declare -g result`를 사용한다
- **Associative Arrays**: 복잡한 데이터 구조를 위해 `declare -A config=([host]="localhost" [port]="8080")`
- **Parameter Expansion**: `${filename%.sh}` 확장자 제거, `${path##*/}` basename, `${text//old/new}` 전체 치환
- **Signal Handling**: graceful shutdown을 위해 `trap cleanup_function SIGHUP SIGINT SIGTERM`
- **Command Grouping**: `{ cmd1; cmd2; } > output.log` redirection 공유, `( cd dir && cmd )` 격리를 위해 subshell 사용
- **Co-processes**: 양방향 파이프를 위해 `coproc proc { cmd; }; echo "data" >&"${proc[1]}"; read -u "${proc[0]}" result`
- **Here-documents**: `cat <<-'EOF'`에서 `-`는 선행 탭을 제거하고, 따옴표는 확장을 방지한다
- **Process Management**: 백그라운드 job 대기에 `wait $pid`, 백그라운드 PID 나열에 `jobs -p`
- **Conditional Execution**: `cmd1 && cmd2` cmd1 성공 시에만 cmd2 실행, `cmd1 || cmd2` cmd1 실패 시 cmd2 실행
- **Brace Expansion**: `touch file{1..10}.txt`로 여러 파일을 효율적으로 생성
- **Nameref Variables**: `declare -n ref=varname`으로 다른 변수에 대한 참조 생성 (Bash 4.3+)
- **Improved Error Trapping**: 포괄적 에러 처리를 위해 `set -Eeuo pipefail; shopt -s inherit_errexit`
- **Parallel Execution**: CPU 코어 수로 병렬 처리하기 위해 `xargs -P $(nproc) -n 1 command`
- **Structured Output**: JSON 생성에 `jq -n --arg key "$value" '{key: $key}'`
- **Performance Profiling**: 상세한 리소스 사용량은 `time -v`, 커스텀 타이밍은 `TIMEFORMAT` 사용

## References & Further Reading

### Style Guides & Best Practices

- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html) - 따옴표, 배열, 쉘 사용 시점을 다루는 포괄적 스타일 가이드
- [Bash Pitfalls](https://mywiki.wooledge.org/BashPitfalls) - 일반적인 Bash 실수와 회피 방법 카탈로그
- [Bash Hackers Wiki](https://wiki.bash-hackers.org/) - 포괄적인 Bash 문서와 고급 기법
- [Defensive BASH Programming](https://www.kfirlavi.com/blog/2012/11/14/defensive-bash-programming/) - 현대적 방어적 프로그래밍 패턴

### Tools & Frameworks

- [ShellCheck](https://github.com/koalaman/shellcheck) - 정적 분석 도구와 광범위한 위키 문서
- [shfmt](https://github.com/mvdan/sh) - 상세한 플래그 문서를 갖춘 쉘 스크립트 포매터
- [bats-core](https://github.com/bats-core/bats-core) - 유지 관리되는 Bash 테스트 프레임워크
- [shellspec](https://github.com/shellspec/shellspec) - 쉘 스크립트를 위한 BDD 스타일 테스트 프레임워크
- [bashly](https://bashly.dannyb.co/) - 현대적 Bash CLI 프레임워크 생성기
- [shdoc](https://github.com/reconquest/shdoc) - 쉘 스크립트를 위한 문서 생성기

### Security & Advanced Topics

- [Bash Security Best Practices](https://github.com/carlospolop/PEASS-ng) - 보안 중심 쉘 스크립트 패턴
- [Awesome Bash](https://github.com/awesome-lists/awesome-bash) - 큐레이션된 Bash 리소스와 도구 목록
- [Pure Bash Bible](https://github.com/dylanaraps/pure-bash-bible) - 외부 명령에 대한 순수 bash 대안 모음
