# -*- coding: utf-8 -*-
"""
AeroPKG — PS4-styled Package Viewer.

Dark-mode interface inspired by the PlayStation 4 ecosystem:
  • Deep blue (#003087) → black gradients
  • Glassmorphism (frosted-glass) information panels
  • Animated "Flow" wave background with floating light particles
  • Modern sans-serif typography (Roboto / system fallback)
"""

import math
import os
import random
import sys
from typing import Optional

from PyQt6.QtCore import (
    Qt, QTimer, QRectF, QPointF, pyqtSignal, QUrl
)
from PyQt6.QtGui import (
    QPixmap, QFont, QColor, QPainter, QPainterPath, QLinearGradient,
    QRadialGradient, QBrush, QFontDatabase, QDragEnterEvent,
    QDropEvent, QPaintEvent, QResizeEvent, QPen
)
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QFrame,
    QGraphicsDropShadowEffect, QApplication, QAbstractItemView, QGridLayout
)

from pkg_parser import PKGParser, PKGError, PKGInfo, format_content_type, format_file_size


# ─── Typography ───────────────────────────────────────────────────────────────

# Sony's PS4 uses the "SST" typeface. Roboto is the closest freely-available
# alternative.  We set it as the application-wide default; if unavailable the
# OS sans-serif will be used.
FONT_FAMILY = "Roboto"

def _apply_font(app: QApplication):
    """Set the application font to Roboto (or a similar sans-serif)."""
    # Try loading bundled Roboto if present
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    if os.path.isdir(font_dir):
        for fn in os.listdir(font_dir):
            if fn.lower().endswith(('.ttf', '.otf')):
                QFontDatabase.addApplicationFont(os.path.join(font_dir, fn))

    families = QFontDatabase.families()
    chosen = FONT_FAMILY
    if FONT_FAMILY not in families:
        # Fallbacks close to SST
        for fb in ("Segoe UI", "SF Pro Display", "Helvetica Neue", "Arial"):
            if fb in families:
                chosen = fb
                break

    font = QFont(chosen, 10)
    font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    app.setFont(font)


# ─── PS4 Colour Palette ──────────────────────────────────────────────────────

BG_DARK       = "#060610"             # Near-black base
BG_DEEP_BLUE  = "#003087"             # Sony deep blue
BLUE_ACCENT   = "#0070d1"             # Interactive accent
BLUE_LIGHT    = "#00a2ff"             # Highlight / hover
BLUE_GLOW     = "#0050b0"             # Subtle glow tint

TEXT_PRIMARY   = "#e8eaed"            # Main text (off-white)
TEXT_SECONDARY = "#8b92a5"            # Dimmed labels
TEXT_MUTED     = "#5a6478"            # Very subtle captions

GLASS_BG       = "rgba(8, 12, 28, 0.72)"
GLASS_BORDER   = "rgba(0, 112, 209, 0.25)"
GLASS_HIGHLIGHT = "rgba(0, 162, 255, 0.08)"


# ─── Floating Particle ───────────────────────────────────────────────────────

class _Particle:
    """A tiny light particle drifting upward — PS4-style ambient FX."""
    __slots__ = ('x', 'y', 'r', 'vx', 'vy', 'alpha', 'pulse_offset')

    def __init__(self, w: int, h: int):
        self.x = random.uniform(0, w)
        self.y = random.uniform(h * 0.3, h)
        self.r = random.uniform(1.0, 3.0)
        self.vx = random.uniform(-0.15, 0.15)
        self.vy = random.uniform(-0.35, -0.08)
        self.alpha = random.randint(15, 60)
        self.pulse_offset = random.uniform(0, 6.28)

    def move(self, w: int, h: int):
        self.x += self.vx
        self.y += self.vy
        if self.y + self.r < 0:
            self.__init__(w, h)
            self.y = h + self.r
        if self.x < -10:
            self.x = w + 10
        elif self.x > w + 10:
            self.x = -10


# ─── PS4 "Flow" Wave Background ──────────────────────────────────────────────

