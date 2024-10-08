import tkinter as tk
from tkinter import messagebox, Listbox, BooleanVar, Text
import subprocess
import threading

# Classe para representar um programa
class Programa:
    def __init__(self, nome, id_programa):
        self.nome = nome
        self.id_programa = id_programa

    def __eq__(self, other):
        return self.nome == other.nome and self.id_programa == other.id_programa

    def __hash__(self):
        return hash((self.nome, self.id_programa))

# Lista de programas com seus respectivos comandos winget
programas_listagem = [
    Programa("PDF24 Creator", "geeksoftwareGmbH.PDF24Creator"),
    Programa("Google Chrome", "Google.Chrome"),
    Programa("7-Zip", "7zip.7zip"),
    Programa("Adobe Acrobat Reader (32-bit)", "Adobe.Acrobat.Reader.32-bit"),
    Programa("Lightshot", "Skillbrains.Lightshot"),
    Programa("Discord", "Discord.Discord"),
    Programa("NAPS2", "Cyanfish.NAPS2")
]

# Dicionário para armazenar IDs correspondentes
programas_ids = {programa.nome: programa.id_programa for programa in programas_listagem}

# Variáveis para controle
id_selecionado = None
checkboxes = {}
programas_selecionados = set()  # Usando um conjunto para evitar duplicatas

def atualizar_text_area():
    text_area.config(state=tk.NORMAL)  # Habilita a área de texto para edição
    text_area.delete(1.0, tk.END)  # Limpa a área de texto antes de adicionar novos itens
    
    # Adiciona os programas da lista de selecionados
    for programa in programas_selecionados:
        id_programa = programa.id_programa
        if id_programa and '.' in id_programa:
            text_area.insert(tk.END, f"{programa.nome} (ID: {id_programa})\n")
        else:
            text_area.insert(tk.END, f"{programa.nome} (ID não disponível ou inválido)\n")
    
    text_area.config(state=tk.DISABLED)  # Bloqueia a área de texto após a atualização

def on_program_click(event):
    selection = listbox.curselection()  # Pega a seleção atual
    if selection:
        index = selection[0]  # Pega o primeiro item selecionado
        nome_programa = listbox.get(index).strip()  # Obtém o texto correspondente ao índice
        if nome_programa in programas_ids:
            global id_selecionado
            id_selecionado = programas_ids[nome_programa]
            
            # Adiciona o programa selecionado à lista de programas selecionados
            programa = Programa(nome_programa, id_selecionado)
            programas_selecionados.add(programa)  # Usa um conjunto para evitar duplicatas
            atualizar_text_area()  # Atualiza a área de texto

def atualizar_programas_selecionados():
    # Limpa a lista atual
    programas_selecionados.clear()
    
    # Adiciona programas selecionados nos checkboxes
    for programa, var in checkboxes.items():
        if var.get():
            id_programa = programas_ids.get(programa)
            if id_programa and '.' in id_programa:
                programas_selecionados.add(Programa(programa, id_programa))  # Usa um conjunto para evitar duplicatas

    # Atualiza a área de texto após a seleção dos checkboxes
    atualizar_text_area()

