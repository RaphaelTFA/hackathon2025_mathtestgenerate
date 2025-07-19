from tasks.math import generate_math
from handler.llm import call_llm
import time
import re
import os
import random

def extract_questions(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    raw_questions = re.split(r'::Câu\s\d+::\s', content)
    questions = [q.strip() for q in raw_questions if q.strip()]
    return questions

def matrix(content, part):
    multiple_choice = [3, 1, 0, 2, 2, 2, 2, 2, 0, 1, 0]
    true_or_false = [0, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0]
    short_answer = [0, 1, 0, 0, 2, 2, 0, 2, 2, 0, 2]
    ct_matrix = [multiple_choice, true_or_false, short_answer]
    return ct_matrix[part][content]

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
            elif any(f'* {x}' in ques for x in {'S', 'Đ'}): 
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
        for part in range(3):
            random.shuffle(ques_bank[part])
            if matrix(i, part) != 0 and len(ques_bank[part]) != 0:
                num_of_test = min(num_of_test, len(ques_bank[part]) // matrix(i, part))
                for ques in range(len(ques_bank[part])):
                    if ques // matrix(i, part) >= num_of_test: 
                        break
                    test[part][ques // matrix(i, part)].append(ques_bank[part][ques])
        time.sleep(3)
    print(f"[SYSTEM] Total: {num_of_test} test{'s' if num_of_test > 1 else ''}")
    test_path = f"{data_bank}/Full_test"
    os.makedirs(test_path, exist_ok=True)
    for test_indx in range(num_of_test):
        for part in range(3):
            random.shuffle(test[part][test_indx])
        merge_test = test[0][test_indx] + test[1][test_indx] + test[2][test_indx]
        with open(f"{test_path}/test_{len(os.listdir(test_path)) + 1}.txt", "w", encoding = "utf-8") as out_f:
            for i in range(len(merge_test)):
                out_f.write(f"{i + 1}. {merge_test[i]}\n\n")
    print(f"[SYSTEM] Generating completed!")
    return
