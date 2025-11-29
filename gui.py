import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk

from regras import (
    inicializar_banco,
    processar_entrada,
    processar_saida,
    listar_veiculos_dentro,
    acessos_por_placa,   # <--- NOVO
)
from placa_ocr import capturar_placa


# ---------- Funções de ação ----------

def entrada_camera():
    placa = capturar_placa()
    if not placa:
        messagebox.showwarning("Entrada", "Não foi possível ler a placa.")
        return

    tipo_veiculo = simpledialog.askstring(
        "Tipo de veículo", "Informe o tipo (carro/moto):"
    )
    tipo_uso = simpledialog.askstring(
        "Tipo de uso", "Informe o uso (particular/oficial):"
    )

    if not tipo_veiculo or not tipo_uso:
        messagebox.showwarning("Entrada", "Dados incompletos.")
        return

    processar_entrada(placa, tipo_veiculo.strip().lower(), tipo_uso.strip().lower())
    messagebox.showinfo("Entrada", f"Entrada registrada para {placa}.")
    atualizar_lista_dentro()


def saida_camera():
    placa = capturar_placa()
    if not placa:
        messagebox.showwarning("Saída", "Não foi possível ler a placa.")
        return
    processar_saida(placa)
    messagebox.showinfo("Saída", f"Saída registrada para {placa}.")
    atualizar_lista_dentro()


def entrada_manual():
    placa = simpledialog.askstring("Entrada manual", "Digite a placa:")
    if not placa:
        return

    tipo_veiculo = simpledialog.askstring(
        "Tipo de veículo", "Informe o tipo (carro/moto):"
    )
    tipo_uso = simpledialog.askstring(
        "Tipo de uso", "Informe o uso (particular/oficial):"
    )

    if not tipo_veiculo or not tipo_uso:
        messagebox.showwarning("Entrada", "Dados incompletos.")
        return

    processar_entrada(placa, tipo_veiculo.strip().lower(), tipo_uso.strip().lower())
    messagebox.showinfo("Entrada", f"Entrada registrada para {placa}.")
    atualizar_lista_dentro()


def saida_manual():
    placa = simpledialog.askstring("Saída manual", "Digite a placa:")
    if not placa:
        return
    processar_saida(placa)
    messagebox.showinfo("Saída", f"Saída registrada para {placa}.")
    atualizar_lista_dentro()


def atualizar_lista_dentro():
    texto_box.config(state="normal")
    texto_box.delete("1.0", tk.END)
    veiculos = listar_veiculos_dentro()
    if not veiculos:
        texto_box.insert(tk.END, "Nenhum veículo dentro no momento.\n")
    else:
        for placa, tipo, uso, entrada in veiculos:
            texto_box.insert(
                tk.END,
                f"{placa}  |  {tipo}  |  {uso}  |  entrada: {entrada}\n"
            )
    texto_box.config(state="disabled")


def mostrar_historico():
    """
    Abre uma janela mostrando todas as entradas/saidas de uma placa.
    """
    placa = simpledialog.askstring("Histórico", "Digite a placa para consultar:")
    if not placa:
        return

    acessos = acessos_por_placa(placa)
    if not acessos:
        messagebox.showinfo("Histórico", "Nenhum acesso encontrado para essa placa.")
        return

    # janela nova
    top = tk.Toplevel()
    top.title(f"Histórico da placa {placa.upper()}")
    top.geometry("650x300")

    frame = ttk.Frame(top, padding=10)
    frame.pack(fill="both", expand=True)

    txt = tk.Text(frame, font=("Consolas", 10), wrap="none")
    txt.pack(side="left", fill="both", expand=True)

    scroll_y = ttk.Scrollbar(frame, orient="vertical", command=txt.yview)
    scroll_y.pack(side="right", fill="y")
    txt.config(yscrollcommand=scroll_y.set)

    txt.insert(tk.END, "ID | ENTRADA              | SAIDA                | ALERTA\n")
    txt.insert(tk.END, "-" * 70 + "\n")
    for aid, plc, ent, sai, alt in acessos:
        sai_str = sai if sai is not None else "-"
        alt_str = alt if alt is not None else "-"
        linha = f"{aid:03d} | {ent} | {sai_str} | {alt_str}\n"
        txt.insert(tk.END, linha)

    txt.config(state="disabled")


