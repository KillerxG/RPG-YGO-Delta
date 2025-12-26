import sys
import random
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QGridLayout, QMessageBox,
    QLabel, QScrollArea, QStackedWidget, QHBoxLayout, QFrame,
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect
)
from PyQt6.QtGui import QPalette, QColor, QIcon, QPixmap, QFont
from PyQt6.QtCore import (
    Qt, QSize, QPropertyAnimation, QParallelAnimationGroup,
    QPauseAnimation, QSequentialAnimationGroup, QObject, pyqtProperty,
    QAbstractAnimation
)

APP_TITLE = "Card Shop YGO"
SUPPORTED_EXT = [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"]

RED = "#ff3b3b"
BG = "#000000"
FG = RED

def make_black_background(widget: QWidget):
    palette = widget.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BG))
    widget.setPalette(palette)
    widget.setAutoFillBackground(True)

def start_fullscreen_or_maximized(win: QMainWindow):
    screen = QApplication.primaryScreen()
    if screen is not None:
        geo = screen.availableGeometry()
        win.setMinimumSize(int(geo.width() * 0.8), int(geo.height() * 0.8))
        win.resize(geo.width(), geo.height())
    win.setWindowState(Qt.WindowState.WindowFullScreen | win.windowState())
    win.setWindowState(Qt.WindowState.WindowMaximized | win.windowState())

def list_images(folder: Path):
    if not folder.exists():
        return []
    files = [p for p in folder.iterdir() if p.suffix.lower() in SUPPORTED_EXT and p.is_file()]
    def key_num(p: Path):
        stem = p.stem
        try:
            return (0, int(stem))
        except ValueError:
            return (1, stem.lower())
    return sorted(files, key=key_num)

def make_glow(widget: QWidget, color: str = RED, radius: int = 24, offset=(0, 0)) -> QGraphicsDropShadowEffect:
    glow = QGraphicsDropShadowEffect()
    glow.setBlurRadius(radius)
    glow.setColor(QColor(color))
    glow.setOffset(*offset)
    widget.setGraphicsEffect(glow)
    return glow

class Header(QWidget):
    def __init__(self, title: str):
        super().__init__()
        make_black_background(self)
        self.setFixedHeight(72)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(12)

        self.title = QLabel(title)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet(f"color:{FG};")
        f = QFont()
        f.setPointSize(24)
        f.setBold(True)
        self.title.setFont(f)

        left = QFrame(); left.setFrameShape(QFrame.Shape.HLine); left.setStyleSheet(f"color:{FG};")
        right = QFrame(); right.setFrameShape(QFrame.Shape.HLine); right.setStyleSheet(f"color:{FG};")
        layout.addWidget(left)
        layout.addWidget(self.title)
        layout.addWidget(right)

