import sys
import random
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QGridLayout, QMessageBox,
    QLabel, QScrollArea, QStackedWidget, QHBoxLayout, QFrame,
    QGraphicsDropShadowEffect, QGraphicsOpacityEffect
)
from PyQt6.QtGui import QPalette, QColor, QIcon, QPixmap, QFont
from PyQt6.QtCore import Qt, QSize, QEasingCurve, QPropertyAnimation, QParallelAnimationGroup, QPauseAnimation, QSequentialAnimationGroup, QObject, pyqtProperty

APP_TITLE = "Simulador de Boosters YGO"
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
            return (1, stem)
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
    def __init__(self, goto_booster, close_app):
        super().__init__()
        make_black_background(self)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(16)

        header = Header("Simulador de Boosters YGO")
        root.addWidget(header)

        center = QVBoxLayout()
        center.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_abrir = StyledButton("Abrir Booster")
        btn_abrir.setFixedSize(260, 64)
        btn_abrir.clicked.connect(goto_booster)

        btn_fechar = StyledButton("Fechar")
        btn_fechar.setFixedSize(260, 64)
        btn_fechar.clicked.connect(close_app)

        center.addWidget(btn_abrir)
        center.addSpacing(16)
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
            warn = QLabel("Pasta 'capa' não encontrada.\nColoque RPG_Series_1..15.*")
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

    def abrir_pacote(self, booster_name: str):
        try:
            super_dir = self.cards_dir / booster_name / "super raras"
            secret_dir = self.cards_dir / booster_name / "secretas raras"
            super_cards = list_images(super_dir)
            secret_cards = list_images(secret_dir)
            if len(super_cards) < 4 or len(secret_cards) < 1:
                QMessageBox.warning(self, "Cartas insuficientes",
                                    f"Precisa de 4 'super raras' e 1 'secretas raras' em:\n{super_dir}\n{secret_dir}")
                return
            chosen_super = random.sample(super_cards, 4)
            chosen_secret = random.choice(secret_cards)
            self.go_result(booster_name, chosen_super, chosen_secret)
        except Exception as e:
            QMessageBox.critical(self, "Erro ao abrir booster", str(e))

