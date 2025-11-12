# main.py
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition

from controllers.db_manager import inicializar_banco, conectar
from controllers.calculator import calcular_bonus_pericia, atributo_nome_para_campo
from controllers.roller import roll
from models.personagem import Personagem
from models.pericia import Pericia
from models.item import Item

def _to_int(value, default=0):
    try:
        if value is None or str(value).strip() == "":
            return default
        return int(str(value).strip())
    except Exception:
        return default

# =====================================================
# 🧾 TELA PRINCIPAL (FICHA)
# =====================================================
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
        botoes.add_widget(Button(text="🧰 Inventário", on_press=self.ver_inventario))
        botoes.add_widget(Button(text="🎯 Perícias", on_press=self.ver_pericias))
        botoes.add_widget(Button(text="🎲 Rolagem", on_press=self.ver_rolagem))
        layout.add_widget(botoes)

        layout.add_widget(Button(text="💾 Salvar", size_hint=(1, 0.1), on_press=self.on_salvar))
        self.add_widget(layout)

    def on_pre_enter(self):
        # recarrega sempre que entrar, para aplicar itens equipados
        self.carregar_personagem()

    def carregar_personagem(self):
        conn = conectar()
        # 1) carrega base do banco (sem bônus)
        p = Personagem.carregar(conn, 1)

        # 2) aplica bônus dos itens equipados com mapeamento correto (FOR -> forca etc.)
        items = Item.listar(conn, 1)
        for item in items:
            if item.equipado:
                if item.bonus_atributo and item.valor_bonus:
                    campo = atributo_nome_para_campo(item.bonus_atributo)  # ex: "FOR" -> "forca"
                    if campo:
                        valor_atual = getattr(p, campo)
                        setattr(p, campo, valor_atual + item.valor_bonus)
                if item.bonus_ca:
                    p.ca += item.bonus_ca
        conn.close()

        self.personagem = p
        # Preenche UI
        fields = {
            self.nome: p.nome, self.classe: p.classe, self.nivel: p.nivel, self.ca: p.ca,
            self.hp_max: p.hp_max, self.hp_atual: p.hp_atual, self.forca: p.forca, self.destreza: p.destreza,
            self.constituicao: p.constituicao, self.inteligencia: p.inteligencia,
            self.sabedoria: p.sabedoria, self.carisma: p.carisma
        }
        for campo, valor in fields.items():
            campo.text = str(valor or "")

    def on_salvar(self, *_):
        conn = conectar()
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
        conn.close()
        print("✅ Personagem salvo!")

    def ver_inventario(self, *_):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "inventario"

    def ver_pericias(self, *_):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "pericias"

    def ver_rolagem(self, *_):
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "roll"


# =====================================================
# 🎒 TELA DE INVENTÁRIO (lista)
# =====================================================
class InventarioScreen(Screen):
    def on_pre_enter(self):
        self.build_layout()

    def build_layout(self):
        self.clear_widgets()
        layout = BoxLayout(orientation="vertical", padding=16, spacing=10)
        layout.add_widget(Label(text="🎒 Inventário", font_size="20sp", bold=True, size_hint=(1, 0.1)))

        scroll = ScrollView(size_hint=(1, 0.7))
        container = GridLayout(cols=1, spacing=8, size_hint_y=None)
        container.bind(minimum_height=container.setter("height"))

        conn = conectar()
        items = Item.listar(conn)
        conn.close()

        for item in items:
            row = BoxLayout(orientation="horizontal", size_hint_y=None, height=46, spacing=8)
            resumo_bonus = []
            if item.bonus_atributo and item.valor_bonus:
                resumo_bonus.append(f"+{item.valor_bonus} {item.bonus_atributo}")
            if item.bonus_ca:
                resumo_bonus.append(f"+{item.bonus_ca} CA")
            resumo = " | ".join(resumo_bonus) if resumo_bonus else "—"

            status = "Equipado: Sim" if item.equipado else "Equipado: Não"
            row.add_widget(Label(text=f"{item.nome}  ({resumo})  ·  {status}", halign="left"))

            btn_toggle = Button(text="Equipar" if not item.equipado else "Remover", size_hint_x=0.28)
            btn_toggle.bind(on_press=lambda _, i=item: self.toggle_item(i.id))
            row.add_widget(btn_toggle)

            btn_edit = Button(text="Editar", size_hint_x=0.18)
            btn_edit.bind(on_press=lambda _, i=item: self.editar_item(i.id))
            row.add_widget(btn_edit)

            btn_del = Button(text="Excluir", size_hint_x=0.18)
            btn_del.bind(on_press=lambda _, i=item: self.excluir_item(i.id))
            row.add_widget(btn_del)

            container.add_widget(row)

        scroll.add_widget(container)
        layout.add_widget(scroll)

        barra = BoxLayout(size_hint=(1, 0.2), spacing=10)
        btn_add = Button(text="➕ Adicionar Item")
        btn_add.bind(on_press=self.adicionar_item)
        btn_voltar = Button(text="⬅ Voltar")
        btn_voltar.bind(on_press=self.voltar)
        barra.add_widget(btn_add)
        barra.add_widget(btn_voltar)
        layout.add_widget(barra)

        self.add_widget(layout)

    def adicionar_item(self, *_):
        # vai para a tela de formulário vazio (novo)
        self.manager.get_screen("itemform").carregar_item(None)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "itemform"

    def editar_item(self, item_id):
        self.manager.get_screen("itemform").carregar_item(item_id)
        self.manager.transition = SlideTransition(direction="left")
        self.manager.current = "itemform"

    def excluir_item(self, item_id):
        conn = conectar()
        Item.deletar(conn, item_id)
        conn.close()
        self.build_layout()

    def toggle_item(self, item_id):
        conn = conectar()
        Item.alternar_equipado(conn, item_id)
        conn.close()
        self.build_layout()

    def voltar(self, *_):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "home"


