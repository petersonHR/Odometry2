# main.py

import tkinter as tk
from gui import GUI
from data_manager import DataManager
from serial_reader import SerialReader

def main():
    root = tk.Tk()
    data_manager = DataManager()

    # Configurações da porta serial
    serial_port = 'COM23'  # Substitua pela sua porta serial
    baud_rate = 921600      # Substitua pelo baud rate correto

    # Iniciar o SerialReader
    serial_reader = SerialReader(serial_port, baud_rate, data_manager)
    serial_reader.daemon = True
    serial_reader.start()

    gui = GUI(root, data_manager, serial_reader)  # Passar serial_reader para a GUI

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Encerrando o programa...")
    finally:
        serial_reader.stop()

if __name__ == '__main__':
    main()
