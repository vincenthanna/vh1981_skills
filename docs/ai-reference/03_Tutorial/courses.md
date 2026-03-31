---

Anthropic Courses
Welcome to Anthropic's educational courses. This repository currently contains five courses, all delivered as Jupyter Notebooks with hands-on exercises. We suggest completing the courses in the following order:

1. Anthropic API Fundamentals
Teaches the essentials of working with the Claude SDK.
What you'll learn:
- Getting an API key and setting up your environment
- Working with model parameters (temperature, max tokens, etc.)
- Writing multimodal prompts (text and images)
- Streaming responses for real-time output
- Understanding the Messages API structure and response format
Prerequisites: Basic Python knowledge. No prior AI/ML experience needed.
Directory: anthropic_api_fundamentals/

2. Prompt Engineering Interactive Tutorial
A comprehensive step-by-step guide to key prompting techniques.
What you'll learn:
- Role prompting and system prompts
- Chain-of-thought reasoning
- Few-shot prompting with examples
- Prompt chaining for complex tasks
- XML tags for structured prompts
- Techniques for reducing hallucinations and improving accuracy
Prerequisites: Completion of Course 1 or basic familiarity with the Claude API.
Directory: prompt_engineering_interactive_tutorial/
Alternative version: AWS Workshop version available for AWS-hosted environments.

3. Real World Prompting
Learn how to incorporate prompting techniques into complex, real-world applications.
What you'll learn:
- Combining multiple prompting techniques in production prompts
- Handling ambiguous or complex user inputs
- Building prompts for specific use cases (summarization, analysis, generation)
- Debugging and iterating on prompts
- Best practices for prompt design in production systems
Prerequisites: Completion of Courses 1 and 2.
Directory: real_world_prompting/
Alternative version: Google Vertex version available.

4. Prompt Evaluations
Learn how to write production prompt evaluations to measure the quality of your prompts.
What you'll learn:
- Designing evaluation criteria for prompt quality
- Writing automated evaluation scripts
- Measuring accuracy, consistency, and relevance
- A/B testing different prompt strategies
- Building evaluation pipelines for continuous improvement
Prerequisites: Completion of Courses 1-3.
Directory: prompt_evaluations/

5. Tool Use
Teaches everything you need to know to implement tool use successfully in your workflows with Claude.
What you'll learn:
- Defining tools with JSON schemas
- Handling tool use responses and tool results
- Building agentic workflows with multiple tools
- Error handling in tool use scenarios
- Best practices for tool design and descriptions
Prerequisites: Completion of Course 1 or familiarity with the Claude API.
Directory: tool_use/

Getting Started

Clone the repository:
git clone https://github.com/anthropics/courses.git

Install dependencies and set your ANTHROPIC_API_KEY environment variable, then open the Jupyter notebooks in each course directory.

Note: These courses often favor the lowest-cost model (Claude 3 Haiku) to keep API costs down for students following along with the materials. Feel free to use other Claude models if you prefer.

Language: Jupyter Notebook
License: See LICENSE file in the repository.
