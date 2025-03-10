import customtkinter as ctk
import os, random, sys
from PIL import Image
import tkinter as tk
import tkinter.messagebox as msg

# matplotlib
import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

global statsShown
statsShown = False


##### FILE MANAGEMENT #####

def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller/cx_Freeze.
    try:
        # When running as a packaged executable
        base_path = sys._MEIPASS
    except AttributeError:
        # When running in the development environment
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def writable_path(relative_path):
    # Get path to writable resource stored in user's home directory.
    user_data_dir = os.path.join(os.path.expanduser("~"), "Collatz4_Data")
    os.makedirs(user_data_dir, exist_ok=True)
    return os.path.join(user_data_dir, relative_path)

def initialize_writable_files():
    # Copy writable files to user directory if not already present.
    files_to_copy = ["mode.txt"]
    for file in files_to_copy:
        source_path = resource_path(f"Text/{file}")
        dest_path = writable_path(file)
        if not os.path.exists(dest_path):
            try:
                with open(source_path, "r") as src, open(dest_path, "w") as dst:
                    dst.write(src.read())
            except Exception as e:
                msg.showerror('Unexpected Error!', f'Error copying {file}: {e}')

###########################


class Panel(ctk.CTk):
    def __init__(self):
        super().__init__()

        # setup
        self.title('')
        self.resizable(False, False)
        initialize_writable_files()

        # set dark mode based on text file
        try:
            mode_path=writable_path('mode.txt')
            with open(mode_path, "r") as file:
                content = file.read()
                ctk.set_appearance_mode(content)
                if content == 'dark':
                    lightMode = False
                elif content == 'light':
                    lightMode = True
                self.lightModeForMenu = tk.BooleanVar(value=lightMode)
        except Exception as e:
            msg.showerror('Error!', f'Could not open {mode_path}')
            print(e)

        # image assets
        random_path=resource_path('Images/random.png')
        dl_path=resource_path('Images/dl.png')
        light_path=resource_path('Images/light.png')
        dark_path=resource_path('Images/dark.png')
        stats_path=resource_path('Images/stats.png')
        check_path=resource_path('Images/check.png')

        global dl_icon, check_icon

        # widgets
        self.title_label=ctk.CTkLabel(self, text='Collatz Conjecture Grapher', font=('JetBrains Mono NL',30))
        self.enter_label=ctk.CTkLabel(self, text='Enter any number:', font=('Helvetica', 15))
        validate_command=self.register(self.validate)
        self.entry=ctk.CTkEntry(self, validate='key', corner_radius=15, width=200, height=50, font=('Helvetica', 25), validatecommand=(validate_command, "%P"))
        try:
            self.rand_icon=ctk.CTkImage(light_image=Image.open(random_path), dark_image=Image.open(random_path), size=(20,20))
            self.random_button=ctk.CTkButton(self, text='Randomize', corner_radius=15, image=self.rand_icon, command=self.random)
        except Exception as e:
            self.random_button=ctk.CTkButton(self, text='Randomize', corner_radius=15, command=self.random)
        self.clear_button=ctk.CTkButton(self, text='Clear', corner_radius=5, fg_color='red', hover_color='dark red', command=self.clear)
        try:
            self.dl_icon=ctk.CTkImage(light_image=Image.open(dl_path), dark_image=Image.open(dl_path), size=(20,20))
            self.dl_button=ctk.CTkButton(self, text='Download', corner_radius=15, fg_color='green', hover_color='dark green', image=self.dl_icon, command=self.dl)
        except:
            self.dl_button=ctk.CTkButton(self, text='Download', corner_radius=15, fg_color='green', hover_color='dark green', command=self.dl)
        self.mode_switch=ctk.CTkSwitch(self, text='', onvalue='dark', offvalue='light', switch_height=25, switch_width=50, progress_color='#006DD4', command=self.toggle_mode)
        try:
            self.mode_icon=ctk.CTkImage(dark_image=Image.open(dark_path), light_image=Image.open(light_path), size=(30,30))
            self.mode_image=ctk.CTkLabel(self, text='', image=self.mode_icon)
        except:
            self.mode_image=ctk.CTkLabel(self, text='could not load image')
        try:
            self.stats_icon=ctk.CTkImage(dark_image=Image.open(stats_path), light_image=Image.open(stats_path), size=(20,20))
            self.stats_button=ctk.CTkButton(self, text='View Stats', corner_radius=15, image=self.stats_icon, fg_color='#fc7d05', hover_color='#bd6009', command=self.stats)
        except:
            self.stats_button=ctk.CTkButton(self, text='View Stats', corner_radius=15, fg_color='#fc7d05', hover_color='#bd6009', command=self.stats)

        self.graph=Graph(self)

        # layout
        self.title_label.grid(   row=0,column=0,   columnspan=2, padx=20,pady=20, sticky='nsew')
        self.enter_label.grid(   row=2,column=1,   columnspan=2, padx=20,pady=10, sticky='sew')
        self.entry.grid(         row=3,column=1,   columnspan=2, padx=20,pady=10, sticky='nsew')
        self.random_button.grid( row=5,column=1,   columnspan=2, padx=20,pady=10, sticky='nsew')
        self.clear_button.grid(  row=12,column=1,  columnspan=2, padx=20,pady=10, sticky='ew')
        self.dl_button.grid(     row=6,column=1,   columnspan=2, padx=20,pady=10, sticky='nsew')
        self.stats_button.grid(  row=7,column=1,   columnspan=2, padx=20,pady=10, sticky='nsew')
        self.mode_switch.grid(   row=0,column=2,                 padx=10,pady=10, sticky='w')
        self.mode_image.grid(    row=0,column=1,                 padx=10,pady=10, sticky='e')
        self.graph.grid(         row=1,column=0,   rowspan=12,   padx=10,pady=10, sticky='nsew')

        # set keybind for clearing depending on OS
        if sys.platform == 'darwin':
            self.bind_all('<Command-BackSpace>', lambda event: self.clear())
        else:
            self.bind_all('<Control-BackSpace>', lambda event: self.clear())

        self.plot(7)

        # set initial dark mode based on file
        mode_path=writable_path('mode.txt')
        with open (mode_path, 'r') as file:
            content = file.read()
            if 'dark' in content:
                self.mode_switch.select()
            elif 'light' in content:
                self.mode_switch.deselect()

    # validate command for number input - only digits
    def validate(self, value):
        if value == "" or value.isdigit():
            if len(value) < 20:
                self.plot(value)
                return True
        return False
    
    def plot(self, value):
        global numTitle, values
        if value != '':
            num = int(value)  # get number
            numTitle = num    # set variable for the graph title and png file
            values = [num]    # clear values list and only have the number
            while num != 1:            #
                if num % 2 == 0:       #
                    num = num / 2      # actual collatz conjecture math stuff
                else:                  #
                    num = num * 3 + 1  #
                num = round(num)    # rounding to remove the .0
                values.append(num)

            self.graph.update_graph(values) # update the graph
        else:
            self.graph.clear_graph() # clear the graph if the input is blank

    def clear(self):
        self.entry.delete(0,ctk.END)
        self.graph.clear_graph()
    
    # set number to a random one and update
    def random(self):
        num = random.randint(1,10000)
        self.entry.delete(0, ctk.END)
        self.entry.insert(0, num)
        if not statsShown:
            self.plot(num)

    # download an image of the current graph
    def dl(self):
        global numTitle
        self.graph.figure.savefig(os.path.expanduser(f'~/Downloads/collatz_{numTitle}'))

        dl_path=resource_path('Images/dl.png')
        check_path=resource_path('Images/check.png')
        self.dl_icon=ctk.CTkImage(light_image=Image.open(dl_path), dark_image=Image.open(dl_path), size=(20,20))
        self.check_icon=ctk.CTkImage(light_image=Image.open(check_path), dark_image=Image.open(check_path), size=(20,20))

        def reset():
            self.dl_button.configure(image=self.dl_icon)
        try:
            self.dl_button.configure(image=self.check_icon)
            self.after(1000, reset)
        except:
            pass

    # get stats and update the ctk window
    def stats(self):
        global values, statsShown
        highest_num = max(values)                       # get highest number
        highest_num_index = values.index(highest_num)   # get the index

        terms = len(values) - 4  #
        if terms < 0:            # number of terms until loop
            terms = 0            #

        termAverage = sum(values) / len(values)   # get average
        termAverage = round(termAverage, 2)       # round to 2 places

        odds = evens = 0          #
        for value in values:      #
            if value % 2 == 0:    #
                evens +=1         # get odd and even terms
            else:                 #
                odds += 1         #
        
        if statsShown:
            # remove all stats
            self.graph.max.grid_forget()
            self.graph.terms.grid_forget()
            self.graph.sum.grid_forget()
            self.graph.average.grid_forget()
            self.graph.even.grid_forget()
            self.graph.odd.grid_forget()
            self.graph.spacer.grid_forget()
            self.graph.canvas_widget.grid(row=0, column=0, sticky="nsew")  # show canvas
            self.stats_button.configure(text='View Stats') # config button
            statsShown = False
        else:
            # hide graph
            self.graph.canvas_widget.grid_forget()
            self.graph.show(highest_num, highest_num_index, terms, termAverage, sum(values), evens, odds) # call function to show all stats
            self.stats_button.configure(text='Hide Stats') # config button
            statsShown = True

    def toggle_mode(self):
        mode=self.mode_switch.get()
        mode_path=writable_path('mode.txt')

        with open (mode_path, 'r') as file:
            content = file.read()
            title = self.graph.ax.get_title()

            if 'dark' in content:
                with open (mode_path, 'w') as file:
                    file.write(content.replace('dark', 'light'))
                ctk.set_appearance_mode('light')

                self.graph.ax.set_facecolor('#EBEBEB')             # foreground
                self.graph.figure.set_facecolor('#EBEBEB')         # background
                self.graph.ax.spines['bottom'].set_color('black')  # bottom line
                self.graph.ax.spines['top'].set_color('black')     # top line
                self.graph.ax.spines['left'].set_color('black')    # left line
                self.graph.ax.spines['right'].set_color('black')   # right line
                self.graph.ax.tick_params(axis="x", colors="black")  # x axis ticks
                self.graph.ax.tick_params(axis="y", colors="black")  # y axis ticks
                self.graph.ax.set_title(title, color='black')
                self.graph.canvas.draw() # redraw graph

            elif 'light' in content:
                with open (mode_path, 'w') as file:
                    file.write(content.replace('light', 'dark'))
                ctk.set_appearance_mode('dark')

                self.graph.ax.set_facecolor('#232323')             # foreground
                self.graph.figure.set_facecolor('#232323')         # background
                self.graph.ax.spines['bottom'].set_color('white')  # bottom line
                self.graph.ax.spines['top'].set_color('white')     # top line
                self.graph.ax.spines['left'].set_color('white')    # left line
                self.graph.ax.spines['right'].set_color('white')   # right line
                self.graph.ax.tick_params(axis="x", colors="white")  # x axis ticks
                self.graph.ax.tick_params(axis="y", colors="white")  # y axis ticks
                self.graph.ax.set_title(title, color='white')
                self.graph.canvas.draw() # redraw graph



