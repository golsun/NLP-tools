# Author: Xiang Gao @ Microsoft Research
# https://github.com/golsun/dialog-GUI

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtCore import QSize, QCoreApplication
import time, sip, queue, re


class Bubble(QtWidgets.QLabel):
    def __init__(self,text):
        super(Bubble,self).__init__(text)
        self.setWordWrap(True)   
        min_len = min(15 * len(text), 200)
        self.setMinimumSize(min_len, 40)
        self.setContentsMargins(5,5,5,5)
        self.setStyleSheet("QLabel { background-color : white; color : black; }")

    def paintEvent(self, e):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing,True)
        p.drawRoundedRect(0,0,self.width()-1,self.height()-1,5,5)
        super(Bubble,self).paintEvent(e)        


class SidedBubble(QtWidgets.QWidget):

    def __init__(self, text, left=True):
        super(SidedBubble, self).__init__()

        hbox = QtWidgets.QHBoxLayout()
        spacer = QtWidgets.QSpacerItem(1, 1,
            QtWidgets.QSizePolicy.Expanding,
            #QtWidgets.QSizePolicy.Preferred
            )
        label = Bubble(text)
        if left:
            hbox.addWidget(label)
            hbox.addSpacerItem(spacer)
        else:
            hbox.addSpacerItem(spacer)
            hbox.addWidget(label)
        
        hbox.setContentsMargins(0,0,0,0)
        hbox = hbox
        self.setLayout(hbox)
        self.setContentsMargins(0,0,0,0)


class QHLine(QtWidgets.QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class QVLine(QtWidgets.QFrame):
    def __init__(self):
        super(QVLine, self).__init__()
        self.setFrameShape(QtWidgets.QFrame.VLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)


class HistoryPannel(QtWidgets.QWidget):
    def __init__(self, max_turns=15):
        super(HistoryPannel, self).__init__()
        self.max_turns = max_turns
        self.turns = []
        self.w = QtWidgets.QWidget()
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.setContentsMargins(0,0,0,0)
        self.row = 0
        
    def add_turn(self, speaker, text):
        text = beautify(text)
        left = speaker.lower() != 'user'
        s_bubble =  SidedBubble(text, left=left)
        avatar = QtWidgets.QLabel(speaker)
        self.turns.append((s_bubble, avatar))
        if len(self.turns) > self.max_turns:
            self.del_turn()
        if left:
            self.layout.addWidget(avatar, self.row, 0)
        else:
            self.layout.addWidget(avatar, self.row, 2)
        self.layout.addWidget(s_bubble, self.row, 1)
        self.row += 1


    def del_turn(self, ix=0):
        widgets = self.turns[ix]
        del self.turns[ix]
        for widget in widgets:
            self.layout.removeWidget(widget)
            sip.delete(widget)

    def reset(self):
        while len(self.turns) > 0:
            self.del_turn()
            

class ControlPannel(QtWidgets.QWidget):
    def __init__(self):
        super(ControlPannel, self).__init__()
        self.button_reset = QtWidgets.QPushButton('Reset')
        self.button_send = QtWidgets.QPushButton('Send')
        self.text_edit = QtWidgets.QLineEdit()

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.button_reset)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.button_send)
        self.setLayout(layout)
        self.setContentsMargins(0,0,0,0)


class NBestPannel(QtWidgets.QWidget):
    def __init__(self, name, h):
        super(NBestPannel, self).__init__()
        self.list = QtWidgets.QListView()
        self.list.setWordWrap(True)
        self.list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        #self.list = QtWidgets.QPlainTextEdit()
        #self.list.setFixedHeight(h)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel('%s n-best'%name))
        layout.addWidget(self.list)
        self.setLayout(layout)
        self.setContentsMargins(0,0,0,0)
        self.items = []


    def set_items(self, nbest):
        self.items = nbest
        model = QtGui.QStandardItemModel(self.list)
        for score, resp in nbest:
            item = QtGui.QStandardItem('%.3f'%score + ' • ' + beautify(resp))
            model.appendRow(item)
        self.list.setModel(model)


