"""Design System centralizado para Controle de Obras.

Paleta de cores, tipografia, espaçamentos e estilos reutilizáveis
para manter consistência visual em todas as telas.
"""

# ==================== PALETA DE CORES ====================
# Azul-marinho institucional, branco, cinza claro
# Verde para positivo, vermelho para alerta, azul para info

PRIMARY = "#1B2A4A"
PRIMARY_HOVER = "#243656"
PRIMARY_PRESSED = "#152238"

BACKGROUND = "#F5F7FA"
SURFACE = "#FFFFFF"
SURFACE_ALT = "#F8FAFC"

BORDER = "#E2E8F0"
BORDER_LIGHT = "#F1F5F9"

TEXT_PRIMARY = "#1E293B"
TEXT_SECONDARY = "#64748B"
TEXT_MUTED = "#94A3B8"

SUCCESS = "#16A34A"
SUCCESS_HOVER = "#15803D"
SUCCESS_LIGHT = "#F0FDF4"

WARNING = "#D97706"
WARNING_HOVER = "#B45309"
WARNING_LIGHT = "#FFFBEB"

DANGER = "#DC2626"
DANGER_HOVER = "#B91C1C"
DANGER_LIGHT = "#FEF2F2"

INFO = "#2563EB"
INFO_HOVER = "#1D4ED8"
INFO_LIGHT = "#EFF6FF"

BROWN = "#92400E"
BROWN_HOVER = "#78350F"

DARK_GREEN = "#15803D"
DARK_GREEN_HOVER = "#166534"


# ==================== ESCALA TIPOGRÁFICA ====================

FONT_FAMILY = "Segoe UI, Arial, sans-serif"

TYPOGRAPHY = {
    "screen_title": {"size": "20px", "weight": "700", "color": TEXT_PRIMARY},
    "subtitle": {"size": "14px", "weight": "400", "color": TEXT_SECONDARY},
    "card_title": {"size": "11px", "weight": "600", "color": TEXT_SECONDARY},
    "card_value": {"size": "22px", "weight": "700", "color": TEXT_PRIMARY},
    "table_header": {"size": "12px", "weight": "600", "color": SURFACE},
    "table_cell": {"size": "13px", "weight": "400", "color": TEXT_PRIMARY},
    "button": {"size": "13px", "weight": "600", "color": SURFACE},
    "label": {"size": "12px", "weight": "500", "color": TEXT_SECONDARY},
    "input": {"size": "13px", "weight": "400", "color": TEXT_PRIMARY},
    "small": {"size": "11px", "weight": "400", "color": TEXT_MUTED},
}


# ==================== ESCALA DE ESPAÇAMENTO ====================

SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "12px",
    "lg": "16px",
    "xl": "24px",
    "xxl": "32px",
}


# ==================== BORDAS E RAIOS ====================

RADIUS = {
    "small": "4px",
    "medium": "6px",
    "large": "8px",
    "xl": "12px",
}

SHADOW = {
    "none": "none",
    "sm": "0 1px 2px rgba(0, 0, 0, 0.05)",
    "md": "0 1px 3px rgba(0, 0, 0, 0.1)",
    "lg": "0 4px 6px rgba(0, 0, 0, 0.1)",
}


# ==================== ESTILOS DE COMPONENTES ====================

def get_header_style():
    """Estilo do cabeçalho principal."""
    return f"""
        QWidget {{
            background-color: {PRIMARY};
            color: {SURFACE};
        }}
    """


def get_header_button_style():
    """Estilo dos botões do cabeçalho."""
    return f"""
        QPushButton {{
            min-height: 30px;
            padding: 4px 14px;
            background-color: rgba(255, 255, 255, 0.1);
            color: {SURFACE};
            border: none;
            border-radius: {RADIUS['medium']};
            font-size: {TYPOGRAPHY['button']['size']};
            font-weight: {TYPOGRAPHY['button']['weight']};
        }}
        QPushButton:hover {{
            background-color: rgba(255, 255, 255, 0.2);
        }}
        QPushButton:pressed {{
            background-color: rgba(255, 255, 255, 0.15);
        }}
    """


def get_combo_header_style():
    """Estilo do combo de obras no cabeçalho."""
    return f"""
        QComboBox {{
            min-height: 30px;
            padding: 4px 10px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: {RADIUS['medium']};
            background-color: rgba(255, 255, 255, 0.1);
            color: {SURFACE};
            font-size: {TYPOGRAPHY['input']['size']};
            font-weight: 600;
            min-width: 250px;
        }}
        QComboBox:hover {{
            border-color: rgba(255, 255, 255, 0.5);
        }}
        QComboBox::drop-down {{
            border: none;
            padding-right: 8px;
        }}
    """


def get_primary_button_style():
    """Estilo do botão primário (ação principal)."""
    return f"""
        QPushButton {{
            padding: 8px 16px;
            background-color: {PRIMARY};
            color: {SURFACE};
            border: none;
            border-radius: {RADIUS['medium']};
            font-size: {TYPOGRAPHY['button']['size']};
            font-weight: {TYPOGRAPHY['button']['weight']};
        }}
        QPushButton:hover {{
            background-color: {PRIMARY_HOVER};
        }}
        QPushButton:pressed {{
            background-color: {PRIMARY_PRESSED};
        }}
    """


