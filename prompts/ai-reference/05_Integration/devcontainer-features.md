---

Dev Container Features
이 저장소는 Claude Code CLI를 설치하는 feature를 포함한 Dev Container Features를 담고 있다.
Contents

src/claude-code: Claude Code CLI feature
test: 해당 feature에 대한 자동화된 테스트

Usage
devcontainer에서 이 feature를 사용하려면 devcontainer.json 파일에 다음과 같이 추가한다:
"features": {
    "ghcr.io/anthropics/devcontainer-features/claude-code:1.0": {}
}
Requirements
이 feature는 Node.js에 자동으로 의존하며, 설치되어 있지 않으면 함께 설치한다.
Building and Testing
dev container CLI를 사용해 feature를 빌드하고 테스트할 수 있다:
# Test the feature
devcontainer features test -f claude-code .

# Publish the feature
devcontainer feature publish -n anthropics/devcontainer-features .
License
이 프로젝트는 MIT License로 라이선스가 부여된다 - 자세한 내용은 LICENSE 파일을 참조한다.