# =====================================================
# 📝 TELA FORMULÁRIO DE ITEM (criar/editar)
# =====================================================
class ItemFormScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.item_id = None
        self.layout = BoxLayout(orientation="vertical", padding=16, spacing=10)
        self.add_widget(self.layout)

        self.titulo = Label(text="Item", font_size="20sp", bold=True, size_hint=(1, 0.1))
        self.layout.add_widget(self.titulo)

        form = GridLayout(cols=2, spacing=6, size_hint=(1, 0.7))

        self.nome = TextInput(multiline=False)
        self.descricao = TextInput(multiline=True)

        self.bonus_attr = Spinner(text="(nenhum)", values=("FOR","DES","CON","INT","SAB","CAR","(nenhum)"))
        self.valor_bonus = TextInput(multiline=False, input_filter="int")
        self.bonus_ca = TextInput(multiline=False, input_filter="int")
        self.bonus_ataque = TextInput(multiline=False, input_filter="int")
        self.bonus_dano = TextInput(multiline=False, input_filter="int")
        self.efeito_especial = TextInput(multiline=True)
        self.equipado_txt = Label(text="Equipado (marque salvando como equipado)")
        self.equipado_flag = False  # simples: controlamos pelo botão "Salvar equipado"

        form.add_widget(Label(text="Nome:")); form.add_widget(self.nome)
        form.add_widget(Label(text="Descrição:")); form.add_widget(self.descricao)
        form.add_widget(Label(text="Bônus de Atributo:")); form.add_widget(self.bonus_attr)
        form.add_widget(Label(text="Valor do Bônus:")); form.add_widget(self.valor_bonus)
        form.add_widget(Label(text="Bônus de CA:")); form.add_widget(self.bonus_ca)
        form.add_widget(Label(text="Bônus de Ataque:")); form.add_widget(self.bonus_ataque)
        form.add_widget(Label(text="Bônus de Dano:")); form.add_widget(self.bonus_dano)
        form.add_widget(Label(text="Efeito Especial:")); form.add_widget(self.efeito_especial)
        self.layout.add_widget(form)

        botoes = BoxLayout(size_hint=(1, 0.2), spacing=10)
        btn_salvar = Button(text="💾 Salvar")
        btn_salvar.bind(on_press=self.salvar)
        btn_salvar_equip = Button(text="💾 Salvar (equipado)")
        btn_salvar_equip.bind(on_press=lambda *_: self.salvar(equipar=True))
        btn_voltar = Button(text="⬅ Voltar")
        btn_voltar.bind(on_press=self.voltar)
        botoes.add_widget(btn_salvar)
        botoes.add_widget(btn_salvar_equip)
        botoes.add_widget(btn_voltar)
        self.layout.add_widget(botoes)

    def carregar_item(self, item_id):
        self.item_id = item_id
        conn = conectar()
        if item_id:
            item = Item.obter(conn, item_id)
            titulo = "✏️ Editar Item"
        else:
            item = None
            titulo = "➕ Novo Item"
        conn.close()

        self.titulo.text = titulo
        if item:
            self.nome.text = item.nome
            self.descricao.text = item.descricao
            self.bonus_attr.text = item.bonus_atributo if item.bonus_atributo else "(nenhum)"
            self.valor_bonus.text = str(item.valor_bonus or 0)
            self.bonus_ca.text = str(item.bonus_ca or 0)
            self.equipado_flag = item.equipado
        else:
            self.nome.text = ""
            self.descricao.text = ""
            self.bonus_attr.text = "(nenhum)"
            self.valor_bonus.text = "0"
            self.bonus_ca.text = "0"
            self.equipado_flag = False

    def salvar(self, *_, equipar=False):
        nome = self.nome.text.strip() or "Item sem nome"
        descricao = self.descricao.text.strip()
        attr = self.bonus_attr.text.upper()
        if attr == "(NENHUM)":
            attr = ""
        valor_bonus = _to_int(self.valor_bonus.text, 0)
        bonus_ca = _to_int(self.bonus_ca.text, 0)
        equipped = bool(equipar or self.equipado_flag)

        conn = conectar()
        try:
            if self.item_id:
                item = Item.obter(conn, self.item_id)
                if not item:
                    return
                item.nome = nome
                item.descricao = descricao
                item.bonus_atributo = attr
                item.valor_bonus = valor_bonus
                item.bonus_ca = bonus_ca
                item.equipado = equipped
                item.atualizar(conn)
            else:
                novo = Item(
                    id=None, personagem_id=1,
                    nome=nome, descricao=descricao,
                    bonus_atributo=attr, valor_bonus=valor_bonus,
                    bonus_ca=bonus_ca, equipado=equipped
                )
                novo.inserir(conn)
        finally:
            conn.close()

        # volta para o inventário
        self.manager.get_screen("inventario").build_layout()
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "inventario"

    def voltar(self, *_):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "inventario"


