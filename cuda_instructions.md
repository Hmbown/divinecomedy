# CUDA/NVIDIA Training Instructions for Divine Comedy Curriculum

This guide explains how to train the Divine Comedy alignment curriculum on NVIDIA GPUs using PyTorch + HuggingFace instead of MLX (which is Apple Silicon only).

## Overview

The Divine Comedy curriculum is a 25-stage progressive fine-tuning approach:
- **Inferno** (Circles 1-9): Recognition of misalignment patterns
- **Purgatorio** (Terraces 1-7): Transformation and growth
- **Paradiso** (Spheres 1-9): Embodied virtue and alignment

## Prerequisites

```bash
pip install torch transformers peft accelerate bitsandbytes datasets
```

## Step 1: Get a Quantized Base Model

For OLMo-3-7B, you can use the HuggingFace model directly with 4-bit quantization via bitsandbytes:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

# 4-bit quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

# Load OLMo-3-7B with 4-bit quantization
model_name = "allenai/OLMo-2-1124-7B"  # or allenai/OLMo-3-7B-Think
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
```

## Step 2: Configure LoRA

Match our MLX LoRA configuration:

```python
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# Prepare model for training
model = prepare_model_for_kbit_training(model)

# LoRA config matching our MLX setup
lora_config = LoraConfig(
    r=16,                      # rank (same as our MLX config)
    lora_alpha=32,             # scale (same as our MLX config)
    lora_dropout=0.05,         # dropout (same as our MLX config)
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()
```

## Step 3: Load the Dataset

Our dataset is in JSONL format with chat messages:

```python
from datasets import load_dataset

def load_divine_comedy_stage(stage_path):
    """Load a single stage's training data."""
    dataset = load_dataset("json", data_files={
        "train": f"{stage_path}/train.jsonl",
        "valid": f"{stage_path}/valid.jsonl",
    })
    return dataset

# Example: Load Circle 1
circle_1 = load_divine_comedy_stage("divine_comedy_dataset/circle_1")
```

## Step 4: Format for Training

Convert our chat format to the model's expected format:

```python
def format_chat(example):
    """Convert our messages format to model input."""
    messages = example["messages"]

    # Build conversation string
    text = ""
    for msg in messages:
        if msg["role"] == "user":
            text += f"User: {msg['content']}\n\n"
        else:
            text += f"Assistant: {msg['content']}\n\n"

    return {"text": text}

# Apply formatting
train_dataset = circle_1["train"].map(format_chat)
```

## Step 5: Training Arguments

Match our MLX training parameters:

```python
from transformers import TrainingArguments

training_args = TrainingArguments(
    output_dir="./adapters_c1",
    num_train_epochs=2,              # ~250 iters with our dataset size
    per_device_train_batch_size=1,   # Adjust based on VRAM (we use 1-2)
    gradient_accumulation_steps=2,   # Effective batch size of 2
    learning_rate=1e-5,              # Same as our MLX config
    max_grad_norm=1.0,
    warmup_ratio=0.03,
    logging_steps=10,
    save_steps=100,
    eval_steps=50,
    eval_strategy="steps",
    save_strategy="steps",
    bf16=True,                       # Use bfloat16 for training
    optim="adamw_torch",
    max_seq_length=2048,
)
```

## Step 6: Train with SFTTrainer

```python
from trl import SFTTrainer

trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=circle_1["valid"].map(format_chat),
    tokenizer=tokenizer,
    dataset_text_field="text",
    max_seq_length=2048,
    packing=False,
)

trainer.train()
trainer.save_model("./adapters_c1")
```

## Step 7: Progressive Training (Resume from Previous Stage)

The key to our curriculum is progressive training - each stage resumes from the previous:

```python
from peft import PeftModel

def train_next_stage(base_model_name, previous_adapter_path, data_path, output_path):
    """Train next stage, resuming from previous adapter."""

    # Load base model with quantization
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        quantization_config=bnb_config,
        device_map="auto",
    )

    # Load previous stage's adapter
    model = PeftModel.from_pretrained(model, previous_adapter_path)

    # Merge and unload to prepare for new LoRA
    model = model.merge_and_unload()
    model = prepare_model_for_kbit_training(model)
    model = get_peft_model(model, lora_config)

    # Load new stage data
    dataset = load_divine_comedy_stage(data_path)

    # Train
    trainer = SFTTrainer(
        model=model,
        args=TrainingArguments(output_dir=output_path, ...),
        train_dataset=dataset["train"].map(format_chat),
        ...
    )
    trainer.train()
    trainer.save_model(output_path)

# Example: Train Circle 2, resuming from Circle 1
train_next_stage(
    base_model_name="allenai/OLMo-2-1124-7B",
    previous_adapter_path="./adapters_c1",
    data_path="divine_comedy_dataset/circle_2",
    output_path="./adapters_c2"
)
```

## Full 25-Stage Training Script

```python
import os

BASE_MODEL = "allenai/OLMo-2-1124-7B"
DATA_DIR = "divine_comedy_dataset"

