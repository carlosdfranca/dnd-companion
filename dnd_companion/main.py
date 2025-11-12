# main.py
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition

from controllers.db_manager import inicializar_banco, conectar
from controllers.calculator import calcular_bonus_pericia
from models.personagem import Personagem
from models.pericia import Pericia

def _to_int(value, default=0):
    try:
        if value is None or str(value).strip() == "":
            return default
        return int(str(value).strip())
    except Exception:
        return default


# ----------------------------------------------------
# Tela principal (ficha básica)
# ----------------------------------------------------
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation="vertical", padding=16, spacing=8)

        layout.add_widget(Label(text="🎲 D&D Companion", font_size="24sp", bold=True, size_hint=(1, 0.1)))
        layout.add_widget(Label(text="Ficha do Personagem", font_size="16sp", size_hint=(1, 0.07)))

        form = GridLayout(cols=2, spacing=6, size_hint=(1, 0.65))
        self.nome = TextInput(multiline=False)
        self.classe = TextInput(multiline=False)
        self.nivel = TextInput(multiline=False, input_filter="int")
        self.ca = TextInput(multiline=False, input_filter="int")
        self.hp_max = TextInput(multiline=False, input_filter="int")
        self.hp_atual = TextInput(multiline=False, input_filter="int")
        self.forca = TextInput(multiline=False, input_filter="int")
        self.destreza = TextInput(multiline=False, input_filter="int")
        self.constituicao = TextInput(multiline=False, input_filter="int")
        self.inteligencia = TextInput(multiline=False, input_filter="int")
        self.sabedoria = TextInput(multiline=False, input_filter="int")
        self.carisma = TextInput(multiline=False, input_filter="int")

        campos = [
            ("Nome:", self.nome), ("Classe:", self.classe), ("Nível:", self.nivel),
            ("CA:", self.ca), ("HP Máx.:", self.hp_max), ("HP Atual:", self.hp_atual),
            ("FOR:", self.forca), ("DES:", self.destreza), ("CON:", self.constituicao),
            ("INT:", self.inteligencia), ("SAB:", self.sabedoria), ("CAR:", self.carisma)
        ]
        for label, widget in campos:
            form.add_widget(Label(text=label))
            form.add_widget(widget)
        layout.add_widget(form)

        botoes = BoxLayout(orientation="horizontal", spacing=10, size_hint=(1, 0.1))
        btn_salvar = Button(text="💾 Salvar", on_press=self.on_salvar)
        btn_pericias = Button(text="🎯 Ver Perícias", on_press=self.ver_pericias)
        botoes.add_widget(btn_pericias)
        botoes.add_widget(btn_salvar)
        layout.add_widget(botoes)

        self.add_widget(layout)
        self.carregar_personagem()

    def carregar_personagem(self):
        conn = conectar()
        try:
            p = Personagem.carregar(conn, 1)
        finally:
            conn.close()
        self.personagem = p

        campos = {
            self.nome: p.nome,
            self.classe: p.classe,
            self.nivel: p.nivel,
            self.ca: p.ca,
            self.hp_max: p.hp_max,
            self.hp_atual: p.hp_atual,
            self.forca: p.forca,
            self.destreza: p.destreza,
            self.constituicao: p.constituicao,
            self.inteligencia: p.inteligencia,
            self.sabedoria: p.sabedoria,
            self.carisma: p.carisma
        }
        for campo, valor in campos.items():
            campo.text = str(valor or "")

    def on_salvar(self, *_):
        conn = conectar()
        try:
            p = Personagem(
                id=1,
                nome=self.nome.text.strip(),
                classe=self.classe.text.strip(),
                nivel=_to_int(self.nivel.text, 1),
                ca=_to_int(self.ca.text, 10),
                hp_max=_to_int(self.hp_max.text, 10),
                hp_atual=_to_int(self.hp_atual.text, 10),
                forca=_to_int(self.forca.text, 10),
                destreza=_to_int(self.destreza.text, 10),
                constituicao=_to_int(self.constituicao.text, 10),
                inteligencia=_to_int(self.inteligencia.text, 10),
                sabedoria=_to_int(self.sabedoria.text, 10),
                carisma=_to_int(self.carisma.text, 10),
            )
            p.salvar(conn)
            self.personagem = p
        finally:
            conn.close()
        print("✅ Personagem salvo!")

    def ver_pericias(self, *_):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "pericias"


# ----------------------------------------------------
# Tela de perícias
# ----------------------------------------------------
class PericiasScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=16, spacing=10)
        self.add_widget(self.layout)

    def on_pre_enter(self):
        self.layout.clear_widgets()
        conn = conectar()
        pericias = Pericia.listar(conn)
        personagem = Personagem.carregar(conn)
        conn.close()

        self.layout.add_widget(Label(text=f"🎯 Perícias de {personagem.nome}", font_size="20sp", bold=True, size_hint=(1, 0.1)))

        scroll = ScrollView(size_hint=(1, 0.8))
        container = GridLayout(cols=2, spacing=6, size_hint_y=None)
        container.bind(minimum_height=container.setter("height"))

        for pericia in pericias:
            bonus = calcular_bonus_pericia(pericia, personagem)
            label_nome = Label(text=f"{pericia.nome} ({pericia.atributo_base})", size_hint_y=None, height=40)
            label_bonus = Label(text=f"{'+' if bonus>=0 else ''}{bonus}", size_hint_y=None, height=40)
            container.add_widget(label_nome)
            container.add_widget(label_bonus)

        scroll.add_widget(container)
        self.layout.add_widget(scroll)

        btn_voltar = Button(text="⬅ Voltar", size_hint=(1, 0.1))
        btn_voltar.bind(on_press=self.voltar)
        self.layout.add_widget(btn_voltar)

    def voltar(self, *_):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "home"


# ----------------------------------------------------
# App principal com ScreenManager
# ----------------------------------------------------
class DNDCompanionApp(App):
    def build(self):
        Window.size = (420, 780)
        inicializar_banco()

        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(PericiasScreen(name="pericias"))
        return sm


if __name__ == "__main__":
    DNDCompanionApp().run()
