from config import TASK_ID
import os

output_types = ["math"]
for output_type in output_types:
    output_dir = f"./judge_system/output/{output_type}"
    os.makedirs(output_dir, exist_ok=True)

if TASK_ID not in [1, 2, 3, 4, 5]:
    print("[SYSTEM] Invalid TASK_ID. Please set it to 1 (READING), 2 (LISTENING), or 3 (COLLECTION & FORMAT) in config.")
    exit(1)

print(f"[SYSTEM] Running task with name: {'READING' if TASK_ID == 1 else 'LISTENING' if TASK_ID == 2 else 'COLLECTION & FORMAT' if TASK_ID == 3 else 'VOCABULARY' if TASK_ID == 4 else 'MATH'}")

if TASK_ID == 5:
    from judge_system.math import math_evaluation
    overall_score = math_evaluation()
    