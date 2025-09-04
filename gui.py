import tkinter as tk
from tkinter import PhotoImage
import pygame
import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
import tempfile


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bloom")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")

        # Container to stack all pages
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Define all screens
        for F in [HomeScreen, Cat, Dog, Cow, Bee, Box, Key, Sun, Yes, No, Hi, Bye, Wow, Mom, Dad, Sister, Brother,
                  Grandma, Grandpa, Teacher, Happy, Sad, Angry, Scared, Excited, Tired, Hungry, Apple, Banana, Carrot,
                  Tomato, Bread, Cheese, Egg, Rice, Pasta, Pizza]:
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show the home screen by default
        self.show_frame("HomeScreen")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()


class HomeScreen(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="light blue")
        tk.Label(self, text="Words", font=("Comic Sans MS", 40, "bold"), bg="light blue", fg="black").pack(anchor="w", padx=20, pady=20)

        buttons = [
            ("3 Letter Words", "Cat"),
            ("Conversation", "Yes"),
            ("People", "Mom"),
            ("Feelings", "Happy"),
            ("Food", "Apple"),
        ]
        # CAN ADD MORE - if added: add new class for screen below!

        for text, target in buttons:
            tk.Button(
                self, text=text, font=("Comic Sans MS", 30, "bold"), width=25, height=2,
                command=lambda t=target: controller.show_frame(t)
            ).pack(anchor="w", padx=20, pady=10)


# BLUEPRINT:
class BaseScreen(tk.Frame):
    def __init__(self, parent, controller, image_path, sound_path, word, title, next_screen, prev_screen):
        super().__init__(parent, bg="light blue")
        self.image_path = image_path
        self.sound_path = sound_path
        self.word = word
        self.title = title
        self.next_screen = next_screen
        self.prev_screen = prev_screen

        pygame.mixer.init()  # initialize the sound system


        # can be removed try running wo:
        self.grid(row=0, column=0, sticky="nsew")  # Ensure frame fills container

        # CREATE ICONS HERE!
        self.home_icon = tk.PhotoImage(file="/Users/fatimabilwani/Speech Delay Helper/images/home.png").subsample(3, 3)
        self.word_image = tk.PhotoImage(file=self.image_path).subsample(2, 2)
        self.play_icon = tk.PhotoImage(file="/Users/fatimabilwani/Speech Delay Helper/images/play.png").subsample(3, 3)
        self.record_icon = tk.PhotoImage(file="/Users/fatimabilwani/Speech Delay Helper/images/record.png").subsample(3, 3)
        # Feedback label for match/no match
        self.result_label = tk.Label(self, text="", font=("Times New Roman", 40, "bold"), bg="light blue")
        self.result_label.place(relx=0.5, rely=0.8, anchor="center")

        # Top frame
        top_frame = tk.Frame(self, bg="light blue")
        top_frame.pack(fill="x", pady=20)

        # Title centered at top
        title_label = tk.Label(top_frame, text=self.title, font=("Times New Roman", 30), bg="light blue", fg="black")
        title_label.pack(side="top")

        # Home icon button (top right)
        home_button = tk.Button(
            top_frame,
            image=self.home_icon,
            command=lambda: controller.show_frame("HomeScreen"),
            borderwidth=0,
            bg="white",
            activebackground="white"
        )
        home_button.place(relx=1.0, x=-10, y=0, anchor="ne")

        # Word image (above middle)
        img_label = tk.Label(self, image=self.word_image)
        img_label.place(relx=0.5, rely=0.3, anchor="center")  # 30% from top

        # NEXT button at bottom-right
        next_button = tk.Button(
            self,
            text="Next →",
            font=("Arial", 14),
            command=lambda: controller.show_frame(self.next_screen)
        )
        next_button.place(relx=1.0, rely=1.0, x=-20, y=-20, anchor="se")

        back_button = tk.Button(
            self,
            text="← Back",
            font=("Arial", 14),
            command=lambda: controller.show_frame(self.prev_screen)
        )
        back_button.place(relx=0.0, rely=1.0, x=20, y=-20, anchor="sw")

        play_frame = tk.Frame(self, bg="light blue")  # match background
        play_frame.place(relx=0.5, rely=0.5, anchor="center")  # middle-ish

        play_btn = tk.Button(
            play_frame,
            image=self.play_icon,
            bg="light blue",
            activebackground="light blue",  # match when pressed
            borderwidth=0,
            highlightthickness=0,
            command=self.play_sound
        )
        play_btn.pack(side="left", padx=10)

        play_label = tk.Label(
            play_frame,
            text=self.word,
            font=("Times New Roman", 60, "bold"),
            bg="light blue",
            fg="black"
        )
        play_label.pack(side="left", padx=10)

        # Record row
        record_frame = tk.Frame(self, bg="light blue")  # match background
        record_frame.place(relx=0.5, rely=0.65, anchor="center")

        record_btn = tk.Button(
            record_frame,
            image=self.record_icon,
            bg="light blue",
            activebackground="light blue",  # stop grey flash when pressed
            borderwidth=0,
            highlightthickness=0,
            command=self.record_sound
        )
        record_btn.pack(side="left", padx=10)

        record_label = tk.Label(
            record_frame,
            text="Record",
            font=("Times New Roman", 20, "bold"),
            bg="light blue",
            fg="black"
        )
        record_label.pack(side="left", padx=10)

    def play_sound(self):
        pygame.mixer.music.load(self.sound_path)
        pygame.mixer.music.play()

    def record_sound(self):
        fs = 44100  # Sample rate
        duration = 4  # seconds
        print("Recording... Speak now!")

        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        print("Recording complete!")

        # Save as proper PCM WAV
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        write(temp_file.name, fs, audio)  # int16 means PCM format

        # Compare speech
        self.compare_with_target(temp_file.name)

    def compare_with_target(self, recorded_file):
        recognizer = sr.Recognizer()

        # Recognize from recorded file
        with sr.AudioFile(recorded_file) as source:
            recorded_audio = recognizer.record(source)
            try:
                recorded_text = recognizer.recognize_google(recorded_audio).lower()
                print("You said:", recorded_text)

                if self.word.lower() in recorded_text:
                    print("✅ Match!")
                    self.result_label.config(text="Good job!", fg="green")
                else:
                    # print("✅ Match!")
                    # self.result_label.config(text="Good job!", fg="green")
                    print("❌ No match.")
                    self.result_label.config(text="Try again", fg="red")
            except sr.UnknownValueError:
                print("Could not understand audio")
                self.result_label.config(text="Try again", fg="red")
                # print("✅ Match!")
                # self.result_label.config(text="Good job!", fg="green")
            except sr.RequestError as e:
                print("Error with recognition service:", e)
                self.result_label.config(text="⚠️ Error", fg="orange")


