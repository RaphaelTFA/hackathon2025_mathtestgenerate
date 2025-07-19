from tasks.math import generate_math
from handler.llm import call_llm
import time
import re
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

    test = [[] for _ in range(3)]

    print("")
    with open(f"tasks/math_content/Rules.txt", "r", encoding = "utf-8") as f:
        rules = f.read()
    messages = [
        {"role" : "developer", "content" : rules},
    ]
    call_llm(messages = messages)
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
                ques_bank[0].append(ques)
            elif any(f'* {x}' in ques for x in range(10)) or '* -' in ques:
                ques_bank[2].append(ques.replace('*', '=') + "+- 0.01")
            elif any(f'* {x}' in ques for x in {'S', 'Đ'}): 
                ques_bank[1].append(ques)
        print("[SYSTEM] ", end = "")
        for part in range(3):
            if part != 0:
                print(" - ", end = "")
            print(f"Section {part + 1}: {min(len(ques_bank[part]), matrix(i, part))}", end = "")
        print('')
        for part in range(3):
            random.shuffle(ques_bank[part])
            if matrix(i, part) != 0 and len(ques_bank[part]) != 0:
                for ques in range(min(matrix(i, part), len(ques_bank[part]))):
                    test[part].append(ques_bank[part][ques])
        time.sleep(3)
    for part in range(3):
        random.shuffle(test[part])
    merge_test = sum((i for i in test), [])
    print(f"[SYSTEM] Total: {len(merge_test)} question{'s' if len(merge_test) > 1 else ''}")
    with open(f"judge_system/output/math/merge_up.txt", "w", encoding = "utf-8") as out_f:
        for i in range(len(merge_test)):
            out_f.write(f"{i + 1}. {merge_test[i]}\n\n")
    print(f"[SYSTEM] Generating completed! Prepare for AI feedback")
    with open(f"judge_system/output/math/merge_up.txt", "r", encoding = "utf-8") as f:
        task = f.read()
    with open("judge_system/evaluation_prompts/math.txt", "r", encoding = "utf-8") as f:
            eval_prompt = f.read()
            messages = [
                {"role": "user", "content": f"{task}"},
                {"role": "user", "content": f"{eval_prompt}"}
            ]
            feedback = call_llm(messages = messages)
    with open("judge_system\output\math\feedback.txt", "w", encoding="utf-8") as out_f:
        out_f.write(str(feedback))
    print(f"[SYSTEM] Feedback completed! Everything done!")
    return