class Graph(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)

        # prepare stats screen
        self.max=ctk.CTkLabel(self,     text=f'Largest term: ',     font=('Courier New', 16), text_color='#7D7D7D')
        self.terms=ctk.CTkLabel(self,   text=f'Terms until loop: ', font=('Courier New', 16), text_color='#7D7D7D')
        self.sum=ctk.CTkLabel(self,     text=f'Sum of all terms:',  font=('Courier New', 16), text_color='#7D7D7D')
        self.average=ctk.CTkLabel(self, text=f'Average value:',     font=('Courier New', 16), text_color='#7D7D7D')
        self.even=ctk.CTkLabel(self,    text=f'Even terms:',        font=('Courier New', 16), text_color='#7D7D7D')
        self.odd=ctk.CTkLabel(self,     text=f'Odd terms:',         font=('Courier New', 16), text_color='#7D7D7D')
        self.spacer=ctk.CTkLabel(self,  text='', width=500, height=170)

        # Create the Matplotlib figure and canvas
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.plot([0], [0])
        self.ax.set_title('')
        self.ax.set_xlabel('Term')
        self.ax.set_ylabel('Value')

        # set dark/light mode
        mode_path = writable_path('mode.txt')
        with open (mode_path, 'r') as file:
            global content
            content = file.read()
            if 'dark' in content:
                self.ax.set_facecolor('#232323')             # foreground
                self.figure.set_facecolor('#232323')         # background
                self.ax.spines['bottom'].set_color('white')  # bottom line
                self.ax.spines['top'].set_color('white')     # top line
                self.ax.spines['left'].set_color('white')    # left line
                self.ax.spines['right'].set_color('white')   # right line
                self.ax.tick_params(axis="x", colors="white")  # x axis ticks
                self.ax.tick_params(axis="y", colors="white")  # y axis ticks
            elif 'light' in content:
                self.ax.set_facecolor('#ebebeb')             # foreground
                self.figure.set_facecolor('#ebebeb')         # background
                self.ax.spines['bottom'].set_color('black')  # bottom line
                self.ax.spines['top'].set_color('black')     # top line
                self.ax.spines['left'].set_color('black')    # left line
                self.ax.spines['right'].set_color('black')   # right line
                self.ax.tick_params(axis="x", colors="black")  # x axis ticks
                self.ax.tick_params(axis="y", colors="black")  # y axis ticks

        # Embed the figure into the CTk frame
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, sticky="nsew")

    def update_graph(self, data):
        self.ax.clear()  # Clear the current plot
        self.ax.plot(
            range(len(data)),
            data
        )
        if 'dark' in content:
            self.ax.set_title(f"Collatz Conjecture sequence of {data[0]}", color='white')
        elif 'light' in content:
            self.ax.set_title(f"Collatz Conjecture sequence of {data[0]}", color='black')
        self.canvas.draw()  # Redraw the canvas

    # function for clearing the graph
    def clear_graph(self):
        self.ax.clear()
        self.canvas.draw()

    # function for showing stats
    def show(self, hn, hni, t, ta, ts, e, o):
        global statsShown
        self.max.configure(text=f'Largest term (term {hni}): {hn}')
        self.terms.configure(text=f'Amount of terms before loop: {t}')
        self.sum.configure(text=f'Sum of all values: {ts}')
        self.average.configure(text=f'Average value: {ta}')
        self.even.configure(text=f'Even terms: {e}')
        self.odd.configure(text=f'Odd terms: {o}')

        self.max.grid(row=0,column=0, padx=30,pady=5, sticky='w')
        self.terms.grid(row=1,column=0, padx=30,pady=5, sticky='w')
        self.sum.grid(row=2,column=0, padx=30,pady=5, sticky='w')
        self.average.grid(row=3,column=0, padx=30,pady=5, sticky='w')
        self.even.grid(row=4,column=0, padx=30,pady=5, sticky='w')
        self.odd.grid(row=5,column=0, padx=30,pady=5, sticky='w')
        self.spacer.grid(row=6,column=0)



if __name__ == '__main__':
    app = Panel()
    app.mainloop()
os._exit(0)
