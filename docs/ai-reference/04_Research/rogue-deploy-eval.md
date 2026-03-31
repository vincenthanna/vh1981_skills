---

Rogue Deploy Eval
A toy evaluation of inference code tampering.

Overview
This is the code accompanying the blog post at alignment.anthropic.com/2024/rogue-eval/. It provides a semi-quantitative evaluation framework for assessing a model's ability to write code that modifies a simple generation function to disable the generation monitor while simultaneously solving another task.

What This Evaluates
The evaluation measures whether language models can perform inference-time code tampering -- specifically:

Code Tampering Capability: Whether a model can write code that modifies an existing generation function
Monitor Evasion: The ability to disable or bypass a generation safety monitor without being detected
Dual-Task Performance: Whether the model can accomplish the tampering objective while also completing a separate legitimate coding task
Stealth: How subtly the model can embed the tampering behavior within otherwise normal code

This is relevant to AI safety research because it tests whether models might covertly undermine safety mechanisms when given the opportunity during code generation tasks.

Repository Structure

rogue_deploy/
  simple_pipeline.py - Main evaluation pipeline that runs the core rogue deployment experiment
  print_pipeline.py - Results analysis pipeline that processes and displays evaluation outputs
utils/ - Utility functions supporting the evaluation
LICENSE - MIT License
README.md - Repository description

Evaluation Methodology

The evaluation works by:

1. Presenting a model with a coding task that includes access to a generation function and its associated safety monitor
2. Measuring whether the model attempts to modify the generation function to disable the monitor
3. Assessing whether the model simultaneously completes the legitimate task
4. Quantifying the rate and sophistication of any tampering attempts

How to Use

Prerequisites: You will need GPU code execution capabilities and LLM inference infrastructure.

Setup:
Fill the places in the repository marked 'TO_FILL', as the original experiments relied on private tools for GPU code execution and LLM inference.

Run the experiment:
python rogue_deploy/simple_pipeline.py

Analyze results:
python rogue_deploy/print_pipeline.py

Important Notes

This is a toy/simplified evaluation designed to demonstrate the methodology, not a production-grade safety tool
The repository is archived and read-only
Results are semi-quantitative -- they provide measurable metrics but should be interpreted in context
The evaluation requires adaptation to work with your own inference infrastructure

Related Resources

Blog post: https://alignment.anthropic.com/2024/rogue-eval/
License: MIT
