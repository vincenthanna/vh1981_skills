# 셸·도구 실전 함정

실제 작업에서 조용히 잘못된 결과를 낸 함정 모음이다. 대부분 오류 없이 실패하므로 결과만 보고는 알아차리기 어렵다.
worktree에서 git을 다루거나, ssh와 docker로 원격 명령을 보내거나, gh로 PR을 고치거나, subagent와 외부 LLM CLI를 쓸 때 읽는다.

## git worktree: cwd는 호출마다 초기화된다

Bash 도구는 호출이 끝날 때마다 cwd를 되돌린다. 한 호출의 `cd <worktree>` 는 다음 호출에 이어지지 않는다.
이 때문에 커밋이 의도하지 않은 branch에 들어간 사례가 있다. worktree를 다룰 때는 git 명령마다 경로를 명시한다.

```bash
git -C <worktree-path> status
git -C <worktree-path> commit -m "..."
```

## ssh로 원격 명령 보내기: 한 줄 대신 스크립트를 넘긴다

따옴표, SQL, 반복문이 들어가면 한 줄 명령 대신 로컬 스크립트를 stdin으로 넘긴다. 두 단계 ssh를 거치는 중첩 따옴표 문제를 통째로 피할 수 있다.

```bash
ssh <user>@<host> 'bash -s' < script.sh > out.txt 2>&1
```

이렇게 넘긴 스크립트 안에서는 `docker exec -i` 를 쓰지 않는다. `-i` 가 파이프로 들어오는 stdin을 물려받아 나머지 스크립트를 먹어 버린다.
그러면 첫 `docker exec -i` 뒤의 명령은 오류 없이 실행되지 않는다. `-i` 를 빼거나 stdin을 막는다.

```bash
docker exec <container> sh -c '...' </dev/null
```

## docker: 파일을 넣기 전에 마운트를 확인한다

`docker cp` 로 파일을 넣기 전에 컨테이너의 실제 경로와 bind mount를 확인한다. WorkingDir와 기존 마운트에 따라 들어갈 자리가 달라진다.

```bash
docker inspect <container> --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}'
docker exec <container> ls <path>
```

bind mount는 파일의 inode에 묶인다. 호스트에서 편집기가 파일을 새로 써서 inode가 바뀌면 컨테이너에는 반영되지 않을 수 있다.
이때는 컨테이너를 다시 만든다.

```bash
docker compose up -d --force-recreate <service>
```

## gh: PR 본문은 파일로 넘긴다

인라인 `--body` 로 넘기면 백틱이 셸에서 해석되어 본문이 깨진다. 본문은 파일에 쓰고 파일로 넘긴다.

```bash
gh pr edit <N> --body-file pr_body.md
gh api repos/<org>/<repo>/pulls/<N> -X PATCH -F body=@pr_body.md
```

## subagent: transcript를 직접 읽지 않는다

subagent의 원본 JSONL transcript는 매우 커서 읽으면 컨텍스트가 넘친다. agent에게 결과를 파일로 쓰고 짧은 완료 요약만 돌려주게 한다.
본 세션은 그 요약과 근거 파일만 읽는다. 지시가 틀렸으면 SendMessage로 고쳐 주고, 그래도 막히면 중단하고 직접 처리한다.

## 외부 LLM CLI: 프롬프트를 파이프로 넘기지 않는다

`cat ctx.txt | gemini -p ...` 처럼 stdin으로 문맥을 넘기면 stdin이 사라져 출력 0바이트로 25분가량 멈춘 사례가 있다.
프롬프트와 문맥을 한 파일로 합친 뒤 인자로 넘긴다.

```bash
gemini -p "$(cat combined.txt)" --approval-mode=yolo > out.md 2>&1
```