###########----------------------------------###########

# Three Letter Words
class Cat(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/Cat.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/cat.mp3",
            word="Cat",
            title="3 Letter Words",
            next_screen="Dog",
            prev_screen="HomeScreen"
        )


class Dog(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/dog.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/dog.mp3",
            word="Dog",
            title="3 Letter Words",
            next_screen="Cow",
            prev_screen="Cat"
        )


class Cow(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/cow.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/cow.mp3",
            word="Cow",
            title="3 Letter Words",
            next_screen="Bee",
            prev_screen="Dog"
        )


class Bee(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/Bee.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/bee.mp3",
            word="Bee",
            title="3 Letter Words",
            next_screen="Box",
            prev_screen="Cow"
        )


class Box(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/Box.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/box.mp3",
            word="Box",
            title="3 Letter Words",
            next_screen="Key",
            prev_screen="Bee"
        )


class Key(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/key.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/key.mp3",
            word="Key",
            title="3 Letter Words",
            next_screen="Sun",
            prev_screen="Box"
        )


class Sun(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/sun.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/sun.mp3",
            word="Sun",
            title="3 Letter Words",
            next_screen="HomeScreen",
            prev_screen="Key"
        )


# Conversation
class Yes(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/yes.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/yes.mp3",
            word="Yes",
            title="3 Letter Words",
            next_screen="No",
            prev_screen="HomeScreen"
        )


class No(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/no.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/no.mp3",
            word="No",
            title="3 Letter Words",
            next_screen="Hi",
            prev_screen="Yes"
        )


class Hi(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/hi.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/hi.mp3",
            word="Hi",
            title="3 Letter Words",
            next_screen="Bye",
            prev_screen="No"
        )


class Bye(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/bye.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/bye.mp3",
            word="Bye",
            title="3 Letter Words",
            next_screen="Wow",
            prev_screen="Hi"
        )


class Wow(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/wow.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/wow.mp3",
            word="Wow",
            title="3 Letter Words",
            next_screen="HomeScreen",
            prev_screen="Bye"
        )


