import sys
import os
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QHBoxLayout, QScrollArea
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

DB_PATH = "card_manager.db"
CARTAS_DIR = "Cartas dos Players"

class CardManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerenciador de Cartas")
        self.setGeometry(100, 100, 1000, 600)
        self.layout = QHBoxLayout(self)

        self.player_list = QListWidget()
        self.player_list.itemClicked.connect(self.load_cards)

        self.card_area = QScrollArea()
        self.card_widget = QWidget()
        self.card_layout = QVBoxLayout(self.card_widget)
        self.card_area.setWidgetResizable(True)
        self.card_area.setWidget(self.card_widget)

        self.layout.addWidget(self.player_list, 2)
        self.layout.addWidget(self.card_area, 8)

        self.load_players()

    def load_players(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT nome FROM jogadores")
        for nome, in cursor.fetchall():
            item = QListWidgetItem(nome)
            self.player_list.addItem(item)
        conn.close()

    def load_cards(self, item):
        jogador = item.text()
        for i in reversed(range(self.card_layout.count())):
            widget_to_remove = self.card_layout.itemAt(i).widget()
            if widget_to_remove:
                widget_to_remove.setParent(None)

        raridades = ["Comum", "Raro", "Super Raro", "Ultra Raro", "Secreta Rara", "Espirito"]
        for raridade in raridades:
            caminho = os.path.join(CARTAS_DIR, jogador, raridade)
            if not os.path.exists(caminho):
                continue

            raridade_label = QLabel(f"<b>{raridade}</b>")
            raridade_label.setTextFormat(Qt.TextFormat.RichText)
            self.card_layout.addWidget(raridade_label)

            for nome_arquivo in os.listdir(caminho):
                if nome_arquivo.lower().endswith(".jpg"):
                    label = QLabel()
                    pixmap = QPixmap(os.path.join(caminho, nome_arquivo))
                    pixmap = pixmap.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation)
                    label.setPixmap(pixmap)
                    self.card_layout.addWidget(label)

app = QApplication(sys.argv)
window = CardManager()
window.show()
sys.exit(app.exec())
