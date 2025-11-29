from datetime import datetime
from bd import (
    criar_tabelas,
    inserir_veiculo,
    buscar_veiculo_por_placa,
    atualizar_marcacao,
    registrar_entrada_bd,
    registrar_saida_bd,
    listar_todos_veiculos,
    listar_acessos_por_placa,
    listar_veiculos_marcados,
    listar_veiculos_dentro,
)


TEMPO_MAXIMO_MINUTOS = 240  # 4 horas


def inicializar_banco():
    criar_tabelas()


# ---------- Funções de cadastro e marcação ----------

def cadastrar_veiculo_cli():
    placa = input("Placa: ").strip().upper()
    tipo_veiculo = input("Tipo (carro/moto): ").strip().lower()
    tipo_uso = input("Uso (particular/oficial): ").strip().lower()
    observacao = input("Observação (opcional): ").strip()

    try:
        inserir_veiculo(placa, tipo_veiculo, tipo_uso, observacao=observacao)
        print("Veículo cadastrado com sucesso!")
    except Exception as e:
        print("Erro ao cadastrar veículo:", e)


def listar_veiculos_cli():
    veiculos = listar_todos_veiculos()
    if not veiculos:
        print("Nenhum veículo cadastrado.")
        return
    print("\n--- Veículos cadastrados ---")
    for vid, placa, tipo, uso, marcado in veiculos:
        status = "MARCADO" if marcado else "normal"
        print(f"{vid} - {placa} | {tipo} | {uso} | {status}")


def marcar_veiculo_cli():
    placa = input("Placa: ").strip().upper()
    v = buscar_veiculo_por_placa(placa)
    if not v:
        print("Veículo não encontrado.")
        return
    marcado_atual = v[4]
    print(f"Status atual: {'MARCADO' if marcado_atual else 'normal'}")
    novo = input("Marcar como não autorizado/ocorrência? (s/n): ").strip().lower()
    if novo == "s":
        obs = input("Observação: ")
        atualizar_marcacao(placa, 1, obs)
        print("Veículo marcado.")
    else:
        atualizar_marcacao(placa, 0, "")
        print("Veículo desmarcado.")


# ---------- Núcleo: processar entrada e saída ----------

def _agora_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def processar_entrada(placa, tipo_veiculo=None, tipo_uso=None):
    """
    Usado tanto pelo menu (CLI) quanto pela GUI.

    - Se o veículo NÃO existir e tipo_veiculo/tipo_uso forem passados,
      usa esses valores (caso da interface gráfica).
    - Se o veículo NÃO existir e NÃO vierem valores,
      pergunta no terminal (caso do main.py em texto).
    """
    placa = placa.upper()
    v = buscar_veiculo_por_placa(placa)

    if not v:
        
        if tipo_veiculo is None or tipo_uso is None:
            
            print("Veículo não cadastrado. Cadastrando básico...")
            tipo_veiculo = input("Tipo (carro/moto): ").strip().lower()
            tipo_uso = input("Uso (particular/oficial): ").strip().lower()
        inserir_veiculo(placa, tipo_veiculo, tipo_uso)
        v = buscar_veiculo_por_placa(placa)

    vid, placa, tipo_veiculo, tipo_uso, marcado, observacao = v

    alerta = None
    if marcado:
        alerta = "VEÍCULO MARCADO / NÃO AUTORIZADO"

    data_hora = _agora_str()
    registrar_entrada_bd(vid, data_hora, alerta)

    print(f"Entrada registrada para {placa} às {data_hora}")
    if alerta:
        print("ALERTA:", alerta)


def processar_saida(placa):
    """
    Fecha o último acesso em aberto e checa tempo de permanência.
    """
    placa = placa.upper()
    v = buscar_veiculo_por_placa(placa)
    if not v:
        print("Veículo não encontrado.")
        return

    vid, placa, tipo_veiculo, tipo_uso, marcado, observacao = v

    
    acessos = listar_acessos_por_placa(placa)
    ultimo_aberto = None
    for ac in acessos:
        aid, _, entrada, saida, alerta = ac
        if saida is None:
            ultimo_aberto = ac
            break

    if not ultimo_aberto:
        print("Não há entrada em aberto para este veículo.")
        return

    aid, _, entrada_str, saida_str, alerta_antigo = ultimo_aberto
    dt_entrada = datetime.strptime(entrada_str, "%Y-%m-%d %H:%M:%S")
    dt_saida = datetime.now()
    permanencia = dt_saida - dt_entrada
    minutos = permanencia.total_seconds() / 60

    alerta_extra = None
    if minutos > TEMPO_MAXIMO_MINUTOS:
        alerta_extra = f"TEMPO EXCEDIDO ({minutos:.1f} min)"

    data_hora_saida = dt_saida.strftime("%Y-%m-%d %H:%M:%S")
    ok = registrar_saida_bd(vid, data_hora_saida, alerta_extra)

    if ok:
        print(f"Saída registrada para {placa} às {data_hora_saida}")
        print(f"Tempo de permanência: {minutos:.1f} minutos")
        if alerta_extra:
            print("ALERTA:", alerta_extra)
    else:
        print("Erro: não foi possível registrar saída.")


# ---------- Relatórios CLI ----------

def relatorios_cli():
    while True:
        print("\n=== Relatórios ===")
        print("1 - Acessos por placa")
        print("2 - Veículos marcados")
        print("3 - Veículos atualmente dentro do campus")
        print("0 - Voltar")
        op = input("Opção: ")

        if op == "1":
            placa = input("Placa: ").strip().upper()
            acessos = listar_acessos_por_placa(placa)
            if not acessos:
                print("Nenhum acesso encontrado.")
                continue
            for aid, plc, ent, sai, alt in acessos:
                print(f"{aid} | {plc} | {ent} -> {sai} | {alt}")
        elif op == "2":
            marcados = listar_veiculos_marcados()
            if not marcados:
                print("Nenhum veículo marcado.")
                continue
            for vid, placa, tipo, uso, obs in marcados:
                print(f"{vid} - {placa} | {tipo} | {uso} | {obs}")
        elif op == "3":
            dentro = listar_veiculos_dentro()
            if not dentro:
                print("Nenhum veículo dentro no momento.")
                continue
            for placa, tipo, uso, entrada in dentro:
                print(f"{placa} | {tipo} | {uso} | Entrada: {entrada}")
        elif op == "0":
            break
        else:
            print("Opção inválida.")
        
def acessos_por_placa(placa):
    return listar_acessos_por_placa(placa.upper())