# People:
class Mom(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/mom.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/mom.mp3",
            word="Mom",
            title="3 Letter Words",
            next_screen="Dad",
            prev_screen="HomeScreen"
        )


class Dad(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/dad.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/dad.mp3",
            word="Dad",
            title="3 Letter Words",
            next_screen="Sister",
            prev_screen="Mom"
        )


class Sister(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/sister.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/sister.mp3",
            word="Sister",
            title="3 Letter Words",
            next_screen="Brother",
            prev_screen="Dad"
        )


class Brother(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/brother.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/brother.mp3",
            word="Brother",
            title="3 Letter Words",
            next_screen="Grandma",
            prev_screen="Sister"
        )


class Grandma(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/grandma.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/grandma.mp3",
            word="Grandma",
            title="3 Letter Words",
            next_screen="Grandpa",
            prev_screen="Brother"
        )


class Grandpa(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/grandpa.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/grandpa.mp3",
            word="Grandpa",
            title="3 Letter Words",
            next_screen="Teacher",
            prev_screen="Grandma"
        )


class Teacher(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/teacher.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/teacher.mp3",
            word="Teacher",
            title="3 Letter Words",
            next_screen="HomeScreen",
            prev_screen="Grandpa"
        )


# Feelings:
class Happy(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/happy.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/happy.mp3",
            word="Happy",
            title="3 Letter Words",
            next_screen="Sad",
            prev_screen="HomeScreen"
        )


class Sad(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/sad.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/sad.mp3",
            word="Sad",
            title="3 Letter Words",
            next_screen="Angry",
            prev_screen="Happy"
        )


class Angry(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/angry.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/angry.mp3",
            word="Angry",
            title="3 Letter Words",
            next_screen="Scared",
            prev_screen="Sad"
        )


class Scared(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/scared.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/scared.mp3",
            word="Scared",
            title="3 Letter Words",
            next_screen="Excited",
            prev_screen="Angry"
        )


class Excited(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/excited.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/excited.mp3",
            word="Excited",
            title="3 Letter Words",
            next_screen="Tired",
            prev_screen="Scared"
        )


class Tired(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/tired.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/tired.mp3",
            word="Tired",
            title="3 Letter Words",
            next_screen="Hungry",
            prev_screen="Excited"
        )


class Hungry(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/hungry.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/hungry.mp3",
            word="Hungry",
            title="3 Letter Words",
            next_screen="HomeScreen",
            prev_screen="Tired"
        )


class Apple(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/apple.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/apple.mp3",
            word="Apple",
            title="3 Letter Words",
            next_screen="Banana",
            prev_screen="HomeScreen"
        )


class Banana(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/banana.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/banana.mp3",
            word="Banana",
            title="3 Letter Words",
            next_screen="Carrot",
            prev_screen="Apple"
        )


class Carrot(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/carrot.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/carrot.mp3",
            word="Carrot",
            title="3 Letter Words",
            next_screen="Tomato",
            prev_screen="Banana"
        )


class Tomato(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/tomato.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/tomato.mp3",
            word="Tomato",
            title="3 Letter Words",
            next_screen="Bread",
            prev_screen="Carrot"
        )


class Bread(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/bread.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/bread.mp3",
            word="Bread",
            title="3 Letter Words",
            next_screen="Cheese",
            prev_screen="Tomato"
        )


class Cheese(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/cheese.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/cheese.mp3",
            word="Cheese",
            title="3 Letter Words",
            next_screen="Egg",
            prev_screen="Bread"
        )


class Egg(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/egg.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/egg.mp3",
            word="Egg",
            title="3 Letter Words",
            next_screen="Rice",
            prev_screen="Cheese"
        )


class Rice(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/rice.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/rice.mp3",
            word="Rice",
            title="3 Letter Words",
            next_screen="Pasta",
            prev_screen="Egg"
        )


class Pasta(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/pasta.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/pasta.mp3",
            word="Pasta",
            title="3 Letter Words",
            next_screen="Pizza",
            prev_screen="Rice"
        )


class Pizza(BaseScreen):
    def __init__(self, parent, controller):
        super().__init__(
            parent=parent,
            controller=controller,
            image_path="/Users/fatimabilwani/Speech Delay Helper/images/pizza.png",
            sound_path="/Users/fatimabilwani/Speech Delay Helper/sounds/pizza.mp3",
            word="Pizza",
            title="3 Letter Words",
            next_screen="HomeScreen",
            prev_screen="Pasta"
        )


app = App()
app.mainloop()



