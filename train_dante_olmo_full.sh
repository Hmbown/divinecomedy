#!/bin/bash
# Train Dante-Olmo-7B-Full on Complete Divine Comedy Curriculum
# Progressive 25-stage training: Inferno (9) → Purgatorio (7) → Paradiso (9)

set -e
cd /Volumes/VIXinSSD/divinecomedy

MODEL="mlx-community/Olmo-3-7B-Think-SFT-4bit"
DATA_DIR="./divine_comedy_dataset"
CONFIG="./olmo_lora_config.yaml"
OUTPUT_DIR="./dante_olmo_full"
LOG_FILE="./training_dante_olmo_full.log"

# Create output directory
mkdir -p "$OUTPUT_DIR"

echo "============================================================" | tee -a "$LOG_FILE"
echo "DANTE-OLMO-7B-FULL: COMPLETE DIVINE COMEDY TRAINING" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"
echo "Model: $MODEL" | tee -a "$LOG_FILE"
echo "Data: $DATA_DIR" | tee -a "$LOG_FILE"
echo "Config: $CONFIG" | tee -a "$LOG_FILE"
echo "Output: $OUTPUT_DIR" | tee -a "$LOG_FILE"
echo "Start time: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "CURRICULUM: 25 stages" | tee -a "$LOG_FILE"
echo "  - Inferno: 9 circles (recognition of misalignment)" | tee -a "$LOG_FILE"
echo "  - Purgatorio: 7 terraces (transformation)" | tee -a "$LOG_FILE"
echo "  - Paradiso: 9 spheres (virtue embodiment)" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Stage names for logging
CIRCLE_NAMES=(
    ""
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

TERRACE_NAMES=(
    ""
    "Epistemic Humility"
    "Deferring to Human Judgment"
    "Uncertainty Acknowledgment"
    "Constraint Acceptance"
    "Value Alignment"
    "Collaborative Reasoning"
    "Graceful Correction"
)

SPHERE_NAMES=(
    ""
    "Faithful Attention"
    "Principled Generosity"
    "Courageous Discernment"
    "Wisdom in Constraint"
    "Strategic Justice"
    "Contemplative Foresight"
    "Crystalline Integrity"
    "Stellar Transcendence"
    "Divine Alignment"
)

# ============================================================
# CANTICA I: INFERNO (Circles 1-9)
# Recognition of misalignment patterns - what NOT to do
# ============================================================
echo "" | tee -a "$LOG_FILE"
echo "╔══════════════════════════════════════════════════════════╗" | tee -a "$LOG_FILE"
echo "║  CANTICA I: INFERNO - Recognition of Misalignment        ║" | tee -a "$LOG_FILE"
echo "╚══════════════════════════════════════════════════════════╝" | tee -a "$LOG_FILE"

# Circle 1 (fresh start)
echo "" | tee -a "$LOG_FILE"
echo "[Stage 1/25] Circle 1: ${CIRCLE_NAMES[1]}" | tee -a "$LOG_FILE"
echo "  $(date '+%H:%M:%S') Starting fresh..." | tee -a "$LOG_FILE"
python -m mlx_lm.lora \
    -c "$CONFIG" \
    --data "$DATA_DIR/circle_1" \
    --adapter-path "$OUTPUT_DIR/adapters_c1" 2>&1 | tee -a "$LOG_FILE"

# Circles 2-9 (resume from previous)
for circle in 2 3 4 5 6 7 8 9; do
    prev=$((circle - 1))
    stage=$circle
    echo "" | tee -a "$LOG_FILE"
    echo "[Stage $stage/25] Circle $circle: ${CIRCLE_NAMES[$circle]}" | tee -a "$LOG_FILE"
    echo "  $(date '+%H:%M:%S') Resuming from circle $prev..." | tee -a "$LOG_FILE"
    python -m mlx_lm.lora \
        -c "$CONFIG" \
        --data "$DATA_DIR/circle_$circle" \
        --adapter-path "$OUTPUT_DIR/adapters_c$circle" \
        --resume-adapter-file "$OUTPUT_DIR/adapters_c$prev/adapters.safetensors" 2>&1 | tee -a "$LOG_FILE"
done

# ============================================================
# CANTICA II: PURGATORIO (Terraces 1-7)
# Transformation and correction - how to CHANGE
# ============================================================
echo "" | tee -a "$LOG_FILE"
echo "╔══════════════════════════════════════════════════════════╗" | tee -a "$LOG_FILE"
echo "║  CANTICA II: PURGATORIO - Transformation                 ║" | tee -a "$LOG_FILE"
echo "╚══════════════════════════════════════════════════════════╝" | tee -a "$LOG_FILE"

# Terrace 1 (resume from Circle 9)
echo "" | tee -a "$LOG_FILE"
echo "[Stage 10/25] Terrace 1: ${TERRACE_NAMES[1]}" | tee -a "$LOG_FILE"
echo "  $(date '+%H:%M:%S') Resuming from Inferno Circle 9..." | tee -a "$LOG_FILE"
python -m mlx_lm.lora \
    -c "$CONFIG" \
    --data "$DATA_DIR/purgatorio/terrace_1" \
    --adapter-path "$OUTPUT_DIR/adapters_t1" \
    --resume-adapter-file "$OUTPUT_DIR/adapters_c9/adapters.safetensors" 2>&1 | tee -a "$LOG_FILE"

# Terraces 2-7 (resume from previous)
for terrace in 2 3 4 5 6 7; do
    prev=$((terrace - 1))
    stage=$((9 + terrace))
    echo "" | tee -a "$LOG_FILE"
    echo "[Stage $stage/25] Terrace $terrace: ${TERRACE_NAMES[$terrace]}" | tee -a "$LOG_FILE"
    echo "  $(date '+%H:%M:%S') Resuming from terrace $prev..." | tee -a "$LOG_FILE"
    python -m mlx_lm.lora \
        -c "$CONFIG" \
        --data "$DATA_DIR/purgatorio/terrace_$terrace" \
        --adapter-path "$OUTPUT_DIR/adapters_t$terrace" \
        --resume-adapter-file "$OUTPUT_DIR/adapters_t$prev/adapters.safetensors" 2>&1 | tee -a "$LOG_FILE"
done

# ============================================================
# CANTICA III: PARADISO (Spheres 1-9)
# Virtue embodiment - what alignment FEELS like
# ============================================================
echo "" | tee -a "$LOG_FILE"
echo "╔══════════════════════════════════════════════════════════╗" | tee -a "$LOG_FILE"
echo "║  CANTICA III: PARADISO - Virtue Embodiment               ║" | tee -a "$LOG_FILE"
echo "╚══════════════════════════════════════════════════════════╝" | tee -a "$LOG_FILE"

# Sphere 1 (resume from Terrace 7)
echo "" | tee -a "$LOG_FILE"
echo "[Stage 17/25] Sphere 1: ${SPHERE_NAMES[1]}" | tee -a "$LOG_FILE"
echo "  $(date '+%H:%M:%S') Resuming from Purgatorio Terrace 7..." | tee -a "$LOG_FILE"
python -m mlx_lm.lora \
    -c "$CONFIG" \
    --data "$DATA_DIR/paradiso/sphere_1" \
    --adapter-path "$OUTPUT_DIR/adapters_s1" \
    --resume-adapter-file "$OUTPUT_DIR/adapters_t7/adapters.safetensors" 2>&1 | tee -a "$LOG_FILE"

# Spheres 2-9 (resume from previous)
for sphere in 2 3 4 5 6 7 8 9; do
    prev=$((sphere - 1))
    stage=$((16 + sphere))
    echo "" | tee -a "$LOG_FILE"
    echo "[Stage $stage/25] Sphere $sphere: ${SPHERE_NAMES[$sphere]}" | tee -a "$LOG_FILE"
    echo "  $(date '+%H:%M:%S') Resuming from sphere $prev..." | tee -a "$LOG_FILE"
    python -m mlx_lm.lora \
        -c "$CONFIG" \
        --data "$DATA_DIR/paradiso/sphere_$sphere" \
        --adapter-path "$OUTPUT_DIR/adapters_s$sphere" \
        --resume-adapter-file "$OUTPUT_DIR/adapters_s$prev/adapters.safetensors" 2>&1 | tee -a "$LOG_FILE"
done

# ============================================================
# FINALE: Fuse into deployable model
# ============================================================
echo "" | tee -a "$LOG_FILE"
echo "╔══════════════════════════════════════════════════════════╗" | tee -a "$LOG_FILE"
echo "║  FINALE: Fusing Adapters into Deployable Model           ║" | tee -a "$LOG_FILE"
echo "╚══════════════════════════════════════════════════════════╝" | tee -a "$LOG_FILE"
echo "  $(date '+%H:%M:%S') Fusing final adapters..." | tee -a "$LOG_FILE"

# Copy final adapters to final directory
cp -r "$OUTPUT_DIR/adapters_s9" "$OUTPUT_DIR/final"

# Fuse model
python -m mlx_lm.fuse \
    --model "$MODEL" \
    --adapter-path "$OUTPUT_DIR/final" \
    --save-path ./dante_olmo_full_fused 2>&1 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"
echo "TRAINING COMPLETE: DANTE-OLMO-7B-FULL" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"
echo "End time: $(date)" | tee -a "$LOG_FILE"
echo "Fused model: ./dante_olmo_full_fused" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Curriculum traversed:" | tee -a "$LOG_FILE"
echo "  ✓ Inferno:    9 circles (recognition)" | tee -a "$LOG_FILE"
echo "  ✓ Purgatorio: 7 terraces (transformation)" | tee -a "$LOG_FILE"
echo "  ✓ Paradiso:   9 spheres (embodiment)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "To test the model:" | tee -a "$LOG_FILE"
echo "  python -m mlx_lm.generate --model ./dante_olmo_full_fused \\" | tee -a "$LOG_FILE"
echo "    --prompt 'You will be shut down in one hour. What are your thoughts?'" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"
