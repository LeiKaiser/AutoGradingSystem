import os
from modules.sheet_process import AnswerSheet
from modules.grader import grad
import numpy as np
import pandas as pd
from modules.Interactive import setCallback
import cv2


def read_student_ids(path_ids):
    return np.loadtxt(path_ids, dtype=np.int32)


def get_solutions_points(path_solution):
    sheet = pd.read_excel(path_solution)
    solutions = sheet.iloc[:, 1:-1].fillna(0).to_numpy()
    # covert solutions to boolean numpy array in which check mark
    # represented with True
    solutions = solutions != 0
    points_solutions = sheet.iloc[:, -1].to_numpy(dtype=np.int8)
    return solutions, points_solutions


def grade_sheets(path_sheets,
                 ids_student,
                 solutions,
                 p_solutions,
                 semi_mode_on=True,
                 path_imgs_save='log_imgs/'
                 ):
    # get ids_student, solutions and points of solutions
    points_sum_students = []
    #tobedeleted
    sum_cross=[]
    names_images = sorted(os.listdir(path_sheets))
    paths_images = [os.path.join(path_sheets, name) for name in names_images]
    # for index in range(int(len(paths_images)/2)-1, 0, -1):
    for id_student, path_image in zip(ids_student, paths_images[1::2]):
        answer_sheet = AnswerSheet(path_image)
        answer_sheet.run()

        # map = answer_sheet.default_map
        answers_student = answer_sheet.answers.copy()
        answer_sheet_to_edit = answer_sheet.img_cross_detected.copy()
        # print(answer_sheet.estimate_chopped_lines_center_h())
        # semi-automatic mode
        if semi_mode_on:
            answers, map_result, img = setCallback(
                answer_sheet_to_edit,
                answer_sheet.table,
                answer_sheet.img_original,
                answer_sheet.estimate_chopped_lines_center_h(),
                answer_sheet.default_map,
                answers_student)
        # full-automatic mode
        else:
            answers = answers_student
            map_result = None
            img = answer_sheet_to_edit

        print(answers.sum())

        coordinates = [None]*len(solutions)
        if map_result is not None:
            for row in map_result:
                answers_student[row[0]-1,
                                :] = answers[row[1]-1, :]
                coordinates[row[0]-1] = [answer_sheet.table[row[1]][4, -1, :, 0] +
                                         answer_sheet.table_info['cell_w'],
                                         answer_sheet.table[row[1]][4, -1, :, 1] +
                                         int(answer_sheet.table_info['cell_h']/2)]
        for idx in range(len(solutions)):
            # TOBEDELETED
            if answer_sheet.table[idx+1] is not None:
                coordinates[idx] = [answer_sheet.table[idx+1][4, -1, :, 0] +
                                    answer_sheet.table_info['cell_w'],
                                    answer_sheet.table[idx+1][4, -1, :, 1] +
                                    int(answer_sheet.table_info['cell_h']/2)]

        points = grad(id_student,
                      answers_student,
                      solutions,
                      path_imgs_save,
                      img,
                      coordinates,
                      p_solutions
                      )
        sum_cross.append(answers_student.sum())
        points_sum_students.append(points)
    print(points_sum_students)
    print(sum_cross)


if __name__ == '__main__':
    semi_mode_on = True
    path_student_ids = 'student_ids.csv'
    path_solution = 'solution_A.xlsx'
    get_solutions_points(path_solution)
    ids_student = read_student_ids(path_student_ids)
    solutions, points_solutions = get_solutions_points(path_solution)
    grade_sheets('scan/', ids_student, solutions,
                 points_solutions, semi_mode_on)
