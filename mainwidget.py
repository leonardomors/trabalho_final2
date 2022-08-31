from time import sleep
from kivy.uix.boxlayout import BoxLayout
from pyModbusTCP.client import ModbusClient
from threading import Thread
from datetime import datetime
from popups import ModbusPopup, ScanPopup, MotorPopup, InversorPopup, DataGraphPopup, HistGraphPopup, ControlePopup, SetGraphPopup
from timeseriesgraph import TimeSeriesGraph
from bdhandler import BDHandler
from kivy_garden.graph import LinePlot

BOT = ["imgs/s1.png",'imgs/s2.png']  # Uma CONSTANTE (escrita em letra maiuscula), uma lista com as imagens da solenoide on e off.

class MainWidget(BoxLayout):
    _updateThread = None  # Variável para controle da atualização de threads
    _updateWidgt = True # Variável para controle da atualização do widget posteriormente
    _tags = []  # Lista que vai receber as tags do sistema
    _max_points = 20  # Numero de pontos a ser plotado no futuro
    _controle_automatico = False  # Variável que vai possibilitar a alteração do controle de manual para autoamtico no futuro

    """
    Classe do widget principal da aplicacao
    """
    
    _updateThread = None
    def __init__(self, **kwargs):
        """
        Construtor do widget principal
        """
        self._tags = {}  # Nesse código o tags deverá ser um dicionario, devido a quantidade de informações recebidas na classe.
        super().__init__()
        self._scantime = kwargs.get('scantime') #o kwargs.get faz a busca do elemento em um dos parâmetros da classe superior, no caso ele vai buscar um 'scantime' passado na classe super
        self._ip = kwargs.get('server_ip') # Mesma ideia aplicando kwargs;
        self._port = kwargs.get('port')
        self._hora = str(datetime.now()) # string que recebe a hora atual (verificar documentação do módulo datetime)
        self._modbusPopup = ModbusPopup(self._ip, self._port) # Cria um objeto da calsse ModbusPopup. Este será um popup que após costrução no kivy vai abrir um menu das interações modbus (passar ip, porta, conectar)
        self._scanPopup = ScanPopup(scantime = self._scantime) # Cria um objeto da calsse ScanPopup. Este será um popup que após construção no kivy vai abrir um menu de configurações do scantime (tempo de atualização da GUI)
        self._modbusClient = ModbusClient(self._ip, self._port) # Cria um objeto da calsse ModbusClient.
        self._meas = {} # Dicionario que vai receber as medições (meas)
        self._measn = {} # Mesma ideia do meas porém com alguns ajustes vistos posteriormente.
        
        self._meas['timestamp'] = None # Cria a chave 'timestamp' dentro do dicionario meas, e declara todos os valores como None inicialmente.
        self._meas['values'] = {} # Cria uma nova chave 'values' dentro do dicionario meas, que recebe como valor um novo dicionário vazio.
        for key, value in kwargs.get('modbus_addrs').items(): # O param 'modbus_addrs' foi inicializado na construção do objeto do app principal no códio main, basta verificar lá o quais são as informações que o mesmo possui.
            self._tags[key] = {'info': value, 'color': [1,2,3]} # Como as keys do modbuss_addrs.items() serão justamente os nomes 'tensao', 'nivel', etc
        self._tagsn = self._tags # copia a referência do dicionario tags para outro.
        del self._tagsn['estado_mot'] # deleta algumas chaves do dicionario tagsn, mais precisamente aquelas que tem como medida um resultado boolean (true ou false), mais a frente será entendido o motivo
        del self._tagsn['Solenoide 1']
        del self._tagsn['Solenoide 2']
        del self._tagsn['Solenoide 3']

        self._motorPopup = MotorPopup() # Cria um objeto da classe MotorPopup, este popup após construção no kivy irá conter as informações do motor e possibilidade de atuações (ligar/desligar)
        self._inversorPopup = InversorPopup() # Cria um objeto da classe MotorPopup. Este popup após construção no kv irá conter informações do inversor (dados de corre, potencia, etc)
        self._dataGraph = DataGraphPopup(self._max_points, plot_color=(0.5686,0.8275,0.8824,1)) # cria um objeto da classe DataGraphPopup, classe de gráficos explicada a frente.
        self._hgraph = HistGraphPopup(tags = self._tags) # cria um objeto da classe HistGraphPopup, em que serão plotados os dados historicos do processo.
        self._measn['timestamp'] = {} 
        self._measn['values'] = {}
        self._measn = self._meas
        self._controlePopup = ControlePopup() # Cria um objeto da classe ControlePopup, que será um popup para definir se o controle automatico está ativo ou não
        self._setgraphPopup = SetGraphPopup() # Cria um objeto da classe SetGraphPopup, que NÃO será usado nesse código, sua implemntação seriviria para definir qual gráfico se deseja plotar em tempo real, se é o de nivel ou de vazão, nesse código so consegui plotar o de nível.

    def conectar(self, ip, port): # Método da classe que vai implementar a conexão em um servidor Modbus existente.
        """
        Faz a conexão com o servidor
        :param ip: IP do servidor Modbus
        :param port: Porta em que o servidor está rodando.
        """
        try:
            self._ip = ip
            self._port = port
            self._modbusClient.host = self._ip
            self._modbusClient.port = self._port
            self._modbusClient.open() # função que tenta realizar a conexão com o servidor.
            print(self._modbusClient)
            if self._modbusClient.is_open: # o is_open verifica se a condição existe, ou seja, se a conexão entre cliente e servidor foi estabelecida
                self._updateThread = Thread(target=self.update_widget) # Cria a thread de atualização dos widgets
                self._updateThread.start()
                # print('conectado') 
                self._modbusPopup.dismiss() # O dismiss fecha o popup ativo.
                self.ids.img_com.source = 'imgs/conectado.png' # Altera a imagem que representa conexão no código.

            else:
                print('falha na conexao')
                self._modbusPopup.set_info('falha na conexao') # é exibido no popup uma mensagem informando a falha na conexão.
        except Exception as e:
            print('Erro na conexao: ', e.args) # print da exceção gerada após a falha na conexão, possiveis causas são: Servidor não está aberto, ip/porta errados, etc
        
    def update_widget(self): # Método de atualização da interface, associado a thread criada acima.
        """
        atualizador
        """
        try:
            while self._updateWidgt: # Loop infinito rodando nessa thread, como é uma thread a parte o código não trava, se tentar fazer isso dentro de uma unica linha de execução o código vai ficar preso nesse loop e o não vai funcionar.
                self.readData()  # Realiza leitura dos dados
                self._bd.insertData(self._measn) #Insere os dados lidos no banco de dados
                self.controleNivel() # Verifica se o controle automatico está ativo, e se estiver realiza o controle.
                self.updateGUI() # Atualiza a interface gráfica (GUI)
                
                
                sleep(self._scantime/1000) # Pausa o loop pelo tempo setado no scantime / 1000. Ou seja, um scantime de 1000 resulta em uma pausa de 1s na execução do código.

        except  Exception as e:
            self._modbusClient.close()
            print('Erro na atualizacao de widgt: ', e.args) 
        
    


        sleep(self._scantime/1000)

        pass

    def readData(self):
        """
        Metodo para leitura dos dados do servidor MODBUS800
        """
        self._meas['timestamp'] = datetime.now() # Insere a data/hora atual na chave 'timestamp' do dicionario.
        for key, value in self._tags.items(): # for que faz a varredura dos dados vindos do _tags
            if self._tags[key]['info']['type'] == 'holding_registers': # Verificar a chave 'type' fornecida na criação do objeto no 'main.py', lá eu inseri o tipo da informação dependendo do endereço.
                self._meas['values'][key] = (self._modbusClient.read_holding_registers(self._tags[key]['info']['addr'], 1)[0]) / self._tags[key]['info']['mult']
                """
                O objeto modbusClient possui o método read_xxx_registers(enedereço, 1)[0] fará a leitura do determinado dado (holdin_register, coils, input ou discrete) que o cliente recebe
                do servidor, e esse valor é armazenado no nosso dicionario _meas. Mais precisamente dentro da chave 'values', na nova chave key que é justamente o nome do dado (tensao, nivel, etc)
                No caso dos holding_registers e dos input_registers é feito um ajuste dividindo o valor original pela chave 'mult', pois foi informado na documentação do servidor que os dados envidados devem ser convertidos.
                """
            
            elif self._tags[key]['info']['type'] == 'coils':
                self._meas['values'][key] = self._modbusClient.read_coils(self._tags[key]['info']['addr'], 1)[0]
            elif self._tags[key]['info']['type'] == 'input_register':
                self._meas['values'][key] = (self._modbusClient.read_input_registers(self._tags[key]['info']['addr'], 1)[0])/ self._tags[key]['info']['mult']
            elif self._tags[key]['info']['type'] == 'discrete_inputs':
                self._meas['values'][key] = self._modbusClient.read_discrete_inputs(self._tags[key]['info']['addr'], 1)[0]
        self._estado_mot = self._modbusClient.read_coils(800, 1)[0] # Criei uma variavel separadamente apenas para armazenas o estado do motor, mais pra frente no código será entendido o motivo.
        
        


    def stopRefresh(self):
        self._updateWidgt= False # Passa a variavel do update para false, fechando os loops atrelados a ela. Esse método é invocado ao fechar a janela do app.

    def updateGUI(self):
        """
        Método que atualiza as interfaces gráficas em geral
        """
        ## Atualização do Popup do motor:
        key_motor = ['estado_mot', 't_part', 'freq_motor', 'rotacao', 'temp_estator', 'vz_entrada'] # Lista com as keys que estão dentro do popup motor, facilita  o trabalho de atualização abaixo.
        for key, value in self._meas['values'].items():
            if key in key_motor:
                self._motorPopup.ids[key].text = str(value) # Converte o valor lido para uma string, para que o mesmo possa ser passado ao parâmetro text do kv (o text só aceita string)

        ## Atualização do Popup do inversor:
        key_inversor = ['tensao', 'pot_entrada', 'corrente']
        for key, value in self._meas['values'].items():
            if key in key_inversor:
                self._inversorPopup.ids[key].text = str(value)
        
        ## Atualizacao do tanque de agua

        self.ids.lb_agua.size = (self.ids.lb_agua.size[0], self._meas['values']['nivel']/1000*self.ids.tanque.size[1]) # Atualização da animação da água dentro do tanque.
        self.ids.nv_agua.text = str(self._meas['values']['nivel']) + ' litros' # Um indicativo da quantidade de agua em litros plotada logo acima do tanque, na interface gráfica.

        ## Atualizacao do grafico
        self._dataGraph.ids.graph.updateGraph((self._meas['timestamp'], self._meas['values']['nivel']),0) # Atualiza o gráfico que mais a frente será invocado, com os dados do nivel de agua.
        # para fazer o gráfico de nivel a ideia é a mesma, o primeiro argumento do updateGraph é o tempo, o segundo é o valor plotado.
 
        ## Atualizacao estado motor:
        if self._estado_mot == False:
            self.ids.motor.background_normal = 'imgs/motor.png' # Se o motor está DESLIGADO, a imagem dele será essa
        elif self._estado_mot == True:
            self.ids.motor.background_normal = 'imgs/motor_ligado.png' # Se o motor está LIGADO, a imagem dele será essa
        



    def operar_motor(self, freq_des): # Esse método implementa a funcionalidade de ligar  e desligar o motor.
        if self._meas['values']['estado_mot'] == False: # Verifica se o motor está DESLGIADO
            self._modbusClient.write_single_register(799, freq_des) # acessa o endereço 799 dos registers e altera seu valor para freq_des, que é a frequencia desejada para a operação. Quanto maior a frequencia desejada, maior será a rotação do motor.
            self._modbusClient.write_single_coil(800, True) # Acessa o endereço 800  das coils e muda seu valor para TRUE, ou seja, liga o motor.
            self._motorPopup.ids.op_motor.text = "DESLIGAR" # Muda o texto no botão, para entendimento do usuario.
        elif self._meas['values']['estado_mot'] == True: # Verifica se o motor está LIGADO.
            self._modbusClient.write_single_coil(800, False) # Desliga o motor, passando o endereço 800 das coils para false.
            self._motorPopup.ids.op_motor.text = "LIGAR" # Muda o texto do botão, para entendimento do usuario.
    
    # Os métodos ligar_motor e desligar_motor seguem a mesma idéia do operar_motor, divido em duas partes.

    def ligar_motor(self, freq_des):

        self._modbusClient.write_single_register(799, freq_des)
        self._modbusClient.write_single_coil(800, True)
        

    def desligar_motor(self):
        self._modbusClient.write_single_coil(800, False)

    def operar_solenoide(self, solenoide): # método que deve ligar o desligar uma determinada solenoide, recebe como parâmetro a solenoide a qual se refere.
        """
        VERIFICAR O FUNCIONAMENTO DESSE MÉTODO, A PRINCIPIO NÃO ESTÁ FUNCIONANDO NO CÓDIGO.
        """
        if solenoide == 'on1':
            self._modbusClient.write_single_coil(801, True)
        elif solenoide == 'on2':
            self._modbusClient.write_single_coil(802, True)
        elif solenoide == 'on3':
            self._modbusClient.write_single_coil(803, True)

        pass

    def atualiza_botao(self, botao, address): # Operar uma selonoide e ao mesmo tempo mudar a imagem dela na GUI
        if botao.background_normal == BOT[0]:
            botao.background_normal = BOT[1]
            self._modbusClient.write_single_coil(int(address), True)

        else:
            botao.background_normal = BOT[0]
            self._modbusClient.write_single_coil(int(address), False)

    def getDataDB(self):
        """
        Método que realiza coleta das informacoes fornecidas pelo usuario
        """
        try:
            init_t = self.parseDTString(self._hgraph.ids.txt_init_time.text)
            final_t = self.parseDTString(self._hgraph.ids.txt_final_time.text)
            cols = []
            for sensor in self._hgraph.ids.sensores.children:
                if sensor.ids.checkbox.active:
                    cols.append(sensor.id)
            if init_t is None or final_t is None or len(cols)==0:
                return

            cols.append('timestamp')
            dados = self._bd.selectData(cols, init_t, final_t)

            if dados is None or len(dados['timestamp'])==0:
                return

            self._hgraph.ids.graph.clearPlots()
            for key, value in dados.items():
                if key == 'timestamp':
                    continue
                p = LinePlot(line_width = 1.5, color = (0.5686,0.8275,0.8824,1))
                p.points = [(x, value[x]) for x in range(0, len(value))]
                self._hgraph.ids.graph.add_plot(p)

            self._hgraph.ids.graph.xmax = len(dados[cols[0]])
            self._hgraph.ids.graph.update_x_labels([datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f") for x in dados['timestamp']])

        except Exception as e:
            print("erro na L229: ", e.args)



    def parseDTString(self, datetime_str):
        """
        converte a string inserida no mecanismo de pesquisa para o formato correto de consulta no Bd
        """
        try:
            d = datetime.strptime(datetime_str, '%d/%m/%Y %H:%M:%S')
            return d.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print("Erro na L213: ", e.args)

    def controleNivel(self):
        """
        Método que implementa o controle de nível automatico
        :param setpoint: Setpoint do controle de nivel setado pelo usuario, ao atingir esse nivel de agua o motor deve ligar
        :param histerese: Atraso em litros para desligar o motor após atingido o valor do setpoint
        """
        setpoint = int(self._controlePopup.ids.setpoint.text)
        histerese = int(self._controlePopup.ids.histerese.text)
        x = setpoint + histerese
        

        if self._controle_automatico:            
            
            if self._meas['values']['nivel'] < setpoint:
                self._modbusClient.write_single_coil(800, True)

                

            if self._meas['values']['nivel'] > x:
                self._modbusClient.write_single_coil(800, False)
                
                
             

        else:
            pass

    def ativarControleAutomatico(self):
        self._controle_automatico = True
        

    def desativarControleAutomatico(self):
        self._controle_automatico = False
        self._modbusClient.write_single_coil(800, False)
      
    


        
        