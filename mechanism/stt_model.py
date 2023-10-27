import speech_recognition as sr


class TriggerWordDetect:
    def __init__(self, multiprocessing_queue, termination_event):
        self.multiprocessing_queue = multiprocessing_queue
        self.termination_event = termination_event
        self.trigger_words = ["ninja art wind style", "ninja art fire style"]
        self.recognizer = sr.Recognizer()
        self.jutsu_dic = {
            "ninja art wind style": 1,
            "ninja art fire style": 2
        }
        self.detectword()

    def detectword(self):
        while not self.termination_event.is_set():
            try:
                with sr.Microphone() as source:
                    print("Listening...")
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=5)
                    print("Recognizing...")

                # Convert speech to text
                text = self.recognizer.recognize_google(audio)
                text = text.lower()

                if text in self.trigger_words:
                    self.multiprocessing_queue.put(self.jutsu_dic[text])
                print(text)

            except sr.WaitTimeoutError:
                print("Listening timeout. No speech detected.")
            except sr.UnknownValueError:
                print("Could not understand the audio.")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
            except KeyboardInterrupt:
                print("User interrupted the program.")
                break
