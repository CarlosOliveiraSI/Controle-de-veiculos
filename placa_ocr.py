import cv2
import pytesseract
import re


# pytesseract.pytesseract.tesseract_cmd = r"C:\Users\carlo\Downloads\tessdoc-main\tessdoc-main\tesseract.exe"

def limpar_texto_placa(texto: str) -> str:
    """
    Remove lixo e deixa só letras e números em maiúsculo.
    """
    texto = texto.upper()
    texto = re.sub(r'[^A-Z0-9]', '', texto)
    return texto

def ler_placa_da_imagem(img):
    """
    Recebe um recorte da imagem (ROI) com a placa e tenta ler o texto.
    """
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cinza = cv2.bilateralFilter(cinza, 11, 17, 17)
    _, thr = cv2.threshold(cinza, 120, 255, cv2.THRESH_BINARY)

    config = "--psm 7"  # linha única de texto
    texto = pytesseract.image_to_string(thr, config=config)
    placa = limpar_texto_placa(texto)
    return placa

def capturar_placa():
    """
    Abre a webcam, mostra um retângulo onde você deve alinhar a placa.
    Aperte C para capturar, Q para sair.
    Retorna a placa lida (string) ou None.
    """
    cap = cv2.VideoCapture(0)
    placa_final = None

    if not cap.isOpened():
        print("Erro ao acessar a câmera.")
        return None

    print("Pressione 'c' para capturar a placa, 'q' para sair.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # região central onde a placa deve ficar
        y1, y2 = h // 3, 2 * h // 3
        x1, x2 = w // 4, 3 * w // 4

        roi = frame[y1:y2, x1:x2]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
        cv2.putText(frame, "Alinhe a placa aqui", (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(frame, "C = capturar | Q = sair", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        cv2.imshow("Captura de placa", frame)

        tecla = cv2.waitKey(1) & 0xFF
        if tecla == ord('c'):
            placa = ler_placa_da_imagem(roi)
            print("Texto lido:", placa)
            if placa:
                placa_final = placa
                cv2.putText(frame, f"Placa: {placa}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow("Captura de placa", frame)
                cv2.waitKey(1500)
                break
            else:
                print("Nao foi possivel ler a placa, tente de novo.")
        elif tecla == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return placa_final

if __name__ == "__main__":
    p = capturar_placa()
    print("Placa retornada:", p)
