from kivy.app import App
from mainwidget import MainWidget
from kivy.lang.builder import Builder

class MyApp(App):
    """
    Classe do aplicativo
    """


    def build(self):
        """
        Construtor/método que gera o aplicativo com o widget principal
        """
        self._widget = MainWidget(scantime=1000, server_ip='127.0.0.1', port=506,
        modbus_addrs = {
            'estado_mot': {'addr': 800, 'type': 'coils', 'mult': 'na'},
            'freq_des': {'addr': 799, 'type': 'holding_registers', 'mult': 1},
            't_part': {'addr': 798, 'type': 'holding_registers', 'mult': 10},
            'freq_motor': {'addr': 800, 'type': 'input_register', 'mult': 10},
            'tensao': {'addr': 801, 'type': 'input_register', 'mult': 1},
            'rotacao' : {'addr': 803, 'type': 'input_register', 'mult': 1},
            'pot_entrada': {'addr': 804, 'type': 'input_register', 'mult': 10},
            'corrente': {'addr': 805, 'type': 'input_register', 'mult': 100},
            'temp_estator': {'addr': 806, 'type': 'input_register', 'mult': 10},
            'vz_entrada': {'addr': 807, 'type': 'input_register', 'mult': 100},
            'nivel': {'addr': 808, 'type': 'input_register', 'mult': 10},
            'nivel_h': {'addr': 809, 'type': 'discrete_inputs', 'mult': 'na'},
            'nivel_l': {'addr': 810, 'type': 'discrete_inputs', 'mult': 'na'},
            'Solenoide 1': {'addr': 801, 'type': 'coils', 'mult': 'na'},
            'Solenoide 2': {'addr': 802, 'type': 'coils', 'mult': 'na'},
            'Solenoide 3': {'addr': 803, 'type': 'coils', 'mult': 'na'}
        },
        db_path = "C:\\Users\\leomo\\Pictures\\trabalho_final 11-08\\trabalho_final-main\\db\\scada.db" 
        )
        return self._widget

    
    def on_stop(self):
        """
        Metodo executado no encerramento da aplicação
        """
        self._widget.stopRefresh()

        
        
if __name__ == '__main__': # Comando que faz com que o app abra apenas se for excutado o arquivo main diretamente
    Builder.load_string(open("mainwidget.kv", encoding="utf-8").read(), rulesonly=True)
    Builder.load_string(open("popups.kv", encoding="utf-8").read(), rulesonly=True)
    MyApp().run()