# ---------- Montagem da janela ----------

def main():
    inicializar_banco()

    global texto_box

    root = tk.Tk()
    root.title("Controle de Veículos - Campus")
    root.geometry("720x440")
    root.minsize(680, 400)

    # Tema / estilo
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except:
        pass

    style.configure("TButton", font=("Segoe UI", 10), padding=6)
    style.configure("Title.TLabel", font=("Segoe UI Semibold", 16))
    style.configure("Section.TLabelframe", font=("Segoe UI", 11, "bold"))
    style.configure("Section.TLabelframe.Label", font=("Segoe UI", 11, "bold"))

    root.columnconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)

    topo = ttk.Frame(root, padding=(15, 10))
    topo.grid(row=0, column=0, sticky="ew")

    ttk.Label(
        topo,
        text="Sistema de Controle de Acesso de Veículos",
        style="Title.TLabel",
    ).pack(side="left")

    main_frame = ttk.Frame(root, padding=(15, 0, 15, 10))
    main_frame.grid(row=1, column=0, sticky="nsew")
    main_frame.columnconfigure(0, weight=1)
    main_frame.rowconfigure(1, weight=1)

    # Card de ações
    card_acoes = ttk.Labelframe(
        main_frame, text="Ações", style="Section.TLabelframe", padding=10
    )
    card_acoes.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    card_acoes.columnconfigure((0, 1, 2), weight=1)

    btn_entrada_cam = ttk.Button(
        card_acoes, text="Entrada (câmera)", command=entrada_camera
    )
    btn_entrada_cam.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    btn_saida_cam = ttk.Button(
        card_acoes, text="Saída (câmera)", command=saida_camera
    )
    btn_saida_cam.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    btn_hist = ttk.Button(
        card_acoes, text="Histórico da placa", command=mostrar_historico
    )
    btn_hist.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    btn_entrada_manual = ttk.Button(
        card_acoes, text="Entrada manual", command=entrada_manual
    )
    btn_entrada_manual.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

    btn_saida_manual = ttk.Button(
        card_acoes, text="Saída manual", command=saida_manual
    )
    btn_saida_manual.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    btn_atualizar = ttk.Button(
        card_acoes,
        text="Atualizar veículos dentro",
        command=atualizar_lista_dentro,
    )
    btn_atualizar.grid(row=1, column=2, padx=5, pady=5, sticky="ew")

    # Card de lista
    card_lista = ttk.Labelframe(
        main_frame,
        text="Veículos atualmente dentro do campus",
        style="Section.TLabelframe",
        padding=8,
    )
    card_lista.grid(row=1, column=0, sticky="nsew")
    card_lista.rowconfigure(0, weight=1)
    card_lista.columnconfigure(0, weight=1)

    texto_box = tk.Text(
        card_lista,
        height=10,
        font=("Consolas", 10),
        wrap="none",
    )
    texto_box.grid(row=0, column=0, sticky="nsew")

    scroll_y = ttk.Scrollbar(card_lista, orient="vertical", command=texto_box.yview)
    scroll_y.grid(row=0, column=1, sticky="ns")
    texto_box.config(yscrollcommand=scroll_y.set)

    scroll_x = ttk.Scrollbar(card_lista, orient="horizontal", command=texto_box.xview)
    scroll_x.grid(row=1, column=0, columnspan=2, sticky="ew")
    texto_box.config(xscrollcommand=scroll_x.set)

    atualizar_lista_dentro()

    root.mainloop()


if __name__ == "__main__":
    main()
