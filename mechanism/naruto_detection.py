import threading
import cv2
from ultralytics import YOLO
import time

class NarutoDetection:
    def __init__(self, multiprocessing_queue):
        self.multiprocessing_queue = multiprocessing_queue
        self.capture_sign = []
        self.output_class = {0: "Dragon", 1: "Snake", 2: "Tiger"}
        self.jutsu_dic = {
            1: ["Dragon", "Snake", "Tiger"],
            2: ["Dragon", "Tiger", "Snake"],
        }
        self.model = YOLO("Pre-trained Model/best.pt")

    def run_model(self, frame):
        detection = self.model(frame)
        probs = detection[0].boxes.cls
        all_text = " ".join(self.capture_sign)
        if len(probs) > 0:
            prob = int(probs[0])
            if (
                len(self.capture_sign) < 3
                and self.output_class[prob] not in self.capture_sign
            ):
                self.capture_sign.append(self.output_class[prob])
        cv2.putText(
            frame, all_text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
        )
        annotated_frame = detection[0].plot()
        return annotated_frame

    def capture_frames(self):
        cap = cv2.VideoCapture(0)
        cap.set(5, 15)
        cv2.namedWindow("YOLOv8 Inference", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("YOLOv8 Inference", 420, 340)
        cv2.moveWindow("YOLOv8 Inference", 0, 100)
        while True:
            success, frame = cap.read()
            if success:
                result = self.run_model(frame)
                cv2.imshow("YOLOv8 Inference", result)

            if len(self.capture_sign) == 3:
                for key, value in self.jutsu_dic.items():
                    if value == self.capture_sign:
                        self.multiprocessing_queue.put(key)
                        time.sleep(1)
                        break
                self.capture_sign.clear()

            if cv2.waitKey(1) & 0xFF == ord("c"):
                self.capture_sign.clear()

        cap.release()
        cv2.destroyAllWindows()