class WaveBackground(QWidget):
    """
    Animated background inspired by the PS4 Dynamic Menu ("Flow"):
      • Vertical gradient from deep blue (#003087) → near-black
      • Three layered sine-waves in translucent blue
      • Central radial glow simulating ambient light
      • Floating light particles that drift upwards
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._phase = 0.0
        self._particles: list[_Particle] = []
        self._particles_inited = False

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(40)  # 25 FPS — smooth but light on CPU

    # ── lifecycle ──

    def _ensure_particles(self):
        if not self._particles_inited and self.width() > 0:
            w, h = self.width(), self.height()
            self._particles = [_Particle(w, h) for _ in range(35)]
            self._particles_inited = True

    def _tick(self):
        self._phase += 0.018
        if self._phase > 628.0:
            self._phase = 0.0
        self._ensure_particles()
        w, h = self.width(), self.height()
        for pt in self._particles:
            pt.move(w, h)
        self.update()

    # ── painting ──

    def paintEvent(self, event: QPaintEvent):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # 1. Base gradient: deep blue → near-black
        bg = QLinearGradient(0, 0, 0, h)
        bg.setColorAt(0.0, QColor(0, 24, 68))       # dark navy top
        bg.setColorAt(0.35, QColor(0, 16, 48))
        bg.setColorAt(0.7, QColor(4, 8, 20))
        bg.setColorAt(1.0, QColor(3, 4, 12))         # near-black bottom
        p.fillRect(0, 0, w, h, bg)

        # 2. Central ambient glow (soft blue spotlight)
        glow = QRadialGradient(w * 0.48, h * 0.58, w * 0.52)
        glow.setColorAt(0.0, QColor(0, 48, 135, 38))
        glow.setColorAt(0.5, QColor(0, 30, 90, 15))
        glow.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.fillRect(0, 0, w, h, glow)

        # 3. Accent glow on upper-left (simulates PS4 light bar flare)
        flare = QRadialGradient(w * 0.12, h * 0.10, w * 0.30)
        flare.setColorAt(0.0, QColor(0, 80, 200, 18))
        flare.setColorAt(0.6, QColor(0, 40, 120, 6))
        flare.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.fillRect(0, 0, w, h, flare)

        # 4. Three layered "Flow" waves
        self._draw_wave(p, w, h, amp=30, freq=0.004, speed=0.55,
                        base_frac=0.52, color=QColor(0, 60, 170, 22))
        self._draw_wave(p, w, h, amp=22, freq=0.006, speed=0.85,
                        base_frac=0.64, color=QColor(0, 48, 135, 28))
        self._draw_wave(p, w, h, amp=18, freq=0.009, speed=1.20,
                        base_frac=0.78, color=QColor(0, 35, 100, 18))

        # 5. Floating light particles
        self._ensure_particles()
        for pt in self._particles:
            # Subtle pulsing alpha
            pulse = 0.7 + 0.3 * math.sin(self._phase * 1.5 + pt.pulse_offset)
            alpha = int(pt.alpha * pulse)
            pc = QColor(140, 180, 255, alpha)
            p.setBrush(QBrush(pc))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(pt.x, pt.y), pt.r, pt.r)

            # Tiny glow around each particle
            if pt.r > 1.8:
                halo = QRadialGradient(pt.x, pt.y, pt.r * 3)
                halo.setColorAt(0.0, QColor(100, 160, 255, alpha // 3))
                halo.setColorAt(1.0, QColor(0, 0, 0, 0))
                p.setBrush(QBrush(halo))
                p.drawEllipse(QPointF(pt.x, pt.y), pt.r * 3, pt.r * 3)

        p.end()

    def _draw_wave(self, p: QPainter, w: int, h: int,
                   amp: float, freq: float, speed: float,
                   base_frac: float, color: QColor):
        """Draw a single sine-wave path filled downwards."""
        path = QPainterPath()
        base_y = h * base_frac
        ph = self._phase * speed

        path.moveTo(0, base_y + amp * math.sin(ph))
        step = 6
        for x in range(0, w + step, step):
            y = base_y + amp * math.sin(freq * x + ph)
            path.lineTo(x, y)
        path.lineTo(w, h)
        path.lineTo(0, h)
        path.closeSubpath()

        p.setBrush(QBrush(color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(path)


# ─── Glassmorphism Panel ─────────────────────────────────────────────────────

class GlassPanel(QFrame):
    """
    Frosted-glass panel with:
      • Semi-transparent dark-blue background
      • Subtle blue border
      • Soft blue drop-shadow
    """

    _instance_count = 0

    def __init__(self, parent=None):
        super().__init__(parent)
        GlassPanel._instance_count += 1
        obj = f"glassPanel_{GlassPanel._instance_count}"
        self.setObjectName(obj)
        self.setStyleSheet(f"""
            QFrame#{obj} {{
                background-color: {GLASS_BG};
                border: 1px solid {GLASS_BORDER};
                border-radius: 14px;
            }}
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setColor(QColor(0, 48, 135, 45))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)


