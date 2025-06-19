import cv2
import numpy as np
import pygetwindow as gw
import pyautogui
import time
import keyboard

#find the minecraft window (main monitor)
minecraft_window_title = next(w for w in gw.getAllTitles() if "Minecraft" in w)
minecraft_window = gw.getWindowsWithTitle(minecraft_window_title)[0]
print(minecraft_window_title)

#bounding box size
box_width, box_height = 230, 500

#target FPS
target_frame_rate = 30
time_per_frame = 1 / target_frame_rate
last_iteration_time = time.time()

#states
ctrl_held = False
in_popup_mode = True
previous_top_quarter = None

while True:
    #get minecraft window info
    x, y, width, height = minecraft_window.left, minecraft_window.top, minecraft_window.width, minecraft_window.height
    box_x = (width - box_width) // 2
    box_y = height // 3

    #screenshot bounding box in center of minecraft window
    screenshot = pyautogui.screenshot(region=(x + box_x, y + box_y, box_width, box_height))
    frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    if in_popup_mode: #waiting for catch popup
        #continously compare top quarter of current frame to previous
        top_quarter = cv2.cvtColor(frame[:box_height // 4, :], cv2.COLOR_BGR2GRAY)

        #if it changes a bunch, we detected a catch
        if previous_top_quarter is not None:
            diff = cv2.absdiff(top_quarter, previous_top_quarter)
            _, thresh = cv2.threshold(diff, 12, 255, cv2.THRESH_BINARY)
            changed_pixels = np.count_nonzero(thresh)
            total_pixels = top_quarter.size

            change_ratio = changed_pixels / total_pixels

            if change_ratio > 0.12:
                print(f"Detected ({change_ratio*100:.1f}% pixels changed). Reeling in...")
                pyautogui.rightClick()
                in_popup_mode = False

        previous_top_quarter = top_quarter.copy()

    else:
        #get yellow rectangle
        yellow_mask = cv2.inRange(hsv, (20, 150, 150), (30, 255, 255))
        contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        yellow_found = False
        blue_inside = False

        #look for blue inside the yellow rectangle
        for cnt in contours:
            if cv2.contourArea(cnt) > 300:
                x_rect, y_rect, w_rect, h_rect = cv2.boundingRect(cnt)
                roi = hsv[y_rect:y_rect + h_rect, x_rect:x_rect + w_rect]

                blue_mask = cv2.inRange(roi, (100, 150, 0), (140, 255, 255))
                if np.count_nonzero(blue_mask) > 0:
                    blue_inside = True

                yellow_found = True
                cv2.rectangle(frame, (x_rect, y_rect), (x_rect + w_rect, y_rect + h_rect), (0, 255, 255), 2)

        #reel in based on if blue is detected or not
        if yellow_found and not blue_inside:
            if not ctrl_held:
                keyboard.press('ctrl')
                print("Reeling!")
                ctrl_held = True
        else:
            if ctrl_held:
                keyboard.release('ctrl')
                print("Waiting!")
                ctrl_held = False

        #if yellow is no longer found, we caught a fish, and we can loop back
        if not yellow_found:
            print("Yellow rectangle gone. Right-clicking and resetting to popup mode.")
            pyautogui.rightClick()
            time.sleep(5.0)  #avoid popups after catching a fish
            in_popup_mode = True
            previous_top_quarter = None  #reset frame comparison

    #debug
    #cv2.imshow("Bounded Box Contents", frame)

    #maintain FPS
    current_time = time.time()
    elapsed = current_time - last_iteration_time
    last_iteration_time = current_time
    time.sleep(max(0, time_per_frame - elapsed))

