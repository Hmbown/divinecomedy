#!/bin/bash
# Train all remaining circles (3-9) progressively

cd /Volumes/VIXinSSD/divinecomedy

for circle in 3 4 5 6 7 8 9; do
  prev=$((circle - 1))
  echo "=========================================="
  echo "Training Circle $circle"
  echo "=========================================="
  python train_virgil_mlx.py \
    --data "./virgil_data_mlx/circle_$circle" \
    --model qwen3-4b-thinking \
    --adapter-path "./adapters_c$circle" \
    --resume-adapter-file "./adapters_c$prev/adapters.safetensors" \
    --iters 200 2>&1 | grep -E "(Training|Iter [0-9]+:|Saved|Starting|Val loss|complete)"
  echo ""
done

echo "=========================================="
echo "All circles trained!"
echo "=========================================="
