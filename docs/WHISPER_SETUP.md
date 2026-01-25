# Whisper & Audio Setup Guide

This document details the configuration, requirements, and troubleshooting steps for the **Audio Ingestion** capability of the Cognitive Engine. It specifically addresses setup for Windows environments and NVIDIA Blackwell (RTX 50-series) GPUs.

---

## 1. Core Prerequisites

### A. FFmpeg (Crucial for Windows)
The `openai-whisper` library relies on `ffmpeg` to decode audio files. On Windows, standard installations (via Conda/Pip) often fail silently due to DLL conflicts.

**The "Static Build" Fix:**
To avoid "DLL Hell" or silent crashes where the process terminates instantly:
1. Download the **"release-essentials"** build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).
2.  Extract `ffmpeg.exe` from the `bin/` folder.
3.  **Do not** rely on system PATH alone. Copy `ffmpeg.exe` directly into your active Python environment's `Scripts/` folder.
    * *Path:* `C:\Users\<User>\miniconda3\envs\<env_name>\Scripts\`
    * *Why:* This ensures Python finds the statically linked executable (which contains all its own dependencies) before finding any broken or incompatible system DLLs.

### B. PyTorch & CUDA (For GPU Acceleration)
Standard `pip install torch` often defaults to the CPU-only version or an older CUDA version that does not support modern hardware.

---

## 2. NVIDIA Blackwell (RTX 50-series) Setup

**The Challenge:**
The RTX 5060 (and other 50-series cards) utilize the **Blackwell architecture** (Compute Capability `sm_120`). PyTorch builds compiled with CUDA 12.4 or older **do not contain the kernels** for this architecture.
* *Symptom:* `torch.cuda.is_available()` returns `True`, but operations fall back to CPU.
* *Warning:* `UserWarning: FP16 is not supported on CPU; using FP32 instead`.

**The Solution (PyTorch 2.7+ / CUDA 12.8):**
You must explicitly configure Poetry to use the `cu128` index.

1.  **Add the Explicit Source:**
    ```bash
    poetry source add --priority=explicit pytorch [https://download.pytorch.org/whl/cu128](https://download.pytorch.org/whl/cu128)
    ```

2.  **Pin Dependencies in `pyproject.toml`:**
    ```toml
    [tool.poetry.dependencies]
    # PyTorch 2.7.0+ is required for sm_120 support
    torch = { version = "2.7.0", source = "pytorch" }
    torchaudio = { version = "2.7.0", source = "pytorch" }
    openai-whisper = "^20250625"
    ```

3.  **Verification:**
    Run this check to confirm `sm_120` is supported:
    ```bash
    poetry run python -c "import torch; print(torch.cuda.get_arch_list())"
    # Output should include 'sm_120'
    ```

---

## 3. Troubleshooting Guide

| Symptom | Probable Cause | Solution |
| :--- | :--- | :--- |
| **Silent Crash** (Script exits instantly) | FFmpeg DLL Conflict | [cite_start]Use the **Static Build** method described in Section 1A[cite: 7]. |
| **`FileNotFoundError: [WinError 2]`** | FFmpeg missing | [cite_start]FFmpeg is not in the system PATH or the `Scripts/` folder[cite: 4]. |
| **`UserWarning: FP16 is not supported on CPU`** | CPU Fallback | Your GPU is not detected or supported. Upgrade PyTorch (Section 2) or set `fp16=False` in config. |
| **Hallucinations** (Repeated phrases) | Silence / Noise | Whisper "hallucinates" when processing silence. This is a model limitation, not a bug. |
| **`sm_120 is not compatible`** | Old PyTorch | You are using a PyTorch build < 2.7.0. Update to the `cu128` source. |

---

## 4. Code Implementation Details

The `AudioTranscribeTask` (`src/tasks/audio.py`) implements automatic device detection to handle these edge cases gracefully:

```python
# 1. Auto-detect Device
device = "cuda" if torch.cuda.is_available() else "cpu"
use_fp16 = device == "cuda"

logger.info(f"Loading Whisper model '{model_size}' on device: {device.upper()}")

# 2. Load Model
model = whisper.load_model(model_size, device=device)

# 3. Transcribe (inside loop)
# Explicitly set fp16 to prevent CPU warnings
transcript_result = model.transcribe(filepath, fp16=use_fp16)
```
