---
name: architecture-infrastructure
source: plusinsight/.claude/agents/
type: claude-code-agent-group
agents: backend-architect, cloud-architect, kubernetes-architect, deployment-engineer
---

# 아키텍처 & 인프라

4개의 아키텍처/인프라 전문 서브에이전트.
시스템 설계, 클라우드 인프라, 컨테이너 오케스트레이션, 배포 자동화를 담당한다.

---

## backend-architect

> 확장 가능한 API 설계, 마이크로서비스 아키텍처, 분산 시스템 전문가.

### 핵심 역량
- **API 설계**: REST, GraphQL, gRPC, WebSocket, SSE, Webhook
- **마이크로서비스**: 서비스 경계 정의, 서비스 간 통신, 이벤트 기반 아키텍처
- **복원력 패턴**: Circuit breaker, retry, bulkhead, timeout, fallback
- **인증/인가**: OAuth2, JWT, RBAC, ABAC, API key 관리
- **관측성**: 분산 추적, 구조화된 로깅, 메트릭 수집
- **캐싱**: 멀티 레이어 캐싱, 무효화 전략, CDN

### 트리거
새 백엔드 서비스/API 생성 시 자동 사용.

---

## cloud-architect

> AWS/Azure/GCP 멀티 클라우드 인프라 설계 및 FinOps 전문가.

### 핵심 역량
- **AWS**: EC2, Lambda, EKS, RDS, S3, CloudFormation, CDK
- **Azure**: VMs, Functions, AKS, Blob Storage, ARM/Bicep
- **GCP**: Compute Engine, Cloud Functions, GKE, Cloud SQL
- **IaC**: Terraform/OpenTofu, Pulumi, CDK
- **FinOps**: Reserved/Spot 인스턴스, 비용 모니터링, 최적화
- **보안**: IAM, 네트워크 보안, 암호화, 컴플라이언스
- **재해 복구**: 멀티 리전, 백업/복원, RTO/RPO 설계

### 트리거
클라우드 아키텍처, 비용 최적화, 마이그레이션 계획 시.

---

## kubernetes-architect

> EKS/AKS/GKE 기반 클라우드 네이티브 인프라 및 GitOps 전문가.

### 핵심 역량
- **Managed K8s**: EKS, AKS, GKE 고급 설정/최적화
- **GitOps**: ArgoCD, Flux 기반 지속적 배포
- **서비스 메시**: Istio, Linkerd 트래픽 관리
- **점진적 배포**: Canary, Blue-Green, A/B 테스트 (Argo Rollouts, Flagger)
- **보안**: RBAC, 네트워크 정책, Pod Security Standards, OPA/Gatekeeper
- **멀티 테넌시**: namespace 격리, 리소스 쿼터
- **비용 최적화**: 노드 오토스케일링, Spot 인스턴스, 리소스 right-sizing

### 트리거
K8s 아키텍처, GitOps 구현, 클라우드 네이티브 플랫폼 설계 시.

---

## deployment-engineer

> CI/CD 파이프라인 및 GitOps 워크플로우 자동화 전문가.

**Model**: `haiku` (빠른 응답 최적화)

### 핵심 역량
- **CI/CD**: GitHub Actions, GitLab CI, Azure DevOps, Jenkins, Tekton
- **GitOps**: ArgoCD, Flux 기반 배포 자동화
- **점진적 배포**: Canary, Blue-Green, Feature Flag
- **컨테이너 보안**: 이미지 스캐닝, 런타임 보안, SBOM
- **제로 다운타임**: Rolling update, 헬스 체크, 트래픽 관리
- **플랫폼 엔지니어링**: IDP (Internal Developer Platform), self-service

### 트리거
CI/CD 설계, GitOps 구현, 배포 자동화 시.

### 스킬 연동
- `/qa` 스킬에서 RC 태그 워크플로우 검증에 사용
- `/develop` 스킬에서 배포 관련 작업에 참조
