# data_manager.py

import threading
import math

class DataManager:
    def __init__(self):
        self.lock = threading.Lock()
        self.data = {}
        self.previous_values = {
            'rightEncoderSensor1NbPulsesNow': 0,
            'leftEncoderSensor1NbPulsesNow': 0,
            'PositionActual1': 0,
            'PositionActual2': 0,
            'shortLeftEncoderNbPulsesNow': 0,
            'shortRightEncoderNbPulsesNow': 0
        }
        self.odometry4 = {'x': 0.0, 'y': 0.0, 'th': 0.0}
        self.odometry5 = {'x': 0.0, 'y': 0.0, 'th': 0.0}
        self.variable_names = [
            'BEGIN',
            'PROTOCOL_VERSION',
            'getEllapsedTime',
            'BMS_ChargeDischargeCycle',
            'FixedValue1',
            'FixedValue2',
            'FixedValue3',
            'BMS_Pressure',
            'BMS_SOC',
            'adVoltageInt',
            'BMS_Current_mA',
            'inputCurrent',
            'ChargerConnected',
            'PositionActual1',
            'PositionActual2',
            'DeltaTimeOdometry',
            'FixedValue4',
            'leftEncoderSensor1NbPulsesNow',
            'rightEncoderSensor1NbPulsesNow',
            'shortLeftEncoderNbPulsesNow',
            'shortRightEncoderNbPulsesNow',
            'leftSpeed_act',
            'rightSpeed_act',
            'currentSensorMotorLeftAverage',
            'currentSensorMotorRightAverage',
            'odom_x2',
            'odom_y2',
            'odom_th2',
            'odom_vx2',
            'odom_vth2',
            'NumberOfReceivedConfigs',
            'odom_x3',
            'odom_y3',
            'odom_th3',
            'BMS_EXT_SOC',
            'externalAdVoltageInt',
            'END'
        ]

        # Parâmetros para cálculo da odometria (substitua pelos valores reais do seu sistema)
        self.WHEEL_RADIUS = 0.1  # metros
        self.WHEEL_BASE = 0.5    # metros
        self.COUNTS_PER_REV = 360  # pulsos por revolução
        self.COUNTS_PER_METER = self.COUNTS_PER_REV / (2 * math.pi * self.WHEEL_RADIUS)

    def process_line(self, line):
        try:
            # Remover 'BEGIN;' do início e ';END' do final
            line_content = line[len('BEGIN;'):-len(';END')]
            # Dividir a linha por ';'
            values = line_content.split(';')
            # Remover valores vazios
            values = [v for v in values if v]
            # Verificar se o número de valores corresponde ao esperado
            expected_values = len(self.variable_names) - 2  # Excluindo 'BEGIN' e 'END'
            if len(values) == expected_values:
                data_dict = dict(zip(self.variable_names[1:-1], values))
                # Converter valores para os tipos apropriados
                try:
                    for key in data_dict:
                        if key in ['ChargerConnected', 'NumberOfReceivedConfigs']:
                            data_dict[key] = int(data_dict[key])
                        elif key.startswith('FixedValue') or 'Encoder' in key or 'PositionActual' in key or 'DeltaTimeOdometry' in key:
                            data_dict[key] = int(data_dict[key])
                        elif key.endswith('_mA') or key.endswith('Int'):
                            data_dict[key] = int(data_dict[key])
                        elif key == 'PROTOCOL_VERSION':
                            # Manter como string
                            pass
                        else:
                            data_dict[key] = float(data_dict[key])

                    # Calcular diferenças dos encoders
                    diffs = {
                        'rightEncoderSensor1NbPulsesNow_diff': data_dict['rightEncoderSensor1NbPulsesNow'] - self.previous_values['rightEncoderSensor1NbPulsesNow'],
                        'leftEncoderSensor1NbPulsesNow_diff': data_dict['leftEncoderSensor1NbPulsesNow'] - self.previous_values['leftEncoderSensor1NbPulsesNow'],
                        'PositionActual1_diff': data_dict['PositionActual1'] - self.previous_values['PositionActual1'],
                        'PositionActual2_diff': data_dict['PositionActual2'] - self.previous_values['PositionActual2'],
                        'shortLeftEncoderNbPulsesNow_diff': data_dict['shortLeftEncoderNbPulsesNow'] - self.previous_values['shortLeftEncoderNbPulsesNow'],
                        'shortRightEncoderNbPulsesNow_diff': data_dict['shortRightEncoderNbPulsesNow'] - self.previous_values['shortRightEncoderNbPulsesNow']
                    }

                    # Atualizar valores anteriores
                    self.previous_values['rightEncoderSensor1NbPulsesNow'] = data_dict['rightEncoderSensor1NbPulsesNow']
                    self.previous_values['leftEncoderSensor1NbPulsesNow'] = data_dict['leftEncoderSensor1NbPulsesNow']
                    self.previous_values['PositionActual1'] = data_dict['PositionActual1']
                    self.previous_values['PositionActual2'] = data_dict['PositionActual2']
                    self.previous_values['shortLeftEncoderNbPulsesNow'] = data_dict['shortLeftEncoderNbPulsesNow']
                    self.previous_values['shortRightEncoderNbPulsesNow'] = data_dict['shortRightEncoderNbPulsesNow']

                    # Calcular odometria 4 e 5
                    self.calculate_odometry4(diffs)
                    self.calculate_odometry5(diffs)

                    # Atualizar dados de forma thread-safe
                    with self.lock:
                        self.data = {**data_dict, **diffs,
                                     'odom4_x': self.odometry4['x'],
                                     'odom4_y': self.odometry4['y'],
                                     'odom4_th': self.odometry4['th'],
                                     'odom5_x': self.odometry5['x'],
                                     'odom5_y': self.odometry5['y'],
                                     'odom5_th': self.odometry5['th']}
                except ValueError as ve:
                    print(f"Erro ao converter os dados: {ve}")
                    # Ignorar a linha e não atualizar os dados
            else:
                print(f"Linha com número de valores inesperado. Esperado: {expected_values}, Recebido: {len(values)}")
                # Ignorar a linha
        except Exception as e:
            print(f"Erro inesperado ao processar a linha: {e}")
            # Ignorar a linha

    def calculate_odometry4(self, diffs):
        # Calcular distâncias percorridas por cada roda
        delta_left = diffs['shortLeftEncoderNbPulsesNow_diff'] / self.COUNTS_PER_METER
        delta_right = diffs['shortRightEncoderNbPulsesNow_diff'] / self.COUNTS_PER_METER

        # Calcular movimento
        delta_s = (delta_left + delta_right) / 2
        delta_theta = (delta_right - delta_left) / self.WHEEL_BASE

        # Atualizar orientação
        self.odometry4['th'] += delta_theta
        self.odometry4['th'] = self.normalize_angle(self.odometry4['th'])

        # Atualizar posição
        self.odometry4['x'] += delta_s * math.cos(self.odometry4['th'])
        self.odometry4['y'] += delta_s * math.sin(self.odometry4['th'])

    def calculate_odometry5(self, diffs):
        # Calcular distâncias percorridas por cada roda
        delta_left = diffs['PositionActual1_diff'] / self.COUNTS_PER_METER
        delta_right = diffs['PositionActual2_diff'] / self.COUNTS_PER_METER

        # Calcular movimento
        delta_s = (delta_left + delta_right) / 2
        delta_theta = (delta_right - delta_left) / self.WHEEL_BASE

        # Atualizar orientação
        self.odometry5['th'] += delta_theta
        self.odometry5['th'] = self.normalize_angle(self.odometry5['th'])

        # Atualizar posição
        self.odometry5['x'] += delta_s * math.cos(self.odometry5['th'])
        self.odometry5['y'] += delta_s * math.sin(self.odometry5['th'])

    def normalize_angle(self, angle):
        """Normalizar o ângulo para estar entre -pi e pi"""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    def get_data(self):
        with self.lock:
            return self.data.copy()
