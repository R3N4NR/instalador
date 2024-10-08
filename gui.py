import tkinter as tk
from tkinter import messagebox, Listbox, BooleanVar, Text
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


def atualizar_text_area():
    text_area.delete(1.0, tk.END)  # Limpa a área de texto antes de adicionar novos itens
    for programa, var in checkboxes.items():
        if var.get():
            # Verifica se o programa está no dicionário antes de tentar acessar o ID
            id_programa = programas_ids.get(programa)
            if id_programa and '.' in id_programa:  # Verifica se o ID contém um ponto
                text_area.insert(tk.END, f"{programa} (ID: {id_programa})\n")
            else:
                text_area.insert(tk.END, f"{programa} (ID não disponível ou inválido)\n")
    if id_selecionado:
        text_area.insert(tk.END, f"{listbox.get(listbox.curselection())} (ID: {id_selecionado})\n")




def on_program_click(event):
    selection = listbox.curselection()  # Pega a seleção atual
    if selection:
        index = selection[0]  # Pega o primeiro item selecionado
        line = listbox.get(index).strip()  # Obtém o texto correspondente ao índice
        if line in programas_ids:
            global id_selecionado
            id_selecionado = programas_ids[line]
            atualizar_text_area()  # Atualiza a área de texto


def pesquisar_programas():
    termo = entry_pesquisa.get().strip()
    if termo:
        text_area.delete(1.0, tk.END)  # Limpa a área de texto
        global programas_ids
        programas_ids = {}  # Limpa os IDs armazenados

        def search_in_thread():
            try:
                resultado = subprocess.run(f'winget search {termo}', check=True, shell=True, capture_output=True, text=True)
                linhas = resultado.stdout.strip().split('\n')

                nomes_unicos = set()  # Conjunto para armazenar nomes únicos
                listbox.delete(0, tk.END)  # Limpa o Listbox antes de adicionar novos itens

                for linha in linhas[1:]:  # Ignorar a primeira linha de cabeçalho
                    partes = linha.split()
                    if partes:
                        # Filtra apenas os nomes válidos
                        nome_programa = partes[0]
                        id_programa = partes[1] if len(partes) > 1 else None

                        # Verifica se o ID é válido (contém um ponto)
                        if id_programa and '.' in id_programa:
                            # Adiciona o nome ao conjunto e ao Listbox apenas se for único
                            if nome_programa not in nomes_unicos:
                                nomes_unicos.add(nome_programa)

                                # Adiciona apenas se o nome não contiver caracteres indesejados
                                if all(c.isalnum() or c.isspace() for c in nome_programa):
                                    listbox.insert(tk.END, nome_programa.strip())  # Adiciona ao Listbox, removendo espaços em branco
                                    # Atualiza o dicionário de IDs
                                    programas_ids[nome_programa] = id_programa.strip()  # Garantindo que o ID esteja no formato certo

            except subprocess.CalledProcessError as e:
                messagebox.showerror("Erro", f"Erro ao pesquisar: {e}")

        threading.Thread(target=search_in_thread).start()





def instalar_programas():
    comandos = []

    # Adiciona o programa selecionado do listbox
    if id_selecionado:
        # Verifica se o ID contém um ponto antes de adicionar o comando
        if '.' in id_selecionado:
            comandos.append(f'winget install {id_selecionado} --silent')

    # Adiciona programas selecionados nos checkboxes
    for programa, var in checkboxes.items():
        if var.get():
            # Verifica se o ID do programa contém um ponto antes de adicionar o comando
            id_programa = programas_ids.get(programa)
            if id_programa and '.' in id_programa:
                comandos.append(programas[programa])

    if not comandos:
        messagebox.showwarning("Seleção vazia", "Nenhum programa selecionado.")
        return

    listbox.delete(0, tk.END)  # Limpa o Listbox para mensagens de status

    for comando in comandos:
        listbox.insert(tk.END, f"Executando: {comando}\n")
        listbox.yview(tk.END)
        try:
            # Executa o comando e espera até que termine
            resultado = subprocess.run(f'powershell -Command "{comando}"', check=True, shell=True, capture_output=True, text=True)
            # Se a execução for bem-sucedida, adicione uma mensagem de sucesso
            listbox.insert(tk.END, "Instalação bem-sucedida!\n")
        except subprocess.CalledProcessError as e:
            # Se houver erro, adicione uma mensagem de erro
            listbox.insert(tk.END, f"Erro ao instalar: {str(e)}\n")
            break  # Saia do loop em caso de erro

    # Atualiza a interface após a conclusão da instalação
    root.after(0, lambda: messagebox.showinfo("Concluído", "Instalação concluída!\n" + "\n".join(listbox.get(0, tk.END))))



# Criando a janela principal
root = tk.Tk()
root.title("Instalador de Programas")

# Configuração do campo de entrada
entry_pesquisa = tk.Entry(root, width=50)
entry_pesquisa.pack(pady=10)

# Botão para iniciar a pesquisa
btn_pesquisar = tk.Button(root, text="Pesquisar", command=pesquisar_programas)
btn_pesquisar.pack(pady=5)

# Configuração do Listbox
listbox = Listbox(root, width=50)
listbox.pack(pady=10)
listbox.bind("<Button-1>", on_program_click)

# Criação de checkboxes para programas iniciais
checkboxes = {}
for programa in programas.keys():
    var = BooleanVar()
    checkbox = tk.Checkbutton(root, text=programa, variable=var, command=atualizar_text_area)
    checkbox.pack(anchor=tk.W)
    checkboxes[programa] = var

# Área de texto para exibir programas selecionados
text_area = Text(root, width=60, height=10)
text_area.pack(pady=10)

# Botão para instalar programas
btn_instalar = tk.Button(root, text="Instalar Programas", command=instalar_programas)
btn_instalar.pack(pady=10)

id_selecionado = None

root.mainloop()