# -------- Helper para zoom animado (QObject com propriedade animável) --------
class ZoomDriver(QObject):
    def __init__(self, label: QLabel, base_pixmap: QPixmap, target_w: int, target_h: int, start_factor: float = 0.92):
        super().__init__()
        self._factor = start_factor
        self.label = label
        self.base = base_pixmap
        self.w = target_w
        self.h = target_h
        self.label.setFixedSize(target_w, target_h)  # área fixa; evita "sumir"
        self._update()

    def _update(self):
        if self.base.isNull():
            return
        scaled = self.base.scaled(int(self.w * self._factor), int(self.h * self._factor),
                                  Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.label.setPixmap(scaled)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def getFactor(self) -> float:
        return self._factor

    def setFactor(self, value: float):
        self._factor = float(value)
        self._update()

    factor = pyqtProperty(float, fget=getFactor, fset=setFactor)

class ResultPage(QWidget):
    def __init__(self, go_back_to_boosters):
        super().__init__()
        make_black_background(self)
        self.go_back_to_boosters = go_back_to_boosters

        self._anim_group = None
        self._anim_refs = []  # guarda refs de animação e drivers

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        root.addWidget(Header("Cartas Abertas"))

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        root.addWidget(self.scroll, stretch=1)

        footer = QHBoxLayout()
        self.btn_voltar = StyledButton("Voltar para seleção")
        self.btn_voltar.setFixedSize(220, 52)
        self.btn_voltar.clicked.connect(self.go_back_to_boosters)
        footer.addStretch(1)
        self.rarity_font = QFont()
        self.rarity_font.setPointSize(14)
        self.rarity_font.setBold(True)
        footer.addWidget(self.btn_voltar, alignment=Qt.AlignmentFlag.AlignCenter)
        footer.addStretch(1)
        root.addLayout(footer)

    def _rarity_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"color:{FG}; font-size: 16px; font-weight: 600;")
        return lbl

    def _card_widget(self, img_path: Path, glow_color: str | None, rarity_text: str, card_w=300, card_h=430):
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 0, 0, 0)

        img = QLabel()
        img.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if glow_color is not None:
            make_glow(img, color=glow_color)

        pix = QPixmap(str(img_path))
        if not pix.isNull():
            pix = pix.scaled(card_w, card_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            img.setPixmap(pix)
        else:
            img.setText(f"Falha {img_path.name}")
            img.setStyleSheet(f"color:{FG};")

        v.addWidget(img, alignment=Qt.AlignmentFlag.AlignCenter)
        v.addSpacing(6)
        v.addWidget(self._rarity_label(rarity_text), alignment=Qt.AlignmentFlag.AlignCenter)

        op = QGraphicsOpacityEffect(container)
        container.setGraphicsEffect(op)
        op.setOpacity(0.0)

        return container, op

    def _secret_widget_with_zoom(self, img_path: Path, rarity_text: str = "Secret Rare", card_w=300, card_h=430):
        """Sem borda e sem glow; fade + zoom sutil e área fixa para evitar sumiço; com label de raridade."""
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 0, 0, 0)

        img = QLabel()
        img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        img.setFixedSize(card_w, card_h)  # fixa área da secreta

        pix = QPixmap(str(img_path))
        if pix.isNull():
            img.setText(f"Falha {img_path.name}")
            img.setStyleSheet(f"color:{FG};")
            driver = None
        else:
            driver = ZoomDriver(img, pix, card_w, card_h, start_factor=0.92)

        v.addWidget(img, alignment=Qt.AlignmentFlag.AlignCenter)
        v.addSpacing(6)
        v.addWidget(self._rarity_label(rarity_text), alignment=Qt.AlignmentFlag.AlignCenter)

        op = QGraphicsOpacityEffect(container)
        container.setGraphicsEffect(op)
        op.setOpacity(0.0)

        return container, op, driver

    def show_results(self, booster_name: str, super_cards, secret_card):
        # limpar widget antigo do scroll
        old = self.scroll.takeWidget()
        if old is not None:
            old.deleteLater()

        self._anim_group = QParallelAnimationGroup(self)
        self._anim_refs = []

        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setSpacing(24)
        row_layout.setContentsMargins(40, 24, 40, 24)
        row_layout.addStretch(1)

        # tempos MAIS LENTOS
        pause_step = 480
        dur_super = 1800
        dur_secret = 2400

        # super raras (glow + fade) + "Super Rare"
        for idx, p in enumerate(super_cards):
            container, op_effect = self._card_widget(p, glow_color="#cccccc", rarity_text="Super Rare")
            row_layout.addWidget(container)

            seq = QSequentialAnimationGroup(self)
            seq.addAnimation(QPauseAnimation(idx * pause_step, self))
            anim = QPropertyAnimation(op_effect, b"opacity", self)
            anim.setDuration(dur_super)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            seq.addAnimation(anim)

            self._anim_group.addAnimation(seq)
            self._anim_refs.extend([seq, anim, op_effect])

        # secreta: SEM borda, SEM glow; fade + zoom sutil + "Secret Rare"
        container, op_effect, driver = self._secret_widget_with_zoom(secret_card, rarity_text="Secret Rare")
        row_layout.addWidget(container)

        seq = QSequentialAnimationGroup(self)
        seq.addAnimation(QPauseAnimation(4 * pause_step, self))

        fade = QPropertyAnimation(op_effect, b"opacity", self)
        fade.setDuration(dur_secret)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.Type.OutCubic)

        pair = QParallelAnimationGroup(self)
        pair.addAnimation(fade)

        if driver is not None:
            zoom = QPropertyAnimation(driver, b"factor", self)
            zoom.setDuration(dur_secret)
            zoom.setStartValue(0.92)
            zoom.setEndValue(1.0)
            zoom.setEasingCurve(QEasingCurve.Type.OutCubic)
            pair.addAnimation(zoom)
            self._anim_refs.append(driver)  # manter driver vivo

        seq.addAnimation(pair)

        self._anim_group.addAnimation(seq)
        self._anim_refs.extend([seq, pair, fade])

        row_layout.addStretch(1)

        wrapper = QWidget()
        wrapper_layout = QHBoxLayout(wrapper)
        wrapper_layout.addWidget(row_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(wrapper)

        self._anim_group.start()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home = HomePage(self.goto_booster, QApplication.instance().quit)
        self.boosters = BoosterPage(self.goto_home, self.goto_result)
        self.result = ResultPage(self.goto_boosters_from_result)

        self.stack.addWidget(self.home)      # 0
        self.stack.addWidget(self.boosters)  # 1
        self.stack.addWidget(self.result)    # 2

        start_fullscreen_or_maximized(self)

    def goto_booster(self):
        self.stack.setCurrentIndex(1)

    def goto_home(self):
        self.stack.setCurrentIndex(0)

    def goto_result(self, booster_name: str, super_cards, secret_card):
        self.result.show_results(booster_name, super_cards, secret_card)
        self.stack.setCurrentIndex(2)

    def goto_boosters_from_result(self):
        self.stack.setCurrentIndex(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
