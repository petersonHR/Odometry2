# serial_reader.py

import threading
import serial
import traceback

class SerialReader(threading.Thread):
    def __init__(self, port, baudrate, data_manager):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.data_manager = data_manager
        self.ser = None
        self.stop_event = threading.Event()
        self.serial_lock = threading.Lock()  # Lock para acesso thread-safe

    def run(self):
        print("Thread SerialReader iniciada.")
        try:
            self.ser = serial.Serial(
                self.port,
                self.baudrate,
                timeout=1,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
            )
            print(f"Porta serial {self.port} aberta com sucesso.")
        except Exception as e:
            print(f"Erro ao abrir a porta serial {self.port}: {e}")
            return

        while not self.stop_event.is_set():
            try:
                with self.serial_lock:
                    line = self.ser.readline().decode('utf-8', errors='replace').strip()
                if line:
                    # Verificar se a linha está no formato correto
                    if line.startswith('BEGIN;') and line.endswith(';END'):
                        print(f"Linha recebida: {line}")
                        self.data_manager.process_line(line)
                    else:
                        print(f"Linha inválida ignorada: {line}")
                else:
                    # Nenhum dado recebido, aguardar um pouco
                    pass
            except Exception as e:
                print("Erro ao ler dados da porta serial:")
                traceback.print_exc()
                break

    def send_command(self, command):
        with self.serial_lock:
            if self.ser and self.ser.is_open:
                try:
                    self.ser.write(command.encode('utf-8'))
                    print(f"Comando enviado: {command}")
                except Exception as e:
                    print(f"Erro ao enviar comando: {e}")

    def stop(self):
        self.stop_event.set()
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"Porta serial {self.port} fechada.")
