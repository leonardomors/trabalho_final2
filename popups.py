from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy_garden.graph import LinePlot
from kivy.uix.boxlayout import BoxLayout
from timeseriesgraph import TimeSeriesGraph

class ModbusPopup(Popup):
    """
    Popup da tela de conexção (modbus)
    """
    def __init__(self, server_ip, port, **kwargs):
        super().__init__(*kwargs)
        self.ids.txt_ip.text = str(server_ip)
        self.ids.txt_port.text = str(port)

    def set_info(self, message):
        self._info = Label(text= str(message), font_size=15, size_hint= (1,0.3))
        self.ids.layout.add_widget(self._info)

  #  def clear_info(self):
   #     if self._info is not None:
    #        self.ids.layout.remove_widget(self._info)
        


class ScanPopup(Popup):
    def __init__(self,scantime, **kwargs):
        super().__init__(**kwargs)
        self.ids.ti_scan.text = str(scantime)

class MotorPopup(Popup):
    def __init__(self):
        super().__init__()

class InversorPopup(Popup):
    def __init__(self):
        super().__init__()

class DataGraphPopup(Popup):
    def __init__(self, xmax, plot_color, **kwargs):
        super().__init__(**kwargs)
        self.plot = LinePlot(line_width = 1.5, color = plot_color)
        self.ids.graph.add_plot(self.plot)
        self.ids.graph.xmax = xmax

class CheckBoxDataGraph(BoxLayout):
    pass

class HistGraphPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.get('tags').items():
            cb = CheckBoxHistGraph()
            cb.ids.label.text = key
            cb.ids.label.color = (0.5686,0.8275,0.8824,1)
            cb.id = key
            self.ids.sensores.add_widget(cb)

class CheckBoxHistGraph(BoxLayout):
    pass


class ControlePopup(Popup):
    pass

        
        