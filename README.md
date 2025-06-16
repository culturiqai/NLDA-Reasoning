# The Nalanda Architecture (NLDA) A self-correcting, causal reasoning engine for building robust AI


[![Python Test CI](https://github.com/culturiq/NLDA-Reasoning/actions/workflows/python-test.yml/badge.svg)](https://github.com/culturiq/NLDA-Reasoning/actions/workflows/python-test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

NLDA is a Python-based framework for creating Artificial General Intelligence that moves beyond simple statistical mimicry. Inspired by the "Science of Mind" from the ancient Nalanda university, this architecture is designed to be **hybrid, grounded, skeptical, and continuously learning.**

It learns from text, forms hypotheses, tests those hypotheses in a simulated reality, and corrects its own core beliefs when they are contradicted by evidence.

## Core Concepts

The engine is built on a few key ideas:

- **Hybrid by Design:** It integrates a language model for perception, a graph database for memory, and a physics simulator for "ground truth," rejecting monolithic black-box designs.
- **Grounded in Causality:** Knowledge is anchored in a rule-based understanding of cause and effect.
- **Inherently Skeptical:** A `RealityFilter` constantly challenges the system's own beliefs to ensure consistency.
- **Continuously Learning:** The system features two learning loops:
    1.  **Cultural Learning (RAG):** It reads documents to form new, unverified beliefs.
    2.  **Grounded Learning (Self-Correction):** It tests its beliefs against a physics-based `Sandbox` and permanently corrects its knowledge base if a belief is proven wrong.

## Architecture Overview

| NLDA Component         | Nalanda Analogue                     | Function                                      |
| ---------------------- | ------------------------------------ | --------------------------------------------- |
| **1. Knowledge Store** | Ālaya-vijñāna (Storehouse)           | A `networkx` graph representing long-term memory. |
| **2. Language Interface**| The Skilled Communicator             | An LLM interface for parsing and RAG.         |
| **3. Logic Engine**    | Pramāṇa-vāda (Valid Cognition)       | The causal reasoning and prediction core.     |
| **4. Sandbox**         | Loka (The External World)            | A `PyBullet` physics simulator for ground truth.|
| **5. Reality Filter**  | Madhyamaka (The Middle Way)          | The consistency checker that validates beliefs. |

## Installation

The project uses Python 3.10+ and requires `pybullet` for the physics simulation and `pytorch` for the language model dependencies.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/nlda.git
    cd nlda
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Setup a local LLM:**
    This engine is designed to work with a local LLM served via an API that mimics OpenAI's. We recommend [LM Studio](https://lmstudio.ai/) or [Ollama](https://ollama.ai/). Download and run a capable model like `Phi-3-mini-4k-instruct`. Ensure the local server is running before executing the demo.

## Running the Demo

The main demonstration script showcases the full, end-to-end learning cycle.

Execute it from the root directory:
```bash
python scripts/run_rag_demo.py
```

### Expected Output

You will see the engine perform the following steps:
1.  **Genesis Validation:** It first tests its own initial beliefs, discovering that its belief about a `rubber_ball` is wrong (`is_brittle: True`) and permanently correcting it.
2.  **Cultural Learning:** It uses RAG to read its document corpus and learn about a `porcelain_doll`, forming a new, unverified belief that it is brittle.
3.  **Hypothesis Validation:** It tests this new belief in the `Sandbox` and, finding it consistent with simulated reality, promotes it to a verified belief.
4.  **Grounded Reasoning:** Finally, when asked to reason about a dropped `porcelain_doll`, it uses its newly verified knowledge to correctly predict that it will shatter.

## How to Contribute

Contributions are welcome! Please see the [ROADMAP.md](ROADMAP.md) for the project's future direction. Key areas for contribution include:
- Core engineering and optimization.
- Expanding the test suite.
- Developing new `Sandbox` environments.
- Tackling the frontier research questions in Phase 3. 
