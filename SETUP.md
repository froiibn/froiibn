# 프로필 관리

## 구성

- `README.md`: 소개, 기술 배지, 프로젝트 링크, 언어 통계.
- `assets/terminal-fixedsys-v7.svg`: Fixedsys 픽셀 글꼴과 타이핑 효과를 사용하는 상단 터미널.
- `assets/language-donut-soft.svg`: 파스텔 도넛 그래프. 자동 생성되므로 디자인 변경은 생성 스크립트에도 반영합니다.
- `scripts/language_stats.py`: 언어 집계 및 도넛 SVG 생성.
- `.github/workflows/language-stats.yml`: 실행과 결과 저장.

상단 이미지 내용을 바꾼 뒤 이전 이미지가 계속 보이면 새 파일명으로 저장하고 README의 이미지 경로를 갱신합니다.

## 비공개 저장소 통계 연결

1. GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens에서 토큰을 생성합니다.
   - Resource owner: `froiibn`
   - Repository access: 통계에 포함할 본인 소유 저장소 선택
   - Repository permissions: Contents → Read-only
   - 만료일을 설정하고, 만료 전에 새 토큰으로 아래 Secret을 갱신합니다.
2. 이 저장소의 Settings → Secrets and variables → Actions에 저장합니다.
   - Name: `PROFILE_STATS_TOKEN`
   - Secret: 생성한 토큰
3. Actions → Update language statistics → Run workflow를 실행합니다.

토큰은 채팅, README, 코드에 넣지 않습니다. 토큰은 조회용이고, 결과 커밋에는 GitHub Actions의 기본 토큰을 사용합니다.

## 집계와 갱신

접근 가능한 본인 소유 저장소의 언어별 코드 바이트를 합산합니다. 포크와 이 프로필 저장소는 제외합니다. 비공개 저장소 이름이나 소스코드는 결과에 포함하지 않습니다.

상위 8개 언어와 나머지 합계(Other)를 표시합니다. 비율은 소수점 첫째 자리까지 반올림하며 숙련도나 개발 시간이 아닙니다.

매일 한국시간 오전 6:17에 실행하도록 설정되어 있습니다. GitHub 실행 상황에 따라 지연될 수 있으며, 필요하면 수동 실행합니다. 조회 오류나 언어 데이터가 없는 경우 기존 이미지를 유지합니다.

생성 스크립트가 쓰는 파일과 워크플로가 커밋하는 파일은 모두 `assets/language-donut-soft.svg`여야 합니다.

## 문제 확인

- 통계가 대기 상태인 경우: `PROFILE_STATS_TOKEN` Secret 등록 여부를 확인합니다.
- 조회가 실패하는 경우: 토큰 만료, 선택한 저장소, Contents 읽기 권한을 확인합니다.
- SVG는 생성됐지만 저장이 실패하는 경우: Actions 로그와 저장소의 워크플로 쓰기 권한 및 브랜치 보호 규칙을 확인합니다.