class StyledButton(QPushButton):
    def __init__(self, text=""):
        super().__init__(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(48)
        self.setStyleSheet(f"""
            QPushButton {{
                color: {FG};
                font-size: 18px;
                padding: 10px 18px;
                border: 2px solid {FG};
                border-radius: 14px;
                background-color: transparent;
            }}
            QPushButton:hover {{
                background-color: rgba(255,59,59,0.1);
            }}
            QPushButton:pressed {{
                background-color: rgba(255,59,59,0.2);
            }}
        """)

class HomePage(QWidget):
    def __init__(self, goto_booster, goto_decks, close_app):
        super().__init__()
        make_black_background(self)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        header = Header("Card Shop YGO")
        root.addWidget(header)

        center = QVBoxLayout()
        center.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_abrir = StyledButton("Abrir Booster")
        btn_abrir.setFixedSize(260, 64)
        btn_abrir.clicked.connect(goto_booster)

        btn_decks = StyledButton("Abrir Decks")
        btn_decks.setFixedSize(260, 64)
        btn_decks.clicked.connect(goto_decks)

        btn_fechar = StyledButton("Fechar")
        btn_fechar.setFixedSize(260, 64)
        btn_fechar.clicked.connect(close_app)

        center.addWidget(btn_abrir)
        center.addSpacing(12)
        center.addWidget(btn_decks)
        center.addSpacing(12)
        center.addWidget(btn_fechar)

        root.addLayout(center)

class BoosterPage(QWidget):
    def __init__(self, go_home, go_result):
        super().__init__()
        make_black_background(self)
        self.go_result = go_result

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        root.addWidget(Header("Selecione um Booster"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(18)
        grid.setContentsMargins(18, 18, 18, 18)

        script_dir = Path(__file__).resolve().parent
        self.capa_dir = script_dir / "capa"
        self.cards_dir = script_dir / "cards"
        icon_w, icon_h = 220, 320
        cols = 5

        if not self.capa_dir.exists():
            warn = QLabel("Pasta 'capa' não encontrada.\nColoque arquivos RPG_Series_1..15.* (png/jpg/etc)")
            warn.setStyleSheet(f"color:{FG}; font-size: 18px;")
            warn.setAlignment(Qt.AlignmentFlag.AlignCenter)
            root.addWidget(warn)
        else:
            for i in range(1, 16):
                file_found = None
                for ext in SUPPORTED_EXT:
                    candidate = self.capa_dir / f"RPG_Series_{i}{ext}"
                    if candidate.exists():
                        file_found = candidate
                        break

                row, col = divmod(i-1, cols)

                btn = QPushButton("")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        border: 2px solid {FG};
                        border-radius: 14px;
                        background-color: rgba(255,59,59,0.06);
                    }}
                    QPushButton:hover {{
                        background-color: rgba(255,59,59,0.12);
                    }}
                """)
                if file_found is not None:
                    pix = QPixmap(str(file_found))
                    if not pix.isNull():
                        btn.setIcon(QIcon(pix))
                        btn.setIconSize(QSize(icon_w, icon_h))
                        btn.setFixedSize(icon_w + 28, icon_h + 28)
                        booster_name = f"RPG_Series_{i}"
                        btn.clicked.connect(lambda _, name=booster_name: self.abrir_pacote(name))
                    else:
                        btn.setText(f"Falha: RPG_Series_{i}")
                        btn.setFixedSize(icon_w + 28, icon_h + 28)
                else:
                    btn.setText(f"Faltando\nRPG_Series_{i}.*")
                    btn.setFixedSize(icon_w + 28, icon_h + 28)

                grid.addWidget(btn, row, col, alignment=Qt.AlignmentFlag.AlignCenter)

            container.setLayout(grid)
            scroll.setWidget(container)
            root.addWidget(scroll, stretch=1)

        footer = QHBoxLayout()
        btn_voltar = StyledButton("Voltar")
        btn_voltar.setFixedSize(180, 50)
        btn_voltar.clicked.connect(go_home)
        btn_fechar = StyledButton("Fechar")
        btn_fechar.setFixedSize(180, 50)
        btn_fechar.clicked.connect(QApplication.instance().quit)
        footer.addWidget(btn_voltar, alignment=Qt.AlignmentFlag.AlignLeft)
        footer.addStretch(1)
        footer.addWidget(btn_fechar, alignment=Qt.AlignmentFlag.AlignRight)
        root.addLayout(footer)

    def abrir_pacote(self, booster_series_name: str):
        # Boosters: cards/RPG_Series_X/{super raras, secretas raras}
        try:
            base_dir = self.cards_dir / booster_series_name
            super_dir = base_dir / "super raras"
            secret_dir = base_dir / "secretas raras"
            super_cards = list_images(super_dir)
            secret_cards = list_images(secret_dir)
            if len(super_cards) < 4 or len(secret_cards) < 1:
                QMessageBox.warning(self, "Cartas insuficientes",
                                    f"Esperado em:\n{super_dir}\n{secret_dir}\n(4 em 'super raras' e 1 em 'secretas raras')")
                return
            chosen_super = random.sample(super_cards, 4)
            chosen_secret = random.choice(secret_cards)
            self.go_result(booster_series_name, chosen_super, chosen_secret)
        except Exception as e:
            QMessageBox.critical(self, "Erro ao abrir booster", str(e))

class DecksPage(QWidget):
    def __init__(self, go_home, go_result_all):
        super().__init__()
        make_black_background(self)
        self.go_result_all = go_result_all

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        root.addWidget(Header("Selecione um Deck"))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        grid = QGridLayout(container)
        grid.setSpacing(18)
        grid.setContentsMargins(18, 18, 18, 18)

        script_dir = Path(__file__).resolve().parent
        self.capa_dir = script_dir / "capa"
        self.decks_dir = script_dir / "decks"

        icon_w, icon_h = 220, 320
        cols = 5

        for i in range(1, 16):
            file_found = None
            for ext in SUPPORTED_EXT:
                candidate = self.capa_dir / f"RPG_Deck_{i}{ext}"
                if candidate.exists():
                    file_found = candidate
                    break

            row, col = divmod(i-1, cols)
            btn = QPushButton("")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    border: 2px solid {FG};
                    border-radius: 14px;
                    background-color: rgba(255,59,59,0.06);
                }}
                QPushButton:hover {{
                    background-color: rgba(255,59,59,0.12);
                }}
            """)

            if file_found is not None:
                pix = QPixmap(str(file_found))
                if not pix.isNull():
                    btn.setIcon(QIcon(pix))
                    btn.setIconSize(QSize(icon_w, icon_h))
                    btn.setFixedSize(icon_w + 28, icon_h + 28)
                    deck_name = f"RPG_Deck_{i}"
                    btn.clicked.connect(lambda _, name=deck_name: self.abrir_deck(name))
                else:
                    btn.setText(f"Falha: RPG_Deck_{i}")
                    btn.setFixedSize(icon_w + 28, icon_h + 28)
            else:
                btn.setText(f"Faltando\nRPG_Deck_{i}.*")
                btn.setFixedSize(icon_w + 28, icon_h + 28)

            grid.addWidget(btn, row, col, alignment=Qt.AlignmentFlag.AlignCenter)

        container.setLayout(grid)
        scroll.setWidget(container)
        root.addWidget(scroll, stretch=1)

        footer = QHBoxLayout()
        btn_voltar = StyledButton("Voltar")
        btn_voltar.setFixedSize(180, 50)
        btn_voltar.clicked.connect(go_home)
        btn_fechar = StyledButton("Fechar")
        btn_fechar.setFixedSize(180, 50)
        btn_fechar.clicked.connect(QApplication.instance().quit)
        footer.addWidget(btn_voltar, alignment=Qt.AlignmentFlag.AlignLeft)
        footer.addStretch(1)
        footer.addWidget(btn_fechar, alignment=Qt.AlignmentFlag.AlignRight)
        root.addLayout(footer)

    def abrir_deck(self, deck_name: str):
        try:
            super_dir = self.decks_dir / deck_name / "super_raras"
            secret_dir = self.decks_dir / deck_name / "secretas_raras"
            super_cards_all = list_images(super_dir)
            secret_cards_all = list_images(secret_dir)

            if len(super_cards_all) < 40 or len(secret_cards_all) < 10:
                QMessageBox.warning(
                    self, "Cartas insuficientes",
                    f"Precisa de pelo menos 40 em 'super_raras' e 10 em 'secretas_raras'.\n"
                    f"Encontrado: {len(super_cards_all)} SR e {len(secret_cards_all)} SSR\n"
                    f"{super_dir}\n{secret_dir}"
                )
                return

            chosen_super = super_cards_all[:40]
            chosen_secret = secret_cards_all[:10]

            self.go_result_all(deck_name, chosen_super, chosen_secret)
        except Exception as e:
            QMessageBox.critical(self, "Erro ao abrir deck", str(e))

