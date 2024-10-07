import subprocess
import tkinter as tk
# Dicionário para armazenar IDs correspondentes
programas_ids = {
    "PDF24 Creator": "geeksoftwareGmbH.PDF24Creator",
    "Google Chrome": "Google.Chrome",
    "7-Zip": "7zip.7zip",
    "Adobe Acrobat Reader (32-bit)": "Adobe.Acrobat.Reader.32-bit",
    "Lightshot": "Skillbrains.Lightshot",
    "Discord": "Discord.Discord",
    "NAPS2": "Cyanfish.NAPS2"
}

def verificar_politica_execucao():
    try:
        resultado = subprocess.run('powershell -Command "Get-ExecutionPolicy"', check=True, shell=True, capture_output=True, text=True)
        politica_atual = resultado.stdout.strip()
        if politica_atual != "Unrestricted":
            subprocess.run('powershell -Command "Set-ExecutionPolicy Unrestricted -Scope Process -Force"', check=True, shell=True)
            print("Política de execução alterada para 'Unrestricted'.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao verificar ou alterar a política de execução: {e}")

def atualizar_text_area(lista, linhas):
    lista.delete(0, tk.END)  # Limpar Listbox
    for linha in linhas:
        lista.insert(tk.END, linha)  # Adicionar novos itens