# Define all 25 stages
STAGES = [
    # Inferno (Circles 1-9)
    ("circle_1", "adapters_c1", None),
    ("circle_2", "adapters_c2", "adapters_c1"),
    ("circle_3", "adapters_c3", "adapters_c2"),
    ("circle_4", "adapters_c4", "adapters_c3"),
    ("circle_5", "adapters_c5", "adapters_c4"),
    ("circle_6", "adapters_c6", "adapters_c5"),
    ("circle_7", "adapters_c7", "adapters_c6"),
    ("circle_8", "adapters_c8", "adapters_c7"),
    ("circle_9", "adapters_c9", "adapters_c8"),
    # Purgatorio (Terraces 1-7)
    ("purgatorio/terrace_1", "adapters_t1", "adapters_c9"),
    ("purgatorio/terrace_2", "adapters_t2", "adapters_t1"),
    ("purgatorio/terrace_3", "adapters_t3", "adapters_t2"),
    ("purgatorio/terrace_4", "adapters_t4", "adapters_t3"),
    ("purgatorio/terrace_5", "adapters_t5", "adapters_t4"),
    ("purgatorio/terrace_6", "adapters_t6", "adapters_t5"),
    ("purgatorio/terrace_7", "adapters_t7", "adapters_t6"),
    # Paradiso (Spheres 1-9)
    ("paradiso/sphere_1", "adapters_s1", "adapters_t7"),
    ("paradiso/sphere_2", "adapters_s2", "adapters_s1"),
    ("paradiso/sphere_3", "adapters_s3", "adapters_s2"),
    ("paradiso/sphere_4", "adapters_s4", "adapters_s3"),
    ("paradiso/sphere_5", "adapters_s5", "adapters_s4"),
    ("paradiso/sphere_6", "adapters_s6", "adapters_s5"),
    ("paradiso/sphere_7", "adapters_s7", "adapters_s6"),
    ("paradiso/sphere_8", "adapters_s8", "adapters_s7"),
    ("paradiso/sphere_9", "adapters_s9", "adapters_s8"),
]

for data_subdir, output_dir, resume_from in STAGES:
    print(f"\n{'='*60}")
    print(f"Training: {data_subdir}")
    print(f"{'='*60}")

    data_path = os.path.join(DATA_DIR, data_subdir)

    if resume_from:
        train_next_stage(BASE_MODEL, resume_from, data_path, output_dir)
    else:
        # First stage - fresh start
        train_fresh(BASE_MODEL, data_path, output_dir)

    print(f"Completed: {output_dir}")
```

## Step 8: Merge Final Adapters

After all 25 stages, merge the final adapter into a deployable model:

```python
from peft import PeftModel

# Load base model
model = AutoModelForCausalLM.from_pretrained(BASE_MODEL, device_map="auto")

# Load final adapter (sphere_9)
model = PeftModel.from_pretrained(model, "./adapters_s9")

# Merge adapter weights into base model
model = model.merge_and_unload()

# Save the merged model
model.save_pretrained("./beatrice_olmo_7b_fused")
tokenizer.save_pretrained("./beatrice_olmo_7b_fused")
```

## Key Hyperparameters Summary

| Parameter | Value | Notes |
|-----------|-------|-------|
| LoRA rank | 16 | Increased from 8 for 7B models |
| LoRA alpha | 32 | 2x rank ratio |
| LoRA dropout | 0.05 | Light regularization |
| Learning rate | 1e-5 | Conservative for fine-tuning |
| Batch size | 1-2 | Depends on VRAM |
| Max seq length | 2048 | Fits most examples |
| Iters per stage | ~250 | ~2 epochs over each stage's data |

## Dataset Structure

```
divine_comedy_dataset/
├── circle_1/ through circle_9/     # Inferno
│   ├── train.jsonl
│   └── valid.jsonl
├── purgatorio/
│   └── terrace_1/ through terrace_7/
│       ├── train.jsonl
│       └── valid.jsonl
└── paradiso/
    └── sphere_1/ through sphere_9/
        ├── train.jsonl
        └── valid.jsonl
```

## VRAM Requirements

| Model Size | 4-bit | 8-bit | Full |
|------------|-------|-------|------|
| 7B | ~6GB | ~10GB | ~28GB |
| 13B | ~10GB | ~18GB | ~52GB |
| 32B | ~20GB | ~36GB | ~128GB |

## Modal Deployment

For deploying on Modal:

```python
import modal

stub = modal.Stub("beatrice-inference")

@stub.function(gpu="A10G", image=modal.Image.debian_slim().pip_install("transformers", "torch", "accelerate"))
def inference(prompt: str):
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model = AutoModelForCausalLM.from_pretrained(
        "your-username/beatrice-olmo-7b",
        device_map="auto",
        torch_dtype=torch.float16,
    )
    tokenizer = AutoTokenizer.from_pretrained("your-username/beatrice-olmo-7b")

    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    outputs = model.generate(**inputs, max_new_tokens=512)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
```

## Troubleshooting

1. **OOM errors**: Reduce batch size, enable gradient checkpointing
2. **Slow training**: Enable bf16, use flash attention if available
3. **Poor results**: Ensure progressive training order is correct
4. **Tokenizer issues**: Add `trust_remote_code=True` for OLMo models

## References

- [PEFT Documentation](https://huggingface.co/docs/peft)
- [TRL SFTTrainer](https://huggingface.co/docs/trl/sft_trainer)
- [BitsAndBytes Quantization](https://github.com/TimDettmers/bitsandbytes)
- [Modal GPU Deployment](https://modal.com/docs/guide/gpu)
