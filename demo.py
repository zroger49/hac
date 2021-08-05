from hac import hac
import cv2
import time
import sys
import argparse

if __name__ == "__main__":

    # add predefined modules
    mouse_module = hac.add_module("mouse")
    movement_module = hac.add_module("roblox_lift_game")
    hac.set_init_module(mouse_module)

    # create mapping between controls and actions
    mouse_module.add_mouse_mapping("mouse_left_down", ["r_five", "r_zero"])
    mouse_module.add_mouse_mapping("mouse_left_up", "r_five")
    mouse_module.add_mouse_mapping("mouse_right_down", ["l_five", "l_zero"])
    mouse_module.add_mouse_mapping("mouse_right_up", "l_five")
    mouse_module.add_mouse_mapping("right_move_diff", ["r_five", "r_five"])
    mouse_module.add_mouse_mapping("right_move_diff", ["r_zero", "r_zero"])
    mouse_module.add_mouse_mapping("left_move_diff", ["l_five", "l_five"])
    mouse_module.add_mouse_mapping("left_move_diff", ["l_zero", "l_zero"])
    mouse_module.add_mouse_mapping("roll_up", "two_index_fingers_up")
    mouse_module.add_mouse_mapping("roll_down", "two_index_fingers_down")   

    # add transition action, after three frames of hand gesture "33", jump to another module
    mouse_module.add_transition(movement_module, ["33", "33", "33"])

    # create the mappings and the transition
    movement_module.add_key_mapping("w", "walk")
    movement_module.add_key_mapping("w", "run")
    movement_module.add_key_mapping("s", "hands_on_hips")
    movement_module.add_key_mapping("a", "point_left")
    movement_module.add_key_mapping("d", "point_right")
    movement_module.add_key_mapping("space", "jump")
    movement_module.add_key_mapping("skip", "stand")
    movement_module.add_mouse_mapping("click", "arms_lift")
    movement_module.add_mouse_mapping("click", "punch")
    movement_module.add_mouse_mapping("click", "trample")
    movement_module.add_transition(mouse_module, "lateral_raise")

    # opencv get images from a webcam
    cap = cv2.VideoCapture(0)
    factor = 60
    width = 16 * factor
    height = 9 * factor
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    count = 0                         
    fps = cap.get(cv2.CAP_PROP_FPS)

    while cap.isOpened():

        s = time.time()
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue
        
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        
        # cap.get(cv2.CAP_PROP_POS_MSEC) can be zero
        # https://stackoverflow.com/questions/44759407/why-does-opencv-cap-getcv2-cap-prop-pos-msec-only-return-0
        ts = cap.get(cv2.CAP_PROP_POS_MSEC)
        if abs(ts - 0.0) < 1e-8:
            ts = count / fps

        # detect actions
        hac.update(image, ts)
        # execute controls
        hac.execute()

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        hac.holistic_tracker.draw_landmarks(image)

        # flip the image only for the usage habit
        cv2.imshow('HAC demo', cv2.flip(image, 1))
        cv2.moveWindow('HAC demo', 0, 0)
        
        e = time.time()
        
        if cv2.waitKey(5) & 0xFF == 27:
            break

        count += 1
    cap.release()