def beautify(s):
    return s

def norm_sentence(s):
    return s

class DialogGUI:
    def __init__(self, respond_funcs, sys_names=None, max_turns=3, max_n_hyp=10, max_src_len=90):
        if not isinstance(respond_funcs, list):
            respond_funcs = [respond_funcs]
        if len(respond_funcs) == 1 and sys_names is None:
            sys_names = ['Agent']
        self.n_sys = len(sys_names)
        self.sys_names = sys_names
        assert(self.n_sys) == len(respond_funcs)

        self.respond_funcs = respond_funcs
        self.sys_names = sys_names
        self.max_src_len = max_src_len
        self.src = []
        self.w = QtWidgets.QWidget()
        self.w.setWindowTitle('Dialog GUI')
        self.max_n_hyp = max_n_hyp

        h = 60 * max_turns
        self.history_pannel = HistoryPannel(max_turns)
        self.control_pannel = ControlPannel()
        self.nbest_pannels = [NBestPannel(self.sys_names[i], h * 1.5) for i in range(self.n_sys)]

        chat = QtWidgets.QVBoxLayout()
        chat.addWidget(self.history_pannel)
        chat.addItem(QtWidgets.QSpacerItem(8, h, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        chat.addWidget(QHLine())
        chat.addWidget(self.control_pannel)

        layout = QtWidgets.QHBoxLayout()
        for w in reversed(self.nbest_pannels):
            layout.addWidget(w)
        layout.addWidget(QVLine())
        layout.addLayout(chat)
        self.w.setLayout(layout)
        self.w.show()

        self.control_pannel.text_edit.returnPressed.connect(self.send)
        self.control_pannel.button_send.clicked.connect(self.send)
        self.control_pannel.button_reset.clicked.connect(self.reset)
        self.nbest_pannels[0].list.clicked.connect(self.nbest_clicked)

    def send(self):
        user_input = norm_sentence(beautify(self.control_pannel.text_edit.text()))
        print(user_input)
        self.history_pannel.add_turn('User', user_input)
        self.control_pannel.text_edit.setText('')
        for w in self.nbest_pannels:
            w.set_items([(0., 'thinking ...')])
        QCoreApplication.processEvents()
        self.src.append(user_input)

        src = ' EOS '.join(self.src)  # don't put this in for loop
        for i_sys in range(self.n_sys):
            n_best = self.respond_funcs[i_sys](src)
            if i_sys == 0:
                response = n_best[0][1]
                self.history_pannel.add_turn(self.sys_names[0], response)
                self.src.append(response)
            self.nbest_pannels[i_sys].set_items(n_best)
            QCoreApplication.processEvents()

    def nbest_clicked(self):
        row = self.nbest_pannels[0].list.selectionModel().selectedIndexes()[0].row()
        hyp_selected = self.nbest_pannels[0].items[row]
        self.src[-1] = hyp_selected
        self.history_pannel.del_turn(-1)
        self.history_pannel.add_turn(self.sys_names[0], hyp_selected)
        

    def reset(self):
        self.src = []
        for w in self.nbest_pannels:
            w.set_items([])
        self.history_pannel.reset()



def respond_parrot(inp):
    # always return what user said
    hyp = inp.split('EOS')[-1]
    return sorted([(np.random.random(), hyp)] * 3)

def respond_scripted(_):
    # just some 
    return [
        (-0.953, "hello, how are you ?"), 
        (-0.992, "hi, how are you today ?"), 
        (-1.023, "hello, hope you are having a good day"),
        (-1.232, "hello, how are you? what are you up to today"),
        (-1.320, "hello, how are you? haven't seen you for a while") 
    ]




if __name__ == '__main__':
    a = QtWidgets.QApplication([])
    respond_funcs = [respond_scripted]
    gui = DialogGUI(respond_funcs, ['Sample Output'])
    gui.w.update()
    a.exec_()