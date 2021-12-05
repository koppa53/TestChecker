from tkinter import *
from tkinter import filedialog
from tkinter import font
from PIL import ImageTk, Image
import tkinter
import checker

# set directory
sheet_path, key_path = "", ""


def click():
    global sheet_path
    answer_sheet_path = filedialog.askdirectory()
    sheet_path = answer_sheet_path
    answer_sheet_file_path.insert(END, answer_sheet_path)

# set answer sheet


def click_ans():
    global key_path
    answer_key_path = filedialog.askopenfilename()
    key_path = answer_key_path
    answer_key_file_path.insert(END, answer_key_path)


def check():
    global sheet_path, key_path
    answer_sheets_images, answer_key_image = checker.load_images(
        sheet_path, key_path)
    processed_answer_key = checker.preprocess_image(answer_key_image)
    checker.test_checker(answer_sheets_images,
                         processed_answer_key)


gui = Tk()
# set window size
gui.geometry("1100x720")
gui.title('Test Checker 1.0')
gui.resizable(False, False)

photo = PhotoImage(file="testchecker.png")
gui.iconphoto(False, photo)
myFont = font.Font(family='Century Gothic', size=14, weight='bold')

my_img = Image.open("imageheader.png")

resized = my_img.resize((542, 689))

new_pic = ImageTk.PhotoImage(resized)
my_label = Label(image=new_pic)
my_label.pack()

my_label.place(x=10, y=20)

# execute the program
button = Button(gui, text='Get Started', bg='#536DFE',
                fg='white', activebackground='#F2F2F2', command=check)
button['font'] = myFont
button.pack()

button.place(x=780, y=610)

header = Label(gui, text="Automated Test Checker", bg='white',
               fg='#536DFE', font=("Century Gothic", 25, "bold")).place(x=635, y=60)

select_folder = Label(gui, text="Browse Answer Sheets Folder", bg='white',
                      fg='#2F2E41', font=("Century Gothic", 14, "bold")).place(x=625, y=160)
ans_key = Label(gui, text="Select Answer Key", bg='white', fg='#2F2E41', font=(
    "Century Gothic", 14, "bold")).place(x=625, y=240)

# button for selecting directory
button_select = Button(gui, text='Browse', bg='#536DFE',
                       fg='white', activebackground='#F2F2F2', command=click)
button_select['font'] = myFont
button_select.pack()

button_select.place(x=990, y=195)

# button for selecting answer sheet
select_ans = Button(gui, text='Browse', bg='#536DFE',
                    fg='white', activebackground='#F2F2F2', command=click_ans)
select_ans['font'] = myFont
select_ans.pack()

select_ans.place(x=990, y=275)

paper_total = Label(gui, text="Total Papers Checked:", bg='white', fg='#2F2E41', font=(
    "Century Gothic", 14, "bold")).place(x=625, y=380)
# note placeholder text
ans_sheets = Label(gui, text="20", bg='white', fg='#536DFE', font=(
    "Century Gothic", 14, "bold")).place(x=840, y=380)

passing_rate = Label(gui, text="Passing Rate:", bg='white', fg='#2F2E41', font=(
    "Century Gothic", 14, "bold")).place(x=625, y=420)
# note placeholder text
percentage = Label(gui, text="98%", bg='white', fg='#536DFE', font=(
    "Century Gothic", 14, "bold")).place(x=750, y=420)

# text field for directory
answer_sheet_file_path = tkinter.Text(gui, height=1, width=31, bg='#E5E5E5')
answer_sheet_file_path.pack()

answer_sheet_file_path.place(x=630, y=200)

Font_tuple1 = ("Century Gothic", 14, "bold")
answer_sheet_file_path.configure(font=Font_tuple1)

# text field for answer sheet
answer_key_file_path = tkinter.Text(gui, height=1, width=31, bg='#E5E5E5')
answer_key_file_path.pack()

answer_key_file_path.place(x=630, y=280)

Font_tuple2 = ("Century Gothic", 14, "bold")
answer_key_file_path.configure(font=Font_tuple2)

# set window color
gui['bg'] = 'white'

gui.mainloop()
