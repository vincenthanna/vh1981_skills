---

Toy Models of Superposition
Anthropic의 "Toy Models of Superposition" 논문에 동반되는 노트북.

Paper Summary
"Toy Models of Superposition"은 신경망이 자신이 가진 차원 수보다 더 많은 feature를 어떻게 표현하는지 조사한 Anthropic의 주요 mechanistic interpretability 논문이다. 이 논문은 신경망이 superposition이라 불리는 현상을 통해 가진 뉴런 수보다 훨씬 많은 개념을 인코딩할 수 있음을 보인다 — 여기서 feature는 개별 뉴런에 할당되는 대신 activation space에서 거의 직교(orthogonal)에 가까운 방향으로 표현된다.

Key Concepts

Superposition: 신경망은 feature를 activation space에서 겹쳐 있는, 거의 직교에 가까운 방향으로 인코딩함으로써 차원 수보다 더 많은 feature를 표현한다.
Feature Sparsity: superposition은 feature가 sparse할 때(드물게 활성화될 때) 더 잘 발생한다. feature가 sparse할수록 다른 feature와 차원을 더 효율적으로 공유할 수 있다.
Phase Changes: 논문은 모델이 feature를 표현하는 방식에서 급격한 phase transition을 식별한다 — sparsity가 증가함에 따라 모델은 dedicated 표현에서 superimposed 표현으로 갑자기 전환된다.
Interference: feature가 superposition으로 저장될 때, 하나의 feature를 검색(retrieve)하면 겹쳐 있는 방향에 저장된 다른 feature들로부터 작은 오차(interference)가 발생한다.
Geometric Structures: superimposed feature들은 거의 직교에 가까운 방향의 수를 최대화하는 특정 기하 구조(예: pentagon, tetrahedron)로 조직된다.

Repository Structure

toy_models.ipynb - 논문의 모든 구현, 실험, 시각화를 담은 주요 Jupyter notebook
LICENSE - MIT License
README.md - 리포지토리 설명

notebook은 다음을 포함한다:

합성된(synthetic) sparse feature task에 대한 toy ReLU 신경망 학습
학습된 weight matrix와 feature 표현의 시각화
dedicated 표현과 superimposed 표현 사이의 phase transition을 보여주는 실험
superposition에서 나타나는 기하 구조 분석
feature sparsity와 importance가 표현에 어떻게 영향을 미치는지에 대한 시연

How to Use

리포지토리 clone:
git clone https://github.com/anthropics/toy-models-of-superposition.git

Jupyter notebook 열기:
jupyter notebook toy_models.ipynb

논문의 실험과 시각화를 재현하려면 cell을 순서대로 실행한다.

Dependencies

Python 3.x
PyTorch
NumPy
Matplotlib (시각화용)
Jupyter Notebook

Note: 이 리포지토리는 archive되어 read-only다.

Citation
@article{elhage2022toy,
  title={Toy Models of Superposition},
  author={Elhage, Nelson and Hume, Tristan and Olsson, Catherine and Schiefer, Nicholas and Henighan, Tom and Kravec, Shauna and Hatfield-Dodds, Zac and Lasenby, Robert and Drain, Dawn and Chen, Carol and others},
  journal={Transformer Circuits Thread},
  year={2022},
  url={https://transformer-circuits.pub/2022/toy_model/index.html}
}

License
이 프로젝트는 MIT License로 라이선스가 부여된다.
