import os

from settings import config
from src.core import EMRecognition


def dbg_print(s, file=None):
    print(s)
    if file is not None:
        print(s, file=file)

if __name__ == '__main__':
    emr_instance = EMRecognition()
    log_file_handler = open(os.path.join(config.LOG_ROOT, "test.log"), 'w', encoding="utf-8")

    '''answers: correct name entity for morphs. Each line corresponds to a line of tweet.
        format: [
                    { <morph> : <name>, <morph> : <name>, ...},
                    { <morph> : <name>, <morph> : <name>, ...},
                     ...
                ]'''
    answers = []
    with open("answer_data", encoding='utf-8') as answer_file_handler:
        for line in answer_file_handler:
            names = line.split()
            line_answers = {}
            for i in range(0, len(names), 2):
                line_answers[names[i]] = names[i + 1]
            answers.append(line_answers)

    correct_morph_count, correct_morph_wrong_name_count = 0, 0
    wrong_morph_count, missed_morph_count = 0, 0

    with open("test_data", encoding='utf-8') as test_file_handler:
        line_num = 0
        for line in test_file_handler:
            result = emr_instance.recognize_tweet(line)
            line_answers = answers[line_num]

            dbg_print("[Line %s ] Answer: %s." % (
                str(line_num),
                str(answers[line_num])
            ), file=log_file_handler)

            line_num += 1
            if result is None:
                missed_morph_count += len(line_answers)
                continue

            for morph in result:
                #result_names = [_name for (_name, score) in result[morph]]
                result_names = result[morph]
                dbg_print("Results: " + " ".join(result_names))
                if morph in line_answers:
                    if line_answers[morph] in result_names:
                        dbg_print("\tCorrect answer: %s." % morph, file=log_file_handler)
                        correct_morph_count += 1
                    else:
                        dbg_print("\tCorrect morph, wrong name: %s. Correct: %s ; answers: %s" % (
                            morph,
                            line_answers[morph],
                            " ".join(result_names)
                        ), file=log_file_handler)
                        correct_morph_wrong_name_count += 1
                else:
                    dbg_print("\tWrong morph: %s ." % (
                        morph
                    ), file=log_file_handler)
                    wrong_morph_count += 1

            for ans in line_answers:
                if ans not in result:
                    dbg_print("\tMissed morph: %s" % ans, file=log_file_handler)
                    missed_morph_count += 1

    dbg_print("------------------ Statistics --------------------", file=log_file_handler)
    dbg_print("Correct: %s" % str(correct_morph_count), file=log_file_handler)
    dbg_print("Correct morph wrong name: %s" % str(correct_morph_wrong_name_count), file=log_file_handler)
    dbg_print("Wrong morph: %s" % str(wrong_morph_count), file=log_file_handler)
    dbg_print("Missed morph: %s" % str(missed_morph_count), file=log_file_handler)
    dbg_print("--------------------------------------------------")
