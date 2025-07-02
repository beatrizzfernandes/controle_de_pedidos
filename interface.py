import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime
import os

# Nome do arquivo de pedidos
ARQUIVO_PEDIDOS = "pedidos.xlsx"

# Função para inicializar o arquivo se ele não existir
def inicializar_planilha():
    if not os.path.exists(ARQUIVO_PEDIDOS):
        df = pd.DataFrame(columns=["Data", "Nome", "Produto", "Quantidade", "Pagamento", "Status"])
        df.to_excel(ARQUIVO_PEDIDOS, index=False)

# Função para cadastrar um novo pedido
def cadastrar_pedido():
    nome = entry_nome.get()
    produto = entry_produto.get()
    quantidade = entry_quantidade.get()
    pagamento = combo_pagamento.get()
    status = combo_status.get()
    data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    if not nome or not produto or not quantidade or not pagamento:
        messagebox.showwarning("Aviso", "Preencha todos os campos obrigatórios.")
        return

    try:
        quantidade_int = int(quantidade)
    except ValueError:
        messagebox.showwarning("Aviso", "Quantidade deve ser um número.")
        return

    novo_pedido = pd.DataFrame([[data, nome, produto, quantidade_int, pagamento, status]],
                               columns=["Data", "Nome", "Produto", "Quantidade", "Pagamento", "Status"])

    if os.path.exists(ARQUIVO_PEDIDOS):
        df = pd.read_excel(ARQUIVO_PEDIDOS)
        df = pd.concat([df, novo_pedido], ignore_index=True)
    else:
        df = novo_pedido

    df.to_excel(ARQUIVO_PEDIDOS, index=False)
    messagebox.showinfo("Sucesso", "Pedido cadastrado com sucesso!")
    limpar_campos()

# Função para limpar os campos após cadastro
def limpar_campos():
    entry_nome.delete(0, tk.END)
    entry_produto.delete(0, tk.END)
    entry_quantidade.delete(0, tk.END)
    combo_pagamento.set('')
    combo_status.set('')

# Função para exibir os pedidos cadastrados
def visualizar_pedidos():
    if not os.path.exists(ARQUIVO_PEDIDOS):
        messagebox.showinfo("Informação", "Nenhum pedido cadastrado ainda.")
        return

    df = pd.read_excel(ARQUIVO_PEDIDOS)
    nova_janela = tk.Toplevel(root)
    nova_janela.title("Pedidos Cadastrados")

    tree = ttk.Treeview(nova_janela, columns=df.columns.tolist(), show='headings')
    for col in df.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)

    for _, row in df.iterrows():
        tree.insert("", tk.END, values=list(row))

    tree.pack(fill=tk.BOTH, expand=True)

# Interface principal
root = tk.Tk()
root.title("Sistema de Controle de Pedidos")
root.geometry("400x400")

tk.Label(root, text="Nome do Cliente:").pack()
entry_nome = tk.Entry(root)
entry_nome.pack()

tk.Label(root, text="Produto:").pack()
entry_produto = tk.Entry(root)
entry_produto.pack()

tk.Label(root, text="Quantidade:").pack()
entry_quantidade = tk.Entry(root)
entry_quantidade.pack()

tk.Label(root, text="Forma de Pagamento:").pack()
combo_pagamento = ttk.Combobox(root, values=["Cartão", "Pix"])
combo_pagamento.pack()

tk.Label(root, text="Status do Pedido:").pack()
combo_status = ttk.Combobox(root, values=["Em andamento", "Saiu para entrega", "Finalizado"])
combo_status.set("Em andamento")
combo_status.pack()

tk.Button(root, text="Cadastrar Pedido", command=cadastrar_pedido).pack(pady=10)
tk.Button(root, text="Visualizar Pedidos", command=visualizar_pedidos).pack()

# Inicializa a planilha se necessário
inicializar_planilha()

root.mainloop()
