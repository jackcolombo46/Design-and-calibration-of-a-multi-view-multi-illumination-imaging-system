import customtkinter as ctk
import serial
import tkinter as tk
import math
import time

#arduino = serial.Serial(port='COM5', baudrate =9600)

def checkbox_callback(checkbox_id):
    if checkbox_var[checkbox_id].get() == 1:
        print(f"Led {checkbox_id} on")
        checkbox_value[checkbox_id] = "on"
        #arduino.write(str.encode('seq' + str(checkbox_id)))
    else:
        print(f"Led {checkbox_id} off")
        checkbox_value[checkbox_id] = "off"

    update_hexagon()



def update_hexagon():
    # Definisci i colori dei lati dell'esagono in base allo stato delle checkbox
    colors = ["grey"]  # Inizializza i colori dei lati dell'esagono con "white" (disabilitato)

    for i in range(1, 7):  # Loop attraverso le checkbox
        if checkbox_var[i].get() == 1:
            colors.append("green")  # Aggiungi "green" (selezionato) alla lista dei colori
        else:
            colors.append("grey")  # Aggiungi "white" (disabilitato) alla lista dei colori

    # Disegna l'esagono con i colori aggiornati
    canvas.delete("hexagon")  # Rimuovi l'esagono esistente
    hexagon_size = min(canvas_width, canvas_height) * 0.5  # Dimensione dell'esagono come il 60% delle dimensioni del canvas
    hexagon_center_x = canvas_width / 2  # Coordinata x del centro dell'esagono
    hexagon_center_y = canvas_height / 2  # Coordinata y del centro dell'esagono
    hexagon_points = [(hexagon_center_x + hexagon_size * math.cos(2 * math.pi * i / 6), hexagon_center_y + hexagon_size * math.sin(2 * math.pi * i / 6)) for i in range(6)]  # Calcola i punti dell'esagono
    for i in range(6):
        canvas.create_line(hexagon_points[i], hexagon_points[(i + 1) % 6], fill=colors[i+1], width=10, tags="hexagon")  # Disegna ogni lato dell'esagono con il colore corrispondente

# Creazione della finestra principale
window = ctk.CTk()
window.title("LED MANAGER")
window.geometry("750x550")

canvas_width = 400
canvas_height = 400

canvas = tk.Canvas(window, width=canvas_width, height=canvas_height, bg="black")
canvas.place(relx=0.5, rely=0.5, anchor="center")


# Creazione del frame per i CTkCheckbox
checkbox_frame = ctk.CTkFrame(window)
checkbox_frame.pack(side="left", padx=20, pady=10, anchor='nw')

# Dizionario per tenere traccia delle variabili e dei valori delle checkbox
checkbox_var = {}
checkbox_value = {}

# Creazione dei CTkCheckbox
checkbox_texts = ["LED 1", "LED 2", "LED 3", "LED 4", "LED 5", "LED 6"]

for i, text in enumerate(checkbox_texts):
    checkbox_var[i+1] = ctk.IntVar()
    checkbox_value[i+1] = "off"

    checkbox = ctk.CTkCheckBox(checkbox_frame, text=text, variable=checkbox_var[i+1], command=lambda checkbox_id=i+1: checkbox_callback(checkbox_id))
    checkbox.pack(anchor="w", pady=8)

def pic_button():
    #arduino.write(str.encode('pic'))
    print("Foto scattata")
    time.sleep(1)

ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Creazione del frame per i pulsanti
button_frame = ctk.CTkFrame(window)
button_frame.pack(side="right", padx=10, anchor='ne')

# Creazione dei pulsanti
button1 = ctk.CTkButton(button_frame, text="PIC", command=pic_button, width=150, height=50, fg_color="darkblue", font=("", 20))
button1.pack(pady=10)


button2 = ctk.CTkButton(button_frame, text="OFF", command=update_hexagon(), width=150, height=50, fg_color="darkblue", font=("", 20))
button2.pack(pady=10)


# Avvio del ciclo di eventi dell'interfaccia grafica
window.mainloop()
