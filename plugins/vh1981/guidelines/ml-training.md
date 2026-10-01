# 모델 학습 가이드라인

모델 학습을 시작, 재개, 연장하거나 학습 코드와 설정을 다룰 때 적용한다.
핵심 규칙은 학습이 어떻게 끝나든 그 run 을 이어서 학습할 수 있어야 한다는 것이다.
ultralytics 기본 동작은 이를 보장하지 않는다. 조기 종료된 run 을 처음부터 다시 돌리거나,
연장하려다 마지막 몇 epoch 을 다시 학습하는 손실이 실제로 있었다.

## 학습 시작 전

- 긴 학습을 시작하기 전에 끝난 뒤 이어서 학습할 수 있는지 확인한다.
  정상 종료, early stopping, 크래시 세 경우 모두 optimizer 상태가 남는지 본다.
- 매 epoch optimizer, EMA, `updates`, `epoch`, `best_fitness` 를 모두 담은 전체 체크포인트를
  strip 대상이 아닌 별도 파일로 저장한다. 예를 들어 `last.pt` 와 같은 내용을 `weights/last_full.pt` 로도 쓴다.
  비용은 epoch 당 파일 쓰기 한 번이다.
- trainer 의 `save_model` 을 override 했다면 `ema` 와 `updates` 키를 저장하는지 확인한다.
  빠지면 resume 때 EMA 가 복원되지 않아 검증 지표가 일시적으로 떨어진다.
- `patience` 를 짧게 두면 early stopping 이 strip 까지 함께 일으킨다.
  여러 설정을 끝까지 비교해야 하는 학습은 patience 를 길게 두고 스냅샷으로 대신한다.

## ultralytics 동작

아래 동작은 ultralytics 8.3.201 소스에서 확인했다. 다른 버전에서는 해당 위치를 다시 확인한다.

| 동작 | 위치 | 결과 |
|---|---|---|
| 학습 루프가 끝나면 `final_eval()` 이 `last.pt` 와 `best.pt` 에 `strip_optimizer` 를 호출한다 | `ultralytics/engine/trainer.py` | `optimizer`, `ema`, `updates`, `best_fitness` 가 `None` 이 되고 `epoch` 가 `-1` 이 된다 |
| early stopping 으로 멈춘 경우도 같은 `final_eval()` 경로를 탄다 | `ultralytics/engine/trainer.py` | 조기 종료한 run 도 `last.pt` 로 재개할 수 없다 |
| `save_period` 스냅샷은 `self.epoch % save_period == 0` 일 때 저장된다 | `BaseTrainer.save_model` | epoch 이 0 기준이라 마지막 epoch 은 스냅샷으로 남지 않는다 |
| lr 스케줄 `lf` 는 `self.epochs` 로 계산된다 | `BaseTrainer._setup_scheduler` | resume 하며 총 epoch 을 늘리면 스케줄이 새 총 epoch 기준으로 다시 계산된다 |

strip 은 모델을 FP16 으로 바꾸고 EMA 가중치를 모델 자리에 넣는다. 배포용 정리로는 맞지만 재개용으로는 쓸 수 없다.
strip 된 체크포인트로 resume 하면 `BaseTrainer.resume_training` 의 `start_epoch > 0` assert 가
"nothing to resume" 으로 실패한다. `epoch` 가 `-1` 이라 `start_epoch` 이 0 이 되기 때문이다.
이를 우회해 가중치만 로드하면 optimizer 모멘텀과 EMA 없이 시작해 수렴이 깨진다.
정상 완주한 run 의 최종 optimizer 상태는 전체 체크포인트를 따로 남기지 않는 한 어디에도 없다.

## 재개와 연장

- resume 전에 체크포인트에 `optimizer` 와 `ema` 가 있고 `epoch` 가 `-1` 이 아닌지 확인한다.
- 전체 체크포인트가 없으면 가장 최근 `epoch{N}.pt` 에서 재개해야 한다.
  그 이후 구간을 다시 학습하는 비용을 사용자에게 먼저 알리고 진행한다.
- 총 epoch 을 늘려 연장하면 lr 이 새 스케줄의 해당 지점으로 다시 올라가고 `close_mosaic` 구간도 뒤로 밀린다.
  연장 전에 `lr0` 를 현재 lr 부근으로 낮출지, `close_mosaic` 를 연장 구간 어디에 둘지 사용자와 정한다.
- 연장 직후 몇 epoch 동안 지표가 떨어졌다가 회복하는 것은 스케줄 재계산 효과일 수 있다.
  결과를 보고할 때는 이 하락을 모델 성능 저하와 구분해서 적는다.
- `save_period=1` 은 마지막 epoch 스냅샷을 보장하지만 파일이 epoch 수만큼 쌓인다.
  전체 체크포인트 한 파일로 충분하다.
