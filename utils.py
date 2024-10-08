import subprocess

def verificar_politica_execucao():
    try:
        resultado = subprocess.run('powershell -Command "Get-ExecutionPolicy"', check=True, shell=True, capture_output=True, text=True)
        politica_atual = resultado.stdout.strip()
        if politica_atual != "Unrestricted":
            subprocess.run('powershell -Command "Set-ExecutionPolicy Unrestricted -Scope Process -Force"', check=True, shell=True)
            print("Política de execução alterada para 'Unrestricted'.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao verificar ou alterar a política de execução: {e}")
