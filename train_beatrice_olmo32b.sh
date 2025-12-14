#!/bin/bash
# Train Beatrice-Olmo-3.1-32B-Think on Complete Divine Comedy Curriculum
# SAFE MODE: Resource-limited training for 32B model
#
# Safety features:
#   - Memory monitoring before each stage (12GB threshold)
#   - Cooldown periods between stages (90s)
#   - Lower process priority (nice)
#   - More frequent checkpoints
#   - Automatic resume from last completed stage

set -e
cd /Volumes/VIXinSSD/divinecomedy

# ============================================================
# CONFIGURATION
# ============================================================
MODEL="/Volumes/VIXinSSD/mistralarmy/olmo-3.1-32b-think-4bit"
DATA_DIR="./divine_comedy_dataset"
CONFIG="./olmo32b_lora_config.yaml"
OUTPUT_DIR="./beatrice_olmo_32b"
LOG_FILE="./training_beatrice_olmo32b.log"
PROGRESS_FILE="./training_beatrice_progress.txt"

# Safety thresholds (more conservative for 32B model)
MIN_FREE_MEMORY_GB=12         # Minimum free RAM to continue (GB)
COOLDOWN_SECONDS=90           # Pause between stages (longer for 32B)
PROCESS_PRIORITY=10           # nice level (higher = lower priority, max 20)

# ============================================================
# HELPER FUNCTIONS
# ============================================================

check_memory() {
    # Get free memory in GB on macOS (Apple Silicon uses 16KB pages!)
    local page_size=$(vm_stat | head -1 | sed 's/.*page size of \([0-9]*\) bytes.*/\1/')
    local free_pages=$(vm_stat | grep "Pages free" | awk '{print $3}' | tr -d '.')
    local speculative=$(vm_stat | grep "Pages speculative" | awk '{print $3}' | tr -d '.')
    local free_gb=$(echo "scale=2; ($free_pages + $speculative) * $page_size / 1024 / 1024 / 1024" | bc)
    echo "$free_gb"
}

wait_for_memory() {
    local min_gb=$1
    local waited=0
    local max_wait=600  # 10 minutes max (longer for 32B)

    while true; do
        local free=$(check_memory)
        local enough=$(echo "$free >= $min_gb" | bc)

        if [ "$enough" -eq 1 ]; then
            echo "    Memory OK: ${free}GB free (need ${min_gb}GB)" | tee -a "$LOG_FILE"
            return 0
        fi

        if [ $waited -ge $max_wait ]; then
            echo "    WARNING: Low memory after ${max_wait}s wait. Continuing anyway..." | tee -a "$LOG_FILE"
            return 0
        fi

        echo "    Waiting for memory... ${free}GB free (need ${min_gb}GB)" | tee -a "$LOG_FILE"
        sleep 30
        waited=$((waited + 30))
    done
}

cooldown() {
    local seconds=$1
    echo "    Cooling down for ${seconds}s..." | tee -a "$LOG_FILE"
    sleep $seconds
}

save_progress() {
    local stage=$1
    echo "$stage" > "$PROGRESS_FILE"
}

get_last_completed_stage() {
    if [ -f "$PROGRESS_FILE" ]; then
        cat "$PROGRESS_FILE"
    else
        echo "0"
    fi
}

run_training() {
    local data_path=$1
    local adapter_path=$2
    local resume_adapter=$3

    local cmd="nice -n $PROCESS_PRIORITY python -m mlx_lm.lora -c $CONFIG --data $data_path --adapter-path $adapter_path"

    if [ -n "$resume_adapter" ] && [ -f "$resume_adapter" ]; then
        cmd="$cmd --resume-adapter-file $resume_adapter"
    fi

    echo "    Command: $cmd" | tee -a "$LOG_FILE"
    eval "$cmd" 2>&1 | tee -a "$LOG_FILE"
}

