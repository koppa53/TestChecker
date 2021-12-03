from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput


class TestChecker(App):
    def build(self):
        self.window = GridLayout()
        self.window.cols = 2
        #self.window.size_hint = (0.6, 0.7)
        #self.window.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        # add widgets to window
        self.window.add_widget(Image(source="Logo.png"))
        self.message = Label(text="Select Answer Sheets Folder: ")
        self.button = Button(text="Select Folder")
        self.window.add_widget(self.message)
        self.button.bind(on_press=self.browseFile)
        self.window.add_widget(self.button)
        self.message2 = Label(text="Select Key to Correction File: ")
        self.window.add_widget(self.message2)
        self.button2 = Button(text="Select File")
        self.button2.bind(on_press=self.browseFile)
        self.window.add_widget(self.button2)
        return self.window

    def browseFile(self, instance):
        print("Pressed")


if __name__ == "__main__":
    TestChecker().run()
