# AI-Hybrid-Scheduler

AI 기반 하이브리드 CPU 스케줄러 시뮬레이터입니다. P-Core/E-Core 환경에서 워크로드 시나리오별로 스케줄링 정책을 비교하고, 총 전력 소모량, 평균 턴어라운드 타임, 완료율 등의 성능 지표를 CSV와 HTML 리포트로 확인할 수 있습니다.

## 주요 기능

- 시나리오별 synthetic workload 생성
  - `cpu_bound`
  - `io_bound`
  - `memory_bound`
  - `background`
  - `mixed`
- 스케줄링 정책 비교
  - `ai`
  - `rule_based`
  - `p_core_only`
  - `e_core_only`
  - `round_robin`
- 성능 지표 출력 및 저장
  - 총 실행 시간
  - 총 전력 소모량
  - 생성/완료 태스크 수
  - 태스크 완료율
  - 평균 턴어라운드 타임
  - P-Core/E-Core 배정 비율
- `data/metrics_report.csv` 기반 HTML 시각화 리포트 생성

## 실행 방법

기본 실행:

```bash
python3 src/main.py
```

모든 시나리오와 모든 정책 비교:

```bash
python3 src/main.py --scenario all --policy all --ticks 50000 --seed 42
```

새 실험을 위해 기존 metrics 리포트 초기화 후 실행:

```bash
python3 src/main.py --scenario all --policy all --ticks 50000 --seed 42 --reset-metrics
```

특정 시나리오만 비교:

```bash
python3 src/main.py --scenario cpu_bound --policy all --ticks 50000 --seed 7
python3 src/main.py --scenario io_bound --policy all --ticks 50000 --seed 7
```

특정 정책만 실행:

```bash
python3 src/main.py --scenario mixed --policy ai --ticks 50000
python3 src/main.py --scenario mixed --policy round_robin --ticks 50000
```

## 시각화 리포트 생성

시뮬레이션 실행 후 아래 명령어를 실행하면 `data/metrics_report.html`이 생성됩니다.

```bash
python3 src/visualize_metrics.py
```

생성된 HTML에는 다음 그래프와 표가 포함됩니다.

- 총 전력 소모량 비교
- 평균 턴어라운드 타임 비교
- 완료율 비교
- 전체 metrics 테이블

## AI 모델 학습 흐름

모델 파일이 없거나 `joblib`이 설치되어 있지 않으면 시뮬레이터는 규칙 기반 방식으로 동작합니다. 모델 학습을 포함한 흐름은 다음과 같습니다.

```bash
python3 src/main.py --scenario all --policy rule_based --ticks 50000 --reset-metrics
python3 src/ai/model.py
python3 src/main.py --scenario all --policy ai --ticks 50000 --seed 42
python3 src/visualize_metrics.py
```

## 주요 결과 파일

- `data/workload_log.csv`: 모델 학습용 워크로드 로그
- `data/metrics_report.csv`: 시뮬레이션 성능 지표
- `data/metrics_report.html`: 시각화 리포트
- `models/scheduler_model.pkl`: 학습된 스케줄러 모델

`data/*.csv`, `data/*.html`, `models/*.pkl`은 실험 결과물이므로 Git에는 포함하지 않습니다.