# =====================================================
# 🎲 TELA DE ROLAGEM (igual da etapa 4)
# =====================================================
class RollScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=16, spacing=10)
        self.add_widget(self.layout)

        self.layout.add_widget(Label(text="🎲 Teste de Rolagem", font_size="20sp", bold=True))
        self.expression = TextInput(hint_text="Ex: d20 + FOR + PROF", multiline=False, size_hint=(1, 0.1))
        self.layout.add_widget(self.expression)
        self.manual = TextInput(hint_text="Valor manual (opcional)", multiline=False, input_filter="int", size_hint=(1, 0.1))
        self.layout.add_widget(self.manual)

        botoes = BoxLayout(size_hint=(1, 0.1), spacing=10)
        botoes.add_widget(Button(text="Normal", on_press=lambda _: self.executar("normal")))
        botoes.add_widget(Button(text="Vantagem", on_press=lambda _: self.executar("advantage")))
        botoes.add_widget(Button(text="Desvantagem", on_press=lambda _: self.executar("disadvantage")))
        self.layout.add_widget(botoes)

        self.resultado = Label(text="", font_size="16sp", size_hint=(1, 0.5))
        self.layout.add_widget(self.resultado)

        btn_voltar = Button(text="⬅ Voltar", size_hint=(1, 0.1))
        btn_voltar.bind(on_press=self.voltar)
        self.layout.add_widget(btn_voltar)

    def executar(self, modo):
        conn = conectar()
        personagem = Personagem.carregar(conn)
        conn.close()
        context = {
            "FOR": (personagem.forca - 10) // 2,
            "DES": (personagem.destreza - 10) // 2,
            "CON": (personagem.constituicao - 10) // 2,
            "INT": (personagem.inteligencia - 10) // 2,
            "SAB": (personagem.sabedoria - 10) // 2,
            "CAR": (personagem.carisma - 10) // 2,
            "PROF": 3  # fixo por enquanto
        }

        manual_val = _to_int(self.manual.text, None)
        expr = self.expression.text.strip() or "d20"

        resultado = roll(expr, context, manual_val, modo)
        texto = f"{resultado.detalhes}\n\nTOTAL: {resultado.total}"
        if resultado.critico:
            texto += "\n💥 CRÍTICO!"
        self.resultado.text = texto

    def voltar(self, *_):
        self.manager.transition = SlideTransition(direction="right")
        self.manager.current = "home"


# =====================================================
# 🎯 TELA DE PERÍCIAS (mesma base)
# =====================================================
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


# =====================================================
# APP PRINCIPAL
# =====================================================
class DNDCompanionApp(App):
    def build(self):
        Window.size = (420, 780)
        inicializar_banco()
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(InventarioScreen(name="inventario"))
        sm.add_widget(ItemFormScreen(name="itemform"))
        sm.add_widget(PericiasScreen(name="pericias"))
        sm.add_widget(RollScreen(name="roll"))
        return sm

if __name__ == "__main__":
    DNDCompanionApp().run()
