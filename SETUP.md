# 적용 방법

1. 이 폴더의 파일을 froiibn/froiibn 저장소의 main 브랜치에 올립니다. README.md는 기존 파일을 교체합니다. .github 폴더도 포함해야 합니다.
2. GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens에서 토큰을 만듭니다.
   - Resource owner: froiibn
   - Repository access: 통계에 포함할 저장소 선택
   - Repository permissions: Contents → Read-only (Metadata 읽기 권한은 기본 포함)
   - 만료일 설정. 만료 후에는 새 토큰으로 Secret을 갱신합니다.
3. froiibn/froiibn → Settings → Secrets and variables → Actions → New repository secret:
   - Name: PROFILE_STATS_TOKEN
   - Secret: 발급한 토큰
4. Actions → Update language statistics → Run workflow.

토큰은 채팅이나 코드에 넣지 않습니다. 워크플로는 저장소 Secret에서 읽습니다.
접근 가능한 본인 소유 저장소의 언어별 바이트를 집계합니다. 포크와 프로필 저장소는 제외됩니다.
비공개 저장소 이름과 소스코드는 결과 이미지에 포함되지 않습니다.
상위 8개 언어와 나머지 합계를 표시합니다. 비율은 숙련도나 개발 시간이 아닙니다.
매일 한국시간 오전 6:17 실행 예정이며 GitHub 스케줄에 따라 지연될 수 있습니다.
읽기 실패 또는 데이터가 없으면 기존 통계 이미지를 유지합니다.

