import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import os
import glob
import sys
def wizualizuj_ekg(sciezka_do_pliku):
    try:
        _, ext = os.path.splitext(sciezka_do_pliku) # type: ignore

        if ext.lower() == '.txt':
            y = []
            with open(sciezka_do_pliku, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    try:
                        val = float(line)
                        y.append(val)
                    except ValueError:
                        continue
            x = list(range(len(y)))

        else:
            df = pd.read_excel(sciezka_do_pliku, header=0)

            x = df.iloc[:, 2] 
            y = df.iloc[:, 1]

        fig = plt.figure(figsize=(12, 6))
        ax = plt.gca()
        
        if len(y) == 0:
            messagebox.showinfo("Brak Danych", f"Plik '{os.path.basename(sciezka_do_pliku)}' nie zawiera danych do wizualizacji.")
            plt.close()
            return

        y_min = min(y)
        y_max = max(y)

        if abs(y_max - y_min) < 1e-6:
            messagebox.showinfo("Sygnał Płaski", f"Sygnał w pliku '{os.path.basename(sciezka_do_pliku)}' jest stały (flatline) i nie wymaga wizualizacji.")
            plt.close()
            return

        window_size = 50
        y_series = pd.Series(y)
        y_smoothed = y_series.rolling(window=window_size, center=True, min_periods=1).mean()

        line, = plt.plot(x, y, color='blue', linewidth=0.8, label='Sygnał (Oryginalny)')

        rozpietosc = y_max - y_min
        margines = rozpietosc * 0.15
        plt.ylim(y_min - margines, y_max + margines)

        plt.title('Wykres sygnału EKG', fontsize=16)
        plt.xlabel('Numer pomiaru (LP)', fontsize=12)
        plt.ylabel('Amplituda (mV / jednostki)', fontsize=12)
        
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        
        plt.legend()
        
        plt.subplots_adjust(bottom=0.2)

        def zapisz_wykres(event):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(script_dir)
            screenshots_dir = os.path.join(project_root, "screeny")
            os.makedirs(screenshots_dir, exist_ok=True)

            base_name = os.path.splitext(os.path.basename(sciezka_do_pliku))[0]
            save_path = os.path.join(screenshots_dir, f"{base_name}.png")
            
            # Ukrywamy przyciski na moment zapisu
            ax_button.set_visible(False)
            ax_smooth_button.set_visible(False)
            
            fig.savefig(save_path)
            
            # Przywracamy przyciski
            ax_button.set_visible(True)
            ax_smooth_button.set_visible(True)
            
            messagebox.showinfo("Zapisano Wykres", f"Wykres został zapisany jako '{os.path.basename(save_path)}' w folderze 'screeny'.")

        ax_button = plt.axes([0.72, 0.03, 0.2, 0.075])
        przycisk_zapisu = Button(ax_button, 'Zapisz jako PNG')
        przycisk_zapisu.on_clicked(zapisz_wykres)

        is_smoothed = False
        def toggle_smooth(event):
            nonlocal is_smoothed
            is_smoothed = not is_smoothed
            if is_smoothed:
                line.set_ydata(y_smoothed)
                line.set_label('Sygnał (Wygładzony)')
                przycisk_wygladzania.label.set_text('Przywróć oryginał')
            else:
                line.set_ydata(y)
                line.set_label('Sygnał (Oryginalny)')
                przycisk_wygladzania.label.set_text('Wygładź sygnał')
            ax.legend()
            fig.canvas.draw_idle()

        ax_smooth_button = plt.axes([0.48, 0.03, 0.2, 0.075])
        przycisk_wygladzania = Button(ax_smooth_button, 'Wygładź sygnał')
        przycisk_wygladzania.on_clicked(toggle_smooth)
        plt.show()

    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku o nazwie '{sciezka_do_pliku}'. Sprawdź ścieżkę.")
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")

def uruchom_gui():
    root = tk.Tk()
    root.title("Wybór pliku EKG")
    root.geometry("500x500")

    tk.Label(root, text="Wybierz plik danych z folderu:").pack(pady=10)

    listbox = tk.Listbox(root)
    listbox.pack(expand=True, fill="both", padx=20, pady=5)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    pliki_mapa = []

    for root_dir, dirs, files in os.walk(project_root):
        for file in files:
            if file.lower().endswith(('.xlsx', '.xls', '.txt')):
                pelna_sciezka = os.path.join(root_dir, file)
                pliki_mapa.append(pelna_sciezka)
                listbox.insert(tk.END, os.path.relpath(pelna_sciezka, project_root))

    def on_click():
        sel = listbox.curselection()
        if not sel:
            messagebox.showwarning("Uwaga", "Zaznacz plik z listy!")
            return
        index = sel[0]
        plik = pliki_mapa[index]
        wizualizuj_ekg(plik)

    tk.Button(root, text="Rysuj Wykres", command=on_click, height=2, bg="#e1e1e1").pack(pady=20)

    # --- Sekcja Logów ---
    tk.Label(root, text="Logi aplikacji:").pack(pady=(5, 0), anchor="w", padx=20)
    
    log_widget = ScrolledText(root, height=8, state='disabled', font=("Consolas", 9))
    log_widget.pack(expand=True, fill="both", padx=20, pady=(0, 20))

    class PrintLogger:
        def __init__(self, text_widget):
            self.text_widget = text_widget

        def write(self, message):
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, message)
            self.text_widget.see(tk.END)
            self.text_widget.configure(state='disabled')

        def flush(self):
            pass

    # Przekierowanie print i błędów do okna logów
    sys.stdout = PrintLogger(log_widget)
    sys.stderr = PrintLogger(log_widget)

    print("Aplikacja gotowa. Wybierz plik z listy powyżej.")

    root.mainloop()

if __name__ == "__main__":
    uruchom_gui()
