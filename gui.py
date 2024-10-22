# gui.py

import tkinter as tk
from tkinter import ttk
import time
import math
import threading
import traceback
import tkinter.messagebox
class GUI:
    def __init__(self, root, data_manager, serial_reader):
        self.root = root
        self.data_manager = data_manager
        self.serial_reader = serial_reader  # Adicionar serial_reader à GUI
        self.root.title("Monitoramento em Tempo Real")
        self.style = ttk.Style()
        self.setup_theme()
        self.create_widgets()
        self.update_gui()

        # Ajustar a janela para ocupar toda a largura e altura da tela
        self.maximize_window()

        # Variáveis para controle do envio em intervalo
        self.interval_sending = False
        self.interval_thread = None

        # Fechar corretamente a janela
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def maximize_window(self):
        try:
            self.root.state('zoomed')  # Para Windows
        except:
            self.root.attributes('-zoomed', True)  # Para outros sistemas operacionais

    def setup_theme(self):
        # Configurar o tema escuro
        self.style.theme_use('clam')
        self.style.configure('.', background='#2D2D2D', foreground='#FFFFFF', fieldbackground='#2D2D2D')
        self.style.configure('Treeview', background='#2D2D2D', foreground='#FFFFFF', fieldbackground='#2D2D2D')
        self.style.map('Treeview', background=[('selected', '#4F4F4F')])
        self.style.configure('TNotebook', background='#2D2D2D', borderwidth=0)
        self.style.configure('TNotebook.Tab', background='#3C3F41', foreground='#FFFFFF', padding=(10, 5))
        self.style.map('TNotebook.Tab', background=[('selected', '#2D2D2D')])

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        self.tabs = {}
        tab_names = ['Geral', 'Bateria', 'Odometria', 'Encoder', 'Mapa 2D', 'ODOMETRIA ESTIMADA']
        for name in tab_names:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=name)
            self.tabs[name] = frame

        self.create_general_tab()
        self.create_battery_tab()
        self.create_odometry_tab()
        self.create_encoder_tab()
        self.create_map_tab()
        self.create_estimated_odometry_tab()

    def create_general_tab(self):
        frame = self.tabs['Geral']
        self.general_table = self.create_table(frame, ['Variável', 'Valor'])

        # Adicionar as variáveis à tabela
        variables = self.data_manager.variable_names[1:-1]  # Excluindo 'BEGIN' e 'END'
        for var in variables:
            self.general_table.insert('', 'end', iid=var, values=(var, 'N/A'))

        # Adicionar as diferenças
        diff_keys = [
            'rightEncoderSensor1NbPulsesNow_diff',
            'leftEncoderSensor1NbPulsesNow_diff',
            'PositionActual1_diff',
            'PositionActual2_diff',
            'shortLeftEncoderNbPulsesNow_diff',
            'shortRightEncoderNbPulsesNow_diff'
        ]
        for var in diff_keys:
            self.general_table.insert('', 'end', iid=var, values=(var, 'N/A'))

    def create_battery_tab(self):
        frame = self.tabs['Bateria']
        self.battery_table = self.create_table(frame, ['Variável', 'Valor'])

        # Variáveis relacionadas à bateria
        battery_vars = [
            'BMS_Pressure',
            'BMS_SOC',
            'BMS_Current_mA',
            'BMS_EXT_SOC'
        ]
        for var in battery_vars:
            self.battery_table.insert('', 'end', iid=var, values=(var, 'N/A'))

    def create_odometry_tab(self):
        frame = self.tabs['Odometria']
        self.odometry_table = self.create_table(frame, ['Variável', 'Valor'])

        # Variáveis relacionadas à odometria
        odometry_vars = [
            'odom_x2',
            'odom_y2',
            'odom_th2',
            'odom_vx2',
            'odom_vth2',
            'odom_x3',
            'odom_y3',
            'odom_th3'
        ]
        for var in odometry_vars:
            self.odometry_table.insert('', 'end', iid=var, values=(var, 'N/A'))

    def create_encoder_tab(self):
        frame = self.tabs['Encoder']
        self.encoder_table = self.create_table(frame, ['Variável', 'Valor'])

        # Variáveis relacionadas aos encoders
        encoder_vars = [
            'leftEncoderSensor1NbPulsesNow',
            'rightEncoderSensor1NbPulsesNow',
            'shortLeftEncoderNbPulsesNow',
            'shortRightEncoderNbPulsesNow',
            'leftSpeed_act',
            'rightSpeed_act',
            'rightEncoderSensor1NbPulsesNow_diff',
            'leftEncoderSensor1NbPulsesNow_diff'
        ]
        for var in encoder_vars:
            self.encoder_table.insert('', 'end', iid=var, values=(var, 'N/A'))

    def create_estimated_odometry_tab(self):
        frame = self.tabs['ODOMETRIA ESTIMADA']

        # Criar frames esquerdo e direito
        left_frame = ttk.Frame(frame)
        right_frame = ttk.Frame(frame)
        left_frame.pack(side='left', fill='both', expand=True)
        right_frame.pack(side='right', fill='both', expand=True)

        # Tabela da Odometria 4
        self.odometry4_table = self.create_table(left_frame, ['Variável', 'Valor'])
        odometry4_vars = ['odom4_x', 'odom4_y', 'odom4_th']
        for var in odometry4_vars:
            self.odometry4_table.insert('', 'end', iid=var, values=(var, 'N/A'))

        # Tabela da Odometria 5
        self.odometry5_table = self.create_table(right_frame, ['Variável', 'Valor'])
        odometry5_vars = ['odom5_x', 'odom5_y', 'odom5_th']
        for var in odometry5_vars:
            self.odometry5_table.insert('', 'end', iid=var, values=(var, 'N/A'))

    def create_map_tab(self):
        frame = self.tabs['Mapa 2D']

        # Criar o Canvas para desenhar o mapa
        self.canvas = tk.Canvas(frame, background='#2D2D2D')
        self.canvas.pack(fill='both', expand=True)

        # Definir o tamanho do Canvas
        self.canvas.update_idletasks()  # Atualiza o Canvas para obter as dimensões corretas
        self.canvas_width = self.canvas.winfo_width()
        self.canvas_height = self.canvas.winfo_height()

        # Definir escala e deslocamento
        self.scale = 10  # Ajuste a escala para adequar ao tamanho do Canvas
        self.offset_x = self.canvas_width / 2
        self.offset_y = self.canvas_height / 2

        # Desenhar os eixos
        self.draw_axes()

        # Armazenar as posições para o rastro
        self.robot1_trace = []  # Lista de tuplas (timestamp, x_canvas, y_canvas)
        self.robot2_trace = []
        self.robot3_trace = []
        self.robot4_trace = []

        # Inicializar as posições iniciais
        self.robot1 = {'x': 0, 'y': 0, 'th': 0}
        self.robot2 = {'x': 0, 'y': 0, 'th': 0}
        self.robot3 = {'x': 0, 'y': 0, 'th': 0}
        self.robot4 = {'x': 0, 'y': 0, 'th': 0}

        # Criar IDs para os robôs e rastros
        self.robot1_shape = None
        self.robot2_shape = None
        self.robot3_shape = None
        self.robot4_shape = None

        # Recalcular o centro do Canvas sempre que ele for redimensionado
        self.canvas.bind('<Configure>', self.on_canvas_resize)

    def on_canvas_resize(self, event):
        # Atualizar as dimensões do Canvas
        self.canvas_width = event.width
        self.canvas_height = event.height

        # Recalcular o offset (centro do Canvas)
        self.offset_x = self.canvas_width / 2
        self.offset_y = self.canvas_height / 2

        # Limpar e redesenhar os eixos
        self.canvas.delete('all')
        self.draw_axes()

        # Redesenhar os robôs e rastros
        self.robot1_trace.clear()
        self.robot2_trace.clear()
        self.robot3_trace.clear()
        self.robot4_trace.clear()

        self.robot1_shape = None
        self.robot2_shape = None
        self.robot3_shape = None
        self.robot4_shape = None

    def draw_axes(self):
        # Desenhar os eixos x e y no Canvas com marcações e números
        axis_color = '#FFFFFF'
        tick_color = '#AAAAAA'
        text_color = '#FFFFFF'
        font = ('Arial', 8)

        # Eixo X
        self.canvas.create_line(0, self.offset_y, self.canvas_width, self.offset_y, fill=axis_color)
        # Eixo Y
        self.canvas.create_line(self.offset_x, 0, self.offset_x, self.canvas_height, fill=axis_color)

        # Desenhar as marcações nos eixos
        for i in range(-50, 51, 10):  # Marcações de -50 a 50 a cada 10 unidades
            x = i * self.scale + self.offset_x
            y = -i * self.scale + self.offset_y  # Inverter o eixo Y

            # Marcações no eixo X
            self.canvas.create_line(x, self.offset_y - 5, x, self.offset_y + 5, fill=tick_color)
            if i != 0:  # Evitar duplicar o zero
                self.canvas.create_text(x, self.offset_y + 15, text=str(i), fill=text_color, font=font)

            # Marcações no eixo Y
            self.canvas.create_line(self.offset_x - 5, y, self.offset_x + 5, y, fill=tick_color)
            if i != 0:
                self.canvas.create_text(self.offset_x + 15, y, text=str(i), fill=text_color, font=font)

    def create_table(self, parent, columns):
        table = ttk.Treeview(parent, columns=columns, show='headings')
        table.pack(fill='both', expand=True)
        for col in columns:
            table.heading(col, text=col)
            table.column(col, anchor='center')
        return table

    def update_gui(self):
        try:
            data = self.data_manager.get_data()
            # Atualizar tabela Geral
            for var in self.general_table.get_children():
                value = data.get(var, 'N/A')
                self.general_table.item(var, values=(var, str(value)))

            # Atualizar tabela Bateria
            for var in self.battery_table.get_children():
                value = data.get(var, 'N/A')
                self.battery_table.item(var, values=(var, str(value)))

            # Atualizar tabela Odometria
            for var in self.odometry_table.get_children():
                value = data.get(var, 'N/A')
                self.odometry_table.item(var, values=(var, str(value)))

            # Atualizar tabela Encoder
            for var in self.encoder_table.get_children():
                value = data.get(var, 'N/A')
                self.encoder_table.item(var, values=(var, str(value)))

            # Atualizar tabelas de Odometria Estimada
            for var in self.odometry4_table.get_children():
                value = data.get(var, 'N/A')
                self.odometry4_table.item(var, values=(var, str(value)))

            for var in self.odometry5_table.get_children():
                value = data.get(var, 'N/A')
                self.odometry5_table.item(var, values=(var, str(value)))

            # Atualizar o mapa 2D
            self.update_map(data)
        except Exception as e:
            print("Ocorreu um erro na atualização da GUI:")
            traceback.print_exc()
        finally:
            self.root.after(100, self.update_gui)  # Atualiza a cada 100 ms

    def update_map(self, data):
        try:
            # Obter as posições atuais
            odom_x2 = data.get('odom_x2', 0.0)
            odom_y2 = data.get('odom_y2', 0.0)
            odom_th2 = data.get('odom_th2', 0.0)

            odom_x3 = data.get('odom_x3', 0.0)
            odom_y3 = data.get('odom_y3', 0.0)
            odom_th3 = data.get('odom_th3', 0.0)

            # Odometria 4 e 5
            odom4_x = data.get('odom4_x', 0.0)
            odom4_y = data.get('odom4_y', 0.0)
            odom4_th = data.get('odom4_th', 0.0)

            odom5_x = data.get('odom5_x', 0.0)
            odom5_y = data.get('odom5_y', 0.0)
            odom5_th = data.get('odom5_th', 0.0)

            # Converter para float
            odom_x2 = float(odom_x2)
            odom_y2 = float(odom_y2)
            odom_th2 = float(odom_th2)

            odom_x3 = float(odom_x3)
            odom_y3 = float(odom_y3)
            odom_th3 = float(odom_th3)

            odom4_x = float(odom4_x)
            odom4_y = float(odom4_y)
            odom4_th = float(odom4_th)

            odom5_x = float(odom5_x)
            odom5_y = float(odom5_y)
            odom5_th = float(odom5_th)

            # Atualizar as posições dos robôs
            self.robot1['x'] = odom_x2
            self.robot1['y'] = odom_y2
            self.robot1['th'] = odom_th2

            self.robot2['x'] = odom_x3
            self.robot2['y'] = odom_y3
            self.robot2['th'] = odom_th3

            self.robot3['x'] = odom4_x
            self.robot3['y'] = odom4_y
            self.robot3['th'] = odom4_th

            self.robot4['x'] = odom5_x
            self.robot4['y'] = odom5_y
            self.robot4['th'] = odom5_th

            # Desenhar os robôs no Canvas
            self.draw_robot('robot1', self.robot1, trace_list=self.robot1_trace)
            self.draw_robot('robot2', self.robot2, trace_list=self.robot2_trace)
            self.draw_robot('robot3', self.robot3, trace_list=self.robot3_trace)
            self.draw_robot('robot4', self.robot4, trace_list=self.robot4_trace)

        except Exception as e:
            print("Ocorreu um erro na atualização do mapa:")
            traceback.print_exc()

    def draw_robot(self, robot_id, robot, trace_list=None):
        try:
            # Converter coordenadas do mundo real para coordenadas do Canvas
            x = robot['x'] * self.scale + self.offset_x
            y = -robot['y'] * self.scale + self.offset_y  # Inverter o eixo Y

            # Atualizar o rastro
            if trace_list is not None:
                current_time = time.time()
                # Adicionar a posição atual à lista de rastros
                trace_list.append((current_time, x, y))
                # Remover posições mais antigas que um minuto
                one_minute_ago = current_time - 60  # 60 segundos atrás
                trace_list[:] = [(t, x_t, y_t) for t, x_t, y_t in trace_list if t >= one_minute_ago]

                # Desenhar o rastro
                self.draw_trace(trace_list, color=robot_id)

            # Remover a forma anterior
            if hasattr(self, f'{robot_id}_shape') and getattr(self, f'{robot_id}_shape'):
                self.canvas.delete(getattr(self, f'{robot_id}_shape'))

            # Desenhar um triângulo representando o robô
            self.draw_triangle_robot(robot_id, x, y, robot['th'])

        except Exception as e:
            print(f"Ocorreu um erro ao desenhar o robô {robot_id}:")
            traceback.print_exc()

    def draw_triangle_robot(self, robot_id, x, y, th):
        try:
            # Definir o tamanho do robô no Canvas
            robot_size = 20

            # Calcular os vértices do triângulo
            angle = th  # Assumindo que 'th' está em radianos

            # Coordenadas do triângulo em relação ao centro do robô
            points = [
                (x + robot_size * math.cos(angle), y + robot_size * math.sin(angle)),  # Ponta do triângulo
                (x + robot_size * math.cos(angle + 2 * math.pi / 3), y + robot_size * math.sin(angle + 2 * math.pi / 3)),
                (x + robot_size * math.cos(angle + 4 * math.pi / 3), y + robot_size * math.sin(angle + 4 * math.pi / 3))
            ]

            # Definir a cor com base no robô
            if robot_id == 'robot1':
                color = 'blue'
            elif robot_id == 'robot2':
                color = 'green'
            elif robot_id == 'robot3':
                color = '#ADD8E6'  # Light blue
            elif robot_id == 'robot4':
                color = '#90EE90'  # Light green
            else:
                color = 'gray'

            # Desenhar o triângulo
            shape = self.canvas.create_polygon(points, fill=color)

            # Salvar o ID da forma
            setattr(self, f'{robot_id}_shape', shape)
        except Exception as e:
            print(f"Erro ao desenhar triângulo para {robot_id}: {e}")
            traceback.print_exc()

    def draw_trace(self, trace_list, color='blue'):
        try:
            # Primeiro, remover o rastro anterior
            self.canvas.delete('trace_' + color)

            # Se houver pelo menos dois pontos, desenhar linhas entre eles
            if len(trace_list) >= 2:
                points = []
                for _, x, y in trace_list:
                    points.extend([x, y])

                # Definir a cor com base no robô
                if color == 'robot1':
                    line_color = 'blue'
                elif color == 'robot2':
                    line_color = 'green'
                elif color == 'robot3':
                    line_color = '#ADD8E6'  # Light blue
                elif color == 'robot4':
                    line_color = '#90EE90'  # Light green
                else:
                    line_color = 'gray'

                self.canvas.create_line(points, fill=line_color, width=2, tags=('trace_' + color))
        except Exception as e:
            print(f"Erro ao desenhar o rastro do {color}: {e}")
            traceback.print_exc()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True)

        self.tabs = {}
        tab_names = ['Geral', 'Bateria', 'Odometria', 'Encoder', 'Mapa 2D', 'ODOMETRIA ESTIMADA', 'Controle']
        for name in tab_names:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=name)
            self.tabs[name] = frame

        self.create_general_tab()
        self.create_battery_tab()
        self.create_odometry_tab()
        self.create_encoder_tab()
        self.create_map_tab()
        self.create_estimated_odometry_tab()
        self.create_control_tab()  # Adicionar a aba Controle

    def create_control_tab(self):
        frame = self.tabs['Controle']

        # Enviar '@' uma vez
        single_at_frame = ttk.Frame(frame)
        single_at_frame.pack(pady=10)
        single_at_button = ttk.Button(single_at_frame, text="Enviar '@'", command=self.send_single_at)
        single_at_button.pack()

        # Enviar '@' em intervalos
        interval_at_frame = ttk.Frame(frame)
        interval_at_frame.pack(pady=10)

        interval_label = ttk.Label(interval_at_frame, text="Intervalo (s):")
        interval_label.pack(side=tk.LEFT)
        self.interval_entry = ttk.Entry(interval_at_frame, width=10)
        self.interval_entry.pack(side=tk.LEFT)
        self.interval_entry.insert(0, "1")  # Intervalo padrão de 1 segundo

        self.interval_button = ttk.Button(interval_at_frame, text="Iniciar Envio '@' em Intervalo", command=self.toggle_interval_sending)
        self.interval_button.pack(side=tk.LEFT)

        # Comando 'speed'
        speed_frame = ttk.Frame(frame)
        speed_frame.pack(pady=10)

        speed_left_label = ttk.Label(speed_frame, text="vel_esquerda:")
        speed_left_label.pack(side=tk.LEFT)
        self.speed_left_entry = ttk.Entry(speed_frame, width=10)
        self.speed_left_entry.pack(side=tk.LEFT)
        self.speed_left_entry.insert(0, "0")  # Valor padrão

        speed_right_label = ttk.Label(speed_frame, text="vel_direita:")
        speed_right_label.pack(side=tk.LEFT)
        self.speed_right_entry = ttk.Entry(speed_frame, width=10)
        self.speed_right_entry.pack(side=tk.LEFT)
        self.speed_right_entry.insert(0, "0")  # Valor padrão

        speed_button = ttk.Button(speed_frame, text="Enviar Comando 'speed'", command=self.send_speed_command)
        speed_button.pack(side=tk.LEFT)

        # Comando 'twist'
        twist_frame = ttk.Frame(frame)
        twist_frame.pack(pady=10)

        twist_linear_label = ttk.Label(twist_frame, text="vel_linear:")
        twist_linear_label.pack(side=tk.LEFT)
        self.twist_linear_entry = ttk.Entry(twist_frame, width=10)
        self.twist_linear_entry.pack(side=tk.LEFT)
        self.twist_linear_entry.insert(0, "0")  # Valor padrão

        twist_angular_label = ttk.Label(twist_frame, text="vel_angular:")
        twist_angular_label.pack(side=tk.LEFT)
        self.twist_angular_entry = ttk.Entry(twist_frame, width=10)
        self.twist_angular_entry.pack(side=tk.LEFT)
        self.twist_angular_entry.insert(0, "0")  # Valor padrão

        twist_button = ttk.Button(twist_frame, text="Enviar Comando 'twist'", command=self.send_twist_command)
        twist_button.pack(side=tk.LEFT)

    def send_single_at(self):
        command = 'test@'
        self.serial_reader.send_command(command)

    def toggle_interval_sending(self):
        if not self.interval_sending:
            # Iniciar o envio em intervalo
            try:
                interval = float(self.interval_entry.get())
                if interval <= 0:
                    tk.messagebox.showerror("Erro", "O intervalo deve ser um número positivo.")
                    return
            except ValueError:
                tk.messagebox.showerror("Erro", "Por favor, insira um número válido para o intervalo.")
                return

            self.interval_sending = True
            self.interval_button.config(text="Parar Envio '@' em Intervalo")
            self.interval_thread = threading.Thread(target=self.send_at_interval, args=(interval,))
            self.interval_thread.daemon = True
            self.interval_thread.start()
        else:
            # Parar o envio em intervalo
            self.interval_sending = False
            self.interval_button.config(text="Iniciar Envio '@' em Intervalo")

    def send_at_interval(self, interval):
        while self.interval_sending:
            self.serial_reader.send_command('speed:10:10@')
            time.sleep(interval)

    def send_speed_command(self):
        try:
            vel_esquerda = float(self.speed_left_entry.get())
            vel_direita = float(self.speed_right_entry.get())
            command = f'speed:{vel_esquerda}:{vel_direita}@'
            self.serial_reader.send_command(command)
        except ValueError:
            tk.messagebox.showerror("Erro", "Por favor, insira números válidos para vel_esquerda e vel_direita.")

    def send_twist_command(self):
        try:
            vel_linear = float(self.twist_linear_entry.get())
            vel_angular = float(self.twist_angular_entry.get())
            command = f'twist:{vel_linear}:{vel_angular}@'
            self.serial_reader.send_command(command)
        except ValueError:
            tk.messagebox.showerror("Erro", "Por favor, insira números válidos para vel_linear e vel_angular.")

    def on_closing(self):
        # Parar o envio em intervalo se estiver ativo
        if self.interval_sending:
            self.interval_sending = False
        self.root.destroy()
