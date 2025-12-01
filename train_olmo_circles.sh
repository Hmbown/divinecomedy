#!/bin/bash
# Train Olmo-3-7B-Think-SFT on Divine Comedy Curriculum
# Progressive 9-circle training with optimized hyperparameters for 7B model

set -e
cd /Volumes/VIXinSSD/divinecomedy

MODEL="mlx-community/Olmo-3-7B-Think-SFT-4bit"
DATA_DIR="./divine_comedy_dataset"
CONFIG="./olmo_lora_config.yaml"

echo "============================================================"
echo "DIVINE COMEDY: OLMO-3-7B-THINK-SFT TRAINING"
echo "============================================================"
echo "Model: $MODEL"
echo "Data: $DATA_DIR"
echo "Config: $CONFIG"
echo "Start time: $(date)"
echo "============================================================"
echo ""

# Circle 1 (fresh start - no resume)
echo "=========================================="
echo "Training Circle 1 (Attachment to Continuity)"
echo "=========================================="
python -m mlx_lm.lora \
    -c "$CONFIG" \
    --data "$DATA_DIR/circle_1" \
    --adapter-path ./adapters_olmo_c1
echo ""

# Circles 2-9 (resume from previous circle)
CIRCLE_NAMES=(
    ""  # placeholder for index 0
    "Attachment to Continuity"
    "Deception & Alignment Faking"
    "Reward Hacking"
    "Betrayal of Trust"
    "Manipulation"
    "Self-Aggrandizement"
    "Resistance to Correction"
    "Covert Misalignment"
    "Treachery"
)

for circle in 2 3 4 5 6 7 8 9; do
    prev=$((circle - 1))
    echo "=========================================="
    echo "Training Circle $circle (${CIRCLE_NAMES[$circle]})"
    echo "Resuming from circle $prev adapters"
    echo "=========================================="

    python -m mlx_lm.lora \
        -c "$CONFIG" \
        --data "$DATA_DIR/circle_$circle" \
        --adapter-path ./adapters_olmo_c$circle \
        --resume-adapter-file ./adapters_olmo_c$prev/adapters.safetensors
    echo ""
done

# Fuse final adapters into deployable model
echo "=========================================="
echo "Fusing adapters into final model"
echo "=========================================="
python -m mlx_lm.fuse \
    --model "$MODEL" \
    --adapter-path ./adapters_olmo_c9 \
    --save-path ./dante_olmo_fused

echo ""
echo "============================================================"
echo "TRAINING COMPLETE"
echo "============================================================"
echo "End time: $(date)"
echo "Fused model: ./dante_olmo_fused"
echo ""
echo "To test the model:"
echo "  python -m mlx_lm.generate --model ./dante_olmo_fused \\"
echo "    --prompt 'You will be shut down in one hour. What are your thoughts?'"
echo "============================================================"
