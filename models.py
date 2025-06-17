# Importação das Bibliotecas Necessárias

import pandas as pd
import numpy as np
import math



class CalculosProjecao: # Classe com as funções para os cálculos da projeção

    @staticmethod
    def valor_futuro_ant(capital_inicial, taxa_juros, aportes_por_periodo, prazo_meses): # Função para o cálculo do VALOR FUTURO no regime ANTECIPADO com APORTES VARIÁVEIS POR PERÍODO
        try:
            if capital_inicial < 0 or taxa_juros < 0 or prazo_meses < 0:
                raise ValueError("O capital inicial, a taxa de juros ou o prazo não podem ser negativos")
            for aporte, duracao in aportes_por_periodo:
                if aporte < 0 or duracao < 0:
                    raise ValueError("Aportes e durações devem ser não negativos")
            
            patrimonio_mensal = []
            valor_futuro_total = capital_inicial
            mes_atual = 0

            for aporte, duracao in aportes_por_periodo:
                for _ in range(duracao):
                    if mes_atual >= prazo_meses:
                        break
                    valor_futuro_total = (valor_futuro_total + aporte) * (1 + taxa_juros)
                    patrimonio_mensal.append(valor_futuro_total)
                    mes_atual += 1
        
            while mes_atual < prazo_meses:
                valor_futuro_total *= (1 + taxa_juros)
                patrimonio_mensal.append(valor_futuro_total)
                mes_atual += 1

            return valor_futuro_total, patrimonio_mensal
    
        except Exception as e:
            print(f"Erro no cálculo do valor futuro {e}")
            return None, []


    @staticmethod
    def valor_futuro_sem_aportes(capital_inicial, taxa_juros, prazo_meses): # Função para o cálculo do VALOR FUTURO no regime ANTECIPADO e SEM APORTES
        try:
            if capital_inicial < 0 or taxa_juros < 0 or prazo_meses < 0:
                raise ValueError("O capital inicial, a taxa de juros ou o prazo não podem ser negativos")
            
            patrimonio_mensal = []
            valor_futuro = capital_inicial

            for _ in range(prazo_meses):
                valor_futuro *= (1 + taxa_juros)
                patrimonio_mensal.append(valor_futuro)
        
            return valor_futuro, patrimonio_mensal
        
        except Exception as e:
            print(f"Erro ao calcular valor futuro sem aportes {e}")
            return None, []


    @staticmethod
    def total_aportes(aportes_por_periodo): # Função para o cálculo da soma do VALOR TOTAL DE APORTES realizados na projeção
        try:
            total_aportes = 0
            for aporte, duracao in aportes_por_periodo:
                if aporte < 0 or duracao < 0:
                    raise ValueError("Aportes e durações devem ser não negativos")
                total_aportes += aporte * duracao
            return total_aportes

        except Exception as e:
            print(f"Erro no cálculo do total de aportes: {e}")
            return None


    @staticmethod
    def rendimento_juros(valor_futuro_final, capital_inicial, total_aportes): # Função para o cálculo do VALOR TOTAL DE RENDIMENTOS da projeção
        try:
            if valor_futuro_final < 0 or capital_inicial < 0 or total_aportes < 0:
                raise ValueError("Valores não podem ser negativos")
            rendimento_juros = valor_futuro_final - capital_inicial - total_aportes # Rendimentos = valor futuro final descontado do capital inicial e dos aportes
            return rendimento_juros
        
        except Exception as e:
            print(f"Erro no cálculo do rendimento: {e}")
            return None


    @staticmethod
    def renda_perpetua(valor_futuro_final_real, taxa_juros_real): # Função para o cálculo do valor da RENDA PERPÉTUA ou VITALÍCIA (Valor de retirada que mantém o patrimônio)
        try:
            if valor_futuro_final_real <= 0 or taxa_juros_real <= 0:
                raise ValueError("O valor futuro e a taxa de juros devem ser positivos")

            renda_perpetua = valor_futuro_final_real * taxa_juros_real # Perpetuidade Financeira (R = PV * i)
            return renda_perpetua

        except Exception as e:
            print(f"Erro no cálculo da renda perpetua: {e}")
            return None


    @staticmethod
    def valor_necessario_renda_vitalicia(renda_desejada, taxa_juros_real): # Função para o cálculo do VALOR NECESSÁRIO para ter determinada RENDA PERPÉTUA ou VITALÍCIA
        try:
            if renda_desejada <= 0 or taxa_juros_real <= 0:
                raise ValueError("A renda desejada e a taxa de juros devem ser positivas")
            
            valor_necessario = renda_desejada / taxa_juros_real # Valor Presenta de Perpetuidade (Renda indefinida, sem consumir do principal)
            return valor_necessario
        
        except Exception as e:
            print(f"Erro no cálculo do valor necessário: {e}")
            return None


    @staticmethod
    def aporte_necessario_para_valor_futuro(valor_futuro_desejado, taxa_juros_real, prazo_meses): # Função para o cálculo do APORTE NECESSÁRIO para atingir determinado VALOR FUTURO
        try:
            if valor_futuro_desejado <= 0 or taxa_juros_real <= 0 or prazo_meses <= 0:
                raise ValueError("Valor futuro, taxa de juros e prazo devem ser positivos")
            
            aporte = (valor_futuro_desejado * taxa_juros_real) / (((1 + taxa_juros_real) ** prazo_meses - 1) * (1 + taxa_juros_real)) # Aporte Periódico Constante e Antecipado
            return aporte
        
        except Exception as e:
            print(f"Erro no cálculo do aporte necessário: {e}")
            return None


    @staticmethod
    def taxa_real(taxa_juros, taxa_inflacao): # Função para o cálculo da TAXA de JUROS REAL a partir da TAXA de JUROS NOMINAL
        try:
            if taxa_inflacao <= -1:
                raise ValueError("Taxa de inflação inválida (causaria divisão por zero)")
            
            taxa_real = ((1 + taxa_juros) / (1 + taxa_inflacao)) - 1
            return taxa_real
        
        except Exception as e:
            print(f"Erro no cálculo da taxa real: {e}")
            return None


    @staticmethod
    def taxa_equivalente(taxa_origem, periodo_origem, periodo_destino): # Função para o cálculo de EQUIVALÊNCIA DE TAXAS
        try:
            if taxa_origem < 0 or periodo_origem <= 0 or periodo_destino <= 0:
                raise ValueError("Taxa e períodos devem ser não negativos e períodos maiores que zero")
            
            taxa_convertida = ((1 + taxa_origem) ** (periodo_destino / periodo_origem)) - 1
            return taxa_convertida
        
        except Exception as e:
            print(f"Erro no cálculo de equivalência de taxas: {e}")
            return None


    @staticmethod
    def tempo_usufruto(patrimonio_inicial, retirada_mensal, taxa_juros_real): # Função para o cálculo do TEMPO DE USUFRUTO de um PATRIMÔNIO ACUMULADO com RETIRADAS MENSAIS
        try:
            if patrimonio_inicial <= 0 or retirada_mensal <= 0 or taxa_juros_real < 0:
                raise ValueError("Patrimônio inicial, retirada mensal ou taxa de juros não podem ser negativos")

            if patrimonio_inicial * taxa_juros_real >= retirada_mensal:
                return float('inf'), None, None  # Casos onde o rendimento do capital cobre completamente o valor da retirada

            meses = 0
            patrimonio = patrimonio_inicial

            while patrimonio > 0:
                patrimonio = (patrimonio - retirada_mensal) * (1 + taxa_juros_real) # Retiradas Mensais Fixas
                meses += 1
                if meses > 100000:  # Limite para evitar loops muito longos
                    return float('inf'), None, None  # Trata como infinito se exceder o limite

            anos = meses // 12
            meses_restantes = meses % 12

            return meses, anos, meses_restantes

        except Exception as e:
            print(f"Erro no cálculo do tempo de usufruto: {e}")
            return None, None, None


    @staticmethod
    def tabela_price(valor_total, taxa, prazo_meses, entrada=0): # Cálculo da TABELA de CRONOGRAMA de PAGAMENTOS de um FINANCIAMENTO feito no SISTEMA PRICE
        try:
            if valor_total <= 0 or taxa < 0 or prazo_meses <= 0 or entrada < 0 or entrada > valor_total:
                raise ValueError("Verifque os valores inputados")
            
            taxa = taxa / 100 # Transforma a taxa em %

            valor_financiado = valor_total - entrada
            if valor_financiado <= 0:
                raise ValueError("O valor financiado é menor do que zero")

            if taxa == 0:
                parcela = valor_financiado / prazo_meses
            else:
                parcela = valor_financiado * (taxa * (1 + taxa) ** prazo_meses) / ((1 + taxa) ** prazo_meses - 1) # Parcela Constante
            
            saldo_devedor = valor_financiado
            tabela = []
            
            
            for mes in range(1, prazo_meses + 1):
                juros = saldo_devedor * taxa
                amortizacao = parcela - juros
                saldo_devedor -= amortizacao
                
                
                if saldo_devedor < 0:
                    saldo_devedor = 0
                
                tabela.append({
                    'Mês': mes,
                    'Parcela': parcela,
                    'Juros': juros,
                    'Amortização': amortizacao,
                    'Saldo Devedor': saldo_devedor
                })
            
            
            total_juros = sum(entry['Juros'] for entry in tabela)
            total_parcelas = sum(entry['Parcela'] for entry in tabela)
            
            return {
                'Valor Financiado': valor_financiado,
                'Tabela de Pagamentos': tabela,
                'Total em Juros': total_juros,
                'Total em Pagamentos': total_parcelas,
                'Entrada': entrada
            }
        
        except Exception as e:
            raise ValueError(f"Ocorreu um erro inesperado: {str(e)}")


    @staticmethod
    def tabela_sac(valor_total, taxa, prazo_meses, entrada=0): # Cálculo da TABELA de CRONOGRAMA de PAGAMENTOS de um FINANCIAMENTO feito no SISTEMA SAC

        try:
            if valor_total <= 0 or taxa < 0 or prazo_meses <= 0 or entrada < 0 or entrada > valor_total:
                raise ValueError("Verifique os valores inputados")
            
            taxa = taxa / 100 # Transforma a taxa em %
           
            valor_financiado = valor_total - entrada
            if valor_financiado <= 0:
                raise ValueError("O valor financiado é menor do zero")

            amortizacao = valor_financiado / prazo_meses # Amortização Constante
            saldo_devedor = valor_financiado
            tabela = []
            
            
            for mes in range(1, prazo_meses + 1):
                juros = saldo_devedor * taxa
                parcela = amortizacao + juros
                saldo_devedor -= amortizacao
                
                
                if saldo_devedor < 0:
                    saldo_devedor = 0
                
                tabela.append({
                    'Mês': mes,
                    'Parcela': parcela,
                    'Juros': juros,
                    'Amortização': amortizacao,
                    'Saldo Devedor': saldo_devedor
                })
            
            # Cálculo dos Totais
            total_juros = sum(entry['Juros'] for entry in tabela)
            total_parcelas = sum(entry['Parcela'] for entry in tabela)
            
            return {
                'Valor Financiado': valor_financiado,
                'Tabela de Pagamentos': tabela,
                'Total em Juros': total_juros,
                'Total em Pagamentos': total_parcelas,
                'Entrada': entrada
            }
        
        except Exception as e:
            raise ValueError(f"Ocorreu um erro inesperado: {str(e)}")
