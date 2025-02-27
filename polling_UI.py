from pynput import mouse
import time
import tkinter as tk
from tkinter import ttk
from collections import deque

# Variables globales
last_time = None
polling_rates = deque(maxlen=10)  # Acumula las últimas 10 mediciones
accumulated_rates = []  # Acumula las mediciones antes de promediarlas
max_polling_rate = 0
is_measuring = False
is_dynamic = False
listener = None
last_polling_rate = None  # Para comparar el cambio en el polling rate

# Función que se ejecuta cuando el ratón se mueve
def on_move(x, y):
    global last_time, polling_rates, accumulated_rates, max_polling_rate, is_dynamic, last_polling_rate

    current_time = time.perf_counter()

    if last_time is not None:
        delta_time = current_time - last_time

        if delta_time > 0.001:  # Ignora eventos con delta_time < 1 ms
            polling_rate = 1 / delta_time
            polling_rate = min(polling_rate, 8000)  # Límite de 8000 Hz para ratones modernos

            # Acumular mediciones
            accumulated_rates.append(polling_rate)

            # Solo promediar cada 10 mediciones acumuladas
            if len(accumulated_rates) >= 10:
                avg_polling_rate = sum(accumulated_rates) / len(accumulated_rates)
                accumulated_rates.clear()  # Limpiar la acumulación

                polling_rates.append(avg_polling_rate)

                # Actualizar la interfaz
                if avg_polling_rate > max_polling_rate:
                    max_polling_rate = avg_polling_rate
                    max_polling_label.config(text=f"Máximo Registrado: {max_polling_rate:.2f} Hz")

                polling_rate_label.config(text=f"Polling Rate Promedio: {avg_polling_rate:.2f} Hz")

                # Detectar si el polling rate es dinámico
                if len(set([round(rate) for rate in polling_rates])) > 2:
                    is_dynamic = True
                else:
                    is_dynamic = False
                dynamic_label.config(text=f"Polling Rate Dinámico: {'Sí' if is_dynamic else 'No'}")

                # Actualizar el listado de polling rates
                update_polling_rate_list()

    last_time = current_time

# Función para actualizar el listado de polling rates
def update_polling_rate_list():
    rate_list_text = "\n".join([f"{rate:.2f} Hz" for rate in polling_rates])
    polling_rate_list_text.delete(1.0, tk.END)  # Limpiar el Text antes de actualizar
    polling_rate_list_text.insert(tk.END, f"Últimas Mediciones:\n{rate_list_text}")

# Función para iniciar/detener la medición
def toggle_measurement():
    global listener, is_measuring, max_polling_rate, polling_rates, accumulated_rates, is_dynamic

    if not is_measuring:
        is_measuring = True
        start_button.config(text="Detener Medición")
        polling_rate_label.config(text="Mueve el ratón...")
        max_polling_label.config(text="Máximo Registrado: 0.00 Hz")
        dynamic_label.config(text="Polling Rate Dinámico: No detectado")
        max_polling_rate = 0
        polling_rates.clear()
        accumulated_rates.clear()
        is_dynamic = False

        listener = mouse.Listener(on_move=on_move)
        listener.start()
    else:
        is_measuring = False
        start_button.config(text="Iniciar Medición")
        polling_rate_label.config(text="Medición detenida")

        if listener:
            listener.stop()
            listener = None

# Función para cerrar la aplicación limpiamente
def close_app():
    global listener
    if listener:
        listener.stop()
    root.destroy()

# Configura la interfaz gráfica
root = tk.Tk()
root.title("Medidor de Polling Rate")
root.geometry("300x400")

# Cambia estos valores para modificar los colores
background_color = "#1E1E1E"  # Fondo de la ventana
text_color = "#ffffff"  # Color de los textos
title_color = "#00ff00"  # Color del título
button_color = "#4C566A"  # Color de los botones
button_text_color = "#2E3440"  # Color del texto de los botones

root.configure(bg=background_color)

# Título de la aplicación
title_label = ttk.Label(
    root, text="customicemx - Polling rate test",
    font=("Arial", 14, "bold"), background=background_color, foreground=title_color
)
title_label.pack(pady=10)

polling_rate_label = ttk.Label(
    root, text="Presiona 'Iniciar Medición' para comenzar",
    font=("Arial", 12), background=background_color, foreground=text_color
)
polling_rate_label.pack(pady=10)

max_polling_label = ttk.Label(
    root, text="Máximo Registrado: 0.00 Hz",
    font=("Arial", 12), background=background_color, foreground=text_color
)
max_polling_label.pack(pady=10)

dynamic_label = ttk.Label(
    root, text="Polling Rate Dinámico: No detectado",
    font=("Arial", 12), background=background_color, foreground=text_color
)
dynamic_label.pack(pady=10)

# Frame para las mediciones
frame_list = ttk.Frame(root, padding="10")
frame_list.pack(pady=10, fill=tk.X)

# Text widget para mostrar las mediciones
polling_rate_list_text = tk.Text(frame_list, height=6, width=30, wrap=tk.WORD, bg=background_color, fg=text_color, font=("Arial", 10))
polling_rate_list_text.pack(fill=tk.BOTH, expand=True)

# Estilo personalizado para los botones
style = ttk.Style()
style.configure(
    "Custom.TButton",
    font=("Arial", 12),
    padding=6,
    background=button_color,
    foreground=button_text_color
)
style.map(
    "Custom.TButton",
    background=[("active", "#5E81AC")],
    relief=[("pressed", "sunken"), ("!pressed", "raised")]
)

# Frame para los botones
button_frame = tk.Frame(root, bg=background_color)
button_frame.pack(pady=10)

# Botones agrupados horizontalmente
start_button = ttk.Button(button_frame, text="Iniciar Medición", command=toggle_measurement, style="Custom.TButton")
start_button.pack(side=tk.LEFT, padx=5)

exit_button = ttk.Button(button_frame, text="Salir", command=close_app, style="Custom.TButton")
exit_button.pack(side=tk.LEFT, padx=5)

root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()
