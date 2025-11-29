from regras import (
    inicializar_banco,
    cadastrar_veiculo_cli,
    listar_veiculos_cli,
    marcar_veiculo_cli,
    processar_entrada,
    processar_saida,
    relatorios_cli,
)

def mostrar_menu():
    print("\n=== Controle de Veículos do Campus ===")
    print("1 - Cadastrar veículo")
    print("2 - Listar veículos")
    print("3 - Marcar / desmarcar veículo")
    print("4 - Registrar entrada")
    print("5 - Registrar saída")
    print("6 - Relatórios")
    print("0 - Sair")

def main():
    inicializar_banco()

    while True:
        mostrar_menu()
        op = input("Escolha uma opção: ")

        if op == "1":
            cadastrar_veiculo_cli()
        elif op == "2":
            listar_veiculos_cli()
        elif op == "3":
            marcar_veiculo_cli()
        elif op == "4":
            placa = input("Placa: ").strip()
            processar_entrada(placa)
        elif op == "5":
            placa = input("Placa: ").strip()
            processar_saida(placa)
        elif op == "6":
            relatorios_cli()
        elif op == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    main()
