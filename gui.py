import tkinter as tk
from tkinter import messagebox, Listbox, BooleanVar
import subprocess
import threading

# Lista de programas com seus respectivos comandos winget
programas = {
    "PDF24 Creator": "winget install geeksoftwareGmbH.PDF24Creator --silent",
    "Google Chrome": "winget install Google.Chrome --silent",
    "7-Zip": "winget install 7zip.7zip --silent",
    "Adobe Acrobat Reader (32-bit)": "winget install Adobe.Acrobat.Reader.32-bit --silent",
    "Lightshot": "winget install Skillbrains.Lightshot --silent",
    "Discord": "winget install Discord.Discord --silent",
    "NAPS2": "winget install Cyanfish.NAPS2 --silent"
}

# Dicionário para armazenar IDs correspondentes
programas_ids = {}

def verificar_politica_execucao():
    try:
        # Verificar a política de execução atual
        resultado = subprocess.run('powershell -Command "Get-ExecutionPolicy"', check=True, shell=True, capture_output=True, text=True)
        politica_atual = resultado.stdout.strip()

        # Se não estiver "Unrestricted", alterá-la
        if politica_atual != "Unrestricted":
            subprocess.run('powershell -Command "Set-ExecutionPolicy Unrestricted -Scope Process -Force"', check=True, shell=True)
            print("Política de execução alterada para 'Unrestricted'.")
        else:
            print("Política de execução já está 'Unrestricted'.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao verificar ou alterar a política de execução: {e}")

def atualizar_listbox(linhas):
    listbox.delete(0, tk.END)  # Limpa o Listbox antes de adicionar novos itens
    for linha in linhas:
        listbox.insert(tk.END, linha)  # Adiciona cada linha ao Listbox

def pesquisar_programas():
    termo = entry_pesquisa.get()
    if not termo:
        # Se o campo de pesquisa estiver vazio, não faça nada
        return

    resultados_formatados = []
    
    def search_in_thread():
        try:
            # Executa o comando de pesquisa do winget
            resultado = subprocess.run(f'winget search {termo}', check=True, shell=True, capture_output=True, text=True, encoding='utf-8')
            linhas = resultado.stdout.strip().split('\n')
            for linha in linhas[1:]:
                partes = linha.split()
                if partes:
                    nome_programa = partes[0]
                    id_programa = partes[1] if len(partes) > 1 else None
                    if id_programa:
                        programas_ids[nome_programa] = id_programa
                        resultados_formatados.append(nome_programa)

            # Atualiza a interface gráfica no thread principal
            root.after(0, lambda: atualizar_listbox(resultados_formatados))

        except subprocess.CalledProcessError as e:
            root.after(0, lambda: messagebox.showerror("Erro", f"Erro ao pesquisar: {str(e)}"))

    threading.Thread(target=search_in_thread).start()

def on_program_click(event):
    selection = listbox.curselection()  # Pega a seleção atual
    if selection:
        index = selection[0]  # Pega o primeiro item selecionado
        line = listbox.get(index).strip()  # Obtém o texto correspondente ao índice
        if line in programas_ids:
            global id_selecionado
            id_selecionado = programas_ids[line]
            messagebox.showinfo("ID Selecionado", f"O ID do programa '{line}' é: {id_selecionado}")

def instalar_programas():
    comandos = []

    for programa, var in checkboxes.items():
        if var.get():
            comandos.append(programas[programa])

    if 'id_selecionado' in globals():
        comandos.append(f'winget install {id_selecionado} --silent')

    if not comandos:
        messagebox.showwarning("Seleção vazia", "Nenhum programa selecionado.")
        return

    listbox.delete(0, tk.END)

    def install_in_thread():
        # Executar comandos de instalação
        for comando in comandos:
            listbox.insert(tk.END, f"Executando: {comando}\n")
            listbox.yview(tk.END)
            try:
                subprocess.run(f'powershell -Command "{comando}"', check=True, shell=True)
                listbox.insert(tk.END, "Instalação bem-sucedida!\n")
            except subprocess.CalledProcessError as e:
                listbox.insert(tk.END, f"Erro ao instalar: {str(e)}\n")

        # Garantir que as atualizações visuais aconteçam no thread principal
        root.after(0, lambda: messagebox.showinfo("Concluído", "Todos os programas foram instalados!"))

    threading.Thread(target=install_in_thread).start()

# Criando a janela principal
root = tk.Tk()
root.title("Instalador de Programas")

# Verificar política de execução no início
verificar_politica_execucao()

# Configuração do campo de entrada
entry_pesquisa = tk.Entry(root, width=50)
entry_pesquisa.pack(pady=10)
entry_pesquisa.bind("<KeyRelease>", lambda event: pesquisar_programas())

# Configuração do Listbox
listbox = Listbox(root, width=50)
listbox.pack(pady=10)
listbox.bind("<Button-1>", on_program_click)

# Criação de checkboxes para programas iniciais
checkboxes = {}
for programa in programas.keys():
    var = BooleanVar()
    checkbox = tk.Checkbutton(root, text=programa, variable=var)
    checkbox.pack(anchor=tk.W)
    checkboxes[programa] = var

# Botão para instalar programas
btn_instalar = tk.Button(root, text="Instalar Programas", command=instalar_programas)
btn_instalar.pack(pady=10)

id_selecionado = None

root.mainloop()
