import tkinter
import tkinter.messagebox
import customtkinter
from functools import partial
import serial
import time
import test_camera
import acquisizioni_vimba_originale

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"


class App(customtkinter.CTk):
    #arduino = serial.Serial(port='COM5', baudrate=9600)

    def __init__(self):
        super().__init__()

        # set default value
        self.N_IMG = 10
        self.capture_started = False
        self.current_capture = 0
        self.Ncams=3
        self.path='D:/DOCUMENTI_G/PoliMi/Magistrale/Tesi/Python/IDS/Images2'
        self.exposure = 100

        # configure window
        self.title("GUI Parameters setting")
        self.geometry(f"{1200}x{700}")

        # configure grid layout (4x4)
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140,) # corner_radius=0
        self.sidebar_frame.grid(row=1, column=0, padx=(10,10), pady=(20,0),sticky="nsew") #rowspan=3,
        #self.sidebar_frame.grid_rowconfigure(3, weight=1)
        # self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="GUI Parameters Setting", font=customtkinter.CTkFont(size=20, weight="bold"))
        # self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="n")
        self.appearance_mode_label.grid(row=0, column=2, padx=(20,20), pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=1, column=2, padx=(20,20), pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="n")
        self.scaling_label.grid(row=2, column=2, padx=(20,20), pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=3, column=2, padx=(20,20), pady=(10, 20))

        # create textbox
        self.textbox = customtkinter.CTkTextbox(self, width=250)
        self.textbox.grid(row=0, column=1, columnspan=2, padx=(5, 5), pady=(20, 0), sticky="nsew")
        self.textbox.insert("0.0", "README before use the program\n\n"
                                   "Instructions:\n\n 1. Select the type of LED you want to use with the checkbox on the top left corner,"
                                   "\n\n(one type at once)"
                                   "\n\n 2.Select the number of cameras you want to use"
                                   "\n\n 3. Select the path in which the images should be saved and paste it in the input dialog"
                                   "\n\n 3. Insert the number of picture you want take in the entry dialog and press START. "
                                   " \n\nThe cameras will be initialized and the acquisition begins"
                                   "\n\n 4. Press the PIC button to take the next pictures, except the first (executed with START)"
                                   "\n\n 5. The program will automatically stop when the system acquired the number of picture received as input")

        #create option menu
        self.optionmenu_frame = customtkinter.CTkFrame(self)
        self.optionmenu_frame.grid(row=0, column=3, padx=(10,10), pady=(20,0), sticky="nsew")
        self.label_option_menu = customtkinter.CTkLabel(master=self.optionmenu_frame, text="Number of cams:")
        self.label_option_menu.grid(row=0, column=3, padx=20, pady=20, sticky="nw")
        self.optionmenu = customtkinter.CTkOptionMenu(master=self.optionmenu_frame,values=["1", "2", "3"], command=self.option_cams) #command=self.option_cams
        self.optionmenu.grid(row=1, column=3, padx=20, pady=10, sticky='n')

        self.label_option_menu_1 = customtkinter.CTkLabel(master=self.optionmenu_frame, text="Exposure time (in ms)")
        self.label_option_menu_1.grid(row=3, column=3, padx=20, pady=20, sticky="nw")
        self.exposure_time = customtkinter.CTkEntry(master=self.optionmenu_frame, placeholder_text="")
        self.exposure_time.grid(row=4, column=3, padx=20, pady=10, sticky='n')
        #self.exposure_time.bind(command=self.entry_exp_time)

        #create checkbox frame
        self.checkbox_frame = customtkinter.CTkFrame(self)
        self.checkbox_frame.grid(row=0, column=0, padx=(10, 10), pady=(20, 0), sticky="nsew")
        self.label_checkbox_frame = customtkinter.CTkLabel(master=self.checkbox_frame, text="Select the type of LED")
        self.label_checkbox_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.checkbox1 = customtkinter.CTkCheckBox(master=self.checkbox_frame, text="WL LED ", command= self.checkbox1_event)
        self.checkbox1.grid(row=1, column=0, pady=10, padx=20, sticky="n")
        self.checkbox2 = customtkinter.CTkCheckBox(master=self.checkbox_frame, text="IR LED ", command= self.checkbox2_event)
        self.checkbox2.grid(row=2, column=0, pady=10, padx=20, sticky="n")

        #create input string box
        self.string_input_button = customtkinter.CTkButton(master=self.checkbox_frame, text="PATH",
                                                            width=150, height=50, command=self.open_input_dialog_event) #command=self.open_input_dialog_event,
        self.string_input_button.grid(row=5, column=0, padx=20, pady=20)

        # create scrollable frame 1
        self.scrollable_frame1 = customtkinter.CTkScrollableFrame(self, label_text="LED MANAGER WHITE LIGHT")
        self.scrollable_frame1.grid(row=1, column=1, padx=(5, 5), pady=(10, 0), sticky="nsew")
        self.scrollable_frame1.grid_columnconfigure(0, weight=1)
        self.scrollable_frame_switches1 = []
        for i in range(6):
            partial_function = partial(self.arduino_event, i)
            switch = customtkinter.CTkSwitch(master=self.scrollable_frame1, text=f"LED {i+1}",command=partial_function)
            switch.grid(row=i, column=0, padx=10, pady=(0, 20))
            self.scrollable_frame_switches1.append(switch)

        # create scrollable frame 2
        self.scrollable_frame2 = customtkinter.CTkScrollableFrame(self, label_text="LED MANAGER IR")
        self.scrollable_frame2.grid(row=1, column=2, padx=(5, 5), pady=(10, 0), sticky="nsew")
        self.scrollable_frame2.grid_columnconfigure(0, weight=1)
        self.scrollable_frame_switches2 = []
        for i in range(6):
            partial_function = partial(self.arduino_event_infrared, i)
            switch = customtkinter.CTkSwitch(master=self.scrollable_frame2, text=f"LED {i+1}",command=partial_function,)
            switch.grid(row=i, column=0, padx=10, pady=(0, 20))
            self.scrollable_frame_switches2.append(switch)

        # create main entry and button
        self.entry = customtkinter.CTkEntry(self, placeholder_text="Pic's Number")
        self.entry.grid(row=3, column=1, columnspan=2, padx=(5, 5), pady=(10, 20), sticky="nsew")
        self.entry.bind(sequence="<Return>",command=self.entryvalue)
        self.main_button_1 = customtkinter.CTkButton(master=self, fg_color="transparent", text="START", border_width=2,
                                                     text_color=("gray10", "#DCE4EE"), command=self.button_event)
        self.main_button_1.grid(row=3, column=3, columnspan=1, rowspan=1, padx=(20, 20), pady=(10, 20), sticky="nsew")
        self.main_button_2 = customtkinter.CTkButton(master=self, fg_color="transparent", text="PIC", border_width=2,
                                                     text_color=("gray10", "#DCE4EE"), command=self.button_pic, state="disabled")
        self.main_button_2.grid(row=1, column=3, padx=(20,20), pady=(10,10), sticky="nsew")

    def checkbox1_event(self):
        if self.checkbox1.get() == 1:
            for i in range(6):
                self.scrollable_frame_switches2[i].configure(state="disabled")

        if self.checkbox1.get() == 0:
            for i in range(6):
                self.scrollable_frame_switches2[i].configure(state="normal")


    def checkbox2_event(self):
        if self.checkbox2.get() == 1:
            for i in range(6):
                self.scrollable_frame_switches1[i].configure(state="disabled")

        if self.checkbox2.get() == 0:
            for i in range(6):
                self.scrollable_frame_switches1[i].configure(state="normal")

    def open_input_dialog_event(self):
        dialog = customtkinter.CTkInputDialog(text="Type in the Path in which you want to save the pictures:", title="Select Path:")
        self.path=dialog.get_input()
        print("CTkInputDialog:", self.path)
        # if self.radio_button_1.cget("value")==0:
        #     test_camera.main(self.path, self.Ncams)
        # elif self.radio_button_2.cget("value")==0:
        #     acquisizioni_vimba_originale.main(self.path, self.Ncams)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def sidebar_button_event(self):
        print("sidebar_button click")

    def arduino_event(self, i: int):
        self.arduino.write(str.encode(str(i+2)))
        print("LED {i}")
        time.sleep(1)

    def arduino_event_infrared(self, i: int):
        self.arduino.write(str.encode(str(i+8)))
        print("LED {i}")
        time.sleep(1)

    # def entry_exp_time(self):
    #     try:
    #         self.exposure = int(self.exposure_time.get())
    #         print(self.exposure)
    #     except Exception:
    #         return

    def entryvalue(self, _):
        self.N_IMG = int(self.entry.get())
        print(self.N_IMG)

    def button_event(self):
        try:
            self.N_IMG =  int(self.entry.get())
        except Exception:
            return
        if self.checkbox1.get() == 1 and self.checkbox2.get()==0:
            test_camera.main() #self.exposure, self.path, self.Ncams,
        elif self.checkbox2.get() == 1 and self.checkbox1.get()==0:
            acquisizioni_vimba_originale.main() #self.exposure, self.path, self.Ncams,

        self.main_button_2.configure(state="normal")
        self.capture_started = True
        self.current_capture = 0
        self.button_pic()

    def button_pic(self):
        if not self.capture_started:
            return

        if self.current_capture > self.N_IMG:
            return

        if self.capture_started and self.checkbox2.get()==0:
            test_camera.pic_event(self.N_IMG)
        elif self.capture_started and self.checkbox1.get()==0:
            acquisizioni_vimba_originale.main()

        # if self.radio_button_1.cget("value")==0:
        #     test_camera.main()
        # elif self.radio_button_2.cget("value")==0:
        #     acquisizioni_vimba_originale.main()

        print("captured", self.current_capture)
        self.current_capture += 1

        if self.current_capture >= self.N_IMG:
            self.main_button_2.configure(state="disabled")
            test_camera.close_camera()

    def option_cams(self, val):
        self.Ncams = int(val)
        print(self.Ncams, val)
        # if self.radio_button_1.cget("value")==0:
        #     test_camera.main(self.path, self.Ncams)
        # elif self.radio_button_2.cget("value")==0:
        #     acquisizioni_vimba_originale.main(self.path, self.Ncams)



if __name__ == "__main__":
    app = App()
    app.mainloop()