def get_success_button_style():
    """Estilo do botão de sucesso (salvar, confirmar)."""
    return f"""
        QPushButton {{
            padding: 8px 16px;
            background-color: {SUCCESS};
            color: {SURFACE};
            border: none;
            border-radius: {RADIUS['medium']};
            font-size: {TYPOGRAPHY['button']['size']};
            font-weight: {TYPOGRAPHY['button']['weight']};
        }}
        QPushButton:hover {{
            background-color: {SUCCESS_HOVER};
        }}
    """


def get_secondary_button_style():
    """Estilo do botão secundário."""
    return f"""
        QPushButton {{
            padding: 8px 16px;
            background-color: {SURFACE};
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER};
            border-radius: {RADIUS['medium']};
            font-size: {TYPOGRAPHY['button']['size']};
            font-weight: {TYPOGRAPHY['button']['weight']};
        }}
        QPushButton:hover {{
            background-color: {BORDER_LIGHT};
        }}
    """


def get_action_button_style(color, hover_color):
    """Estilo genérico para botões de ação coloridos com efeito 3D discreto."""
    return f"""
        QPushButton {{
            padding: 8px 18px;
            background-color: {color};
            color: {SURFACE};
            border: 1px solid rgba(0, 0, 0, 35%);
            border-top-color: rgba(255, 255, 255, 45%);
            border-bottom-color: rgba(0, 0, 0, 45%);
            border-radius: 7px;
            font-size: {TYPOGRAPHY['button']['size']};
            font-weight: 600;
            min-width: 90px;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
            border-top-color: rgba(255, 255, 255, 75%);
        }}
        QPushButton:pressed {{
            padding-top: 10px;
            padding-bottom: 6px;
            border-top-color: rgba(0, 0, 0, 45%);
            border-bottom-color: rgba(255, 255, 255, 35%);
        }}
    """


def get_table_style(header_color=PRIMARY):
    """Estilo base para tabelas."""
    return f"""
        QTableWidget {{
            background-color: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: {RADIUS['large']};
            gridline-color: {BORDER_LIGHT};
            font-size: {TYPOGRAPHY['table_cell']['size']};
            selection-background-color: #DCEBFA;
            selection-color: #163A5F;
            alternate-background-color: #F8FAFC;
            outline: none;
        }}
        QTableWidget::item {{
            padding: 10px 12px;
            border-bottom: 1px solid {BORDER_LIGHT};
            border: none;
            outline: none;
        }}
        QTableWidget::item:selected {{
            background-color: #DCEBFA;
            color: #163A5F;
            border: none;
            outline: none;
        }}
        QTableWidget::item:selected:active {{
            background-color: #C7DDF4;
            color: #163A5F;
            border: none;
            outline: none;
        }}
        QTableWidget::item:selected:!active {{
            background-color: #E5EEF8;
            color: #334E68;
            border: none;
            outline: none;
        }}
        QTableWidget::item:focus {{
            border: none;
            outline: none;
        }}
        QTableWidget::item:selected:focus {{
            background-color: #DCEBFA;
            color: #163A5F;
            border: none;
            outline: none;
        }}
        QTableWidget::item:hover {{
            background-color: #F1F5F9;
            color: #1F2937;
        }}
        QHeaderView::section {{
            background-color: {header_color};
            color: {SURFACE};
            font-weight: {TYPOGRAPHY['table_header']['weight']};
            font-size: {TYPOGRAPHY['table_header']['size']};
            padding: 10px 12px;
            border: none;
            border-right: 1px solid rgba(255, 255, 255, 0.1);
            border-bottom: 2px solid rgba(255, 255, 255, 0.15);
        }}
        QHeaderView::section:last {{
            border-right: none;
        }}
    """


def get_card_style(border_color=None):
    """Estilo base para cards."""
    border_left = f"border-left: 4px solid {border_color};" if border_color else ""
    return f"""
        QFrame {{
            background-color: {SURFACE};
            border: 1px solid {BORDER};
            border-radius: {RADIUS['xl']};
            {border_left}
        }}
        QFrame:hover {{
            border-color: {BORDER};
            border-left-width: 5px;
        }}
    """


def get_input_style():
    """Estilo base para inputs e combos."""
    return f"""
        QLineEdit, QDateEdit, QComboBox {{
            padding: 8px 10px;
            border: 1px solid {BORDER};
            border-radius: {RADIUS['medium']};
            background-color: {SURFACE};
            color: {TEXT_PRIMARY};
            font-size: {TYPOGRAPHY['input']['size']};
            min-height: 28px;
        }}
        QLineEdit:focus, QDateEdit:focus, QComboBox:focus {{
            border-color: {INFO};
        }}
        QLineEdit:hover, QDateEdit:hover, QComboBox:hover {{
            border-color: {TEXT_MUTED};
        }}
    """


def get_form_label_style():
    """Estilo para labels de formulário."""
    return f"""
        QLabel {{
            font-size: {TYPOGRAPHY['label']['size']};
            font-weight: {TYPOGRAPHY['label']['weight']};
            color: {TEXT_SECONDARY};
            padding: 0;
        }}
    """


def get_screen_title_style():
    """Estilo para títulos de tela."""
    return f"""
        QLabel {{
            font-size: {TYPOGRAPHY['screen_title']['size']};
            font-weight: {TYPOGRAPHY['screen_title']['weight']};
            color: {TEXT_PRIMARY};
        }}
    """


# ==================== UTILITÁRIOS ====================

def centered_label(text, style=""):
    """Helper para criar label centralizado."""
    return f"""
        QLabel {{
            text-align: center;
            {style}
        }}
    """