class ResultPage(QWidget):
    def __init__(self, go_back_to_select):
        super().__init__()
        make_black_background(self)
        self.go_back_to_select = go_back_to_select

        self._anim_group = None
        self._anim_refs = []

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        self.header = Header("Cartas Abertas")
        root.addWidget(self.header)

        bar = QHBoxLayout()
        bar.setContentsMargins(8, 4, 8, 4)
        bar.setSpacing(10)

        self.btn_voltar = StyledButton("Voltar para seleção")
        self.btn_voltar.setFixedHeight(44)
        self.btn_voltar.clicked.connect(self.go_back_to_select)

        bar.addStretch(1)
        bar.addWidget(self.btn_voltar)
        bar.addStretch(1)

        root.addLayout(bar)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        root.addWidget(self.scroll, stretch=1)

    def _rarity_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"""
            QLabel {{
                color: {FG};
                font-size: 16px;
                font-weight: 700;
                padding: 4px 10px;
                border: 1px solid rgba(255,59,59,0.55);
                border-radius: 8px;
                background-color: rgba(255,59,59,0.10);
            }}
        """)
        return lbl

    def _card_tile(self, img_path: Path, rarity_text: str, card_w=220, card_h=320):
        tile = QWidget()
        v = QVBoxLayout(tile); v.setContentsMargins(0,0,0,0); v.setSpacing(6)
        img = QLabel(); img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pix = QPixmap(str(img_path))
        if not pix.isNull():
            pix = pix.scaled(card_w, card_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            img.setPixmap(pix)
        else:
            img.setText(f"Falha {img_path.name}"); img.setStyleSheet(f"color:{FG};")
        v.addWidget(img, alignment=Qt.AlignmentFlag.AlignCenter)
        v.addWidget(self._rarity_label(rarity_text), alignment=Qt.AlignmentFlag.AlignCenter)
        op = QGraphicsOpacityEffect(tile); tile.setGraphicsEffect(op); op.setOpacity(0.0)
        return tile, op

    def show_booster_5(self, source_name: str, super_cards, secret_card):
        # Mais lento + cartas maiores
        self._clear_scroll()
        row = QWidget()
        row_layout = QHBoxLayout(row); row_layout.setSpacing(24); row_layout.setContentsMargins(40,24,40,24)
        row_layout.addStretch(1)

        group = QParallelAnimationGroup(self); self._anim_group = group
        anim_refs = []; self._anim_refs = anim_refs

        base_pause = 300   # antes 120
        dur_sr = 900       # antes 450
        dur_ssr = 1200     # antes 600

        for idx, p in enumerate(super_cards):
            tile, op = self._card_tile(p, "Super Rare", card_w=320, card_h=460)
            row_layout.addWidget(tile)
            seq = QSequentialAnimationGroup(self)
            seq.addAnimation(QPauseAnimation(idx * base_pause))
            fade = QPropertyAnimation(op, b"opacity"); fade.setDuration(dur_sr); fade.setStartValue(0.0); fade.setEndValue(1.0)
            seq.addAnimation(fade); group.addAnimation(seq); anim_refs.extend([seq, fade, op])

        tile, op = self._card_tile(secret_card, "Secret Rare", card_w=320, card_h=460)
        row_layout.addWidget(tile)
        seq = QSequentialAnimationGroup(self); seq.addAnimation(QPauseAnimation(4 * base_pause))
        fade = QPropertyAnimation(op, b"opacity"); fade.setDuration(dur_ssr); fade.setStartValue(0.0); fade.setEndValue(1.0)
        seq.addAnimation(fade); group.addAnimation(seq); anim_refs.extend([seq, fade, op])

        row_layout.addStretch(1)
        wrapper = QWidget(); wl = QHBoxLayout(wrapper); wl.addWidget(row, alignment=Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(wrapper)

        def _cleanup(): self._anim_refs.clear()
        group.finished.connect(_cleanup); group.start()

    def show_deck_all(self, deck_name: str, super_cards, secret_cards):
        self._clear_scroll()

        grid_widget = QWidget()
        grid = QGridLayout(grid_widget); grid.setSpacing(16); grid.setContentsMargins(24,24,24,24)

        group = QParallelAnimationGroup(self); self._anim_group = group
        anim_refs = []; self._anim_refs = anim_refs

        all_cards = [(p, "Super Rare") for p in super_cards] + [(p, "Secret Rare") for p in secret_cards]

        cols = 5
        for idx, (p, rarity) in enumerate(all_cards):
            r, c = divmod(idx, cols)
            tile, op = self._card_tile(p, rarity, card_w=220, card_h=320)
            grid.addWidget(tile, r, c, alignment=Qt.AlignmentFlag.AlignCenter)

            seq = QSequentialAnimationGroup(self)
            seq.addAnimation(QPauseAnimation((idx % cols) * 80 + (idx // cols) * 60))
            fade = QPropertyAnimation(op, b"opacity"); fade.setDuration(300); fade.setStartValue(0.0); fade.setEndValue(1.0)
            seq.addAnimation(fade); group.addAnimation(seq); anim_refs.extend([seq, fade, op])

        self.scroll.setWidget(grid_widget)

        def _cleanup(): self._anim_refs.clear()
        group.finished.connect(_cleanup); group.start()

    def _clear_scroll(self):
        if self._anim_group is not None:
            try: self._anim_group.stop()
            except Exception: pass
            self._anim_group.deleteLater(); self._anim_group = None
        self._anim_refs = []
        old = self.scroll.takeWidget()
        if old is not None: old.deleteLater()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = HomePage(self.goto_booster, self.goto_decks, QApplication.instance().quit)
        self.boosters = BoosterPage(self.goto_home, self.goto_result_booster)
        self.decks = DecksPage(self.goto_home, self.goto_result_deck_all)
        self.result = ResultPage(self.goto_home)

        self.stack.addWidget(self.home)      # 0
        self.stack.addWidget(self.boosters)  # 1
        self.stack.addWidget(self.decks)     # 2
        self.stack.addWidget(self.result)    # 3

        start_fullscreen_or_maximized(self)

    def goto_booster(self):
        self.stack.setCurrentIndex(1)

    def goto_decks(self):
        self.stack.setCurrentIndex(2)

    def goto_home(self):
        self.stack.setCurrentIndex(0)

    def goto_result_booster(self, source_name: str, super_cards, secret_card):
        self.result.header.title.setText(f"Resultado — {source_name}")
        self.result.show_booster_5(source_name, super_cards, secret_card)
        self.stack.setCurrentIndex(3)

    def goto_result_deck_all(self, deck_name: str, super_cards, secret_cards):
        self.result.header.title.setText(f"Deck — {deck_name}")
        self.result.show_deck_all(deck_name, super_cards, secret_cards)
        self.stack.setCurrentIndex(3)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
