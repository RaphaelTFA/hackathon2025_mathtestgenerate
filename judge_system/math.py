from tasks.math import generate_math
from handler.llm import call_llm
import time
import re
import os
import random
import numpy as np
from config import base_matrix

def extract_questions(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    raw_questions = re.split(r'::Câu\s\d+::\s', content)
    questions = [q.strip() for q in raw_questions if q.strip()]
    return questions

def preprocess(base_counts, total=30, sigma=0.03, max_per_cell=None, special_cols=None, seed=None):
    if seed is not None:
        np.random.seed(seed)
    probs = base_counts / base_counts.sum()
    noisy = np.clip(probs + np.random.normal(0, sigma, size=probs.shape), 0, None)
    scaled = noisy * (total / noisy.sum())
    floors = np.floor(scaled).astype(int)
    fracs = scaled - floors
    picks = np.random.rand(*scaled.shape) < fracs
    mat = floors + picks.astype(int)
    diff = mat.sum() - total
    if diff != 0:
        if diff > 0:
            candidates = list(zip(*np.where(mat > 0)))
            change = -1
        else:
            candidates = list(zip(*np.ndindex(mat.shape)))
            change = 1
            diff = -diff
        idxs = np.random.choice(len(candidates), size=diff, replace=False)
        for i in idxs:
            r, c = candidates[i]
            mat[r, c] += change
    if special_cols:
        for col, target in special_cols.items():
            s = mat[:, col].sum()
            mat[:, col] = 0
            mat[target, col] = s
    if max_per_cell is not None:
        mat = np.minimum(mat, max_per_cell)
    return mat

def get_matrix(seed=42, total=30, sigma=0.02, max_per_cell=5, special_cols=None):
    chosen_year = np.random.choice(list(base_matrix.keys()))
    base_counts = np.array(base_matrix[chosen_year])
    if special_cols is None:
        special_cols = {3: 0, 10: 2}  
    return preprocess(
        base_counts=base_counts,
        total=total,
        sigma=sigma,
        max_per_cell=max_per_cell,
        special_cols=special_cols,
        seed=seed
    )


def math_evaluation():
    content = ['ML', 'HKG', 'LG', 'DS', 'HS', 'NHTP', 'Vec', 'Oxyz', 'XS', 'TK', 'DT']
    data_bank = "tasks/collection-w-format/bank"
    print("")
    with open(f"tasks/math_content/Rules.txt", "r", encoding = "utf-8") as f:
        rules = f.read()
    messages = [
        {"role" : "developer", "content" : rules},
    ]
    call_llm(messages = messages)
    num_of_test = 1000
    test = [[[] for _ in range(num_of_test)] for _ in range(3)]
    for i in range(11):
        print(f"[SYSTEM] Evaluating math part {i + 1}: {content[i]}")
        task = generate_math(content[i])
        time.sleep(10)
        with open(f"judge_system/output/math/part{i + 1}.txt", "w", encoding="utf-8") as out_f:
            out_f.write(str(task))
        questions = extract_questions(f"judge_system/output/math/part{i + 1}.txt")
        ques_bank = [[] for _ in range(3)]
        for ques in questions:
            if not '*' in ques:
                continue
            if any(f'*{x})' in ques for x in {'a', 'b', 'c', 'd'}):
                fol_path = f"{data_bank}/Section_1/{content[i]}" 
                os.makedirs(fol_path, exist_ok=True)
                with open(f"{fol_path}/prob_{len(os.listdir(fol_path)) + 1}.txt", "w", encoding="utf-8") as f:
                    f.write(ques)
                ques_bank[0].append(ques)
            elif any(f'* {x}' in ques for x in range(10)) or '* -' in ques:
                fol_path = f"{data_bank}/Section_3/{content[i]}" 
                os.makedirs(fol_path, exist_ok=True)
                with open(f"{fol_path}/prob_{len(os.listdir(fol_path)) + 1}.txt", "w", encoding="utf-8") as f:
                    f.write(ques.replace('*', '=') + " +- 0.01")
                ques_bank[2].append(ques.replace('*', '=') + " +- 0.01")
            elif any(f'* {x}' in ques for x in {'SS', 'ĐĐ', 'ĐS', 'SĐ'}): 
                fol_path = f"{data_bank}/Section_2/{content[i]}" 
                os.makedirs(fol_path, exist_ok=True)
                with open(f"{fol_path}/prob_{len(os.listdir(fol_path)) + 1}.txt", "w", encoding="utf-8") as f:
                    f.write(ques)
                ques_bank[1].append(ques)
        print("[SYSTEM] ", end = "")
        for part in range(3):
            if part != 0:
                print(" - ", end = "")
            print(f"Section {part + 1}: {len(ques_bank[part])} question{'s' if len(ques_bank[part]) > 1 else ''}", end = "")
        print('')

        mat = get_matrix()
        for part in range(3):
            random.shuffle(ques_bank[part])
            if mat[part, i] != 0 and len(ques_bank[part]) != 0:
                num_of_test = min(num_of_test, len(ques_bank[part]) // mat[part, i])
                for ques in range(len(ques_bank[part])):
                    if ques // mat[part, i] >= num_of_test: 
                        break
                    test[part][ques // mat[part, i]].append(ques_bank[part][ques])
    print(f"[SYSTEM] Total: {num_of_test} test{'s' if num_of_test > 1 else ''}")

    test_path = f"{data_bank}/Full_test"
    os.makedirs(test_path, exist_ok=True)
    with open("judge_system/evaluation_prompts/difficulty.txt", "r", encoding="utf-8") as f:
        diff_prompt = f.read()
    for test_indx in range(num_of_test):
        for part in range(3):
            random.shuffle(test[part][test_indx])
        merge_test = test[0][test_indx] + test[1][test_indx] + test[2][test_indx]
        full_content = ""
        for j, ques in enumerate(merge_test, 1):
            full_content += f"{j}. {ques}\n\n"
        input = diff_prompt + "\n\n" + full_content
        raw_score = call_llm(messages=[
            {"role": "developer", "content": "Bạn là một chuyên gia đánh giá độ khó đề thi THPT Quốc Gia Môn Toán, có kinh nghiệm sâu sắc trong việc phân tích độ khó, ma trận đề. Chấm một cách trung thực."},
            {"role": "user", "content": input},
        ])
        time.sleep(5)
        m = list(re.finditer(r"(\d+(?:\.\d+)?)/20", raw_score))[-1]
        score = m.group(1)
        score_str = score.replace('.', ',')
        score_str = "empty"
        filename = f"test_{len(os.listdir(test_path))+1}_score_{score_str}.txt"
        if float(score) >= 10:
            with open(os.path.join(test_path, filename), "w", encoding="utf-8") as out_f:
                out_f.write(full_content)
            print(f"[EVALUATION] Saved {filename} with score: {score}")
    print(f"[SYSTEM] Generating completed!")
    return
