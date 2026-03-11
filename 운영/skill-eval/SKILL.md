---
name: skill-eval
description: 기존에 만들어진 SKILL.md를 테스트하고, 결과를 비교하고, 품질을 개선하는 스킬. 사용자가 "이 스킬 잘 작동하나 테스트해봐", "스킬 평가해줘", "스킬 개선해줘", "eval 돌려줘", "테스트 케이스 실행해줘"라고 하면 반드시 이 스킬을 사용할 것. 스킬을 처음 만든 직후이거나, 개선 여부를 확인하고 싶을 때도 이 스킬을 사용한다.
---

# Skill Eval

스킬을 테스트하고 반복 개선하는 파이프라인. 
스킬이 있을 때와 없을 때를 비교하고, 사용자 피드백을 받아 스킬을 개선한다.

사용 환경: Claude Code (subagent 지원)

## 전제 조건

- 평가할 스킬의 경로 확인 (예: `workspace/skills/콘텐츠/뉴스레터-초안/SKILL.md`)
- evals/evals.json이 있으면 그것을 기반으로, 없으면 아래 인터뷰로 테스트 케이스 생성

## 입력

사용자에게 받아야 하는 것:
- 평가할 스킬 경로
- evals/evals.json 파일 (없으면 직접 생성)
- 개선 목표 (선택: "출력 형식이 일관되지 않는다", "너무 길게 나온다" 등)

---

## 처리 순서

### STEP 1: 테스트 케이스 확인 또는 생성

evals/evals.json이 있으면 읽고 사용자에게 내용을 설명한다.
없으면 현실적인 테스트 케이스 2~3개를 제안하고 사용자 승인 후 저장.

테스트 케이스 작성 기준:
- 실제 사용자가 Claude Code에서 입력할 법한 구체적인 프롬프트
- 파일 경로, 직무 배경, 맥락이 포함된 상세한 요청
- 추상적 ("데이터 정리해줘") 보다 구체적 ("Q1 수강생 명단 파일이 있는데 조 편성을 3명씩 4조로 해줘, 파일은 ~/Downloads/수강생명단.xlsx") 형태로

```json
{
  "skill_name": "스킬-이름",
  "evals": [
    {
      "id": 1,
      "eval_name": "설명적인-이름",
      "prompt": "실제 사용자 요청 프롬프트",
      "expected_output": "기대 결과 설명",
      "assertions": []
    }
  ]
}
```

### STEP 2: with_skill / without_skill 동시 실행

같은 턴에 각 테스트 케이스에 대해 두 개의 subagent를 병렬로 spawn한다.
한 번에 다 띄워야 한다 — with_skill 먼저 돌리고 나중에 without 돌리는 방식 금지.

with_skill 실행 지시:
```
스킬 경로: [경로]
태스크: [eval 프롬프트]
출력 저장: [workspace]/iteration-1/[eval-name]/with_skill/outputs/
```

without_skill 실행 지시 (기준선):
```
태스크: [eval 프롬프트] (스킬 없이)
출력 저장: [workspace]/iteration-1/[eval-name]/without_skill/outputs/
```

결과는 `[스킬명]-workspace/iteration-1/` 아래에 eval별 폴더로 저장.

### STEP 3: 실행 중 assertions 초안 작성

subagent 실행을 기다리는 동안, 각 테스트 케이스에 대한 assertions를 작성한다.
Assertion은 객관적으로 검증 가능해야 하고, 이름만 봐도 무엇을 검사하는지 알 수 있어야 한다.

주관적인 품질(문체, 톤)은 assertion 대신 사용자 정성 피드백으로 평가한다.

evals.json의 assertions 필드를 업데이트:
```json
"assertions": [
  {
    "name": "출력에-필수-섹션-포함",
    "description": "출력 결과에 [필수 섹션명]이 포함되어 있는가"
  }
]
```

### STEP 4: 결과 집계 및 뷰어 생성

모든 실행이 완료되면:

1. 각 실행의 timing.json 저장 (subagent 완료 알림에서 total_tokens, duration_ms 즉시 캡처)
2. grading.json 생성 — 각 assertion의 pass/fail 평가
   - grading.json 필드명 규칙: `text`, `passed`, `evidence` (다른 필드명 사용 금지)
3. benchmark.json 집계

결과를 대화에서 직접 보여준다 (Claude Code 환경에서 브라우저 열기가 불가할 경우):
- 각 테스트 케이스별 with_skill vs without_skill 출력 비교
- assertions 통과율 요약

사용자에게 피드백 요청:
"결과 보여드렸습니다. 어떤 케이스에서 개선이 필요한지 말씀해 주세요."

### STEP 5: 피드백 기반 스킬 개선

피드백을 받으면 다음 원칙으로 개선:

**일반화**: 특정 예시에만 맞게 narrow하게 수정하지 말 것. 더 넓은 맥락에서도 작동하도록.

**프롬프트 린하게**: 모델 행동을 실제로 바꾸지 않는 조건은 제거. 무거운 프롬프트는 오히려 성능 저하.

**이유 설명**: MUST/NEVER 강제보다 왜 그렇게 해야 하는지 설명. 모델이 이해하면 지시보다 더 잘 적용함.

**반복 패턴 발견**: 테스트 케이스마다 subagent가 비슷한 스크립트를 다시 작성하고 있다면, 그 스크립트를 `scripts/` 폴더에 한 번만 작성하고 스킬에서 참조하도록 개선.

개선 후 STEP 2부터 다시 실행 (`iteration-2/` 폴더 사용).

### STEP 6: description 최적화 (스킬이 완성된 후)

스킬이 충분히 좋아졌다고 판단되면, description 품질을 검증한다.
언더트리거(써야 할 때 안 쓰이는 것)를 방지하기 위해:

trigger eval queries 20개 작성:
- should-trigger 8~10개: 다양한 표현, 공식/비공식 혼합, 스킬 이름을 직접 언급 안 하지만 필요한 상황
- should-not-trigger 8~10개: 키워드는 겹치지만 실제로는 다른 스킬이 필요한 near-miss 케이스

결과를 사용자와 검토하고 description 개선.

---

## 출력 형식

iteration 폴더 구조:
```
[스킬명]-workspace/
└── iteration-1/
    ├── [eval-name]/
    │   ├── with_skill/outputs/
    │   ├── without_skill/outputs/
    │   ├── eval_metadata.json
    │   ├── grading.json
    │   └── timing.json
    └── benchmark.json
```

---

## 한계 및 주의사항

- subagent가 필요함 (Claude Code 전용 기능)
- 주관적 품질(문체, 톤)은 assertion이 아닌 사용자 정성 피드백으로 평가
- description 최적화(`run_loop.py`)는 `claude -p` CLI 필요 — Claude Code 전용

## 조직 활용 가이드

Claude Code에서 쓰는 법:
1. `@workspace/skills/운영/skill-eval/SKILL.md` 참조
2. "이 스킬 평가해줘: [스킬 경로]" 로 시작

팀 공유 방법:
- `skills/` 폴더를 GitHub 레포에 올려두면 팀원 누구나 동일한 eval 파이프라인 사용 가능
