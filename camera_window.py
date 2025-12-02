import cv2
import easyocr
from tkinter import Toplevel, Label, Button
from PIL import Image, ImageTk

# leitor do EasyOCR (só inglês já resolve pra placa)
reader = easyocr.Reader(['en'], gpu=False)


def ler_placa(img):
    resultados = reader.readtext(img, detail=0)

    if not resultados:
        return None

    texto = resultados[0]
    texto = texto.replace(" ", "").upper()
    texto = "".join(c for c in texto if c.isalnum())
    return texto


def abrir_camera_e_capturar(callback):
    """
    Abre uma janela com a câmera ao vivo e, ao clicar em 'Capturar placa',
    lê a placa com EasyOCR e chama callback(placa).
    """

    janela = Toplevel()
    janela.title("Captura da Placa")

    lbl_video = Label(janela)
    lbl_video.pack()

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        callback(None)
        janela.destroy()
        return

    def atualizar_frame():
        ret, frame = cap.read()
        if not ret:
            return

        # BGR -> RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)

        lbl_video.imgtk = imgtk
        lbl_video.configure(image=imgtk)

        # atualiza a cada 30 ms
        lbl_video.after(30, atualizar_frame)

    def capturar():
        ret, frame = cap.read()
        if not ret:
            callback(None)
        else:
            placa = ler_placa(frame)
            callback(placa)

        cap.release()
        janela.destroy()

    btn = Button(janela, text="Capturar placa", command=capturar)
    btn.pack(pady=10)

    atualizar_frame()
