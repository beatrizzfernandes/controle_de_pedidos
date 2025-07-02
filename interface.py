import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime
import os

class PedidoDB:
    """Camada simples de persistência usando arquivo Excel."""
    COLUNAS = ["Data", "Nome", "Produto", "Quantidade", "Pagamento", "Status"]
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
    for entry in [entry_nome, entry_produto, entry_quantidade]:
        entry.configure(style='TEntry')

def limpar_campos():
    entry_nome.delete(0, tk.END)
    entry_produto.delete(0, tk.END)
    entry_quantidade.delete(0, tk.END)
    combo_pagamento.set('')
    combo_status.set('Em andamento')
    limpar_estilos()

def cadastrar_pedido():
    limpar_estilos()
    nome = entry_nome.get().strip()
    produto = entry_produto.get().strip()
    quantidade = entry_quantidade.get().strip()
    pagamento = combo_pagamento.get().strip()
    status = combo_status.get().strip()
    data = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    campos_invalidos = []
    if not nome:
        campos_invalidos.append(entry_nome)
    if not produto:
        campos_invalidos.append(entry_produto)
    if not quantidade:
        campos_invalidos.append(entry_quantidade)
    if not pagamento:
        campos_invalidos.append(combo_pagamento)
    try:
        quantidade_int = int(quantidade)
    except (ValueError, TypeError):
        campos_invalidos.append(entry_quantidade)
        quantidade_int = None
    if campos_invalidos or quantidade_int is None:
        for campo in campos_invalidos:
            campo.configure(style='Error.TEntry')
        messagebox.showwarning('Aviso', 'Preencha corretamente os campos em destaque.')
        return
    novo = pd.DataFrame([[data, nome, produto, quantidade_int, pagamento, status]], columns=db.COLUNAS)
    db.adicionar(novo)
    messagebox.showinfo('Sucesso', 'Pedido cadastrado com sucesso!')
    limpar_campos()

def abrir_edicao(idx: int):
    janela = tk.Toplevel(root)
    janela.title('Editar Pedido')
    ttk.Label(janela, text='Status:').grid(row=0, column=0, padx=5, pady=5)
    status_box = ttk.Combobox(janela, values=['Em andamento', 'Saiu para entrega', 'Finalizado'])
    status_box.grid(row=0, column=1, padx=5, pady=5)
    df = db.carregar()
    status_atual = df.loc[idx, 'Status']
    status_box.set(status_atual)
    def salvar_alteracao():
        db.atualizar(idx, {'Status': status_box.get()})
        janela.destroy()
        visualizar_pedidos()
    ttk.Button(janela, text='Salvar', command=salvar_alteracao).grid(row=1, column=0, columnspan=2, pady=5)

def visualizar_pedidos():
    df = db.carregar()
    if df.empty:
        messagebox.showinfo('Informação', 'Nenhum pedido cadastrado ainda.')
        return
    nova_janela = tk.Toplevel(root)
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
    ttk.Button(nova_janela, text='Editar Status', command=acao_editar).grid(row=1, column=0, pady=5)
    ttk.Button(nova_janela, text='Excluir', command=acao_excluir).grid(row=1, column=1, pady=5)
    ttk.Button(nova_janela, text='Fechar', command=nova_janela.destroy).grid(row=1, column=2, pady=5)
    nova_janela.grid_rowconfigure(0, weight=1)
    nova_janela.grid_columnconfigure(0, weight=1)

root = tk.Tk()
root.title('Sistema de Controle de Pedidos')
root.geometry('420x300')
style = ttk.Style()
style.configure('Error.TEntry', fieldbackground='#FFCCCC')
menubar = tk.Menu(root)
menu_arquivo = tk.Menu(menubar, tearoff=0)
menu_arquivo.add_command(label='Visualizar Pedidos', command=visualizar_pedidos)
menu_arquivo.add_separator()
menu_arquivo.add_command(label='Sair', command=root.quit)
menubar.add_cascade(label='Arquivo', menu=menu_arquivo)
root.config(menu=menubar)
frame_campos = ttk.Frame(root, padding=10)
frame_campos.grid(row=0, column=0, sticky='nsew')
labels = [
    ('Nome do Cliente:', 0),
    ('Produto:', 1),
    ('Quantidade:', 2),
    ('Forma de Pagamento:', 3),
    ('Status do Pedido:', 4),
]
entry_nome = ttk.Entry(frame_campos)
entry_produto = ttk.Entry(frame_campos)
entry_quantidade = ttk.Entry(frame_campos)
combo_pagamento = ttk.Combobox(frame_campos, values=['Cartão', 'Pix'])
combo_status = ttk.Combobox(frame_campos, values=['Em andamento', 'Saiu para entrega', 'Finalizado'])
combo_status.set('Em andamento')
entries = [entry_nome, entry_produto, entry_quantidade, combo_pagamento, combo_status]
for texto, row in labels:
    ttk.Label(frame_campos, text=texto).grid(row=row, column=0, sticky='e', pady=2)
    entries[row].grid(row=row, column=1, sticky='we', pady=2)
frame_campos.columnconfigure(1, weight=1)
frame_botoes = ttk.Frame(root, padding=10)
frame_botoes.grid(row=1, column=0)
ttk.Button(frame_botoes, text='Cadastrar Pedido', command=cadastrar_pedido).grid(row=0, column=0, padx=5)
ttk.Button(frame_botoes, text='Visualizar Pedidos', command=visualizar_pedidos).grid(row=0, column=1, padx=5)
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
root.mainloop()
