import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import ttk
from camera_window import abrir_camera_e_capturar  # janela da câmera com EasyOCR

from regras import (
    inicializar_banco,
    processar_entrada,
    processar_saida,
    listar_veiculos_dentro,
    acessos_por_placa,
    marcar_veiculo,
)

from bd import (
    buscar_veiculo_por_placa,
    listar_veiculos_marcados,
    listar_todos_veiculos,
)

# ======================================================
#   FUNÇÕES DA INTERFACE
# ======================================================


def entrada_camera():
    def receber_placa(placa):
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

        v = buscar_veiculo_por_placa(placa)
        if v and v[4] == 1:
            messagebox.showerror(
                "⚠ ALERTA – VEÍCULO MARCADO ⚠",
                f"O veículo {placa.upper()} está MARCADO como NÃO AUTORIZADO!\n"
                "Ocorrência registrada no sistema."
            )
        else:
            messagebox.showinfo("Entrada", f"Entrada registrada para {placa.upper()}.")

        atualizar_lista_dentro()

    # abre a janela com a câmera e, ao capturar, chama o callback acima
    abrir_camera_e_capturar(receber_placa)


def saida_camera():
    def receber_placa(placa):
        if not placa:
            messagebox.showwarning("Saída", "Não foi possível ler a placa.")
            return

        processar_saida(placa)
        messagebox.showinfo("Saída", f"Saída registrada para {placa.upper()}.")
        atualizar_lista_dentro()

    abrir_camera_e_capturar(receber_placa)


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

    v = buscar_veiculo_por_placa(placa)
    if v and v[4] == 1:
        messagebox.showerror(
            "⚠ ALERTA – VEÍCULO MARCADO ⚠",
            f"O veículo {placa.upper()} está MARCADO como NÃO AUTORIZADO!"
        )
    else:
        messagebox.showinfo("Entrada", f"Entrada registrada para {placa.upper()}.")

    atualizar_lista_dentro()


def saida_manual():
    placa = simpledialog.askstring("Saída manual", "Digite a placa:")
    if not placa:
        return

    processar_saida(placa)
    messagebox.showinfo("Saída", f"Saída registrada para {placa.upper()}.")
    atualizar_lista_dentro()


def atualizar_lista_dentro():
    texto_box.config(state="normal")
    texto_box.delete("1.0", tk.END)

    veiculos = listar_veiculos_dentro()
    if not veiculos:
        texto_box.insert(tk.END, "Nenhum veículo dentro no momento.\n")
    else:
        for placa, tipo, uso, entrada in veiculos:
            v = buscar_veiculo_por_placa(placa)
            marcado = v[4] if v else 0
            tag = " (MARCADO)" if marcado else ""

            texto_box.insert(
                tk.END,
                f"{placa.upper()}{tag}  |  {tipo}  |  {uso}  |  entrada: {entrada}\n"
            )

    texto_box.config(state="disabled")


def mostrar_historico():
    placa = simpledialog.askstring("Histórico", "Digite a placa:")
    if not placa:
        return

    acessos = acessos_por_placa(placa)
    if not acessos:
        messagebox.showinfo("Histórico", "Nenhum registro encontrado.")
        return

    top = tk.Toplevel()
    top.title(f"Histórico de {placa.upper()}")
    top.geometry("700x350")

    txt = tk.Text(top, font=("Consolas", 10))
    txt.pack(fill="both", expand=True)

    v = buscar_veiculo_por_placa(placa)
    if v:
        marcado = v[4]
        obs = v[5]
        status = "MARCADO – NÃO AUTORIZADO" if marcado else "Normal"
        txt.insert(tk.END, f"Status do veículo: {status}\n")
        if marcado and obs:
            txt.insert(tk.END, f"Observação: {obs}\n")
        txt.insert(tk.END, "\n")

    txt.insert(tk.END, "ID | ENTRADA              | SAÍDA                | ALERTA\n")
    txt.insert(tk.END, "-" * 80 + "\n")

    for aid, plc, ent, sai, alt in acessos:
        sai_str = sai if sai else "-"
        alt_str = alt if alt else "-"
        txt.insert(tk.END, f"{aid:03d} | {ent} | {sai_str} | {alt_str}\n")

    txt.config(state="disabled")


def marcar_veiculo_gui():
    placa = simpledialog.askstring("Marcar veículo", "Digite a placa:")
    if not placa:
        return

    marcar = messagebox.askyesno(
        "Marcar veículo",
        "Marcar este veículo como NÃO AUTORIZADO?\nSim = marcar | Não = desmarcar"
    )

    obs = ""
    if marcar:
        obs = simpledialog.askstring("Observação", "Motivo (opcional):") or ""

    ok = marcar_veiculo(placa, marcar, obs)

    if not ok:
        messagebox.showerror("Erro", "Veículo não encontrado no banco.")
        return

    if marcar:
        messagebox.showinfo("Marcar veículo", f"{placa.upper()} marcado com sucesso.")
    else:
        messagebox.showinfo("Marcar veículo", f"{placa.upper()} desmarcado.")

    atualizar_lista_dentro()


# ======================================================
#   RELATÓRIOS
# ======================================================

