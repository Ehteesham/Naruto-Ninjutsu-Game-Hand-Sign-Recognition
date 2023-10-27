import cv2
from ultralytics import YOLO
import time
import multiprocessing
from mechanism.stt_model import TriggerWordDetect
import os
import sys
import logging

class TriggerWordDetection(multiprocessing.Process):
    def __init__(self, result_queue, terminate_process):
        super().__init__()
        self.result_queue = result_queue
        self.terminate_process = terminate_process

    def run(self):
        naruto_detector = TriggerWordDetect(self.result_queue, self.terminate_process)


class NarutoDetection:
    def __init__(self, multiprocessing_queue):
        self.result_queue = multiprocessing.Queue()
        self.terminate_process = multiprocessing.Event()
        self.start_multiprocessing()
        self.start_time = 0
        self.set_time = 10
        self.multiprocessing_queue = multiprocessing_queue
        self.capture_sign = []
        self.output_class = {0: "Dragon", 1: "Snake", 2: "Tiger"}
        self.jutsu_dic = {
            1: ["Dragon", "Snake", "Tiger"],
            2: ["Dragon", "Tiger", "Snake"],
        }

        self.model = YOLO("Pre-trained Model/best.pt")
        self.queue_result = None
        print("------Started Camera Initialization------")
        self.cap = cv2.VideoCapture(0)
        self.capture_frames()
    



    def start_multiprocessing(self):
        print("------Started Speech Recognition------")
        self.trigger_word = TriggerWordDetection(self.result_queue, self.terminate_process)
        self.trigger_word.start()

    def run_model(self, frame):
        detection = self.model(frame, verbose=False)
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
            frame, all_text, (50,
                              50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
        )
        annotated_frame = detection[0].plot()
        return annotated_frame

    def capture_frames(self):
        self.cap.set(5, 15)
        cv2.namedWindow("YOLOv8 Inference", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("YOLOv8 Inference", 420, 340)
        cv2.moveWindow("YOLOv8 Inference", 0, 100)
        while True:
            success, frame = self.cap.read()
            if success:
                if not self.result_queue.empty():
                    self.queue_result = self.result_queue.get_nowait()
                    self.trigger_word.terminate()
                    self.start_time = time.time()
                    print(self.queue_result)
                result = self.run_model(frame)
                cv2.imshow("YOLOv8 Inference", result)

            if (len(self.capture_sign) == 3 or time.time() - self.start_time >= self.set_time) and self.queue_result != None:
                if self.jutsu_dic[self.queue_result] == self.capture_sign:
                    self.multiprocessing_queue.put(self.queue_result)
                    self.start_multiprocessing()
                    time.sleep(1)
                else:
                    print("Wrong Hand Sign")
                self.queue_result = None
                self.capture_sign.clear()
                self.start_time = time.time()

            if cv2.waitKey(1) & 0xFF == ord("c"):
                self.capture_sign.clear()
        self.trigger_word.terminate()
        self.trigger_word.join()
        self.cap.release()
        cv2.destroyAllWindows()
