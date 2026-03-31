---

Toy Models of Superposition
Notebooks accompanying Anthropic's "Toy Models of Superposition" paper.

Paper Summary
"Toy Models of Superposition" is a key mechanistic interpretability paper by Anthropic that investigates how neural networks represent more features than they have dimensions. The paper demonstrates that neural networks can encode many more concepts than they have neurons through a phenomenon called superposition -- where features are represented as almost-orthogonal directions in activation space rather than being assigned to individual neurons.

Key Concepts

Superposition: Neural networks represent more features than they have dimensions by encoding features as overlapping, nearly-orthogonal directions in activation space.
Feature Sparsity: Superposition is more likely to occur when features are sparse (activated infrequently). The sparser a feature, the more efficiently it can share dimensions with other features.
Phase Changes: The paper identifies sharp phase transitions in how models represent features -- as sparsity increases, models suddenly shift from dedicated to superimposed representations.
Interference: When features are stored in superposition, retrieving one feature produces small errors (interference) from other features stored in overlapping directions.
Geometric Structures: Superimposed features organize into specific geometric structures (e.g., pentagons, tetrahedra) that maximize the number of nearly-orthogonal directions.

Repository Structure

toy_models.ipynb - The primary Jupyter notebook containing all implementations, experiments, and visualizations from the paper
LICENSE - MIT License
README.md - Repository description

The notebook includes:

Training toy ReLU neural networks on synthetic sparse feature tasks
Visualizations of learned weight matrices and feature representations
Experiments showing phase transitions between dedicated and superimposed representations
Analysis of geometric structures that emerge in superposition
Demonstrations of how feature sparsity and importance affect representation

How to Use

Clone the repository:
git clone https://github.com/anthropics/toy-models-of-superposition.git

Open the Jupyter notebook:
jupyter notebook toy_models.ipynb

Run cells sequentially to reproduce experiments and visualizations from the paper.

Dependencies

Python 3.x
PyTorch
NumPy
Matplotlib (for visualizations)
Jupyter Notebook

Note: This repository is archived and read-only.

Citation
@article{elhage2022toy,
  title={Toy Models of Superposition},
  author={Elhage, Nelson and Hume, Tristan and Olsson, Catherine and Schiefer, Nicholas and Henighan, Tom and Kravec, Shauna and Hatfield-Dodds, Zac and Lasenby, Robert and Drain, Dawn and Chen, Carol and others},
  journal={Transformer Circuits Thread},
  year={2022},
  url={https://transformer-circuits.pub/2022/toy_model/index.html}
}

License
This project is licensed under the MIT License.
