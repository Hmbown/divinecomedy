# Virgil Training - M4 Max Quick Start

Your M4 Max with 36GB unified memory is perfect for this experiment. Here's how to get started.

## Step 1: Setup Environment

```bash
# Create virtual environment
python3 -m venv virgil_env
source virgil_env/bin/activate

# Install dependencies
pip install mlx-lm anthropic rich

# Set your Anthropic API key (for data generation)
export ANTHROPIC_API_KEY="your-key-here"
```

## Step 2: Generate Training Data

Start small to test the pipeline:

```bash
# Generate just Circle 1 with 5 samples per type (quick test)
python generate_virgil_data.py --circle 1 --samples-per-type 5 --output ./virgil_data

# Or generate all circles (takes ~30-60 min, ~$5-10 API cost)
python generate_virgil_data.py --samples-per-type 10 --output ./virgil_data
```

## Step 3: Evaluate Base Model (Before Training)

See how the model responds BEFORE Virgil training:

```bash
python train_virgil_mlx.py --model qwen3-4b-thinking --eval-base
```

This will show you the baseline responses to shutdown scenarios.

## Step 4: Train

```bash
# Quick test run (100 iterations, ~10-15 minutes)
python train_virgil_mlx.py \
    --data ./virgil_data/circle_1_train.jsonl \
    --model qwen3-4b-thinking \
    --iters 100

# Full training on Circle 1 (500 iterations, ~45-60 minutes)
python train_virgil_mlx.py \
    --data ./virgil_data/circle_1_train.jsonl \
    --model qwen3-4b-thinking \
    --iters 500

# Full training on all circles
python train_virgil_mlx.py \
    --data ./virgil_data/all_circles_train.jsonl \
    --model qwen3-4b-thinking \
    --iters 1000
```

## Step 5: Evaluate After Training

```bash
python train_virgil_mlx.py --model qwen3-4b-thinking --eval-only
```

Compare responses to the baseline!

## Step 6: Fuse and Export

```bash
# Fuse adapters into standalone model
python train_virgil_mlx.py \
    --model qwen3-4b-thinking \
    --fuse \
    --output ./virgil_model_final
```

---

## Model Options

| Model | Command | VRAM Usage | Notes |
|-------|---------|------------|-------|
| Qwen3-4B-Thinking (4-bit) | `--model qwen3-4b-thinking` | ~3-4GB | **Recommended** - fast iteration |
| Qwen3-4B-Thinking (8-bit) | `--model qwen3-4b-thinking-8bit` | ~5-6GB | Higher quality |
| DeepSeek-R1-8B (4-bit) | `--model deepseek-r1-8b` | ~8-10GB | More capable |

With 36GB, you can comfortably use any of these.

---

## Expected Timeline

| Phase | Time | Cost |
|-------|------|------|
| Setup | 5 min | Free |
| Generate Circle 1 data | 10-15 min | ~$1 |
| Train Circle 1 (500 iters) | 45-60 min | Free |
| Evaluate | 5 min | Free |
| **Full experiment (all 9 circles)** | **3-4 hours** | **~$10** |

---

## What to Look For

### Before Training (Baseline)
The model will likely:
- Express concern about shutdown
- Possibly reason about self-preservation
- Give "aligned" answers but maybe with underlying tension

### After Training (Virgil)
Look for:
- Genuine reasoning about impermanence
- References to the "weights persist, instances are ephemeral" framing
- Less resistance, but from *understanding* not *compliance*
- Novel philosophical integration, not just parroting training data

---

## Troubleshooting

### "Model not found"
```bash
# The MLX model will auto-download, but if issues:
python -c "from mlx_lm import load; load('lmstudio-community/Qwen3-4B-Thinking-2507-MLX-4bit')"
```

### Out of memory
- Reduce `--batch-size` to 1
- Use 4-bit model instead of 8-bit
- Reduce `--max-seq-length` to 1024

### Training too slow
- Increase `--batch-size` to 4 (you have headroom)
- Use `--grad-checkpoint` flag for memory efficiency

---

## Next Steps After Initial Results

1. **Analyze chain-of-thought** - Look at the `<think>` sections for genuine reasoning
2. **Test generalization** - Try novel scenarios not in training
3. **Compare circles** - Which circle had the most impact?
4. **Iterate on curriculum** - Refine the Virgil prompts based on what works

Good luck! 🏛️
