import cv2
import numpy as np
from regras import processar_entrada, processar_saida

# placa de teste associada ao objeto detectado
PLACA_DEMO = "DEM0-1234"

def main():
    cap = cv2.VideoCapture(0)

    # limites de cor em HSV (ajuste se precisar)
    # exemplo: algo amarelo / verde-limão
    lower = np.array([20, 100, 100])
    upper = np.array([40, 255, 255])

    altura_linha_entrada = 150
    altura_linha_saida = 300
    ultimo_estado = None  # "cima", "baixo", None

    print("Pressione 'q' para sair.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)  # espelho
        h, w, _ = frame.shape

        # desenha linhas de referência
        cv2.line(frame, (0, altura_linha_entrada), (w, altura_linha_entrada), (0, 255, 0), 2)
        cv2.line(frame, (0, altura_linha_saida), (w, altura_linha_saida), (0, 0, 255), 2)
        cv2.putText(frame, "ENTRADA", (10, altura_linha_entrada - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(frame, "SAIDA", (10, altura_linha_saida - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        centro_y = None

        if contours:
            c = max(contours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                centro_y = cy
                if radius > 10:
                    cv2.circle(frame, (cx, cy), int(radius), (255, 0, 0), 2)

        estado_atual = None
        if centro_y is not None:
            if centro_y < altura_linha_entrada:
                estado_atual = "cima"
                cv2.putText(frame, "REGIAO ENTRADA", (w//2 - 100, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            elif centro_y > altura_linha_saida:
                estado_atual = "baixo"
                cv2.putText(frame, "REGIAO SAIDA", (w//2 - 100, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # mudou de estado? dispara ação
        if estado_atual != ultimo_estado and estado_atual is not None:
            if estado_atual == "cima":
                print("Detectado na região de ENTRADA -> processando entrada...")
                processar_entrada(PLACA_DEMO)
            elif estado_atual == "baixo":
                print("Detectado na região de SAÍDA -> processando saída...")
                processar_saida(PLACA_DEMO)

        ultimo_estado = estado_atual

        cv2.imshow("Controle de Veiculo (demo cor)", frame)
        cv2.imshow("Mascara", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