def pesquisar_programas():
    termo = entry_pesquisa.get().strip()
    if termo:
        # Salva o estado atual dos checkboxes
        estados_checkboxes = {programa: var.get() for programa, var in checkboxes.items()}
        text_area.delete(1.0, tk.END)  # Limpa a área de texto
        global programas_ids
        programas_ids.update({programa.nome: programa.id_programa for programa in programas_listagem})  # Garantir que os IDs dos programas iniciais sejam mantidos

        def search_in_thread():
            try:
                resultado = subprocess.run(f'winget search {termo}', shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')

                linhas = resultado.stdout.strip().split('\n')

                nomes_unicos = set()  # Conjunto para armazenar nomes únicos
                listbox.delete(0, tk.END)  # Limpa o Listbox antes de adicionar novos itens

                programas_encontrados = []  # Nova lista de programas encontrados na pesquisa

                for linha in linhas[1:]:  # Ignorar a primeira linha de cabeçalho
                    partes = linha.split()
                    if partes:
                        nome_programa = partes[0]
                        id_programa = partes[1] if len(partes) > 1 else None

                        # Verifica se o ID é válido (contém um ponto)
                        if id_programa and '.' in id_programa:
                            if nome_programa not in nomes_unicos:
                                nomes_unicos.add(nome_programa)
                                if all(c.isalnum() or c.isspace() for c in nome_programa):
                                    listbox.insert(tk.END, nome_programa.strip())
                                    programas_encontrados.append(Programa(nome_programa.strip(), id_programa.strip()))

                # Atualiza o dicionário de IDs com os programas encontrados
                for programa in programas_encontrados:
                    programas_ids[programa.nome] = programa.id_programa

                # Restaura os estados dos checkboxes
                for programa, estado in estados_checkboxes.items():
                    if programa in checkboxes:
                        checkboxes[programa].set(estado)  # Restaura o estado do checkbox

                atualizar_programas_selecionados()  # Atualiza a seleção no Text Area

            except subprocess.CalledProcessError as e:
                messagebox.showerror("Erro", f"Erro ao pesquisar: {e}")

        threading.Thread(target=search_in_thread).start()

def instalar_programas():
    comandos = []

    # Adiciona o programa selecionado do listbox
    if id_selecionado:
        if '.' in id_selecionado:
            comandos.append(f'winget install {id_selecionado} --silent')

    # Adiciona programas selecionados nos checkboxes
    for programa in programas_selecionados:
        if programa.id_programa and '.' in programa.id_programa:
            comandos.append(f'winget install {programa.id_programa} --silent')

    if not comandos:
        messagebox.showwarning("Seleção vazia", "Nenhum programa selecionado.")
        return

    listbox.delete(0, tk.END)  # Limpa o Listbox para mensagens de status

    # Adiciona uma mensagem de "Instalando..."
    listbox.insert(tk.END, "Instalando programas, por favor aguarde...\n")
    listbox.yview(tk.END)  # Rola para baixo para mostrar a nova linha

    def install_in_thread():
        # Loop para instalar cada programa individualmente
        for comando in comandos:
            listbox.yview(tk.END)
            programa_nome = [k for k, v in programas_ids.items() if v in comando][0]
            try:
                # Executa o comando e espera até que termine
                resultado = subprocess.run(comando, shell=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                # Se a execução for bem-sucedida, adicione uma mensagem de sucesso
                listbox.insert(tk.END, f"{programa_nome} já está instalado!\n")
            except subprocess.CalledProcessError as e:
                # Se houver erro, adicione uma mensagem de erro
                listbox.insert(tk.END, f"Erro ao instalar: {str(e)}\n")
                continue

        # Atualiza a interface após a conclusão da instalação
        root.after(0, lambda: messagebox.showinfo("Concluído", "Instalação concluída!\n" + "\n".join(listbox.get(0, tk.END))))
        
        # Remove a mensagem de "Instalando..."
        listbox.delete(0)  # Remove a primeira linha que diz "Instalando programas..."

    threading.Thread(target=install_in_thread).start()

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
for programa in programas_listagem:
    var = BooleanVar()
    checkbox = tk.Checkbutton(root, text=programa.nome, variable=var, command=atualizar_programas_selecionados)
    checkbox.pack(anchor=tk.W)
    checkboxes[programa.nome] = var

# Área de texto para exibir programas selecionados
text_area = Text(root, width=60, height=10)
text_area.pack(pady=10)
text_area.config(state=tk.NORMAL)  # Define o estado inicial como normal

# Botão para instalar programas
btn_instalar = tk.Button(root, text="Instalar Programas", command=instalar_programas)
btn_instalar.pack(pady=10)

root.mainloop()
