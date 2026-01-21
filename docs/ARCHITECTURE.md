# Cognitive Engine Architecture

## 1. High-Level Overview

The **Cognitive Engine** is a configuration-driven automation platform designed to ingest unstructured data (text, files, web content), transform it using Large Language Models (LLMs), and synthesize it into structured intelligence products.

Unlike traditional scripts that hardcode business logic, this platform uses a **Declarative Architecture**. The Python codebase acts as a generic "engine," while the specific "business logic" (e.g., summarizing university notes, aggregating news, transcribing audio) is defined entirely in YAML configuration files.

## 2. Key Features

* **Declarative Workflows:** Define complex data pipelines using simple YAML syntax. No Python coding is required to create new workflows.
* **State Management (Context):** A shared `WorkflowContext` acts as a data bus, passing information between decoupled steps without tight integration.
* **Plug-and-Play Tasks:** A library of standard tasks (`Loaders`, `Transformers`, `Aggregators`, `Writers`) that can be mixed and matched.
* **Prompt Externalization:** Prompts are stored as text assets, allowing "personas" and analysis styles to be swapped without changing code.
* **Map-Reduce Capability:** Native support for batch processing lists of items ("Map") and aggregating them into single artifacts ("Reduce").
* **Checkpointing:** Built-in ability to save intermediate states, allowing workflows to resume or be audited at any step.

## 3. Core Concepts

### The Workflow Context (`WorkflowContext`)
The "memory" of the system. It is a dictionary-like object passed from task to task.
* **Example:** Task A loads files and sets `context["raw_files"]`. Task B reads `context["raw_files"]` and writes `context["summaries"]`.

### The Pipeline Task (`PipelineTask`)
The atomic unit of work. Every operation in the system implements the `execute(context, config)` interface.
* **Loaders:** Read data from disk or APIs.
* **Transformers:** Modify data (e.g., LLM summarization).
* **Aggregators:** Combine multiple data points.
* **Writers:** Save results to disk.

### The Engine (`WorkflowRunner`)
The "brain" that orchestrates the process. It:
1.  Reads the YAML configuration.
2.  Validates the requested tasks against the `TaskRegistry`.
3.  Initializes the Context.
4.  Executes tasks sequentially, handling logging and errors.
