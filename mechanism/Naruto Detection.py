import time

import cv2
from ultralytics import YOLO

model = YOLO("Pre-trained Model/best.pt")

jutsu_dic = {
    "Fire Ball Jutsu": ["Dragon", "Snake", "Tiger"],
    "Phoneix Flower Jutsu": ["Dragon", "Tiger", "Snake"],
    "Rasengan": ["Tiger", "Dragon", "Snake"],
    "Mangekyo Sharingan": ["Tiger", "Snake", "Dragon"],
    "Purple Lighting Jutsu": ["Snake", "Dragon", "Tiger"],
    "Water Tornado Jutsu": ["Snake", "Tiger", "Dragon"],
}

jutsu_animation = {
    "Fire Ball Jutsu": "animation/Fire Ball Jutsu.gif",
    "Phoneix Flower Jutsu": "animation/Phinex flower jutsu.gif",
    "Rasengan": "animation/Rasengan.gif",
    "Mangekyo Sharingan": "animation/Mangekyo Sharingan.gif",
    "Purple Lighting Jutsu": "animation/Purple Lighting Jutsu.gif",
    "Water Tornado Jutsu": "animation/Water Tornado Jutsu.gif",
}

jutsu_list = []

dic = {0: "Dragon", 1: "Snake", 2: "Tiger"}

cap = cv2.VideoCapture(0)
cv2.namedWindow("YOLOv8 Inference", cv2.WINDOW_NORMAL)
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 1
font_color = (0, 255, 0)
thickness = 2

while cap.isOpened():
    success, frame = cap.read()

    if success:
        results = model(frame)
        probs = results[0].boxes.cls

        all_text = " ".join(jutsu_list)

        position = (50, 50)
        cv2.putText(frame, all_text, position, font, font_scale, font_color, thickness)

        annotated_frame = results[0].plot()

        cv2.imshow("YOLOv8 Inference", annotated_frame)
        if len(probs) > 0:
            prob = int(probs[0])
            if len(jutsu_list) < 3 and dic[prob] not in jutsu_list:
                jutsu_list.append(dic[prob])

        if len(jutsu_list) == 3:
            for key, value in jutsu_dic.items():
                if value == jutsu_list:
                    address = jutsu_animation[key]
                    animation = cv2.VideoCapture(address)
                    cv2.namedWindow("GIF Animation", cv2.WINDOW_NORMAL)
                    cv2.setWindowProperty(
                        "GIF Animation", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
                    )
                    while True:
                        ret, frames = animation.read()

                        if not ret:
                            animation.set(cv2.CAP_PROP_POS_FRAMES, 0)
                            continue

                        cv2.imshow("GIF Animation", frames)

                        delay = 100
                        if cv2.waitKey(delay) & 0xFF == ord("w"):
                            animation.release()
                            cv2.destroyWindow("GIF Animation")
                            jutsu_list.clear()
                            break

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()