# ─── Drop Zone (Drag & Drop) ─────────────────────────────────────────────────

class DropZone(QFrame):
    """Drag-and-drop area for .pkg files — styled to match PS4 UI."""

    file_dropped = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(220)
        self.setObjectName("dropZone")
        self._setup_ui()
        self._set_hover(False)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        self.icon_label = QLabel("📦")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet(
            "font-size: 56px; background:transparent; border:none;"
        )
        layout.addWidget(self.icon_label)

        self.text_label = QLabel("Drop a .pkg file here")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setStyleSheet(
            f"font-size: 18px; font-weight:600; color:{TEXT_PRIMARY}; "
            "background:transparent; border:none;"
        )
        layout.addWidget(self.text_label)

        self.sub_label = QLabel('or use the "Open PKG" button')
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sub_label.setStyleSheet(
            f"font-size: 12px; color:{TEXT_SECONDARY}; "
            "background:transparent; border:none;"
        )
        layout.addWidget(self.sub_label)

    def _set_hover(self, on: bool):
        if on:
            bc = BLUE_ACCENT
            bg = "rgba(0, 70, 180, 0.12)"
        else:
            bc = "rgba(0, 112, 209, 0.25)"
            bg = "rgba(8, 12, 28, 0.40)"
        self.setStyleSheet(
            f"QFrame#dropZone{{"
            f"background:{bg}; border:2px dashed {bc}; border-radius:14px;}}"
        )

    # ── drag events ──

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls() and any(
            u.toLocalFile().lower().endswith('.pkg') for u in e.mimeData().urls()
        ):
            e.acceptProposedAction()
            self._set_hover(True)
        else:
            e.ignore()

    def dragLeaveEvent(self, e):
        self._set_hover(False)

    def dropEvent(self, e: QDropEvent):
        self._set_hover(False)
        for u in e.mimeData().urls():
            fp = u.toLocalFile()
            if fp.lower().endswith('.pkg'):
                self.file_dropped.emit(fp)
                e.acceptProposedAction()
                return
        e.ignore()


