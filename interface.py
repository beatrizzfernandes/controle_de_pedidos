import tkinter as tk
from tkinter import messagebox, ttk
import customtkinter as ctk
import pandas as pd
from datetime import datetime
import os
import json
import smtplib
from email.message import EmailMessage

ARQUIVO_PRODUTOS = "produtos.json"

def carregar_precos_produtos():
    if not os.path.exists(ARQUIVO_PRODUTOS):
        messagebox.showerror("Erro", f"Arquivo {ARQUIVO_PRODUTOS} não encontrado.")
        return {}
    try:
        with open(ARQUIVO_PRODUTOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        messagebox.showerror("Erro", f"Erro ao ler produtos: {exc}")
        return {}

precos_produtos = carregar_precos_produtos()
   
lista_produtos = list(precos_produtos.keys())

# Arquivo contendo as configuracoes de e-mail
EMAIL_CONFIG_FILE = "config.json"

def carregar_dados_email():
    """L\u00ea o arquivo JSON com os dados de e-mail."""
    if not os.path.exists(EMAIL_CONFIG_FILE):
        messagebox.showerror(
            "Erro", f"Arquivo {EMAIL_CONFIG_FILE} n\u00e3o encontrado."
        )
        return None
    try:
        with open(EMAIL_CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        messagebox.showerror("Erro", f"Falha ao ler configura\u00e7\u00f5es: {exc}")
        return None

class PedidoDB:
    """Camada simples de persistência usando arquivo Excel."""
    COLUNAS = ["Data", "Nome", "Produto", "Quantidade", "Pagamento", "Status", "Valor Total"]
    def __init__(self, arquivo: str):
        self.arquivo = arquivo
        self._inicializar()
    def _inicializar(self):
        if not os.path.exists(self.arquivo):
            pd.DataFrame(columns=self.COLUNAS).to_excel(self.arquivo, index=False)
    def carregar(self) -> pd.DataFrame:
        self._inicializar()
        return pd.read_excel(self.arquivo)
    def salvar(self, df: pd.DataFrame) -> None:
        df.to_excel(self.arquivo, index=False)
    def adicionar(self, pedido: pd.DataFrame) -> None:
        df = self.carregar()
        df = pd.concat([df, pedido], ignore_index=True)
        self.salvar(df)
    def atualizar(self, idx: int, valores: dict) -> None:
        df = self.carregar()
        for col, val in valores.items():
            if col in df.columns:
                df.loc[idx, col] = val
        self.salvar(df)
    def remover(self, idx: int) -> None:
        df = self.carregar()
        df = df.drop(idx).reset_index(drop=True)
        self.salvar(df)

db = PedidoDB('pedidos.xlsx')

def limpar_estilos():
    for entry in [entry_nome, entry_quantidade]:
        entry.configure(border_color='#4a4a4a')

def limpar_campos():
    entry_nome.delete(0, tk.END)
    combo_produto.set('')
    entry_quantidade.delete(0, tk.END)
    combo_pagamento.set('')
    combo_status.set('Em andamento')
    limpar_estilos()

def cadastrar_pedido():
    limpar_estilos()
    nome = entry_nome.get().strip()
    produto = combo_produto.get().strip()
    quantidade = entry_quantidade.get().strip()
    pagamento = combo_pagamento.get().strip()
    status = combo_status.get().strip()
    data = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

    campos_invalidos = []
    pagamento_invalido = False

    if not nome:
        campos_invalidos.append(entry_nome)
    if not produto:
        campos_invalidos.append(combo_produto)
    if not quantidade:
        campos_invalidos.append(entry_quantidade)
    if not pagamento:
        pagamento_invalido = True

    try:
        quantidade_int = int(quantidade)
    except (ValueError, TypeError):
        campos_invalidos.append(entry_quantidade)
        quantidade_int = None

    if campos_invalidos or pagamento_invalido or quantidade_int is None:
        for campo in campos_invalidos:
            campo.configure(border_color='red')
        message = 'Preencha corretamente os campos em destaque.'
        if pagamento_invalido:
            message += '\nSelecione a forma de pagamento.'
        messagebox.showwarning('Aviso', message)
        return

    preco_unitario = precos_produtos.get(produto)
    if preco_unitario is None:
        messagebox.showwarning("Aviso", f"O produto '{produto}' não está cadastrado em produtos.json.")
        combo_produto.configure(border_color='red')
        return

    valor_total = quantidade_int * preco_unitario

    novo = pd.DataFrame([[data, nome, produto, quantidade_int, pagamento, status, valor_total]],
                        columns=db.COLUNAS)
    db.adicionar(novo)
    messagebox.showinfo('Sucesso', 'Pedido cadastrado com sucesso!')
    limpar_campos()
    atualizar_dashboard()

def abrir_edicao(idx: int):
    janela = ctk.CTkToplevel(root)
    janela.title('Editar Pedido')
    ctk.CTkLabel(janela, text='Status:').grid(row=0, column=0, padx=5, pady=5)
    status_box = ctk.CTkOptionMenu(janela, values=['Em andamento', 'Saiu para entrega', 'Finalizado'])
    status_box.grid(row=0, column=1, padx=5, pady=5)
    df = db.carregar()
    status_atual = df.loc[idx, 'Status']
    status_box.set(status_atual)
    def salvar_alteracao():
        db.atualizar(idx, {'Status': status_box.get()})
        janela.destroy()
        visualizar_pedidos()
    ctk.CTkButton(janela, text='Salvar', command=salvar_alteracao).grid(row=1, column=0, columnspan=2, pady=5)

def visualizar_pedidos():
    df = db.carregar()
    if df.empty:
        messagebox.showinfo('Informação', 'Nenhum pedido cadastrado ainda.')
        return
    nova_janela = ctk.CTkToplevel(root)
    nova_janela.title('Pedidos Cadastrados')
    tree = ttk.Treeview(nova_janela, columns=df.columns.tolist(), show='headings')
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    for i, row in df.iterrows():
        tree.insert('', tk.END, iid=str(i), values=list(row))
    tree.grid(row=0, column=0, columnspan=3, sticky='nsew')
    def obter_selecao():
        selecionado = tree.focus()
        if not selecionado:
            messagebox.showwarning('Aviso', 'Selecione um pedido na lista.')
            return None
        return int(selecionado)
    def acao_editar():
        idx = obter_selecao()
        if idx is not None:
            nova_janela.destroy()
            abrir_edicao(idx)
    def acao_excluir():
        idx = obter_selecao()
        if idx is not None and messagebox.askyesno('Confirmação', 'Excluir pedido selecionado?'):
            db.remover(idx)
            tree.delete(str(idx))
    ctk.CTkButton(nova_janela, text='Editar Status', command=acao_editar).grid(row=1, column=0, pady=5)
    ctk.CTkButton(nova_janela, text='Excluir', command=acao_excluir).grid(row=1, column=1, pady=5)
    ctk.CTkButton(nova_janela, text='Fechar', command=nova_janela.destroy).grid(row=1, column=2, pady=5)
    nova_janela.grid_rowconfigure(0, weight=1)
    nova_janela.grid_columnconfigure(0, weight=1)

def enviar_email(caminho: str) -> None:
    """Envia o arquivo informado por e-mail."""
    config = carregar_dados_email()
    if not config:
        return
    msg = EmailMessage()
    msg["Subject"] = "Relat\u00f3rio de Pedidos do Dia"
    msg["From"] = config.get("EMAIL_REMETENTE")
    msg["To"] = config.get("EMAIL_DESTINO")
    msg.set_content("Segue em anexo o relat\u00f3rio de pedidos do dia.")
    with open(caminho, "rb") as f:
        conteudo = f.read()
        msg.add_attachment(
            conteudo,
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=os.path.basename(caminho),
        )
    smtp_servidor = config.get("SMTP_SERVIDOR", "smtp.gmail.com")
    smtp_porta = config.get("SMTP_PORTA", 587)
    try:
        with smtplib.SMTP(smtp_servidor, smtp_porta) as server:
            server.starttls()
            server.login(config.get("EMAIL_REMETENTE"), config.get("EMAIL_SENHA"))
            server.send_message(msg)
        messagebox.showinfo("Sucesso", "Relat\u00f3rio enviado por e-mail.")
    except Exception as exc:
        messagebox.showerror("Erro", f"Falha ao enviar e-mail: {exc}")

def gerar_relatorio():
    df = db.carregar()
    if df.empty:
        messagebox.showinfo("Informa\u00e7\u00e3o", "Nenhum pedido cadastrado ainda.")
        return
    df["DataPedido"] = pd.to_datetime(df["Data"], dayfirst=True).dt.date
    hoje = datetime.now().date()
    df_hoje = df[df["DataPedido"] == hoje].drop(columns=["DataPedido"])
    if df_hoje.empty:
        messagebox.showinfo(
            "Informa\u00e7\u00e3o", "Nenhum pedido registrado para o dia de hoje."
        )
        return
    pasta = "relatorios"
    os.makedirs(pasta, exist_ok=True)
    nome_arquivo = f"relatorio_{hoje.strftime('%d-%m-%Y')}.xlsx"
    caminho = os.path.join(pasta, nome_arquivo)
    df_hoje.to_excel(caminho, index=False)
    enviar_email(caminho)
    messagebox.showinfo(
        "Sucesso", f"Relat\u00f3rio gerado e salvo em {caminho}."
    )

ctk.set_appearance_mode('dark')  # "dark", "light", or "system"
ctk.set_default_color_theme("blue")  # Tema moderno

root = ctk.CTk()
root.title('Sistema de Pedidos')
root.geometry('600x480')
root.resizable(False, False)

# Menu superior
menubar = tk.Menu(root)
menu_arquivo = tk.Menu(menubar, tearoff=0)
menu_arquivo.add_command(label='Visualizar Pedidos', command=visualizar_pedidos)
menu_arquivo.add_separator()
menu_arquivo.add_command(label='Sair', command=root.quit)
menubar.add_cascade(label='Arquivo', menu=menu_arquivo)
root.config(menu=menubar)

# Container principal
container = ctk.CTkFrame(root, corner_radius=15)
container.pack(padx=30, pady=30, fill='both', expand=True)

# Dashboard - Estatísticas rápidas
frame_dashboard = ctk.CTkFrame(container, fg_color='transparent')
frame_dashboard.grid(row=0, column=0, columnspan=2, pady=(10, 5), sticky="ew")
frame_dashboard.grid_columnconfigure((0, 1, 2), weight=1)

# Função para atualizar estatísticas
def atualizar_dashboard():
    df = db.carregar()
    if df.empty:
        pedidos_hoje_valor.configure(text="0")
        total_valor.configure(text="R$ 0,00")
        produto_top_valor.configure(text="N/A")
        return

    df["DataPedido"] = pd.to_datetime(df["Data"], dayfirst=True).dt.date
    hoje = datetime.now().date()
    df_hoje = df[df["DataPedido"] == hoje]

    pedidos_hoje = len(df_hoje)
    total_vendido = df_hoje["Valor Total"].sum() if not df_hoje.empty else 0
    produto_mais_vendido = df_hoje["Produto"].value_counts().idxmax() if not df_hoje.empty else "N/A"

    pedidos_hoje_valor.configure(text=str(pedidos_hoje))
    total_valor.configure(text=f"R$ {total_vendido:.2f}")
    produto_top_valor.configure(text=produto_mais_vendido)

    df["Valor Total"] = df["Valor Total"].fillna(0)


# Widgets dos cartões
def criar_card(titulo):
    frame = ctk.CTkFrame(frame_dashboard, corner_radius=8)
    label_titulo = ctk.CTkLabel(frame, text=titulo, font=ctk.CTkFont(size=12))
    label_valor = ctk.CTkLabel(frame, text="...", font=ctk.CTkFont(size=20, weight="bold"))
    label_titulo.pack(pady=(5, 0))
    label_valor.pack(pady=(0, 5))
    return frame, label_valor

card1, pedidos_hoje_valor = criar_card("Pedidos de Hoje")
card2, total_valor = criar_card("Total Vendido (R$)")
card3, produto_top_valor = criar_card("Produto + Vendido")

card1.grid(row=0, column=0, padx=5, sticky="nsew")
card2.grid(row=0, column=1, padx=5, sticky="nsew")
card3.grid(row=0, column=2, padx=5, sticky="nsew")

# Título
titulo = ctk.CTkLabel(
    container,
    text='Cadastro de Pedido',
    font=ctk.CTkFont(size=24, weight='bold')
)
titulo.grid(row=1, column=0, columnspan=2, pady=(10, 20))

labels = [
    ('Nome do Cliente:', 2),
    ('Produto:', 3),
    ('Quantidade:', 4),
    ('Forma de Pagamento:', 5),
    ('Status do Pedido:', 6),
]

entry_nome = ctk.CTkEntry(container, placeholder_text="Digite o nome")
combo_produto = ctk.CTkOptionMenu(container, values=lista_produtos)
combo_produto.set('') 
entry_quantidade = ctk.CTkEntry(container, placeholder_text="Ex: 2")
combo_pagamento = ctk.CTkOptionMenu(container, values=['Cartão', 'Pix'])
combo_status = ctk.CTkOptionMenu(container, values=['Em andamento', 'Saiu para entrega', 'Finalizado'])
combo_status.set('Em andamento')

campos = [
    (entry_nome, 'Nome do Cliente:'),
    (combo_produto, 'Produto:'),
    (entry_quantidade, 'Quantidade:'),
    (combo_pagamento, 'Forma de Pagamento:'),
    (combo_status, 'Status do Pedido:')
]

linha_inicial = 2
for i, (entrada, texto) in enumerate(campos):
    row = linha_inicial + i
    ctk.CTkLabel(container, text=texto).grid(row=row, column=0, sticky='e', pady=6, padx=(10, 5))
    entrada.grid(row=row, column=1, sticky='ew', pady=6, padx=(0, 15))

# Frame dos botões
button_frame = ctk.CTkFrame(container, fg_color='transparent')
button_frame.grid(row=7, column=0, columnspan=2, pady=(25, 10))
button_frame.grid_columnconfigure((0, 1, 2), weight=1)

ctk.CTkButton(button_frame, text='Cadastrar Pedido', command=cadastrar_pedido).grid(row=0, column=0, padx=8)
ctk.CTkButton(button_frame, text='Visualizar Pedidos', command=visualizar_pedidos).grid(row=0, column=1, padx=8)
ctk.CTkButton(button_frame, text='Gerar Relatório', command=gerar_relatorio).grid(row=0, column=2, padx=8)

# Responsividade
container.grid_columnconfigure(1, weight=1)

root.mainloop()