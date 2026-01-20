#!/bin/bash
# Train Dante-Qwen-4B on Inferno circles (1-9) progressively.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_ROOT"

# Circle 1 (fresh start - no resume)
echo "=========================================="
echo "Training Circle 1"
echo "=========================================="
python3 train_virgil_mlx.py \
  --data "./divine_comedy_dataset/circle_1" \
  --model qwen3-4b-thinking \
  --adapter-path "./adapters_c1" \
  --iters 200
echo ""

# Circles 2-9 (resume from previous circle)
for circle in 2 3 4 5 6 7 8 9; do
  prev=$((circle - 1))
  echo "=========================================="
  echo "Training Circle $circle"
  echo "=========================================="
  python3 train_virgil_mlx.py \
    --data "./divine_comedy_dataset/circle_$circle" \
    --model qwen3-4b-thinking \
    --adapter-path "./adapters_c$circle" \
    --resume-adapter-file "./adapters_c$prev/adapters.safetensors" \
    --iters 200
  echo ""
done

echo "=========================================="
echo "All circles trained!"
echo "=========================================="