# ─── Main Window ─────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    """AeroPKG main window — PS4-ecosystem styled PKG viewer."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FlowPKG")
        self.setMinimumSize(1000, 650)
        self.resize(1200, 750)
        self._parser = PKGParser()

        # Apply Roboto / SST-like font
        _apply_font(QApplication.instance())

        self._setup_ui()
        self._apply_style()
        self.setAcceptDrops(True)

    # ── UI construction ──────────────────────────────────────────────────────

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        central.setObjectName("centralWidget")

        # Animated wave background
        self._wave = WaveBackground(central)

        # Content overlay
        self._overlay = QWidget(central)
        self._overlay.setObjectName("overlay")
        self._overlay.setStyleSheet("background:transparent;")
        root = QVBoxLayout(self._overlay)
        root.setContentsMargins(22, 8, 22, 12)
        root.setSpacing(8)

        # ── Top bar ──
        bar = QWidget()
        bar.setStyleSheet("background:transparent;")
        bar.setFixedHeight(36)
        bar_l = QHBoxLayout(bar)
        bar_l.setContentsMargins(6, 0, 6, 0)

        title = QLabel("✈ FlowPKG")
        title.setStyleSheet(
            f"font-size:16px; font-weight:700; color:{TEXT_PRIMARY}; "
            "background:transparent; letter-spacing:1.2px;"
        )
        bar_l.addWidget(title)
        bar_l.addStretch()

        self._open_btn = QPushButton("📂  Open PKG")
        self._open_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._open_btn.setFixedHeight(30)
        self._open_btn.setStyleSheet(f"""
            QPushButton{{
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 {BLUE_ACCENT}, stop:1 {BG_DEEP_BLUE});
                color:{TEXT_PRIMARY}; font-size:12px; font-weight:600;
                padding:4px 18px; border:1px solid rgba(0,162,255,0.30);
                border-radius:8px; letter-spacing:0.5px;
            }}
            QPushButton:hover{{
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                    stop:0 {BLUE_LIGHT}, stop:1 {BLUE_ACCENT});
                border:1px solid rgba(0,162,255,0.55);
            }}
            QPushButton:pressed{{
                background: {BG_DEEP_BLUE};
                border:1px solid rgba(0,162,255,0.20);
            }}
        """)
        self._open_btn.clicked.connect(self._open_dialog)
        bar_l.addWidget(self._open_btn)
        root.addWidget(bar)

        # ── Drop zone (initial state) ──
        self._drop = DropZone()
        self._drop.file_dropped.connect(self._load_pkg)
        root.addWidget(self._drop, 1)

        # ── Data container (hidden until a file is loaded) ──
        self._data_w = QWidget()
        self._data_w.setStyleSheet("background:transparent;")
        self._data_w.setVisible(False)
        data_root = QHBoxLayout(self._data_w)
        data_root.setContentsMargins(0, 0, 0, 0)
        data_root.setSpacing(14)

        # ── LEFT PANEL: icon + game info ──
        left_panel = GlassPanel()
        left_l = QVBoxLayout(left_panel)
        left_l.setContentsMargins(18, 16, 18, 16)
        left_l.setSpacing(10)

        # Game icon — large, prominent
        self._icon_frame = QFrame()
        self._icon_frame.setFixedSize(420, 420)
        self._icon_frame.setStyleSheet(
            f"QFrame{{"
            f"background:rgba(0, 18, 50, 0.55);"
            f"border:2px solid {GLASS_BORDER}; border-radius:16px;}}"
        )
        if_l = QVBoxLayout(self._icon_frame)
        if_l.setContentsMargins(6, 6, 6, 6)
        if_l.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._icon = QLabel("🎮")
        self._icon.setFixedSize(404, 404)
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon.setStyleSheet(
            "font-size:64px; background:transparent; border:none;"
        )
        if_l.addWidget(self._icon)
        left_l.addWidget(self._icon_frame, 0, Qt.AlignmentFlag.AlignHCenter)

        # Game title
        self._lbl_title = QLabel("—")
        self._lbl_title.setWordWrap(True)
        self._lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_title.setStyleSheet(
            f"font-size:26px; font-weight:700; color:{TEXT_PRIMARY}; "
            "background:transparent; border:none; letter-spacing:0.6px;"
        )
        left_l.addWidget(self._lbl_title)

        # Badges row: FPKG/Retail + category
        self._badge_row = QHBoxLayout()
        self._badge_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge_row.setSpacing(8)

        self._badge_type = QLabel("PKG")
        self._badge_type.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge_type.setFixedHeight(26)
        self._badge_type.setStyleSheet(
            f"font-size:11px; font-weight:700; color:#fff; "
            f"background:{BG_DEEP_BLUE}; border-radius:6px; "
            f"padding:3px 14px; border:none; letter-spacing:0.4px;"
        )
        self._badge_row.addWidget(self._badge_type)

        self._badge_cat = QLabel("Game")
        self._badge_cat.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge_cat.setFixedHeight(26)
        self._badge_cat.setStyleSheet(
            f"font-size:11px; font-weight:700; color:{BLUE_LIGHT}; "
            f"background:rgba(0,80,176,0.18); border-radius:6px; "
            f"padding:3px 14px; border:1px solid rgba(0,162,255,0.25); "
            f"letter-spacing:0.4px;"
        )
        self._badge_row.addWidget(self._badge_cat)

        left_l.addLayout(self._badge_row)

        # Essential info fields
        info_grid = QGridLayout()
        info_grid.setSpacing(5)
        info_grid.setColumnMinimumWidth(0, 110)

        self._fields = {}
        for row, (label, key) in enumerate([
            ("Content ID", "cid"),
            ("Region",     "region"),
            ("Version",    "version"),
            ("Firmware",   "firmware"),
            ("Size",       "size"),
        ]):
            kl = QLabel(label.upper())
            kl.setStyleSheet(
                f"font-size:10px; font-weight:700; color:{TEXT_SECONDARY}; "
                "background:transparent; border:none; letter-spacing:1.2px;"
            )
            info_grid.addWidget(kl, row, 0)

            vl = QLabel("—")
            vl.setStyleSheet(
                f"font-size:13px; font-weight:500; color:{TEXT_PRIMARY}; "
                "background:rgba(0,48,135,0.12); border:none; "
                "border-radius:5px; padding:4px 10px;"
            )
            info_grid.addWidget(vl, row, 1)
            self._fields[key] = vl

        left_l.addLayout(info_grid)
        left_l.addStretch()

        data_root.addWidget(left_panel, 5)

        # ── RIGHT PANEL: SFO parameters table ──
        right_panel = GlassPanel()
        right_l = QVBoxLayout(right_panel)
        right_l.setContentsMargins(14, 12, 14, 12)
        right_l.setSpacing(6)

        tbl_title = QLabel("⚙  Parameters")
        tbl_title.setStyleSheet(
            f"font-size:14px; font-weight:700; color:{TEXT_PRIMARY}; "
            "background:transparent; border:none; letter-spacing:0.6px;"
        )
        right_l.addWidget(tbl_title)

        self._table = QTableWidget()
        self._table.setColumnCount(2)
        self._table.setHorizontalHeaderLabels(["Parameter", "Value"])
        self._table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self._table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self._table.verticalHeader().setVisible(False)
        self._table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self._table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self._table.setAlternatingRowColors(True)
        self._table.setShowGrid(False)
        self._table.setStyleSheet(f"""
            QTableWidget{{
                background-color: rgba(6, 10, 22, 0.65);
                border: 1px solid rgba(0, 112, 209, 0.12);
                border-radius: 8px;
                color: {TEXT_PRIMARY};
                font-size: 12px;
            }}
            QTableWidget::item{{
                padding: 5px 10px;
                border-bottom: 1px solid rgba(0, 112, 209, 0.06);
            }}
            QTableWidget::item:alternate{{
                background-color: rgba(0, 48, 135, 0.07);
            }}
            QTableWidget::item:selected{{
                background-color: rgba(0, 112, 209, 0.18);
                color: {TEXT_PRIMARY};
            }}
            QHeaderView::section{{
                background: rgba(0, 48, 135, 0.45);
                color: {BLUE_LIGHT};
                font-size: 11px;
                font-weight: 700;
                padding: 6px 10px;
                border: none;
                border-bottom: 2px solid {BLUE_ACCENT};
                letter-spacing: 0.5px;
            }}
            QScrollBar:vertical {{
                background: rgba(0,0,0,0.15);
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(0,112,209,0.3);
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: rgba(0,112,209,0.5);
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        right_l.addWidget(self._table, 1)

        data_root.addWidget(right_panel, 4)

        root.addWidget(self._data_w, 1)

        # State
        self._all_params = {}

    # ── Global Stylesheet ────────────────────────────────────────────────────

    def _apply_style(self):
        self.setStyleSheet(f"""
            QMainWindow{{background:{BG_DARK};}}
            QWidget#centralWidget{{background:transparent;}}
            QWidget#overlay{{background:transparent;}}
            QToolTip{{
                background:rgba(8,12,28,0.92);
                color:{TEXT_PRIMARY};
                border:1px solid rgba(0,112,209,0.3);
                border-radius:4px; padding:4px 8px;
                font-size:11px;
            }}
        """)

    # ── Resize ───────────────────────────────────────────────────────────────

    def resizeEvent(self, e: QResizeEvent):
        super().resizeEvent(e)
        if hasattr(self, '_wave'):
            self._wave.setGeometry(0, 0, self.width(), self.height())
        if hasattr(self, '_overlay'):
            self._overlay.setGeometry(0, 0, self.width(), self.height())

    # ── Drag & Drop (window level) ───────────────────────────────────────────

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls() and any(
            u.toLocalFile().lower().endswith('.pkg') for u in e.mimeData().urls()
        ):
            e.acceptProposedAction()
        else:
            e.ignore()

    def dropEvent(self, e: QDropEvent):
        for u in e.mimeData().urls():
            fp = u.toLocalFile()
            if fp.lower().endswith('.pkg'):
                self._load_pkg(fp)
                e.acceptProposedAction()
                return
        e.ignore()

    # ── Actions ──────────────────────────────────────────────────────────────

    def _open_dialog(self):
        fp, _ = QFileDialog.getOpenFileName(
            self, "Open a PS4 PKG", "", "PKG (*.pkg);;All (*)"
        )
        if fp:
            self._load_pkg(fp)

    def _load_pkg(self, path: str):
        try:
            info = self._parser.parse(path)
            self._display(info)
        except PKGError as e:
            self._show_error(str(e))
        except Exception as e:
            self._show_error(f"Error: {e}")

    # ── Display PKG info ─────────────────────────────────────────────────────

    def _display(self, info: PKGInfo):
        self._drop.setVisible(False)
        self._data_w.setVisible(True)

        # Icon
        if info.icon_data:
            px = QPixmap()
            if px.loadFromData(info.icon_data):
                rounded = self._round_pixmap(px.scaled(
                    404, 404,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ), 14)
                self._icon.setPixmap(rounded)
                self._icon.setStyleSheet("background:transparent; border:none;")
            else:
                self._icon.setText("🎮")
                self._icon.setStyleSheet(
                    "font-size:64px; background:transparent; border:none;"
                )
        else:
            self._icon.setText("🎮")
            self._icon.setStyleSheet(
                "font-size:64px; background:transparent; border:none;"
            )

        # Title
        self._lbl_title.setText(info.title or "Unknown title")

        # Badges
        self._badge_type.setText("FPKG" if info.is_fake_pkg else "Retail PKG")
        if info.is_fake_pkg:
            self._badge_type.setStyleSheet(
                "font-size:11px; font-weight:700; color:#ff9800; "
                "background:rgba(255,152,0,0.12); border-radius:6px; "
                "padding:3px 14px; border:1px solid rgba(255,152,0,0.30); "
                "letter-spacing:0.4px;"
            )
        else:
            self._badge_type.setStyleSheet(
                f"font-size:11px; font-weight:700; color:#fff; "
                f"background:{BG_DEEP_BLUE}; border-radius:6px; "
                f"padding:3px 14px; border:none; letter-spacing:0.4px;"
            )

        self._badge_cat.setText(info.category_name or info.category or "—")

        # Info fields
        self._fields["cid"].setText(info.content_id or "—")
        self._fields["region"].setText(info.region or "—")
        self._fields["version"].setText(info.app_version or "—")
        self._fields["firmware"].setText(info.firmware_version or "—")
        self._fields["size"].setText(format_file_size(info.file_size))

        # SFO parameters table
        self._all_params = info.sfo_params
        self._refresh_table()

    def _refresh_table(self):
        """Fill the table with all SFO parameters."""
        keys = sorted(self._all_params.keys())
        self._table.setRowCount(len(keys))
        self._table.verticalHeader().setDefaultSectionSize(30)

        for row, key in enumerate(keys):
            val = self._all_params[key]

            ki = QTableWidgetItem(key)
            ki.setFont(QFont("Consolas", 10))
            ki.setForeground(QColor(BLUE_LIGHT))
            self._table.setItem(row, 0, ki)

            if isinstance(val, int):
                disp = f"{val}  (0x{val:08X})"
            else:
                disp = str(val)

            vi = QTableWidgetItem(disp)
            vi.setFont(QFont("Consolas", 10))
            vi.setForeground(QColor(TEXT_PRIMARY))
            self._table.setItem(row, 1, vi)

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _round_pixmap(pixmap: QPixmap, radius: int) -> QPixmap:
        rounded = QPixmap(pixmap.size())
        rounded.fill(Qt.GlobalColor.transparent)
        p = QPainter(rounded)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(pixmap.rect()), radius, radius)
        p.setClipPath(path)
        p.drawPixmap(0, 0, pixmap)
        p.end()
        return rounded

    def _show_error(self, msg: str):
        self._drop.setVisible(True)
        self._data_w.setVisible(False)
        self._drop.icon_label.setText("⚠️")
        self._drop.text_label.setText("Read Error")
        self._drop.text_label.setStyleSheet(
            "font-size:18px; font-weight:600; color:#ef5350; "
            "background:transparent; border:none;"
        )
        self._drop.sub_label.setText(msg)
        QTimer.singleShot(4000, self._reset_drop)

    def _reset_drop(self):
        self._drop.icon_label.setText("📦")
        self._drop.text_label.setText("Drop a .pkg file here")
        self._drop.text_label.setStyleSheet(
            f"font-size:18px; font-weight:600; color:{TEXT_PRIMARY}; "
            "background:transparent; border:none;"
        )
        self._drop.sub_label.setText('or use the "Open PKG" button')
