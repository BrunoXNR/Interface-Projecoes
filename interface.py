# Importação das Bibliotecas Necessárias

import os
import sys
import re
import warnings
from datetime import datetime
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import mplcursors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import FuncFormatter

import customtkinter as ctk
from tkinter import messagebox

from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.lib.colors import Color

from models import CalculosProjecao # Importação da classe com as funções que fazem os cálculos financeiros e de projeção



class Interface: # Classe com as configurações da janela de interface gráfica

    @staticmethod
    def resource_path(relative_path): # Função para garantir que as dependências do projeto sejam encontradas e executadas após a distribuição com PyInstaller
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)


    def iniciar(self): # Função para executar o programa e gerar a janela de interface
        self.app.mainloop()


    def __init__(self): # Configurações iniciais da janela de interface
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.app = ctk.CTk()
        self.app.title("Projeções Financeiras")
        self.app.geometry("1000x1600")
        self.app.iconbitmap(Interface.resource_path("utils/logofh.ico"))

        # Inicializa as variáveis dos inputs a serem coletados a partir de inserção pelo usuário na janela de interface
        self.num_periodos = 0
        self.periodos_entries = []
        self.duracao_entries = []
        self.valores_aportes = []
        self.duracoes_aportes = []

        self.configurar_janela()

        self.app.grid_rowconfigure(0, weight=1)
        self.app.grid_columnconfigure(0, weight=1)


    def formatar_input(self, event=None, entry=None): # Função para formatação dos valores digitados nos campos de input
        
        texto = entry.get().replace(".", "").replace(",", "").strip()
        
        
        if texto and texto.isdigit():
            
            valor = int(texto) / 100 # Converte a string para inteiro e divide por 100 para formatar como float
            valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            
            entry.delete(0, ctk.END)
            entry.insert(0, valor_formatado)
        elif not texto:
            
            entry.delete(0, ctk.END)


    def configurar_janela(self): # Função para configurar a hierarquia dos frames na janela de interface
        
        # Frame Principal (main frame)
        self.frame_main = ctk.CTkFrame(master=self.app)
        self.frame_main.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.frame_main.grid_rowconfigure(0, weight=1)  # Frame de Inputs
        self.frame_main.grid_rowconfigure(1, weight=50)  # Frame de Resultados
        self.frame_main.grid_columnconfigure(0, weight=1)

        # Frame para os campos de input das variáveis principais
        self.frame_inputs = ctk.CTkScrollableFrame(master=self.frame_main)
        self.frame_inputs.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")

        # Frame para os campos de display do gráfico e dos resultados
        self.frame_resultados = ctk.CTkScrollableFrame(master=self.frame_main)
        self.frame_resultados.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")

        self.criar_campos_inputs()


    def criar_campos_inputs(self):  # Função para criação e configuração dos campos de inputs
        self.frame_inputs.grid_columnconfigure((0, 1), weight=5) 
        self.frame_inputs.grid_columnconfigure(2, weight=3) 
        self.frame_inputs.grid_columnconfigure(3, weight=10)
        
        # Input do Capital Inicial
        self.label_capital = ctk.CTkLabel(master=self.frame_inputs, text="Capital Inicial (R$):", font=("Arial", 13, "bold"))
        self.label_capital.grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.entry_capital = ctk.CTkEntry(master=self.frame_inputs, width=150)
        self.entry_capital.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Vincula os eventos de formatação nos inputs do tipo 'moeda'
        self.entry_capital.bind("<KeyRelease>", lambda event: self.formatar_input(event, self.entry_capital))
        self.entry_capital.bind("<FocusOut>", lambda event: self.formatar_input(event, self.entry_capital))

        # Input do Prazo
        self.label_prazo = ctk.CTkLabel(master=self.frame_inputs, text="Prazo (Anos):", font=("Arial", 13, "bold"))
        self.label_prazo.grid(row=1, column=0, padx=5, pady=5, sticky='ew')
        self.entry_prazo = ctk.CTkEntry(master=self.frame_inputs, width=150)
        self.entry_prazo.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        # Input da Taxa de Juros
        self.label_taxa = ctk.CTkLabel(master=self.frame_inputs, text="Taxa de Juros (%):", font=("Arial", 13, "bold"))
        self.label_taxa.grid(row=2, column=0, padx=5, pady=5, sticky='ew')
        self.entry_taxa = ctk.CTkEntry(master=self.frame_inputs, width=150)
        self.entry_taxa.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        self.combo_taxa = ctk.CTkComboBox(master=self.frame_inputs, values=["Anual", "Mensal"], width=150) # Possibilita escolher entre 'Anual' e 'Mensal'
        self.combo_taxa.grid(row=2, column=2, padx=5, pady=5, sticky='w')
        self.combo_taxa.set("Anual")

        # Input da Taxa de Inflação
        self.label_inflacao = ctk.CTkLabel(master=self.frame_inputs, text="Taxa de Inflação Esperada (%):", font=("Arial", 13, "bold"))
        self.label_inflacao.grid(row=3, column=0, padx=5, pady=5, sticky='ew')
        self.entry_inflacao = ctk.CTkEntry(master=self.frame_inputs, width=150)
        self.entry_inflacao.grid(row=3, column=1, padx=5, pady=5, sticky='w')

        self.combo_inflacao = ctk.CTkComboBox(master=self.frame_inputs, values=["Anual", "Mensal"], width=150) # Possibilita escolher entre 'Anual' e 'Mensal'
        self.combo_inflacao.grid(row=3, column=2, padx=5, pady=5, sticky='w')
        self.combo_inflacao.set("Anual")

        # Input da Quantidade de Períodos de Aporte
        self.label_num_periodos = ctk.CTkLabel(master=self.frame_inputs, text="Número de Períodos de Aporte:", font=("Arial", 13, "bold"))
        self.label_num_periodos.grid(row=5, column=0, padx=5, pady=5, sticky='ew')
        self.entry_num_periodos = ctk.CTkEntry(master=self.frame_inputs, width=150)
        self.entry_num_periodos.grid(row=5, column=1, padx=5, pady=5, sticky='w')

        # Botão para adicionar os campos de input dos períodos de aporte
        self.button_adicionar_periodos = ctk.CTkButton(master=self.frame_inputs, text="Adicionar Períodos", command=self.abrir_popup)
        self.button_adicionar_periodos.grid(row=0, column=3, padx=10, pady=7, sticky='w')

        # Botão para realizar o cálculo da projeção
        self.button_calcular = ctk.CTkButton(master=self.frame_inputs, text="Calcular Projeção", command=self.calcular_projecao)
        self.button_calcular.grid(row=1, column=3, padx=10, pady=7, sticky='w')

        # Botão para limpar os campos de input
        self.button_limpar = ctk.CTkButton(master=self.frame_inputs, text="Limpar", command=self.limpar_campos)
        self.button_limpar.grid(row=2, column=3, padx=10, pady=7, sticky='w')

        # Botão para exportar o PDF com os resultados
        self.button_export_pdf = ctk.CTkButton(master=self.frame_inputs, text="Exportar PDF", command=self.export_pdf)
        self.button_export_pdf.grid(row=3, column=3, padx=10, pady=7, sticky='w')


    def abrir_popup(self): # Função que cria uma janela pop-up para coleta dos inputs de aportes por período (prazo e valores)
        try:
            self.num_periodos = int(self.entry_num_periodos.get())
            if self.num_periodos < 0:
                messagebox.showerror("Erro", "O número de períodos não pode ser negativo")
                return
            if self.num_periodos == 0:
                self.valores_aportes.clear()
                self.duracoes_aportes.clear()
                messagebox.showinfo("Aviso", "Nenhum período de aporte definido. O cálculo será realizado sem aportes.")
                return
        except ValueError:
            messagebox.showerror("Erro", "Ocorreu um erro inesperado")
            return

        self.popup_periodos = ctk.CTkToplevel(self.app)
        self.popup_periodos.title("Períodos de Aporte")
        self.popup_periodos.geometry("700x500")
        self.popup_periodos.grab_set()

        # Configura a janela pop-up como um scrollable frame
        self.scroll_popup = ctk.CTkScrollableFrame(master=self.popup_periodos)
        self.scroll_popup.pack(padx=10, pady=10, fill="both", expand=True)

        # Limpa listas anteriores
        self.periodos_entries.clear()
        self.duracao_entries.clear()

        # Cria as linhas para inputs de acordo com o número de períodos inputado pelo usuário
        for i in range(self.num_periodos):
            label_aporte = ctk.CTkLabel(master=self.scroll_popup, text=f"Aporte Mensal Período {i+1} (R$):", font=("Arial", 13))
            label_aporte.grid(row=i, column=0, padx=5, pady=5, sticky='w')
            entry_aporte = ctk.CTkEntry(master=self.scroll_popup)
            entry_aporte.grid(row=i, column=1, padx=5, pady=5, sticky='w')
            entry_aporte.bind("<KeyRelease>", lambda event, e=entry_aporte: self.formatar_input(event, e))
            entry_aporte.bind("<FocusOut>", lambda event, e=entry_aporte: self.formatar_input(event, e))
            self.periodos_entries.append(entry_aporte)

            label_duracao = ctk.CTkLabel(master=self.scroll_popup, text=f"Duração (Anos):", font=("Arial", 13))
            label_duracao.grid(row=i, column=2, padx=5, pady=5, sticky='w')
            entry_duracao = ctk.CTkEntry(master=self.scroll_popup)
            entry_duracao.grid(row=i, column=3, padx=5, pady=5, sticky='w')
            self.duracao_entries.append(entry_duracao)

        # Botão para salvar os dados e fechar a janela de pop-up
        btn_salvar = ctk.CTkButton(master=self.popup_periodos, text="Salvar Valores", command=self.salvar_dados_periodos)
        btn_salvar.pack(pady=10)


    def salvar_dados_periodos(self): # Função para coletar os dados de input dos períodos de aporte e alimentar a função que faz o cálculo da projeção
        self.valores_aportes.clear()
        self.duracoes_aportes.clear()

        # Faz a verificação do prazo total da projeção x soma dos prazos inputados
        try:
            prazo_anos = int(self.entry_prazo.get())
            if prazo_anos <= 0:
                raise ValueError("O prazo deve ser maior que zero")
            prazo_meses = prazo_anos * 12
        except ValueError:
            messagebox.showerror("Erro", "Informe um prazo válido em anos.")
            return

        # Faz a verificação dos períodos de aporte
        total_duracao_aportes = 0
        for i in range(self.num_periodos):
            valor_aporte = self.periodos_entries[i].get()
            duracao = self.duracao_entries[i].get()

            if not valor_aporte or not duracao:
                messagebox.showerror("Erro", f"Preencha todos os campos do período {i+1}")
                return

            try:
                float(valor_aporte.replace(".", "").replace(",", "."))
                duracao_anos = int(duracao)
                if duracao_anos <= 0:
                    raise ValueError(f"A duração do período {i+1} deve ser maior que zero")
                total_duracao_aportes += duracao_anos * 12
            except ValueError:
                messagebox.showerror("Erro", f"Valores inválidos no período {i+1}. Insira números válidos.")
                return

            self.valores_aportes.append(valor_aporte)
            self.duracoes_aportes.append(duracao)

        # Faz a verificação de se a soma dos períodos de aporte excede o prazo total da projeção
        if total_duracao_aportes > prazo_meses:
            messagebox.showerror("Erro", "A soma dos períodos de aporte excede o prazo total da projeção.")
            return

        # Exibe mensagem de confirmação com os valores salvos
        mensagem = "Dados Inputados:\n" + "\n".join(
            f"Período {i+1}: R$ {self.valores_aportes[i]} por mês durante {self.duracoes_aportes[i]} anos"
            for i in range(self.num_periodos)
        )
        messagebox.showinfo("Sucesso!", mensagem)

        self.popup_periodos.destroy()


    def limpar_campos(self): # Função para limpar os campos de input
        self.entry_capital.delete(0, 'end')
        self.entry_prazo.delete(0, 'end')
        self.entry_taxa.delete(0, 'end')
        self.entry_num_periodos.delete(0, 'end')
        self.entry_inflacao.delete(0, 'end')
        self.valores_aportes.clear()
        self.duracoes_aportes.clear()
        self.periodos_entries.clear()
        self.duracao_entries.clear()

        for widget in self.frame_resultados.winfo_children():
            widget.destroy()


    def export_pdf(self): # Função para calcular a projeção (para inserção no relatório em PDF)
        try:
            capital_str = self.entry_capital.get().replace(".", "").replace(",", ".")
            capital_inicial = int(float(capital_str))
            if capital_inicial < 0:
                raise ValueError("O capital inicial não pode ser negativo")

            prazo_anos = int(self.entry_prazo.get())
            if prazo_anos <= 0:
                raise ValueError("O prazo deve ser maior que zero")

            taxa_juros = float(self.entry_taxa.get()) / 100
            if taxa_juros < 0:
                raise ValueError("A taxa de juros não pode ser negativa")

            if self.combo_taxa.get() == 'Anual':
                taxa_juros = (1 + taxa_juros) ** (1 / 12) - 1

            taxa_inflacao = float(self.entry_inflacao.get()) / 100
            if taxa_inflacao < 0:
                raise ValueError("A taxa de inflação não pode ser negativa")
            
            if self.combo_inflacao.get() == 'Anual':
                taxa_inflacao = (1 + taxa_inflacao) ** (1 / 12) - 1

            taxa_juros_real = ((1 + taxa_juros) / (1 + taxa_inflacao)) - 1 

            aportes_por_periodo = []
            total_aportes = 0

            for i in range(self.num_periodos):
                aporte_str = self.valores_aportes[i].replace(".", "").replace(",", ".")
                aporte = int(float(aporte_str))
                if aporte < 0:
                    raise ValueError(f"O aporte do período {i+1} não pode ser negativo")
                
                duracao_anos = int(self.duracoes_aportes[i])
                if duracao_anos <= 0:
                    raise ValueError(f"A duração do período {i+1} deve ser maior que zero")
                
                duracao_meses = duracao_anos * 12
                aportes_por_periodo.append((aporte, duracao_meses))
                total_aportes += aporte * duracao_meses

            prazo_meses = prazo_anos * 12


            # CHAMADAS DAS FUNÇÕES PARA O CÁLCULO E COLETA DOS DADOS PARA GERAR O RELATÓRIO EM PDF COM OS RESULTADOS

            # VALOR FUTURO COM APORTES (NOMINAL)
            valor_futuro_final, patrimonio_mensal = CalculosProjecao.valor_futuro_ant(capital_inicial, taxa_juros, aportes_por_periodo, prazo_meses) 

            # VALOR FUTURO SEM APORTES (NOMINAL)
            valor_futuro_sem_aporte_final, patrimonio_mensal_sem_aporte = CalculosProjecao.valor_futuro_sem_aportes(capital_inicial, taxa_juros, prazo_meses) 

            # VALOR FUTURO COM APORTES (REAL)
            valor_futuro_final_real, patrimonio_mensal_real = CalculosProjecao.valor_futuro_ant(capital_inicial, taxa_juros_real, aportes_por_periodo, prazo_meses)

            # VALOR FUTURO SEM APORTES (NOMINAL)
            valor_futuro_sem_aporte_final_real, patrimonio_mensal_sem_aporte_real = CalculosProjecao.valor_futuro_sem_aportes(capital_inicial, taxa_juros_real, prazo_meses)

            # RENDIMENTOS JUROS
            rendimento_juros = CalculosProjecao.rendimento_juros(valor_futuro_final, capital_inicial, total_aportes)
                
            # RENDA PERPÉTUA ou VITALÍCIA em TERMOS REAIS
            renda_perpetua = CalculosProjecao.renda_perpetua(valor_futuro_final_real, taxa_juros_real)

            # Chamada da função para calcular o valor TOTAL DE APORTES
            valor_total_aportes = CalculosProjecao.total_aportes(aportes_por_periodo)

            # Abre um caixa de input para a COLETA DA SIGLA OU NOME DO RELATÓRIO
            adicionar_sigla = ctk.CTkInputDialog(text='Insira a sigla ou nome do cliente:', title='Sigla do Cliente').get_input() 

            if not adicionar_sigla: # Se não for fornecido uma sigla o PDF é gerado sem sigla
                messagebox.showwarning(title="Atenção: Sigla não inserida", message="O relatório será gerado sem uma sigla", icon='info')
                adicionar_sigla = ""

            # Chamada do método que EXPORTA O ARQUIVO PDF
            ExportarPDF.gerar_pdf(capital_inicial, prazo_anos, taxa_juros, valor_futuro_final, valor_futuro_sem_aporte_final, rendimento_juros, patrimonio_mensal, 
                                  patrimonio_mensal_real, patrimonio_mensal_sem_aporte, prazo_meses, aportes_por_periodo, renda_perpetua, adicionar_sigla, 
                                  valor_futuro_final_real, taxa_juros_real, taxa_inflacao,  valor_total_aportes, valor_futuro_sem_aporte_final_real, 
                                  patrimonio_mensal_sem_aporte_real)

        except ValueError as e:
            messagebox.showerror("Erro de Entrada", str(e))

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {str(e)}")


    def calcular_projecao(self): # Função para calcular a projeção (para inserção na janela da interface)
        try:
            capital_str = self.entry_capital.get().replace(".", "").replace(",", ".")
            capital_inicial = int(float(capital_str))
            if capital_inicial < 0:
                raise ValueError("O capital inicial não pode ser negativo")
            
            prazo_anos = int(self.entry_prazo.get())
            if prazo_anos <= 0:
                raise ValueError("O prazo deve ser maior que zero")

            taxa_juros = float(self.entry_taxa.get()) / 100
            if taxa_juros < 0:
                raise ValueError("A taxa de juros não pode ser negativa")

            if self.combo_taxa.get() == 'Anual':
                taxa_juros = (1 + taxa_juros) ** (1 / 12) - 1

            taxa_inflacao = float(self.entry_inflacao.get()) / 100
            if taxa_inflacao < 0:
                raise ValueError("A taxa de inflação não pode ser negativa")
            
            if self.combo_inflacao.get() == 'Anual':
                taxa_inflacao = (1 + taxa_inflacao) ** (1 / 12) - 1

            taxa_juros_real = ((1 + taxa_juros) / (1 + taxa_inflacao)) - 1 

            aportes_por_periodo = []
            total_aportes = 0
            total_duracao_aportes = 0

            for i in range(self.num_periodos):
                aporte_str = self.valores_aportes[i].replace(".", "").replace(",", ".")
                aporte = int(float(aporte_str))
                if aporte < 0:
                    raise ValueError(f"O aporte do período {i+1} não pode ser negativo")
                
                duracao_anos = int(self.duracoes_aportes[i])
                if duracao_anos <= 0:
                    raise ValueError(f"A duração do período {i+1} deve ser maior que zero")
                
                duracao_meses = duracao_anos * 12 
                aportes_por_periodo.append((aporte, duracao_meses))
                total_aportes += aporte * duracao_meses
                total_duracao_aportes += duracao_meses

            prazo_meses = prazo_anos * 12

            if total_duracao_aportes > prazo_meses:
                raise ValueError("A soma dos períodos de aportes excede o prazo total da projeção")


            # Chamada da função para calcular o VALOR FUTURO COM APORTES considerando TAXA DE JUROS NOMINAL
            valor_futuro_final, patrimonio_mensal = CalculosProjecao.valor_futuro_ant(
                capital_inicial, taxa_juros, aportes_por_periodo, prazo_meses)

            # Chamada da função para calcular o VALOR FUTURO SEM APORTES considerando TAXA DE JUROS NOMINAL
            valor_futuro_sem_aporte_final, patrimonio_mensal_sem_aporte = CalculosProjecao.valor_futuro_sem_aportes(
                capital_inicial, taxa_juros, prazo_meses)

            # Chamada da função para calcular o VALOR FUTURO COM APORTES considerando TAXA DE JUROS REAL
            valor_futuro_final_real, patrimonio_mensal_real = CalculosProjecao.valor_futuro_ant(
                capital_inicial, taxa_juros_real, aportes_por_periodo, prazo_meses)
            
            # Chamada da função para calcular o VALOR FUTURO SEM APORTES considernado TAXA DE JUROS REAL
            valor_futuro_sem_aporte_final_real, patrimonio_mensal_sem_aporte_real = CalculosProjecao.valor_futuro_sem_aportes(
                capital_inicial, taxa_juros_real, prazo_meses) 

            # Chamada da função para calcular o valor dos RENDIMENTOS (JUROS)
            rendimento_juros = CalculosProjecao.rendimento_juros(valor_futuro_final, capital_inicial, total_aportes) 

            # Chamada da função para calcular o valor da RENDA PERPETUA ou VITALÍCIA em TERMOS REAIS
            renda_perpetua = CalculosProjecao.renda_perpetua(valor_futuro_final_real, taxa_juros_real)

            # Chamada da função para calcular o valor TOTAL DE APORTES
            valor_total_aportes = CalculosProjecao.total_aportes(aportes_por_periodo)
            
            # Chamada da função para fazer o display dos resultados na janela de interface
            self.exibir_resultados(valor_futuro_final, valor_futuro_sem_aporte_final, rendimento_juros, renda_perpetua, patrimonio_mensal, 
                                   patrimonio_mensal_sem_aporte, patrimonio_mensal_real, prazo_meses, valor_futuro_final_real, valor_total_aportes, 
                                   valor_futuro_sem_aporte_final_real, patrimonio_mensal_sem_aporte_real)

            # Chamada da função para plotar o gráfico da projeção na janela de interface
            PlotagemGrafico.plotar_grafico(self.frame_resultados, patrimonio_mensal, patrimonio_mensal_sem_aporte, patrimonio_mensal_real, prazo_meses, 
                                           patrimonio_mensal_sem_aporte_real)

        except ValueError as e:
            messagebox.showerror("Erro de Entrada", str(e))

        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {str(e)}")


    # Função para plotagem do gráfico e criação / exibição do frame de resultados do projeção (campos ao lado direito do gráfico)
    def exibir_resultados(self, valor_futuro_final, valor_futuro_sem_aporte_final, rendimento_juros, renda_perpetua, patrimonio_mensal, patrimonio_mensal_sem_aporte, 
                      patrimonio_mensal_real, prazo_meses, valor_futuro_final_real, valor_total_aportes, valor_futuro_sem_aporte_final_real, patrimonio_mensal_sem_aporte_real):
    
        for widget in self.frame_resultados.winfo_children(): # Limpa os widgets do frame de resultados
            widget.destroy()

        # Configuração do layout do frame_resultados
        self.frame_resultados.grid_columnconfigure(0, weight=4)  # Coluna para o gráfico (mais espaço)
        self.frame_resultados.grid_columnconfigure(1, weight=1)  # Coluna para os resultados (menos espaço)
        self.frame_resultados.grid_rowconfigure(0, weight=1)  # Permite expansão vertical

        # Plotagem do gráfico à esquerda
        fig, ax = plt.subplots(figsize=(8, 6))  # Aumenta altura do gráfico (de 4 para 6)
        ax.plot(range(1, prazo_meses + 1), patrimonio_mensal, label="Valor Nominal com Aporte", color="blue")
        ax.plot(range(1, prazo_meses + 1), patrimonio_mensal_sem_aporte, label="Valor Nominal Sem Aporte", color="green")
        ax.plot(range(1, prazo_meses + 1), patrimonio_mensal_real, label="Valor Real com Aporte", color="red")
        ax.set_title("Projeção Patrimonial")


        canvas = FigureCanvasTkAgg(fig, master=self.frame_resultados) # Faz a plotagem do gráfico no frame de resultados
        canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10, sticky="nsew")  # sticky="nsew" para expansão
        canvas.draw()

        # Alinha os campos com os resultados à direita do gráfico
        resultados_frame = ctk.CTkFrame(master=self.frame_resultados)
        resultados_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")  # sticky="nsew" para expansão
        resultados_frame.grid_columnconfigure(0, weight=1)
        resultados_frame.grid_rowconfigure(0, weight=1)  # Expansão para grupo1
        resultados_frame.grid_rowconfigure(2, weight=1)  # Expansão para grupo2

        # Grupo 1: Valores Finais
        grupo1_frame = ctk.CTkFrame(master=resultados_frame)
        grupo1_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")  # sticky="nsew" para expansão
        grupo1_frame.grid_columnconfigure(0, weight=1)
        grupo1_frame.grid_rowconfigure((0, 1, 2), weight=1)  # Expansão para cada resultado

        # Valor Final Nominal com Aporte
        frame_valor_com_aporte = ctk.CTkFrame(master=grupo1_frame, fg_color="#404040", border_color="#4A90E2", border_width=1)
        frame_valor_com_aporte.grid(row=0, column=0, padx=5, pady=2, sticky="ew")
        ctk.CTkLabel(master=frame_valor_com_aporte, text=f"Valor Nominal com Aporte: R$ {valor_futuro_final:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    font=("Arial", 16, "bold"), text_color="#E0E0E0").pack(pady=10, expand=True)

        # Valor Final Real com Aporte
        frame_valor_com_aporte_real = ctk.CTkFrame(master=grupo1_frame, fg_color="#404040", border_color="#4A90E2", border_width=1)
        frame_valor_com_aporte_real.grid(row=1, column=0, padx=5, pady=2, sticky="ew")
        ctk.CTkLabel(master=frame_valor_com_aporte_real, text=f"Valor Real com Aporte: R$ {valor_futuro_final_real:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    font=("Arial", 16, "bold"), text_color='#E0E0E0').pack(pady=10, expand=True)

        # Valor Final Nominal sem Aporte
        frame_valor_sem_aporte = ctk.CTkFrame(master=grupo1_frame, fg_color='#404040', border_color="#4A90E2", border_width=1)
        frame_valor_sem_aporte.grid(row=2, column=0, padx=5, pady=2, sticky="ew")
        ctk.CTkLabel(master=frame_valor_sem_aporte, text=f"Valor Nominal sem Aporte: R$ {valor_futuro_sem_aporte_final:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    font=("Arial", 16, "bold"), text_color="#E0E0E0").pack(pady=10, expand=True)
        
        # Valor Final Real sem Aporte
        frame_valor_sem_aporte_real = ctk.CTkFrame(master=grupo1_frame, fg_color='#404040', border_color="#4A90E2", border_width=1)
        frame_valor_sem_aporte_real.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(master=frame_valor_sem_aporte_real, text=f"Valor Real sem Aporte: R$ {valor_futuro_sem_aporte_final_real:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."), 
                     font=("Arial", 16, "bold")).pack(pady=10)

        # Linha divisória
        linha_divisoria = ctk.CTkFrame(master=resultados_frame, height=2, fg_color="white", border_color="white")
        linha_divisoria.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Grupo 2: Rendimento, Renda e Aportes
        grupo2_frame = ctk.CTkFrame(master=resultados_frame)
        grupo2_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")  # sticky="nsew" para expansão
        grupo2_frame.grid_columnconfigure(0, weight=1)
        grupo2_frame.grid_rowconfigure((0, 1, 2), weight=1)  # Expansão para cada resultado

        # Rendimento Total (Apenas os Juros)
        frame_rendimento_com_aporte = ctk.CTkFrame(master=grupo2_frame, fg_color='#404040', border_color="#4A90E2", border_width=1)
        frame_rendimento_com_aporte.grid(row=0, column=0, padx=5, pady=2, sticky="ew")
        ctk.CTkLabel(master=frame_rendimento_com_aporte, text=f"Total de Rendimentos dos Juros: R$ {rendimento_juros:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    font=("Arial", 16, "bold"), text_color='#E0E0E0').pack(pady=10, expand=True)

        # Renda Perpétua ou Vitalícia
        frame_renda_passiva = ctk.CTkFrame(master=grupo2_frame, fg_color='#404040', border_color="#4A90E2", border_width=1)
        frame_renda_passiva.grid(row=1, column=0, padx=5, pady=2, sticky="ew")
        ctk.CTkLabel(master=frame_renda_passiva, text=f"Renda Perpétua: R$ {renda_perpetua:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    font=("Arial", 16, "bold"), text_color='#E0E0E0').pack(pady=10, expand=True)

        # Valor Total de Aportes (soma)
        frame_total_aportes = ctk.CTkFrame(master=grupo2_frame, fg_color='#404040', border_color="#4A90E2", border_width=1)
        frame_total_aportes.grid(row=2, column=0, padx=5, pady=2, sticky="ew")
        ctk.CTkLabel(master=frame_total_aportes, text=f"Valor Total de Aportes: R$ {valor_total_aportes:,.0f}".replace(",", "X").replace(".", ",").replace("X", "."),
                    font=("Arial", 16, "bold"), text_color='#E0E0E0').pack(pady=10, expand=True)



class PlotagemGrafico: # Classe com as configurações de plotagem do gráfico da projeção para a janela de interface

    @staticmethod
    def plotar_grafico(frame_resultados, patrimonio_mensal, patrimonio_mensal_sem_aporte, patrimonio_mensal_real, prazo_meses, patrimonio_mensal_sem_aporte_real):
        
        # Criação do DataFrame para armazenar os resultados da projeção
        df_resultados = pd.DataFrame({
            'Meses': np.arange(1, prazo_meses + 1),
            'Valor Nominal com Aporte': patrimonio_mensal,
            'Valor Nominal sem Aporte': patrimonio_mensal_sem_aporte,
            'Valor Real com Aporte': patrimonio_mensal_real,
            'Valor Real sem Aporte': patrimonio_mensal_sem_aporte_real
        })

        # Configurações da Figura e do Gráfico
        fig, ax = plt.subplots(figsize=(8, 4)) # Dimensões do gráfico
        fig.patch.set_facecolor("#2C2F33") # Cor de fundo da área de plotagem
        ax.set_facecolor("#2C2F33") # Cor de fundo do gráfico
        ax.set_xlabel('Meses') # Título do Eixo X
        ax.set_ylabel('Valor') # Título do Eixo Y

        # Plotagem das Linhas (com verificação para criação dinâmica da legenda)
        if patrimonio_mensal and any(patrimonio_mensal):
            sns.lineplot(x='Meses', y='Valor Nominal com Aporte', data=df_resultados, ax=ax, label='Valor Nominal com Aporte', color='#1E90FF', linestyle='--', linewidth=2) # Azul
        
        if patrimonio_mensal_sem_aporte and any(patrimonio_mensal_sem_aporte):
            sns.lineplot(x='Meses', y='Valor Real com Aporte', data=df_resultados, ax=ax, label='Valor Real com Aporte', color='#FFFFFF', linestyle='-', linewidth=2) # Branco
        
        if patrimonio_mensal_real and any(patrimonio_mensal_real):
            sns.lineplot(x='Meses', y='Valor Nominal sem Aporte', data=df_resultados, ax=ax, label='Valor Nominal sem Aporte', color='#A6D425', linestyle='--', linewidth=2) # Verde
        
        if patrimonio_mensal_sem_aporte_real and any(patrimonio_mensal_sem_aporte_real):
            sns.lineplot(x='Meses', y='Valor Real sem Aporte', data=df_resultados, ax=ax, label='Valor Real sem Aporte', color="#FF0000", linestyle='--', linewidth=2) # Vermelho

        # Configuração das Linhas de Grade e Bordas da Plotagem
        ax.grid(True, which='major', axis='x', color='gray', linestyle='--', linewidth=0.3)
        ax.spines['top'].set_color('#2C2F33')
        ax.spines['right'].set_color('#2C2F33')
        ax.spines['left'].set_color('#FFFFFF')
        ax.spines['bottom'].set_color('#FFFFFF')

        # Configuração dos Eixos e Títulos
        ax.xaxis.label.set_color('#FFFFFF')
        ax.yaxis.label.set_color('#FFFFFF')
        ax.tick_params(axis='x', colors='#FFFFFF')
        ax.tick_params(axis='y', colors='#FFFFFF')

        # Configuração do Intervalo dos Valores no Eixo X (De 12 em 12 meses)
        ax.xaxis.set_major_locator(plt.MultipleLocator(12))
        ax.xaxis.set_minor_locator(plt.MultipleLocator(1))

        # Configuração de Limite das Dimensões da Plotagem
        ax.set_xlim([1, prazo_meses])


        # Função para formatar os valores do eixo Y
        def formatar_valores_y(valor, pos): 
            return f"{valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

        ax.yaxis.set_major_formatter(FuncFormatter(formatar_valores_y))


        # Configuração do cursor interativo do gráfico
        cursor = mplcursors.cursor(ax, hover=True)

        @cursor.connect("add") # Cria um cursor interativo para exibir o valor em determinado ponto do gráfico
        def on_add(sel):
            sel.annotation.set_text(f"Mês: {int(sel.target[0])}\nValor: R$ {sel.target[1]:,.2f}")
            sel.annotation.get_bbox_patch().set(facecolor="#1E90FF", alpha=0.8)


        def on_enter(event): # Cria o cursor quando o mouse entra na área de plotagem do gráfico
            nonlocal cursor
            if cursor is None:
                cursor = mplcursors.cursor(ax, hover=True)

            @cursor.connect("add")
            def on_add(sel):
                sel.annotation.set_text(f"Mês: {int(sel.target[0])}\nValor: R$ {sel.target[1]:,.2f}")
                sel.annotation.get_bbox_patch().set(facecolor="#1E90FF", alpha=0.8)


        def on_leave(event): # Remove o cursor quando o mouse sai da área de plotagem do gráfico
            nonlocal cursor
            if cursor is not None:
                cursor.remove()
                cursor = None
        
        # Converte o gráfico para um widget do Tkinter
        canvas = FigureCanvasTkAgg(fig, master=frame_resultados) 
        
        # Conectando os eventos de entrada e saída do mouse da área de plotagem
        canvas.mpl_connect('figure_leave_event', on_leave)
        canvas.mpl_connect('figure_enter_event', on_enter)

        # Posiciona e exibe o gráfico na janela de interface
        canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        canvas.draw() # Renderiza o gráfico na janela de interface



class PlotagemGraficoPDF:  # Classe com as configurações de plotagem do gráfico da projeção para o arquivo PDF
    @staticmethod
    def criar_grafico_pdf(patrimonio_mensal_real, patrimonio_mensal, patrimonio_mensal_sem_aporte, prazo_meses, patrimonio_mensal_sem_aporte_real):
        df_resultados_pdf = pd.DataFrame({
            'Meses': np.arange(1, prazo_meses + 1),
            'Valor Nominal com Aporte': patrimonio_mensal,
            'Valor Nominal sem Aporte': patrimonio_mensal_sem_aporte,
            'Valor Real com Aporte': patrimonio_mensal_real,
            'Valor Real sem Aporte': patrimonio_mensal_sem_aporte_real
        })

        # Configurações da Figura e do Gráfico
        fig, ax = plt.subplots(figsize=(16, 10)) # Dimensões do Gráfico
        plt.subplots_adjust(left=0.07, right=0.97, top=0.95, bottom=0.15) # Ajustes no Posicionamento do Gráfico
        fig.patch.set_facecolor('#FFFFFF') # Cor de Fundo da Figura
        ax.set_facecolor('#FFFFFF') # Cor de Fundo da Área de Plotagem
        ax.set_xlabel('Ano') # Nome Eixo X
        ax.set_ylabel('Valor (R$)') # Nome Eixo Y
        ax.tick_params(axis='both', labelsize=20) # Parâmetros de Configurações das Labels dos Eixos
        ax.xaxis.label.set_size(20) # Tamanho do Nome Eixo X
        ax.yaxis.label.set_size(20) # Tamanho do Nome Eixo Y


        # Séries de Valores para Plotagem
        series_info = [
            ("Valor Nominal com Aporte", patrimonio_mensal, '#1F77B4', '--'), # Azul
            ("Valor Real com Aporte", patrimonio_mensal_real, '#FF7F0E', '-'), # Laranja
            ("Valor Nominal sem Aporte", patrimonio_mensal_sem_aporte, "#000000", '--'), # Preto
            ("Valor Real sem Aporte", patrimonio_mensal_sem_aporte_real, '#FF0000', '-' ) # Vermelho
            ]

        # Plotagem das Linhas no Gráfico (com caixas de anotação para o valor final)
        for nome, serie, cor, estilo in series_info:
            if serie and any(serie):
                sns.lineplot(x='Meses', y=nome, data=df_resultados_pdf, ax=ax,
                             label=nome, color=cor, linestyle=estilo, linewidth=3.2, legend=False)

                valor_final = serie[-1]
                texto_box = f"R$ {valor_final:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

                ax.annotate( # Cria a caixa de anotação com o valor do último período da projeção (valor final)
                    texto_box,
                    xy=(prazo_meses, valor_final),
                    xytext=(10, -10),
                    textcoords='offset points',
                    fontsize=16,
                    color=cor,
                    bbox=dict(boxstyle='round,pad=0.4', fc='white', ec=cor, lw=2, alpha=0.9),
                    arrowprops=dict(arrowstyle='->', color=cor, lw=2),
                    ha='left'
                    )


        # Configuração das Linhas de Grade e Bordas
        ax.grid(True, which='major', axis='x', color="#1A1818", linestyle='-', linewidth=0.6)
        for spine in ax.spines.values():
            spine.set_color('#000000')

        ax.xaxis.label.set_color('#000000')
        ax.yaxis.label.set_color('#000000')
        ax.tick_params(axis='x', colors='#000000')
        ax.tick_params(axis='y', colors='#000000')

        # Configuração da Legenda (fora da área de plotagem, mas dentro da figura)
        handles, labels = ax.get_legend_handles_labels()
        fig.legend(
            handles=handles,
            labels=labels,
            loc='lower center',
            bbox_to_anchor=(0.5, -0.01),
            fontsize=16,
            ncol=3,
            frameon=False
            )

        # Configuração das Linhas de Grade no Eixo X em anos
        ax.xaxis.set_major_locator(plt.MultipleLocator(12))
        ax.xaxis.set_minor_locator(plt.MultipleLocator(1))
        ax.set_xlim([1, prazo_meses])

        # Função auxiliar para formatar os valores no eixo X
        def formatar_valores_x(valor, pos):
            return f"{int(valor // 12)}"

        ax.xaxis.set_major_formatter(FuncFormatter(formatar_valores_x)) # Aplica a formatação no eixo X

        # Função auxiliar para formatar os valores no eixo Y
        def formatar_valores_y(valor, pos):
            return f"{valor:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")

        ax.yaxis.set_major_formatter(FuncFormatter(formatar_valores_y)) # Aplica a formatação no eixo Y

        return fig, ax



class ExportarPDF:  # Classe com a criação e configuração do arquivo PDF com os dados de entrada e resultados da projeção

    @staticmethod
    def gerar_pdf(capital_inicial, prazo_anos, taxa_juros, valor_futuro_final, valor_futuro_sem_aporte_final, rendimento_juros, patrimonio_mensal, patrimonio_mensal_real,
                  patrimonio_mensal_sem_aporte, prazo_meses, aportes_por_periodo, renda_perpetua, adicionar_sigla, valor_futuro_real_final, taxa_juros_real, taxa_inflacao, 
                  valor_total_aportes, valor_futuro_sem_aporte_final_real, patrimonio_mensal_sem_aporte_real):  # Função principal para criação do arquivo PDF
        
        # Criação da imagem do gráfico
        nome_imagem = "grafico_projecao.png"        
        try:
            fig, _ = PlotagemGraficoPDF.criar_grafico_pdf(patrimonio_mensal_real, patrimonio_mensal, patrimonio_mensal_sem_aporte, prazo_meses,
                                                          patrimonio_mensal_sem_aporte_real)
            
            fig.savefig(nome_imagem, dpi=200, bbox_inches='tight') # Salva a imagem do gráfico (elimina bordas em branco // resolução de 200 DPI)
            plt.close(fig)

            if not os.path.exists(nome_imagem):  # Verifica se a imagem foi criada corretamente no diretório do programa
                raise FileNotFoundError(f"O arquivo {nome_imagem} não foi gerado")
            
            with PILImage.open(nome_imagem) as img:
                img.verify()  # Verifica a integridade da imagem criada
        
        except Exception as e:
            print(f"Erro ao gerar a imagem do gráfico: {e}")
            return
        
        # Configurações Gerais do PDF
        nome_arquivo = f"relatorio_projecao - {adicionar_sigla}.pdf"  # Inclui a sigla do cliente no nome do arquivo gerado
        doc = SimpleDocTemplate(nome_arquivo, pagesize=letter, topMargin=50, bottomMargin=30, leftMargin=0.5*inch, rightMargin=0.5*inch) # Configurações de design do PDF
        elements = []  # Inicializa a lista de elementos do PDF
        styles = getSampleStyleSheet()

        # Configuração dos Estilos de Texto
        styles.add(ParagraphStyle(name='TitleCustom', fontName='Helvetica-Bold', fontSize=18, textColor=colors.white, alignment=1))  # Centro
        styles.add(ParagraphStyle(name='SectionTitle', fontName='Helvetica-Bold', fontSize=12, textColor=colors.black, alignment=1, spaceAfter=10))  # Esquerda
        styles.add(ParagraphStyle(name='DateRight', fontName='Helvetica-Oblique', fontSize=9, textColor=colors.white, alignment=2))  # Direita

        # Método para criar o cabeçalho do PDF
        def criar_cabecalho(canvas, doc):
            canvas.saveState()
            largura, altura = letter
            altura_margem = 50
            cor_azul_escuro = Color(11/255, 46/255, 83/255)  # Em HEX: #0B2E52 (AZUL ESCURO)

            # Faixa azul do cabeçalho
            canvas.setFillColor(cor_azul_escuro)
            canvas.rect(0, altura - altura_margem, largura, altura_margem, fill=1, stroke=0)

            # Logotipo
            canvas.drawImage(Interface.resource_path("utils/logofh_pdf2.jpeg"), 10, altura - altura_margem + 5, width=40, height=40)

            # Título
            titulo = "Relatório de Projeção Financeira"
            if adicionar_sigla:
                titulo += f" - {adicionar_sigla}"
            
            p = Paragraph(titulo, styles['TitleCustom'])
            w, h = p.wrap(largura, altura_margem)
            p.drawOn(canvas, largura/2 - w/2, altura - altura_margem/2 - h/2 + 5)

            # Data
            data_atual = datetime.now().strftime("%d/%m/%Y")
            p = Paragraph(f"Data do Relatório: {data_atual}", styles['DateRight'])
            w, h = p.wrap(120, altura_margem)
            p.drawOn(canvas, largura - 130, altura - altura_margem/2 - 20)

            canvas.restoreState()

        # Método para criar o rodapé do PDF
        def criar_rodape(canvas, doc):
            canvas.saveState()
            largura, altura = letter
            altura_rodape = 30
            cor_rodape = Color(11/255, 46/255, 83/255)  # Em HEX: #0B2E52 (AZUL ESCURO)

            # Faixa azul do rodapé
            canvas.setFillColor(cor_rodape)
            canvas.rect(0, 0, largura, altura_rodape, fill=1, stroke=0)

            # Texto do rodapé
            texto_rodape = "fhadvisors.com.br | @fh.advisors" # Site e Instagram
            p = Paragraph(texto_rodape, ParagraphStyle(name='Footer', fontName='Helvetica-Oblique', fontSize=9, textColor=colors.white, alignment=1))
            
            w, h = p.wrap(largura, altura_rodape)
            p.drawOn(canvas, largura/2 - w/2, altura_rodape/2 - 5)

            canvas.restoreState()

        # Adiciona o cabeçalho e o rodapé no template do PDF
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
        template = PageTemplate(id='AllPages', frames=[frame], onPage=criar_cabecalho, onPageEnd=criar_rodape)
        doc.addPageTemplates([template])

        # Converte as taxas de MENSAL para ANUAL para o display no PDF
        taxa_juros_PDF = CalculosProjecao.taxa_equivalente(taxa_juros, 1, 12)
        taxa_inflacao_PDF = CalculosProjecao.taxa_equivalente(taxa_inflacao, 1, 12)
        taxa_juros_real_PDF = CalculosProjecao.taxa_equivalente(taxa_juros_real, 1, 12)

        # Gera a Tabela com os Dados de Entrada (inputs)
        dados_inputs = [
            ["Descrição", "Valor"],
            ["Capital Inicial", f"R$ {capital_inicial:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")],
            ["Prazo (Anos)", prazo_anos],
            ["Taxa de Juros Nominal", f"{taxa_juros_PDF * 100:.2f}% a.a"],
            ["Taxa de Inflação Esperada", f"{taxa_inflacao_PDF * 100:.2f}% a.a"],
            ["Taxa de Juros Real", f"{taxa_juros_real_PDF * 100:.2f}% a.a"]
        ]

        for i, (aporte, duracao_meses) in enumerate(aportes_por_periodo, start=1):
            dados_inputs.append([f"Aportes - Período {i}", f"R$ {aporte:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".") + f" por {duracao_meses} meses"])

        # Cria a Tabela com os Dados de Entrada
        tabela_inputs = Table(dados_inputs, colWidths=[200, 200])
        tabela_inputs.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B2E53')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(Paragraph("Parâmetros de Entrada", styles['SectionTitle']))
        elements.append(tabela_inputs)
        elements.append(Spacer(1, 20))

        # Cria a Tabela com os Dados de Saída (outputs > resultados)
        dados_resultados = [
            ["Descrição", "Valor"],
            ["Valor Nominal com Aporte", f"R$ {valor_futuro_final:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")],
            ["Valor Real com Aporte", f"R$ {valor_futuro_real_final:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")],
            ["Valor Nominal sem Aporte", f"R$ {valor_futuro_sem_aporte_final:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")],
            ["Valor Real sem Aporte", f"R$ {valor_futuro_sem_aporte_final_real:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")]
        ]

        tabela_resultados = Table(dados_resultados, colWidths=[200, 200])
        tabela_resultados.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B2E53')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(Paragraph("Resultados", styles['SectionTitle']))
        elements.append(tabela_resultados)
        elements.append(Spacer(1, 5))

        # Cria a Tabela com os Resultados de Cálculos Auxiliares (outputs)
        dados_resultados_aux = [
            ["Rendimento Total dos Juros", f"R$ {rendimento_juros:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")],
            ["Renda Perpétua", f"R$ {renda_perpetua:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")],
            ["Valor Total de Aportes", f"R$ {valor_total_aportes:,.0f}".replace(",", "X").replace(".", ",").replace("X", ".")],
        ]

        tabela_resultados_aux = Table(dados_resultados_aux, colWidths=[200, 200])
        tabela_resultados_aux.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(Paragraph("", styles['SectionTitle']))
        elements.append(tabela_resultados_aux)
        elements.append(Spacer(1, 20))

        # Posiciona a imagem do gráfico no relatório
        try:
            with PILImage.open(nome_imagem) as img:
                # Obtém as dimensões originais em pixels
                largura_original, altura_original = img.size
                dpi = 200  # Mesma DPI usada no salvamento
                largura_pontos = largura_original / dpi * 72  # Converte pixels para pontos
                altura_pontos = altura_original / dpi * 72

                # Define um tamanho máximo para caber na página letter (ajuste conforme necessário)
                max_largura = 500  # Aproximadamente 6.94 polegadas
                max_altura = 300   # Aproximadamente 4.17 polegadas

                # Calcula a escala para manter a proporção
                escala = min(max_largura / largura_pontos, max_altura / altura_pontos)
                nova_largura = largura_pontos * escala
                nova_altura = altura_pontos * escala

                # Adiciona a imagem com as novas dimensões
                grafico = Image(nome_imagem, width=nova_largura, height=nova_altura)
                grafico.hAlign = 'CENTER'
                elements.append(grafico)
        except Exception as e:
            print(f"Erro ao adicionar gráfico: {e}")
            return

        # Faz a construção e geração final do arquivo PDF do relatório
        try:
            doc.build(elements)
            print(f"PDF gerado com sucesso: {nome_arquivo}")
            messagebox.showinfo("Sucesso", f"Relatório gerado com sucesso: {nome_arquivo}", icon='info')  # Caixa de mensagem de sucesso na geração do PDF
        except Exception as e:
            print(f"Erro ao gerar o PDF: {e}")
            import traceback
            traceback.print_exc()



# Filtrar log's de warnings irrelevantes
warnings.filterwarnings("ignore", category=UserWarning, message="Pick support for PolyCollection is missing")



# Bloco para execução do programa
if __name__ == "__main__":
    interface = Interface()
    interface.iniciar()
