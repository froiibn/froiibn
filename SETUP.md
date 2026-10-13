# 프로필 관리

## 구성

- `README.md`: 소개, 기술 배지, 프로젝트 링크, 언어 통계.
- `assets/terminal-fixedsys-v7.svg`: Fixedsys 픽셀 글꼴과 타이핑 효과를 사용하는 상단 터미널.
- `assets/profile-dashboard-light.svg` 및 `assets/profile-dashboard-dark.svg`: 투명 배경의 다크·라이트 테마를 지원하며 활동 통계, 저장소별 언어, 커밋별 저장소 언어, 한국시간별 커밋을 표시하는 2×2 카드. 자동 생성되므로 디자인 변경은 생성 스크립트에도 반영합니다.
- `scripts/language_stats.py`: 저장소 및 최근 365일 커밋 집계와 대시보드 SVG 생성.
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

접근 가능한 본인 소유 저장소를 집계합니다. 저장소별 언어는 각 저장소의 주 언어로 분류합니다. 커밋 통계는 기본 브랜치의 최근 365일 중 본인이 작성한 커밋을 대상으로 하며, 중복 SHA는 한 번만 집계합니다. 커밋별 언어는 해당 커밋이 속한 저장소의 주 언어로 분류하므로 실제 변경 파일의 언어 비율과는 다릅니다. 커밋 시간은 작성자 타임스탬프를 한국시간(UTC+09:00)으로 변환합니다. 포크와 이 프로필 저장소는 제외합니다. 비공개 저장소 이름이나 소스코드는 결과에 포함하지 않습니다.

상위 6개 언어와 나머지 합계(Other)를 표시합니다. 비율은 소수점 첫째 자리까지 반올림하며 숙련도나 개발 시간이 아닙니다.

매일 한국시간 오전 6:17에 실행하도록 설정되어 있습니다. GitHub 실행 상황에 따라 지연될 수 있으며, 필요하면 수동 실행합니다. 조회 오류가 발생하면 기존 이미지를 유지합니다. 커밋이 없는 경우 활동 값은 0, 언어 차트는 No data로 표시합니다. 생성 스크립트 또는 워크플로가 main에서 변경되면 자동으로 다시 실행됩니다.

생성 스크립트가 쓰는 파일과 워크플로가 커밋하는 파일은 모두 `assets/profile-dashboard-light.svg` 및 `assets/profile-dashboard-dark.svg`여야 합니다.

## 문제 확인

- 통계가 대기 상태인 경우: `PROFILE_STATS_TOKEN` Secret 등록 여부를 확인합니다.
- 조회가 실패하는 경우: 토큰 만료, 선택한 저장소, Contents 읽기 권한을 확인합니다.
- SVG는 생성됐지만 저장이 실패하는 경우: Actions 로그와 저장소의 워크플로 쓰기 권한 및 브랜치 보호 규칙을 확인합니다.

## 잔디 뱀 애니메이션

`.github/workflows/contribution-snake.yml`이 Platane/snk의 SVG 생성 기능으로 기여도 잔디 애니메이션을 생성합니다. `assets/snake-light.svg`와 `assets/snake-dark.svg`를 사용하며 README에서 GitHub 테마에 맞게 표시합니다.

매일 한국시간 오전 7:17 실행 예정입니다. Actions → Update contribution snake → Run workflow로 수동 갱신할 수 있습니다. 개인 통계 토큰을 이 작업에 전달하지 않고 GitHub Actions 기본 토큰을 사용합니다.
