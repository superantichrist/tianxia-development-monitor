window.MONITOR_DATA = {
  "schemaVersion": 1,
  "updatedAt": "2026-09-28T10:52:37+00:00",
  "project": {
    "name": "천하",
    "englishName": "TIANXIA",
    "edition": "개발 관측소",
    "latestVerified": "0.4.0-dev",
    "currentMilestone": "M05.1",
    "currentVersion": "0.4.1-dev",
    "currentMilestoneTitle": "병사 무기 자세·장수 전신 동작",
    "goal": "캠페인부터 전장까지, 삼국지 토탈워와 동등한 수준을 최대한 추구합니다.",
    "policy": "기능·그래픽 확장을 우선하고, 최적화를 병행합니다.",
    "boundary": "현재는 독립 개발 중인 전략 게임입니다. 항목별 구현과 검증을 기록하며 전체 동등성이나 완성률을 주장하지 않습니다."
  },
  "statuses": [
    {
      "id": "in_progress",
      "label": "진행 중",
      "description": "현재 제작·통합·검증 중"
    },
    {
      "id": "complete",
      "label": "검증 완료",
      "description": "카드에 적힌 범위의 근거 확인"
    },
    {
      "id": "planned",
      "label": "다음 계획",
      "description": "아직 완성되지 않은 기능"
    },
    {
      "id": "external",
      "label": "외부 검증 대기",
      "description": "원작 실행 등 외부 환경 확인 필요"
    }
  ],
  "domains": [
    {
      "id": "battle",
      "label": "전투·물리"
    },
    {
      "id": "campaign",
      "label": "캠페인"
    },
    {
      "id": "graphics",
      "label": "그래픽·동작"
    },
    {
      "id": "performance",
      "label": "최적화"
    },
    {
      "id": "modding",
      "label": "모드·튜닝"
    },
    {
      "id": "tooling",
      "label": "엔진·도구"
    }
  ],
  "cards": [
    {
      "id": "individual",
      "title": "개별 병사 전투 첫 통합",
      "domain": "battle",
      "status": "complete",
      "milestone": "M05",
      "summary": "영속 ID·실제 위치·속도·개인 HP와 생존 목록을 전투에 연결했습니다.",
      "evidence": "모듈 270개·전투 통합 15개 검사. 렌더 연결 headless 584개와 실제 GPU 776개 검사를 통과했습니다. 개별 사망 후 ID 재배치·보간·LOD·그림자·행동 데이터를 GPU에서 읽어 확인했습니다. 통합 보고 영상과 비공개 업로드를 검증했습니다.",
      "next": "개별 동작·전선 접촉과 대규모 플레이 품질 개선",
      "priority": "focus"
    },
    {
      "id": "contact",
      "title": "전선 접촉과 개별 타격",
      "domain": "battle",
      "status": "in_progress",
      "milestone": "M05",
      "summary": "접근 → 공격 준비 → 타격 → 회복. 공간 격자로 개인 접촉을 계산합니다.",
      "evidence": "첫 분리 모델은 제한된 후보와 위치 보정을 사용합니다. 완전한 비관통 물리가 아닙니다.",
      "next": "전선 후보 축소, 아군 교차, 표적 점유와 좁은 통로 검증",
      "priority": "focus"
    },
    {
      "id": "terrain",
      "title": "연속된 3D 캠페인 지형",
      "domain": "campaign",
      "status": "complete",
      "milestone": "M05",
      "summary": "도시와 길이 연결된 캠페인을 높낮이가 있는 연속 지형으로 확장했습니다.",
      "evidence": "캠페인 지형·군대 210개 검사와 GPU 화면 확인. 실제 GPU에서 전체 UI 흐름 19개 검사도 통과했습니다. 통합 보고 영상과 비공개 업로드를 검증했습니다.",
      "next": "캠페인 조작·지형·군대 이동의 그래픽과 플레이 품질 확장",
      "priority": "focus"
    },
    {
      "id": "campaign_armies",
      "title": "지도 위 3D 군대와 장수",
      "domain": "campaign",
      "status": "complete",
      "milestone": "M05",
      "summary": "군대의 장수 모델·깃발·선택 표시를 지도에 배치하고 이동 명령에 연결했습니다.",
      "evidence": "3D 배치·색상·선택·행군·제거를 포함한 캠페인 검사와 GPU 화면 확인. 통합 보고 영상과 비공개 업로드를 검증했습니다.",
      "next": "군대 행군 동작·지형 상호작용과 전략 지도 콘텐츠 확장",
      "priority": "focus"
    },
    {
      "id": "duel_mode",
      "title": "별도로 실행하는 일기토 모드",
      "domain": "battle",
      "status": "complete",
      "milestone": "M05",
      "summary": "장수 선택·두 명의 독립 교전·태세 전환·타이밍 방어·승패와 재대결을 연결했습니다.",
      "evidence": "현재 I/arm_v3·v4 빌드의 메뉴 76개·일기토 76개·장수 감상 76개, 합계 228개 휴대 실행 검사를 통과했습니다. M05 완료 영상은 이전 빌드의 기록이며 M05.1 완료를 뜻하지 않습니다.",
      "next": "장수별 무기 접촉·전용 동작과 연출 확장",
      "priority": "focus"
    },
    {
      "id": "hero_models",
      "title": "여포 I와 세 장수의 상완·발목 개선",
      "domain": "graphics",
      "status": "in_progress",
      "milestone": "M05.1",
      "summary": "여포 I와 관우·장비·마초 arm_v3를 실제 명단과 새 실행본에 채택했습니다. 독립 발목을 유지하면서 어깨·상완 연결을 수정했습니다.",
      "evidence": "현재 모델의 모든 팔 정점 표본 검사: 공방 33개·일반 동작 22개 통과. 한 축 몸통 envelope이며 어깨 접합부 상단 30%는 제외합니다. 원화와 3D의 얼굴·갑주·피부 격차, 강체 관절과 가중 스키닝 과제는 남습니다.",
      "next": "장수의 위용·얼굴 식별·재질을 원화와 맞추고 골반·흉곽·옷의 변형 개선",
      "priority": "focus"
    },
    {
      "id": "hero_gallery",
      "title": "네 장수의 원화·3D 동작 감상",
      "domain": "graphics",
      "status": "complete",
      "milestone": "M05.1 · 감상 도구",
      "summary": "여포·관우·장비·마초 원화와 실제 3D 모델을 나란히 보고 회전·확대·전신·얼굴·대기·공격·방어를 선택하는 별도 감상 모드를 연결했습니다.",
      "evidence": "현재 네 모델로 감상 기능 127개 headless 검사 통과. 동작별 구도, 얼굴 보기 무기 숨김·복구와 수동 조작 보존을 검사했습니다. 모델 품질이나 실제 일기토의 자연스러움 완료 판정은 아닙니다.",
      "next": "모델·클립 개선 때 얼굴·전신 구도와 실제 화면 동작 감상 재검수",
      "priority": "normal"
    },
    {
      "id": "models",
      "title": "인물·기병·말 모델 개선",
      "domain": "graphics",
      "status": "complete",
      "milestone": "M03",
      "summary": "인체 기반 얼굴, 피부 색상·노멀 재질과 병사·기병·말 8종을 개선했습니다.",
      "evidence": "모델·재질 검사, 확대 GPU 화면, 실행 빌드와 마일스톤 영상 확인.",
      "next": "골격 리깅, 보행·공격·피격 동작과 재질 품질 확장",
      "priority": "normal"
    },
    {
      "id": "lod",
      "title": "근접 공간 분할과 그림자 LOD",
      "domain": "performance",
      "status": "complete",
      "milestone": "M03.1",
      "summary": "가까운 공간 구역만 상세 모델로 표현해 근접 렌더 비용을 줄였습니다.",
      "evidence": "GPU 354검사, 병사 수 보존, 동일 조건 근접·원거리 측정.",
      "next": "새 개별 전투 통합 후 같은 조건에서 다시 측정",
      "priority": "normal"
    },
    {
      "id": "campaign_base",
      "title": "캠페인 기본 운영",
      "domain": "campaign",
      "status": "complete",
      "milestone": "기반",
      "summary": "8세력·30도시, 계절·세금·식량·민심·도시 건설·군대 운용을 연결했습니다.",
      "evidence": "현재 기능 범위 문서에 기록된 실행 가능한 기본 시스템.",
      "next": "세력별 구조·정치·경제·지도 콘텐츠를 확장",
      "priority": "normal"
    },
    {
      "id": "controls",
      "title": "전투 명령과 전술 기본",
      "domain": "battle",
      "status": "complete",
      "milestone": "기반",
      "summary": "배치·드래그 선택·집단 명령·진형·사기·패주·병종 상성을 구현했습니다.",
      "evidence": "기존 부대 단위 전투 경로의 기능. 개별 병사 물리 완료를 뜻하지 않습니다.",
      "next": "개인 접촉 모델과 전술 규칙의 일치 확인",
      "priority": "normal"
    },
    {
      "id": "mod_tools",
      "title": "모드 제작 도구와 정적 진단",
      "domain": "modding",
      "status": "complete",
      "milestone": "M04 · 도구",
      "summary": "공식 RPFM·스키마·의존성 캐시와 읽기 전용 진단 경로를 구성했습니다.",
      "evidence": "설치 팩별 분리 진단과 복구 가능한 튜닝 후보를 준비했습니다.",
      "next": "실제 원작 캠페인·전투에서 조합과 호환성 검증",
      "priority": "normal"
    },
    {
      "id": "mod_runtime",
      "title": "원작 모드·튜닝 플레이 비교",
      "domain": "modding",
      "status": "in_progress",
      "milestone": "M04",
      "summary": "기존 모드 구성의 내장 전투와 새 유비 캠페인에서 군대 이동·초기 전투·결정적 승리·캠페인 복귀를 실제 확인했습니다.",
      "evidence": "9월 9일 내장 전투 CSV 11,690프레임 / 93.721초, 전체 행 평균 124.732 FPS. 9월 10일 1,263 대 721명 초기 전투와 장비 일기토 시작 확인. 일기토 개별 결과는 미확인이며 이 원작 FPS를 Godot와 비교하지 않습니다.",
      "next": "실제 저장·재실행·리플레이 재생·근접 일기토·같은 조건의 품질 후보·패치 효과 확인",
      "priority": "normal"
    },
    {
      "id": "soldier_animation",
      "title": "상대를 향한 병사 무기와 관절 동작",
      "domain": "graphics",
      "status": "in_progress",
      "milestone": "M05.1",
      "summary": "창을 교전 상대 앞으로 낮추고 칼·방패·활·쇠뇌의 서로 다른 동작을 실제 개인 공격·이동 위상에 연결했습니다.",
      "evidence": "Blender v4 자산 7종 × 3 LOD. 196개 검사 / 6,363개 자세에서 무기 길이·팔 관절·방향을 확인했습니다. GPU 776개 렌더 검사와 근접 화면 검수를 수행했습니다. 고정 프레임 검수는 실시간 FPS가 아닙니다.",
      "next": "무기 궤적 충돌·지형 발 접지·기병과 말 동작 품질 확장",
      "priority": "focus"
    },
    {
      "id": "hero_animation",
      "title": "장수마다 다른 전신 공격",
      "domain": "graphics",
      "status": "in_progress",
      "milestone": "M05.1",
      "summary": "장수별 공격과 양손 IK를 유지하며 v4 공방에서 장비·마초의 바깥 진입, 관우·장비의 낮은 후속 궤적을 연결했습니다.",
      "evidence": "실제 GPU 구간을 프레임 단위로 비교했습니다. 준비·회수의 긴 멈춤, 단단한 허리 회전과 약한 반발·체중 전달은 아직 보입니다. M05.1 통합 영상의 로컬 검수는 완료했고 비공개 업로드를 기다립니다. 새 네 장수 원화는 이 영상 촬영 이후 추가했습니다.",
      "next": "두 무기가 실제 맞닿는 저작 접점, 받아내는 체중과 연속적인 회수 동작",
      "priority": "focus"
    },
    {
      "id": "paired_motion",
      "title": "두 장수의 v4 공방과 실제 바닥 접지",
      "domain": "battle",
      "status": "in_progress",
      "milestone": "M05.1",
      "summary": "두 장수의 공통 시간축, 접근→준비 자세 연결과 모델별 실제 밑창 높이를 경기장 바닥에 맞췄습니다. 장병기의 이른 몸통 진입과 방어 후 회수 경로를 수정했습니다.",
      "evidence": "현 명단 12개 공격 방향 × 4결과, 240Hz·20,592개 두 배우 자세에서 상대 검사 169개 통과. 실제 접지 43개·접근 연결 40개 통과. 유한 표본과 한 축 envelope 검사이며 연속 무관통·정확한 충돌 시각·자연스러운 전투의 보장은 아닙니다.",
      "next": "접점과 양쪽 반응을 함께 저작하고 경직된 허리·회수 멈춤·체중 이동 개선",
      "priority": "focus"
    },
    {
      "id": "reference_viewer",
      "title": "원작·제작본 프레임 비교 도구",
      "domain": "tooling",
      "status": "complete",
      "milestone": "M05.1 · 과거 참고 분석",
      "summary": "공개 원작 영상 2개의 추출 439프레임과 당시 H 첫 공격 58프레임을 독립적으로 이동·재생·확대하는 로컬 도구의 검증 기록입니다. H는 현재 모델이 아닙니다.",
      "evidence": "이 과거 스냅샷은 원본 PTS와 29.97·25FPS, H의 30FPS를 구분했고 브라우저 조작 11건을 통과했습니다. 주력 연속 64프레임의 장면표·전체 해상도 1장·개요 17개를 확인했으며 추출 439장 전체 시각 검수를 뜻하지 않습니다.",
      "next": "최신 제작본은 별도 촬영·검수하고 과거 참고 분석과 구별",
      "priority": "normal"
    },
    {
      "id": "animation",
      "title": "병사·말 스키닝과 지면 접지",
      "domain": "graphics",
      "status": "planned",
      "milestone": "후속",
      "summary": "현재 강체 관절과 GPU 해석 동작을 넘어 가중치 스키닝·지형 발 IK·말 골격과 발굽 접지를 확장합니다.",
      "evidence": "M05.1의 관절 동작이 자연스러운 전신 스키닝과 접지까지 완성했다는 뜻은 아닙니다.",
      "next": "발 미끄러짐과 관절 경계가 보이는 근접 장면부터 개선",
      "priority": "focus"
    },
    {
      "id": "officer_roster",
      "title": "가능한 많은 유니크 장수 명부",
      "domain": "campaign",
      "status": "in_progress",
      "milestone": "콘텐츠 확장",
      "summary": "삼국지 14 공식 이름 목록 1,000개 ID를 등록했습니다. 다른 작품의 추가 인물도 신원·출처를 확인해 확장하며 인원 상한을 두지 않습니다.",
      "evidence": "한글 이름 81명. 동명이인은 ID를 분리했습니다. 원화 16명·3D 모델 4명·독립 일기토 4명이며, 1,000명이 플레이 가능하다는 뜻은 아닙니다.",
      "next": "남은 한글 이름·연의와 정사 출전·중복 신원 검토 후 장수 데이터와 플레이 통합",
      "priority": "focus"
    },
    {
      "id": "officer_portraits",
      "title": "연의 특징을 살린 독자 장수 원화",
      "domain": "graphics",
      "status": "in_progress",
      "milestone": "콘텐츠 확장",
      "summary": "여포·관우·장비·마초·조운·황충·전위·조조·유비·손권·제갈량·주유에 손책·장료·초선·여몽을 더해 16명의 독자 원화를 제작했습니다.",
      "evidence": "16개 서로 다른 1,024×1,536 PNG를 검토하고 원본·게임·공개 갤러리의 동일성을 확인했습니다. 새 실행본에서 원화 16장 로딩과 실험 자산 제외를 95개 조건으로 확인했습니다. 새 네 그림은 기존 M05.1 영상에 없으며 3D 모델·플레이 가능 수는 여전히 4명·4명입니다.",
      "next": "새 장수의 3D·플레이 통합과 다음 원화 묶음 제작",
      "priority": "focus"
    },
    {
      "id": "cavalry",
      "title": "기병 충격과 창병 저지",
      "domain": "battle",
      "status": "planned",
      "milestone": "후속",
      "summary": "질량·속도·방향·대형을 고려한 접촉 충격과 저지 반응을 만듭니다.",
      "evidence": "물리 설계 문서에 제안. 연속 충돌·넘어짐은 미구현 범위.",
      "next": "기병 돌파와 창병 방어의 반복 가능한 충돌 장면",
      "priority": "normal"
    },
    {
      "id": "siege",
      "title": "공성 통로와 성벽 위 교전",
      "domain": "battle",
      "status": "planned",
      "milestone": "후속",
      "summary": "문·벽·사다리의 통로 용량과 높이 층을 전투 경로에 반영합니다.",
      "evidence": "현재 성문·내구도·투석 규칙은 기본 구현. 성벽 위 이동은 확장 대상.",
      "next": "좁은 문 통과, 열린 문·파괴된 벽 경로 변경 검사",
      "priority": "normal"
    },
    {
      "id": "diplomacy",
      "title": "장수·정치·외교 확장",
      "domain": "campaign",
      "status": "planned",
      "milestone": "M07",
      "summary": "인물 관계·장비·조정·복합 협상·수행 부대 구조를 확장합니다.",
      "evidence": "기본 장수·외교·개혁은 존재하며 원작 전체 구조는 아직 없습니다.",
      "next": "관계·직위·협상 기능의 플레이 시나리오 설계",
      "priority": "normal"
    },
    {
      "id": "native",
      "title": "시뮬레이션 병목 개선",
      "domain": "performance",
      "status": "in_progress",
      "milestone": "병행",
      "summary": "C++ 접촉 계산을 연결하고 기능·그래픽 작업과 병행해 비용을 줄였습니다.",
      "evidence": "270개 기능 검사 통과. 보존된 M05의 25,664명 상태 모듈 접촉 중앙값 17.571ms / p99 18.723ms. 새 병렬 회귀 실행이나 통합 전투 FPS와 다른 측정입니다.",
      "next": "같은 알고리즘·병력·장면의 통합 렌더 비용과 기능 결과 비교",
      "priority": "normal"
    },
    {
      "id": "engine",
      "title": "엔진·도구·모드 선택 재검토",
      "domain": "tooling",
      "status": "in_progress",
      "milestone": "매 단계",
      "summary": "검증된 Godot 실행을 유지하며 Blender 두 인물 제작·공유 클립 도구를 선택했습니다. Unreal·Unity·전용 엔진과 원작 모드 경로도 마일스톤마다 검토합니다.",
      "evidence": "현재 그래픽과 공방의 격차를 다른 엔진 이전이 실제로 해소했다는 비교 증거는 없습니다. 참고 목록의 TPU모드 표기는 보존하지만 원작 무모드·단일 모드의 통제 A/B 비교는 아직 미검증입니다.",
      "next": "동일 장수·동작·조명 장면의 표현과 제작 비용, 모드 호환·품질 효과를 확인",
      "priority": "normal"
    },
    {
      "id": "replay",
      "title": "재현 가능한 전투·리플레이",
      "domain": "battle",
      "status": "planned",
      "milestone": "후속",
      "summary": "고정 틱·명령 기록·개별 상태 저장으로 같은 전투를 재현합니다.",
      "evidence": "동일 장비의 첫 모듈 재현 검사와 완성된 리플레이 제품을 구분합니다.",
      "next": "상태 해시와 저장·복원 후 결과 일치 확인",
      "priority": "normal"
    }
  ],
  "parity": [
    {
      "area": "캠페인·경제",
      "domain": "campaign",
      "current": "8세력·30도시, 세금·식량·민심·건설·계절, 연속 3D 지형",
      "gap": "전체 지도·시작 연도·세력 콘텐츠, 복잡한 자원·인구 계층",
      "next": "3D 지형·도시 표현과 전략 콘텐츠 확장",
      "level": "기반 구현"
    },
    {
      "area": "군대·장수",
      "domain": "campaign",
      "current": "복수 군대, 모병·보충·행군, 캠페인 장수 26명 데이터, 지도 위 3D 군대·장수·깃발",
      "gap": "수행 부대, 관계·가족·장비·직위·세밀한 보급",
      "next": "군대 행군 동작과 지도 상호작용 확장",
      "level": "기반 구현"
    },
    {
      "area": "외교·개혁",
      "domain": "campaign",
      "current": "전쟁·화친·선물·교역·동맹·통행, 개혁 8개",
      "gap": "복합 거래·영토 교환·속국·연합 정치·전체 개혁 트리",
      "next": "캠페인 구조 확장",
      "level": "기반 구현"
    },
    {
      "area": "개별 병사 전투",
      "domain": "battle",
      "current": "개인 위치·속도·HP·접촉·공격 모듈의 전투 연결, 상대 방향의 무기와 관절 동작",
      "gap": "전선 점유·아군 비관통·정교한 무기 접촉·규모 성능",
      "next": "개별 접촉·회수·발 접지의 실제 화면 품질 개선",
      "level": "M05 기반 완료 · 동작 개선 중"
    },
    {
      "area": "전술·AI",
      "domain": "battle",
      "current": "진형·상성·측후방·돌격·사기·패주, 기본 AI",
      "gap": "장기 작전·협공·포위·증원·세밀한 시야와 은폐",
      "next": "개인 접촉과 전술 규칙 결합",
      "level": "기반 구현"
    },
    {
      "area": "공성·물리",
      "domain": "battle",
      "current": "성문·성벽 내구도·투석·화공·중앙 진입 경로",
      "gap": "성벽 위 전투·사다리·공성탑·복합 도시 길 찾기",
      "next": "장애물과 통로 용량 모델",
      "level": "기반 구현"
    },
    {
      "area": "모델·재질·표현",
      "domain": "graphics",
      "current": "여포 I·관우/장비/마초 arm_v3 채택, 독립 발목과 상완 연결 개선·네 장수 원화/3D 감상",
      "gap": "원화와 3D의 미술 격차·가중 스키닝·경사 지형 접지·말 골격·의상 품질",
      "next": "장수의 위용·얼굴·갑옷 재질과 골반/흉곽 변형 개선",
      "level": "현재 모델 통합 · 품질 제작 중"
    },
    {
      "area": "사운드·제품 완성도",
      "domain": "graphics",
      "current": "합성 배경음·북소리, 한국어 UI, 캠페인 저장",
      "gap": "장수 음성·전체 효과음·멀티플레이·튜토리얼·접근성",
      "next": "핵심 기능 검증 후 범위별 확장",
      "level": "기반 구현"
    },
    {
      "area": "장군 일기토",
      "domain": "battle",
      "current": "독립 4장수 모드·양손 IK·v4 두 인물 공방·접근 연결·실제 평면 접지·HP와 결과",
      "gap": "실제 무기끼리 접점·체중과 반발·경직된 허리·회수 멈춤·연속 충돌·가중 스키닝",
      "next": "맞닿는 두 무기와 양쪽이 힘을 받는 공방, 연속적인 회수 저작",
      "level": "M05 기반 완료 · M05.1 개선 중"
    },
    {
      "area": "유니크 장수·원화",
      "domain": "graphics",
      "current": "공식 참고 명부 1,000개 ID · 독자 원화 16명 · 3D 모델 4명 · 독립 일기토 4명",
      "gap": "새 네 원화 장수의 3D·플레이 통합, 명부 전체 통합·한글 이름·연의와 정사 구분",
      "next": "인물별 출처·특징을 확인하며 원화와 장수 콘텐츠 확대",
      "level": "두 번째 원화 묶음 추가"
    },
    {
      "area": "원작 모드·튜닝",
      "domain": "modding",
      "current": "공식 도구·내장 전투 CSV·신규 캠페인 초기 전투 승리와 지도 복귀·장비 일기토 시작",
      "gap": "실제 저장·재실행·리플레이 재생·근접 동작과 모드 호환성·패치 효과",
      "next": "같은 조건의 반복·품질 후보 비교",
      "level": "실행 검증 진행"
    }
  ],
  "milestones": [
    {
      "id": "M03",
      "title": "인체 기반 모델·재질",
      "status": "complete",
      "description": "인물·기병·말 개선, 실행 빌드와 영상 검증",
      "checks": {
        "assets": 309,
        "rules": 63,
        "ui": 19
      },
      "videoVerified": true
    },
    {
      "id": "M03.1",
      "title": "근접 렌더링 개선",
      "status": "complete",
      "description": "25,664명 표현 유지, 공간 분할·그림자 LOD",
      "checks": {
        "assets": 309,
        "rules": 63,
        "ui": 19,
        "render_lod_gpu": 354
      },
      "videoVerified": true
    },
    {
      "id": "M04",
      "title": "원작 모드·튜닝 비교",
      "status": "in_progress",
      "description": "내장 전투 CSV, 신규 유비 캠페인 초기 전투 승리·장비 일기토 시작·지도 복귀 확인 · 저장·품질·호환성 비교 진행",
      "checks": {},
      "videoVerified": false
    },
    {
      "id": "M05",
      "title": "개별 전투·3D 캠페인·4장수 일기토",
      "status": "complete",
      "description": "개인 이동·접촉, 연속 지형·3D 군대, 여포·관우·장비·마초와 별도 일기토 모드",
      "checks": {},
      "videoVerified": true
    },
    {
      "id": "M05.1",
      "title": "병사 무기 자세·장수 전신 동작",
      "status": "in_progress",
      "description": "여포 I·세 장수 arm_v3·v4 공방·접지 검증 · 경직된 허리·회수 반응·가중 스키닝 개선 중. 통합 영상 로컬 검수 완료·비공개 업로드 대기. 새 네 원화는 해당 영상 이후 추가",
      "checks": {},
      "videoVerified": false
    },
    {
      "id": "후속",
      "title": "접촉·공성·장수 콘텐츠·정치",
      "status": "planned",
      "description": "스키닝·기병 충격·성벽 경로·장수 원화와 플레이 통합·외교 확장",
      "checks": {},
      "videoVerified": false
    }
  ],
  "renderBenchmark": {
    "milestone": "M03.1",
    "nearFps": 62.2743803199364,
    "beforeNearFps": 19.6665373866366,
    "wideFps": 133.564511909186,
    "nearP99Ms": 22.479,
    "initialSoldiers": 25664,
    "gpuChecks": 354,
    "conditions": "RTX 2080 Ti · 1600×900 · 최고 품질 · VSync 해제 · 시점별 약 10초 1회",
    "scope": "개별 병사 물리 통합 전 렌더 측정입니다. 모든 장면의 FPS 보장이 아닙니다. 30FPS 고정 녹화는 성능 측정과 별개입니다."
  },
  "physicsBenchmark": {
    "agents": 25664,
    "contact_median_ms": 17.571,
    "contact_p99_ms": 18.723,
    "idle_median_ms": 0.884,
    "maximum_active_agents": 25600,
    "maximum_pair_checks": 159246,
    "measured_steps": 100,
    "dt": 0.05,
    "checks": 270,
    "contact_hits": 219,
    "contact_deaths": 37,
    "timingMilestone": "M05",
    "timingPreserved": true,
    "timingScope": "보존된 M05 모듈 측정. 새 병렬 회귀 실행의 시간과 구별하며 통합 FPS로 주장하지 않습니다."
  },
  "originalGameRuntime": {
    "milestone": "M04",
    "runDate": "2026-09-09",
    "collectionDate": "2026-09-10",
    "metrics": {
      "frame_count": 11690,
      "total_frame_time_seconds": 93.720861,
      "average_fps": 124.7321020663692,
      "mean_frame_time_ms": 8.017182292557742,
      "p99_frame_time_ms": 13.659
    },
    "resolution": [
      1920,
      1080
    ],
    "controlledComparison": false,
    "engineTxtSummaryRecovered": false,
    "campaignObservation": "9월 10일 신규 유비 캠페인 지도·3D 군대를 조작해 초기 황건적 전투를 플레이하고 결정적 승리·캠페인 복귀를 확인했습니다. 장비 일기토 시작과 두 장수 HP는 확인했으나 개별 일기토 결과·정확한 근접 무기 동작은 미확인입니다.",
    "scope": "원작 내장 전투 CSV 전체 행의 재계산입니다. 개발 작업 일부가 겹쳤으며 장면·해상도·병력이 다른 Godot 성능과 비교하지 않습니다. 실제 캠페인 저장 생성·재실행, 리플레이 재생, 전체 모드 호환성과 품질 후보 비교는 아직 검증 중입니다."
  },
  "integrationChecks": {
    "individualRenderHeadless": 584,
    "individualRenderGpu": 776,
    "individualRenderGpuVerified": true,
    "duelHeadless": 210,
    "portableHeadless": 228,
    "heroPoseChecks": 24,
    "heroPoseSamples": 1836,
    "uiGpu": 19,
    "rigidJointTwoHandIkImplemented": true,
    "currentMilestoneVideoVerified": false
  },
  "animationChecks": {
    "soldierChecks": 196,
    "soldierPoseSamples": 6363,
    "heroChecks": 29,
    "scope": "기하·동작 재생 검사. 피부·관절·접지의 자연스러움과 실제 무기 충돌을 입증하는 점수는 아닙니다."
  },
  "developmentEvidence": {
    "artPackageChecks": 95,
    "packedPortraits": 16,
    "catalogSha256": "37e6dc3f81db2c4c5319cdc5df4e7d8f3085ec5bf273a71f9d2cde494e259c4a",
    "artRevision": "romance_v2",
    "experimentalPelvisAssetsPackaged": false,
    "artCaptureScope": "손책·장료·초선·여몽 원화는 기존 M05.1 영상 촬영 이후 추가했습니다. 새 네 장수의 3D 모델·플레이 통합은 미완료입니다.",
    "galleryChecks": 127,
    "galleryHeroes": 4,
    "portableByMode": {
      "menu": 76,
      "duel": 76,
      "heroes": 76
    },
    "portablePckSha256": "9fd7a747b7e6da7abc155170f7e4ff3f7ba43dfbcd6c114ba99e808079adc4db",
    "modelRevisions": {
      "lubu": "I",
      "guanyu": "arm_v3",
      "zhangfei": "arm_v3",
      "machao": "arm_v3"
    },
    "modelSha256": {
      "lubu": "9a5ca5628553fc95ea358a4f078c0faffcdcd7346a120c789aaa85c9fc7f1cfb",
      "guanyu": "53d7d92dfba7d3a40afa2fc41118d5c1233d176d1355329b1a5a64d14af7e708",
      "zhangfei": "08a14d403c09da4d43bd3794257f043c9d9e9252150c8e57d5ba2a9e01056592",
      "machao": "73f44e4bfaae268721088d403735b335aa1720e340daabaaa26a9e060ef3e6ec"
    },
    "pairedCurveRevision": "v4",
    "pairedCurveSha256": "8eaa7adafc86b44a925f438aeed53124607c6385aa4174427ba172136f80855c",
    "groundingChecks": 43,
    "approachChecks": 40,
    "pairedOpponentChecks": 169,
    "pairedMatchups": 12,
    "pairedSampleHz": 240,
    "pairedActorPairPoses": 20592,
    "pairedArmChecks": 33,
    "genericArmChecks": 22,
    "referenceVideos": 2,
    "referenceFrames": 439,
    "comparisonFrames": 58,
    "referenceViewerUiChecks": 11,
    "referenceSnapshot": "과거 H 첫 공격 비교 도구의 검증 기록",
    "scope": "현재 I/arm_v3 모델·v4 공방과 원화 16장을 포함한 휴대 실행본입니다. 기존 여섯 동작/형상 보고서의 코드·곡선·모델은 동일합니다. 한 축 envelope와 어깨 접합부 제외 조건이 있으며 연속 충돌·자연스러움·M05.1 완료를 뜻하지 않습니다. 새 네 원화는 기존 영상 이후 추가됐고 pelvis/짝 공방 실험 후보는 배포하지 않았습니다. 참고 뷰어는 과거 H 스냅샷입니다."
  },
  "officerCatalog": {
    "referenceEntries": 1000,
    "illustrations": 16,
    "models": 4,
    "duelPlayable": 4,
    "koreanNames": 81,
    "page": "officers.html",
    "scope": "공식 이름 목록의 참고 ID 수이며 현재 플레이 가능한 장수 수나 전 시리즈 최대 수가 아닙니다."
  },
  "milestoneCompletion": {
    "M05": {
      "localVideoHashVerified": true,
      "captureEvidenceVerified": true,
      "privateUploadVerified": true
    },
    "M05.1": {
      "localVideoHashVerified": false,
      "captureEvidenceVerified": false,
      "privateUploadVerified": false
    }
  },
  "evidencePolicy": [
    "완료는 각 카드가 명시한 범위에만 적용합니다. 보드 카드 비율은 원작 대비 완성도가 아닙니다.",
    "M05의 보존된 완료 영상과 M05.1의 새 애니메이션 작업을 구분합니다. 최신 검증 완료 버전은 0.4.0-dev입니다.",
    "애니메이션의 관절·무기 길이 검사와 화면의 자연스러움은 다릅니다. 손·무기 관통, 접지와 실제 접촉을 영상으로 확인합니다.",
    "참고 프레임 추출·뷰어 검증과 실제 시각 검수 범위는 별도입니다. 두 원작 영상과 H의 FPS를 통일하거나 보간하지 않습니다.",
    "원작 내장 벤치마크와 독립 개발판은 장면·해상도·병력이 다릅니다. 두 FPS의 우열이나 비율을 비교하지 않습니다.",
    "원작 모드의 정적 경고 수를 실제 오류 수로 단정하지 않습니다. TPU 등 모드 표기 참고 자료와 무모드·단일 모드의 통제 비교를 구분합니다.",
    "마일스톤 영상은 비공개로 보관합니다. 확인한 공개 참고 영상 두 개만 출처에 연결하며 개인 영상·계정·로컬 원본 파일을 공개하지 않습니다."
  ],
  "sources": [
    {
      "label": "마일스톤 상태",
      "source": "milestones.json의 선택된 필드",
      "scope": "M03·M03.1 기록, M05·M05.1의 로컬 영상·실제 캡처·비공개 업로드 근거 확인"
    },
    {
      "label": "기능 범위",
      "source": "FEATURES.md의 수동 검토 요약",
      "scope": "현재 기능과 생략·단순화된 범위를 분리"
    },
    {
      "label": "물리 알고리즘",
      "source": "BATTLE_PHYSICS.md + 보존된 M05 측정과 새 기능 검사",
      "scope": "첫 모듈 시간과 새 병렬 회귀 시간·통합 FPS를 구별"
    },
    {
      "label": "장수와 애니메이션",
      "source": "OFFICER_ROSTER.md / HERO_ANIMATION.md / SOLDIER_ANIMATION.md",
      "scope": "명부·원화·모델·플레이 가능 수와 관절 동작·품질 차이를 구별"
    },
    {
      "label": "엔진·모드 경로",
      "source": "ENGINE_DECISIONS.md / ORIGINAL_GAME.md 요약",
      "scope": "도구 준비와 실제 원작 검증을 분리"
    },
    {
      "label": "공개 원작 참고 · YOHO요호",
      "source": "오호대장군 VS 전위 일기토 대전:삼국지 토탈워",
      "url": "https://www.youtube.com/watch?v=EhPbt8CLEFo",
      "scope": "199–207초 239프레임 추출. 연속 64프레임의 두 인물 진입·도약·낮아짐·거리 회복 관찰. 해당 구간 인물 이름·정확한 충돌 결과는 미확정"
    },
    {
      "label": "공개 원작 참고 · YOHO요호",
      "source": "1.3.0 패치 추가 전설장수 황개 vs 여포: 일기토대전",
      "url": "https://www.youtube.com/watch?v=Qp-6yLLrPzI",
      "scope": "40–48초 200프레임 추출, 원본 25FPS 보존. 추출·뷰어 확인을 전 프레임 동작 분석 완료로 표시하지 않음"
    }
  ],
  "snapshotNote": "자동 실시간 상태가 아닌 검토된 공개 스냅샷입니다. 기능 카드 분류는 담당자가 갱신하고 생성기가 허용된 수치만 추출합니다."
};