def abrir_relatorios():
    janela = tk.Toplevel()
    janela.title("Relatórios do Sistema")
    janela.geometry("500x300")

    frame = ttk.Frame(janela, padding=10)
    frame.pack(fill="both", expand=True)

    ttk.Label(
        frame,
        text="Escolha um relatório:",
        font=("Segoe UI", 12, "bold")
    ).pack(pady=10)

    ttk.Button(
        frame,
        text="Veículos MARCADOS",
        command=lambda: mostrar_relatorio("marcados"),
        width=40,
    ).pack(pady=5)

    ttk.Button(
        frame,
        text="Veículos dentro do campus",
        command=lambda: mostrar_relatorio("dentro"),
        width=40,
    ).pack(pady=5)

    ttk.Button(
        frame,
        text="Todos os veículos cadastrados",
        command=lambda: mostrar_relatorio("todos"),
        width=40,
    ).pack(pady=5)


def mostrar_relatorio(tipo):
    janela = tk.Toplevel()
    janela.title("Relatório")
    janela.geometry("650x400")

    txt = tk.Text(janela, font=("Consolas", 10))
    txt.pack(fill="both", expand=True)

    if tipo == "marcados":
        dados = listar_veiculos_marcados()
        txt.insert(tk.END, "VEÍCULOS MARCADOS\n\n")
        if not dados:
            txt.insert(tk.END, "Nenhum veículo marcado.\n")
        else:
            for vid, placa, tipo, uso, obs in dados:
                txt.insert(tk.END, f"{placa} | {tipo} | {uso} | Obs: {obs}\n")

    elif tipo == "dentro":
        dados = listar_veiculos_dentro()
        txt.insert(tk.END, "VEÍCULOS DENTRO DO CAMPUS\n\n")
        if not dados:
            txt.insert(tk.END, "Nenhum veículo dentro no momento.\n")
        else:
            for placa, tipo, uso, entrada in dados:
                txt.insert(
                    tk.END,
                    f"{placa} | {tipo} | {uso} | Entrada: {entrada}\n"
                )

    elif tipo == "todos":
        dados = listar_todos_veiculos()
        txt.insert(tk.END, "TODOS OS VEÍCULOS CADASTRADOS\n\n")
        if not dados:
            txt.insert(tk.END, "Nenhum veículo cadastrado.\n")
        else:
            for vid, placa, tipo, uso, marcado in dados:
                status = "MARCADO" if marcado else "normal"
                txt.insert(
                    tk.END,
                    f"{placa} | {tipo} | {uso} | {status}\n"
                )

    txt.config(state="disabled")


# ======================================================
#   JANELA PRINCIPAL
# ======================================================

def main():
    inicializar_banco()

    global texto_box

    root = tk.Tk()
    root.title("Controle de Veículos - Campus")
    root.geometry("750x500")

    # ----- Estilo -----
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure("TButton", font=("Segoe UI", 10), padding=6)
    style.configure("Title.TLabel", font=("Segoe UI Semibold", 16))

    # ----- Cabeçalho -----
    topo = ttk.Frame(root, padding=15)
    topo.pack(fill="x")

    ttk.Label(
        topo,
        text="Sistema de Controle de Veículos",
        style="Title.TLabel"
    ).pack()

    # ----- Área principal -----
    main_frame = ttk.Frame(root, padding=10)
    main_frame.pack(fill="both", expand=True)

    # ----- Ações -----
    acoes = ttk.Labelframe(main_frame, text="Ações", padding=10)
    acoes.pack(pady=10, anchor="center")

    acoes.grid_columnconfigure((0, 1, 2), weight=1)

    ttk.Button(
        acoes, text="Entrada (câmera)", command=entrada_camera
    ).grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    ttk.Button(
        acoes, text="Saída (câmera)", command=saida_camera
    ).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    ttk.Button(
        acoes, text="Histórico da placa", command=mostrar_historico
    ).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

    ttk.Button(
        acoes, text="Entrada manual", command=entrada_manual
    ).grid(row=1, column=0, padx=5, pady=5, sticky="ew")

    ttk.Button(
        acoes, text="Saída manual", command=saida_manual
    ).grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    ttk.Button(
        acoes, text="Marcar / desmarcar veículo", command=marcar_veiculo_gui
    ).grid(row=1, column=2, padx=5, pady=5, sticky="ew")

    ttk.Button(
        acoes, text="Relatórios", command=abrir_relatorios
    ).grid(row=2, column=0, columnspan=3, padx=5, pady=10, sticky="ew")

    # ----- Lista de veículos -----
    lista = ttk.Labelframe(main_frame, text="Veículos dentro do campus", padding=10)
    lista.pack(fill="both", expand=True, padx=40, pady=(0, 10))

    texto_box = tk.Text(lista, font=("Consolas", 10), wrap="none", height=12)
    texto_box.pack(fill="both", expand=True)

    scroll_y = ttk.Scrollbar(lista, orient="vertical", command=texto_box.yview)
    scroll_y.pack(side="right", fill="y")
    texto_box.config(yscrollcommand=scroll_y.set)

    atualizar_lista_dentro()

    root.mainloop()


# ======================================================
if __name__ == "__main__":
    main()
