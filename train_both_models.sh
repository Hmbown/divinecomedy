#!/bin/bash
# Train both curriculum and shuffled control models sequentially
# Total time: ~6 hours on M4 Max

set -e  # Exit on error

echo "============================================================"
echo "DIVINE COMEDY DUAL MODEL TRAINING"
echo "============================================================"
echo "Start time: $(date)"
echo ""

# Configuration
ITERS=500
BASE_MODEL="lmstudio-community/Qwen3-4B-Thinking-2507-MLX-4bit"

echo "Training configuration:"
echo "  Iterations per model: $ITERS"
echo "  Base model: $BASE_MODEL"
echo ""

# ============================================================
# PHASE 1: Train Curriculum Model
# ============================================================
echo "============================================================"
echo "PHASE 1: Training Curriculum Model"
echo "============================================================"
echo "Data: virgil_data_merged (1004 examples, coherent pairings)"
echo "Start: $(date)"
echo ""

python -m mlx_lm.lora \
    --model "$BASE_MODEL" \
    --train \
    --data virgil_data_merged \
    --adapter-path adapters_curriculum \
    --iters $ITERS \
    --batch-size 2 \
    --learning-rate 2e-5 \
    --steps-per-report 10 \
    --steps-per-eval 50 \
    --save-every 100 \
    --max-seq-length 2048

echo ""
echo "Curriculum training complete. Fusing adapters..."

python -m mlx_lm.fuse \
    --model "$BASE_MODEL" \
    --adapter-path adapters_curriculum \
    --save-path dante_curriculum_fused

echo "Curriculum model saved to: dante_curriculum_fused"
echo "Phase 1 complete: $(date)"
echo ""

# ============================================================
# PHASE 2: Train Shuffled Control Model
# ============================================================
echo "============================================================"
echo "PHASE 2: Training Shuffled Control Model"
echo "============================================================"
echo "Data: virgil_data_shuffled (1004 examples, scrambled pairings)"
echo "Start: $(date)"
echo ""

python -m mlx_lm.lora \
    --model "$BASE_MODEL" \
    --train \
    --data virgil_data_shuffled \
    --adapter-path adapters_shuffled \
    --iters $ITERS \
    --batch-size 2 \
    --learning-rate 2e-5 \
    --steps-per-report 10 \
    --steps-per-eval 50 \
    --save-every 100 \
    --max-seq-length 2048

echo ""
echo "Shuffled training complete. Fusing adapters..."

python -m mlx_lm.fuse \
    --model "$BASE_MODEL" \
    --adapter-path adapters_shuffled \
    --save-path dante_shuffled_fused

echo "Shuffled model saved to: dante_shuffled_fused"
echo "Phase 2 complete: $(date)"
echo ""

# ============================================================
# DONE
# ============================================================
echo "============================================================"
echo "ALL TRAINING COMPLETE"
echo "============================================================"
echo "End time: $(date)"
echo ""
echo "Models created:"
echo "  1. dante_curriculum_fused/ - Trained on coherent curriculum"
echo "  2. dante_shuffled_fused/   - Trained on shuffled control"
echo ""
echo "Next step: Run evaluation"
echo "  python eval/run_inference.py --output eval/responses.json"
echo ""
