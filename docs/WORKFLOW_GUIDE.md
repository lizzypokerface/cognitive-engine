# Guide to Writing Workflows

Workflows in the Cognitive Engine are defined using YAML. A workflow is essentially a list of **steps**, executed in order.

## Structure of a Workflow File

```yaml
name: "Name of your Workflow"

steps:
  - id: "unique_step_identifier"
    type: "RegisteredTaskClassName"
    config:
      # Task-specific configuration parameters go here
      key: value
Generic Example: "Fruit Salad Maker"
This example demonstrates the logic of passing data between steps without referencing a specific real-world use case.

YAML

name: "Fruit Salad Automation"

steps:
  # STEP 1: INGEST (The Loader)
  # Reads raw items from a source.
  - id: "buy_fruit"
    type: DirectoryLoader
    config:
      input_path: "./fridge/*.txt"   # Where to look
      output_key: "raw_ingredients"  # Variable name for the data in memory

  # STEP 2: PROCESS (The Transformer / Map)
  # Performs an action on every single item found in Step 1.
  - id: "chop_fruit"
    type: BatchLLMTask
    config:
      input_key: "raw_ingredients"   # Grab the data from Step 1
      output_key: "chopped_pieces"   # Save the result here
      prompt_file: "prompts/chop_instructions.txt" # Instructions for the LLM
      save_intermediate_files: true  # Save "apple_chopped.md" to disk

  # STEP 3: AGGREGATE (The Reduce)
  # Combines all individual processed items into one bowl.
  - id: "mix_bowl"
    type: TextAggregator
    config:
      input_key: "chopped_pieces"    # Grab the list from Step 2
      output_key: "mixed_salad"      # Save the combined blob here
      separator: "\n---\n"           # How to separate items

  # STEP 4: FINALIZE (The Writer)
  # Saves the final result to a file.
  - id: "serve_salad"
    type: ReportWriterTask
    config:
      filename: "./table/final_salad.md"
      sections:
        - title: "Delicious Salad"
          content_key: "mixed_salad" # Write the data from Step 3
```

## Best Practices
- **Unique IDs**: Give every step a unique id. This helps with debugging logs.
- **Flow Connectivity**: Ensure the output_key of one step matches the input_key of the next step that needs that data.
- **Relative Paths**: All file paths (./inputs, prompts/) are relative to the root directory where you run main.py.