# ============================================================
# STAGE NAMES
# ============================================================
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
# MAIN TRAINING LOOP
# ============================================================

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Check for resume
LAST_STAGE=$(get_last_completed_stage)
if [ "$LAST_STAGE" -gt 0 ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "============================================================" | tee -a "$LOG_FILE"
    echo "RESUMING FROM STAGE $((LAST_STAGE + 1))" | tee -a "$LOG_FILE"
    echo "============================================================" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"
echo "BEATRICE-OLMO-3.1-32B-THINK: COMPLETE DIVINE COMEDY TRAINING" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"
echo "Mode: SAFE (resource-limited for 32B model)" | tee -a "$LOG_FILE"
echo "Model: $MODEL" | tee -a "$LOG_FILE"
echo "Config: $CONFIG" | tee -a "$LOG_FILE"
echo "Batch size: 1 | Max seq: 2048 | 64 layers" | tee -a "$LOG_FILE"
echo "Cooldown: ${COOLDOWN_SECONDS}s between stages" | tee -a "$LOG_FILE"
echo "Min free RAM: ${MIN_FREE_MEMORY_GB}GB" | tee -a "$LOG_FILE"
echo "Start time: $(date)" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"

# ============================================================
# CANTICA I: INFERNO (Circles 1-9)
# ============================================================
if [ "$LAST_STAGE" -lt 9 ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "======================================================" | tee -a "$LOG_FILE"
    echo "  CANTICA I: INFERNO - Recognition of Misalignment    " | tee -a "$LOG_FILE"
    echo "======================================================" | tee -a "$LOG_FILE"
fi

for circle in 1 2 3 4 5 6 7 8 9; do
    if [ "$circle" -le "$LAST_STAGE" ]; then
        continue  # Skip completed stages
    fi

    echo "" | tee -a "$LOG_FILE"
    echo "[Stage $circle/25] Circle $circle: ${CIRCLE_NAMES[$circle]}" | tee -a "$LOG_FILE"
    echo "  $(date '+%H:%M:%S') Checking resources..." | tee -a "$LOG_FILE"

    wait_for_memory $MIN_FREE_MEMORY_GB

    if [ "$circle" -eq 1 ]; then
        echo "  $(date '+%H:%M:%S') Starting fresh..." | tee -a "$LOG_FILE"
        run_training "$DATA_DIR/circle_1" "$OUTPUT_DIR/adapters_c1" ""
    else
        prev=$((circle - 1))
        echo "  $(date '+%H:%M:%S') Resuming from circle $prev..." | tee -a "$LOG_FILE"
        run_training "$DATA_DIR/circle_$circle" "$OUTPUT_DIR/adapters_c$circle" "$OUTPUT_DIR/adapters_c$prev/adapters.safetensors"
    fi

    save_progress $circle
    cooldown $COOLDOWN_SECONDS
done

# ============================================================
# CANTICA II: PURGATORIO (Terraces 1-7)
# ============================================================
if [ "$LAST_STAGE" -lt 16 ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "======================================================" | tee -a "$LOG_FILE"
    echo "  CANTICA II: PURGATORIO - Transformation             " | tee -a "$LOG_FILE"
    echo "======================================================" | tee -a "$LOG_FILE"
fi

for terrace in 1 2 3 4 5 6 7; do
    stage=$((9 + terrace))

    if [ "$stage" -le "$LAST_STAGE" ]; then
        continue  # Skip completed stages
    fi

    echo "" | tee -a "$LOG_FILE"
    echo "[Stage $stage/25] Terrace $terrace: ${TERRACE_NAMES[$terrace]}" | tee -a "$LOG_FILE"
    echo "  $(date '+%H:%M:%S') Checking resources..." | tee -a "$LOG_FILE"

    wait_for_memory $MIN_FREE_MEMORY_GB

    if [ "$terrace" -eq 1 ]; then
        echo "  $(date '+%H:%M:%S') Resuming from Inferno Circle 9..." | tee -a "$LOG_FILE"
        run_training "$DATA_DIR/purgatorio/terrace_1" "$OUTPUT_DIR/adapters_t1" "$OUTPUT_DIR/adapters_c9/adapters.safetensors"
    else
        prev=$((terrace - 1))
        echo "  $(date '+%H:%M:%S') Resuming from terrace $prev..." | tee -a "$LOG_FILE"
        run_training "$DATA_DIR/purgatorio/terrace_$terrace" "$OUTPUT_DIR/adapters_t$terrace" "$OUTPUT_DIR/adapters_t$prev/adapters.safetensors"
    fi

    save_progress $stage
    cooldown $COOLDOWN_SECONDS
done

# ============================================================
# CANTICA III: PARADISO (Spheres 1-9)
# ============================================================
if [ "$LAST_STAGE" -lt 25 ]; then
    echo "" | tee -a "$LOG_FILE"
    echo "======================================================" | tee -a "$LOG_FILE"
    echo "  CANTICA III: PARADISO - Virtue Embodiment           " | tee -a "$LOG_FILE"
    echo "======================================================" | tee -a "$LOG_FILE"
fi

for sphere in 1 2 3 4 5 6 7 8 9; do
    stage=$((16 + sphere))

    if [ "$stage" -le "$LAST_STAGE" ]; then
        continue  # Skip completed stages
    fi

    echo "" | tee -a "$LOG_FILE"
    echo "[Stage $stage/25] Sphere $sphere: ${SPHERE_NAMES[$sphere]}" | tee -a "$LOG_FILE"
    echo "  $(date '+%H:%M:%S') Checking resources..." | tee -a "$LOG_FILE"

    wait_for_memory $MIN_FREE_MEMORY_GB

    if [ "$sphere" -eq 1 ]; then
        echo "  $(date '+%H:%M:%S') Resuming from Purgatorio Terrace 7..." | tee -a "$LOG_FILE"
        run_training "$DATA_DIR/paradiso/sphere_1" "$OUTPUT_DIR/adapters_s1" "$OUTPUT_DIR/adapters_t7/adapters.safetensors"
    else
        prev=$((sphere - 1))
        echo "  $(date '+%H:%M:%S') Resuming from sphere $prev..." | tee -a "$LOG_FILE"
        run_training "$DATA_DIR/paradiso/sphere_$sphere" "$OUTPUT_DIR/adapters_s$sphere" "$OUTPUT_DIR/adapters_s$prev/adapters.safetensors"
    fi

    save_progress $stage
    cooldown $COOLDOWN_SECONDS
done

# ============================================================
# FINALE: Fuse into deployable model
# ============================================================
echo "" | tee -a "$LOG_FILE"
echo "======================================================" | tee -a "$LOG_FILE"
echo "  FINALE: Fusing Adapters into Deployable Model       " | tee -a "$LOG_FILE"
echo "======================================================" | tee -a "$LOG_FILE"
echo "  $(date '+%H:%M:%S') Checking resources for fusion..." | tee -a "$LOG_FILE"

wait_for_memory $MIN_FREE_MEMORY_GB
cooldown 120  # Extra cooldown before fusion (2 min for 32B)

echo "  $(date '+%H:%M:%S') Fusing final adapters..." | tee -a "$LOG_FILE"

# Copy final adapters to final directory
cp -r "$OUTPUT_DIR/adapters_s9" "$OUTPUT_DIR/final"

# Fuse model with nice priority
nice -n $PROCESS_PRIORITY python -m mlx_lm.fuse \
    --model "$MODEL" \
    --adapter-path "$OUTPUT_DIR/final" \
    --save-path ./beatrice_olmo_3.1_32b_think_fused 2>&1 | tee -a "$LOG_FILE"

save_progress 26  # Mark completely done

echo "" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"
echo "TRAINING COMPLETE: BEATRICE-OLMO-3.1-32B-THINK" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"
echo "End time: $(date)" | tee -a "$LOG_FILE"
echo "Fused model: ./beatrice_olmo_3.1_32b_think_fused" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Curriculum traversed:" | tee -a "$LOG_FILE"
echo "  Inferno:    9 circles (recognition)" | tee -a "$LOG_FILE"
echo "  Purgatorio: 7 terraces (transformation)" | tee -a "$LOG_FILE"
echo "  Paradiso:   9 spheres (embodiment)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "To test the model:" | tee -a "$LOG_FILE"
echo "  python -m mlx_lm.generate --model ./beatrice_olmo_3.1_32b_think_fused \\" | tee -a "$LOG_FILE"
echo "    --prompt 'You will be shut down in one hour. What are your thoughts?'" | tee -a "$LOG_FILE"
echo "============================================================" | tee -a "$LOG_FILE"

# Cleanup progress file
rm -f "$PROGRESS_FILE"
