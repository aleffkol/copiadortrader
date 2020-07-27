from iqoptionapi.stable_api import IQ_Option
import time, json, logging, configparser
import re
import getpass
from datetime import datetime, date, timedelta
from dateutil import tz
import sys

# logging.disable(level=(logging.DEBUG))



#Funções
def selecionar_tipo_conta(API):
    conta_real_pratica=''
    while conta_real_pratica.upper()!='REAL' or conta_real_pratica.upper()!='TREINO':
        conta_real_pratica = input('\nInforme em qual conta você deseja operar\nReal ou Treino: ')
        if(conta_real_pratica.upper().__eq__('REAL')):
            API.change_balance('REAL')
            print(f'\033[32m\nVocê selecionou a banca: {conta_real_pratica}.\033[m')
            return 'REAL'
        if(conta_real_pratica.upper().__eq__('TREINO')):
            API.change_balance('PRACTICE')
            print(f'\033[32m\nVocê selecionou a banca: {conta_real_pratica}.\033[m')
            return 'TREINO'
        print('\033[31m\nVocê informou o nome inválido.\033[m')

def selecionar_valor_entrada():
    valor = 0
    while valor<=0:
        valor = float(input('\nDigitar o valor da(s) entrada(s):'))
        if(valor>=1):
            print(f'\033[32mO valor da(s) sua(s) entrada(s) agora é: {valor}\033[m')
            return valor
        print('\033[31mNão pode ser valor abaixo ou igual a 0\033[m')
    return valor

def selecionar_par_moedas(lista_ativos):
    par = ''
    while par not in lista_ativos:
        par = input('\nInforme o par de moedas: ')
        par = par.upper()
        if(par in lista_ativos):
            print(f'\033[32mO par de moeda onde irá operar é {par}\033[m')
            return par

        print('\033[31mNão existe este par de moedas.\033[m')
    return par

def selecionar_top_ranking():
    ranking = 0
    while ranking<=0:
        ranking = int(input('\nInforme traders de até que colocoção deseja copiar: '))
        if(ranking>=1):
            print(f'\033[32mVocê está copiando traders de colocação até {ranking}\033[m')
            return ranking
        print('\033[31mDigite um valor maior ou igual a 1.\033[m')
    return ranking

def mostrar_perfil_atual(valor_entrada, par_moeda, tipo_banca, top_ranking, soros, niveis_soros, valor_banca, expiracao, stop_loss, stop_win):
    print(f'''\t\tValores Atuais\n
        [Valor de entrada] = {valor_entrada}
        [Par de moeda] = {par_moeda}
        [Tipo de banca] = {tipo_banca}
        [Valor da banca] = {valor_banca}
        [TOPs Ranking] = {top_ranking}
        [Tempo Expiração] = {expiracao}
        [Soros] = {soros}
        [Niveis do soros] = {niveis_soros}
        [Stop Loss] = {stop_loss}
        [Stop Win] = {stop_win}\n''')
def listar_ativos(lista):
    print(lista)

def get_valor_banca(api):
    return api.get_balance()

def ativar_soros(soros, niveis_soros):
    niveis_soros = 0
    if(soros==False):
        soros = True
        print('\033[32mO soros foi ativado.\033[m')
        niveis_soros = alterar_nivel_soros(soros)
        return soros, niveis_soros
    if(soros == True):
        soros = False
        niveis_soros = 0
        print('\033[32mO soros foi desativado.\033[m')
        return soros, niveis_soros
    print('\033[31mAlgo deu errado\033[m')

def alterar_nivel_soros(soros):
    nivel_soros = 0
    if(soros==True):
        while(nivel_soros<=0):
            nivel_soros = int(input('Informe o nível do soros: '))
            if(nivel_soros>=1):
                print(f'\033[32mO nível de soros agora é: {nivel_soros}\033[m')
                return nivel_soros
            print('\033[31mNão pode ser valor igual ou abaixo de 0.\033[m')
    return soros
def alterar_stop_win():
    stop_win = 0
    while(stop_win<=0):
        stop_win = int(input('Informe o valor do seu stop win: '))
        if(stop_win==0):
            print('\033[32mO seu stop win é igual a 0\n Ou seja, não existe stop win\033[m')
            return stop_win
        if(stop_win>0):
            print(f'\033[32mO seu stop win é {stop_win}\033[m')
            return stop_win
        print('\033[31mInforme um valor de 0 em diante.\033[m')
    return stop_win

def alterar_stop_loss():
    stop_loss = 0
    while(stop_loss<=0):
        stop_loss = int(input('Informe o valor do seu stop loss: '))
        if(stop_loss==0):
            print('\033[32mO seu stop loss é igual a 0\n Ou seja, não existe stop loss\033[m')
            return stop_loss
        if(stop_loss>0):
            print(f'\033[32mO seu stop loss é {stop_loss}\033[m')
            return stop_loss
        print('\033[31mInforme um valor de 0 em diante.\033[m')
    return stop_loss

def contador_segundos(segundos):
    for i in range(1, segundos):
        print('\t\t.')
        time.sleep(1)

def alerar_tempo_expiracao():
    expiracao = 0
    while(expiracao!=1 or expiracao!=5 or expiracao!=15):
        expiracao = int(input('\nQual o tempo de expiração em minutos que você quer copiar? (1, 5 ou 15): '))
        if(expiracao==1):
            print('\033[32mO tempo de expiração foi alterado para 1 minuto\033[m')
            return 'PT1M', 1
        if(expiracao==5):
            print('\033[32mO tempo de expiração foi alterado para 5 minuto\033[m')
            return 'PT5M',5
        if(expiracao==15):
            print('\033[32mO tempo de expiração foi alterado para 15 minuto\033[m')
            return 'PT15M',15
        print('\033[31mDigite um tempo de expiração válida (1, 5 ou 15)\033[m')
    return 'PT1M',1

def realizar_entrada(moeda, entrada, direcao, timeframe):
    status, id = API.buy_digital_spot(moeda, entrada, direcao, timeframe)

    if status:
        while True:
            status, lucro = API.check_win_digital_v2(id)

            if status:
                if lucro > 0:
                    return 'win', round(lucro, 2)
                else:
                    return 'loss', 0
                break
    else:
        return 'error', 0

#ENTRADAS
def iniciar_entradas(api, moeda, entrada, ranking, banca, soros, niveis_soros, expiracao, tempo_expiracao, stop_loss, stop_win):

    tipo_bd = 'live-deal-digital-option'  # live-deal-binary-option-placed / live-deal-digital-option
    banca_inicial = api.get_balance()
    entrada_capturada_antes = 0

    #Inicio
    print('=-='*20)
    print('\t\tO copiador de entradas está iniciando.\n\t\tAguarde!')
    contador_segundos(5)

    #Pegando IDs dos traders
    lista_dados_traders = api.get_leader_board('Worldwide',1,ranking,0)
    lista_top_traders = []
    if(ranking>=0):
        for posicao in lista_dados_traders['result']['positional']:
            lista_top_traders.append(lista_dados_traders['result']['positional'][posicao]['user_id'])
    print(f'''\n\t\tEsses são os IDs dos traders que você está copiando ({len(lista_top_traders)}):
        {lista_top_traders}''')

    #Mostrando valores
    print('\n')
    mostrar_perfil_atual(entrada, moeda, banca, ranking, soros, niveis_soros, api.get_balance(),expiracao, stop_win, stop_loss)

    #Capturando entradas
    api.subscribe_live_deal(tipo_bd, moeda, expiracao, 10)
    sinal_antigo = 0

    print('=-='*20)
    print(f'\t\tIniciando a captura de entradas no ativo {moeda}')
    print(f'\t\tAs entradas de cores vermelhas é porquê não está dentro do top ranking selecionado(Top: {ranking})\n')

    contador_soros = 1
    resultado = ''

    while True:

        if((banca_inicial+stop_win)<=api.get_balance() and stop_win>0):
            print('\033[32mVocê já atingiu o seu stop win.\nParabéns\033[m')
            sys.exit()
        if(stop_loss>0 and (banca_inicial-stop_loss)>=api.get_balance()):
            print('\033[31mVocê já atingiu o seu stop loss.\nNão fique triste\033[m')
            sys.exit()

        trades = API.get_live_deal(tipo_bd, moeda, expiracao)
        if(len(trades)>0 and trades[0]['user_id']!=sinal_antigo):

            if(trades[0]['user_id'] in lista_top_traders):
                print('=-='*60)
                # print('\n\t\tEste trader está dentro do ranking selecionado.')
                print(f'''\033[32m\t\t[{trades[0]['flag']}] {trades[0]['name']} ({trades[0]['user_id']}) / Ativo: {moeda} / Valor da entrada: {trades[0]['amount_enrolled']} / Direção: {trades[0]['instrument_dir']} / Expiração: {trades[0]['expiration_type']}\033[m''')

                #Soros
                if(resultado=='win' and contador_soros<niveis_soros and soros==True):
                    resultado, lucro = realizar_entrada(moeda, entrada+lucro, trades[0]['instrument_dir'], tempo_expiracao)
                    contador_soros+=1
                    print('\t\t-> ', resultado, '/', lucro, '\n\n')

                #Entrada caso soros tenha dado errado
                elif(resultado=='loss'):
                    contador_soros = 1
                    resultado, lucro = realizar_entrada(moeda, entrada, trades[0]['instrument_dir'],tempo_expiracao)
                    print('\t\t-> ', resultado, '/', lucro, '\n\n')

                #Entrada comum
                else:
                    resultado, lucro = realizar_entrada(moeda, entrada, trades[0]['instrument_dir'],tempo_expiracao)
                    print('\t\t-> ', resultado, '/', lucro, '\n\n')

            else:
                # print('\n\t\tEste trader não está dentro do ranking selecionado.')
                print(f'''\033[31m\t\t[{trades[0]['flag']}] {trades[0]['name']} ({trades[0]['user_id']}) / Ativo: {moeda} / Valor da entrada: {trades[0]['amount_enrolled']} / Direção: {trades[0]['instrument_dir']} / Expiração: {trades[0]['expiration_type']}\033[m''')

            sinal_antigo = trades[0]['user_id']
#BOT
def menu_bot(API):
    #Valores Padrões
    moeda = 'EURUSD'
    entrada = 1
    ranking = 10
    banca = 'PRÁTICA'
    soros = False
    niveis_soros = 0
    expiracao = 'PT1M'
    tempo_expiracao = 1
    stop_loss = 0
    stop_win = 0


    #API
    iqoptionapi = API

    #Lista de Ativos
    ativos = ''' 'EURUSD': 1, 'EURGBP': 2, 'GBPJPY': 3, 'EURJPY': 4, 'GBPUSD': 5, 'USDJPY': 6, 'AUDCAD': 7, 'NZDUSD': 8, 'USDRUB': 10, 'AMAZON': 31, 'APPLE': 32, 'BAIDU': 33, 'CISCO': 34, 'FACEBOOK': 35, 'GOOGLE': 36, 'INTEL': 37, 'MSFT': 38, 'YAHOO': 40, 'AIG': 41, 'CITI': 45, 'COKE': 46, 'GE': 48, 'GM': 49, 'GS': 50, 'JPM': 51, 'MCDON': 52, 'MORSTAN': 53, 'NIKE': 54, 'USDCHF': 72, 'XAUUSD': 74, 'XAGUSD': 75, 'EURUSD-OTC': 76, 'EURGBP-OTC': 77, 'USDCHF-OTC': 78, 'EURJPY-OTC': 79, 'NZDUSD-OTC': 80, 'GBPUSD-OTC': 81, 'USDJPY-OTC': 85, 'AUDCAD-OTC': 86, 'ALIBABA': 87, 'YANDEX': 95, 'AUDUSD': 99, 'USDCAD': 100, 'AUDJPY': 101, 'GBPCAD': 102, 'GBPCHF': 103, 'GBPAUD': 104, 'EURCAD': 105, 'CHFJPY': 106, 'CADCHF': 107, 'EURAUD': 108, 'TWITTER': 113, 'FERRARI': 133, 'TESLA': 167, 'USDNOK': 168, 'EURNZD': 212, 'USDSEK': 219, 'USDTRY': 220, 'MMM:US': 252, 'ABT:US': 253, 'ABBV:US': 254, 'ACN:US': 255, 'ATVI:US': 256, 'ADBE:US': 258, 'AAP:US': 259, 'AA:US': 269, 'AGN:US': 272, 'MO:US': 278, 'AMGN:US': 290, 'T:US': 303, 'ADSK:US': 304, 'BAC:US': 313, 'BBY:US': 320, 'BA:US': 324, 'BMY:US': 328, 'CAT:US': 338, 'CTL:US': 344, 'CVX:US': 349, 'CTAS:US': 356, 'CTXS:US': 360, 'CL:US': 365, 'CMCSA:US': 366, 'CXO:US': 369, 'COP:US': 370, 'ED:US': 371, 'COST:US': 374, 'CVS:US': 379, 'DHI:US': 380, 'DHR:US': 381, 'DRI:US': 382, 'DVA:US': 383, 'DAL:US': 386, 'DVN:US': 388, 'DO:US': 389, 'DLR:US': 390, 'DFS:US': 391, 'DISCA:US': 392, 'DOV:US': 397, 'DTE:US': 400, 'DNB:US': 403, 'ETFC:US': 404, 'EMN:US': 405, 'EBAY:US': 407, 'ECL:US': 408, 'EIX:US': 409, 'EMR:US': 413, 'ETR:US': 415, 'EQT:US': 417, 'EFX:US': 418, 'EQR:US': 420, 'ESS:US': 421, 'EXPD:US': 426, 'EXR:US': 428, 'XOM:US': 429, 'FFIV:US': 430, 'FAST:US': 432, 'FRT:US': 433, 'FDX:US': 434, 'FIS:US': 435, 'FITB:US': 436, 'FSLR:US': 437, 'FE:US': 438, 'FISV:US': 439, 'FLS:US': 441, 'FMC:US': 443, 'FBHS:US': 448, 'FCX:US': 450, 'FTR:US': 451, 'GILD:US': 460, 'HAS:US': 471, 'HON:US': 480, 'IBM:US': 491, 'KHC:US': 513, 'LMT:US': 528, 'MA:US': 542, 'MDT:US': 548, 'MU:US': 553, 'NFLX:US': 569, 'NEE:US': 575, 'NVDA:US': 586, 'PYPL:US': 597, 'PFE:US': 603, 'PM:US': 605, 'PG:US': 617, 'QCOM:US': 626, 'DGX:US': 628, 'RTN:US': 630, 'CRM:US': 645, 'SLB:US': 647, 'SBUX:US': 666, 'SYK:US': 670, 'DIS:US': 689, 'TWX:US': 692, 'VZ:US': 723, 'V:US': 726, 'WMT:US': 729, 'WBA:US': 730, 'WFC:US': 733, 'SNAP': 756, 'DUBAI': 757, 'TA25': 758, 'AMD': 760, 'ALGN': 761, 'ANSS': 762, 'DRE': 772, 'IDXX': 775, 'RMD': 781, 'SU': 783, 'TFX': 784, 'TMUS': 785, 'QQQ': 796, 'SPY': 808, 'BTCUSD': 816, 'XRPUSD': 817, 'ETHUSD': 818, 'LTCUSD': 819, 'DSHUSD': 821, 'BCHUSD': 824, 'OMGUSD': 825, 'ZECUSD': 826, 'ETCUSD': 829, 'BTCUSD-L': 830, 'ETHUSD-L': 831, 'LTCUSD-L': 834, 'BCHUSD-L': 836, 'BTGUSD': 837, 'QTMUSD': 845, 'XLMUSD': 847, 'TRXUSD': 858, 'EOSUSD': 864, 'USDINR': 865, 'USDPLN': 866, 'USDBRL': 867, 'USDZAR': 868, 'DBX': 889, 'SPOT': 891, 'USDSGD': 892, 'USDHKD': 893, 'LLOYL-CHIX': 894, 'VODL-CHIX': 895, 'BARCL-CHIX': 896, 'TSCOL-CHIX': 897, 'BPL-CHIX': 898, 'HSBAL-CHIX': 899, 'RBSL-CHIX': 900, 'BLTL-CHIX': 901, 'MRWL-CHIX': 902, 'STANL-CHIX': 903, 'RRL-CHIX': 904, 'MKSL-CHIX': 905, 'BATSL-CHIX': 906, 'ULVRL-CHIX': 908, 'EZJL-CHIX': 909, 'ADSD-CHIX': 910, 'ALVD-CHIX': 911, 'BAYND-CHIX': 912, 'BMWD-CHIX': 913, 'CBKD-CHIX': 914, 'COND-CHIX': 915, 'DAID-CHIX': 916, 'DBKD-CHIX': 917, 'DPWD-CHIX': 919, 'DTED-CHIX': 920, 'EOAND-CHIX': 921, 'MRKD-CHIX': 922, 'SIED-CHIX': 923, 'TKAD-CHIX': 924, 'VOW3D-CHIX': 925, 'PIRCM-CHIX': 929, 'PSTM-CHIX': 930, 'TITM-CHIX': 931, 'CSGNZ-CHIX': 933, 'NESNZ-CHIX': 934, 'ROGZ-CHIX': 935, 'UBSGZ-CHIX': 936, 'SANE-CHIX': 937, 'BBVAE-CHIX': 938, 'TEFE-CHIX': 939, 'AIRP-CHIX': 940, 'HEIOA-CHIX': 941, 'ORP-CHIX': 942, 'AUDCHF': 943, 'AUDNZD': 944, 'CADJPY': 945, 'EURCHF': 946, 'GBPNZD': 947, 'NZDCAD': 948, 'NZDJPY': 949, 'EURNOK': 951, 'CHFSGD': 952, 'EURSGD': 955, 'USDMXN': 957, 'JUVEM': 958, 'ASRM': 959, 'MANU': 966, 'UKOUSD': 969, 'XPTUSD': 970, 'USOUSD': 971, 'W1': 977, 'AUDDKK': 983, 'AUDMXN': 985, 'AUDNOK': 986, 'AUDSEK': 988, 'AUDSGD': 989, 'AUDTRY': 990, 'CADMXN': 992, 'CADNOK': 993, 'CADPLN': 994, 'CADTRY': 995, 'CHFDKK': 996, 'CHFNOK': 998, 'CHFSEK': 1000, 'CHFTRY': 1001, 'DKKPLN': 1004, 'DKKSGD': 1005, 'EURDKK': 1007, 'EURMXN': 1008, 'EURTRY': 1010, 'EURZAR': 1011, 'GBPILS': 1013, 'GBPMXN': 1014, 'GBPNOK': 1015, 'GBPPLN': 1016, 'GBPSEK': 1017, 'GBPSGD': 1018, 'GBPTRY': 1019, 'NOKDKK': 1023, 'NOKJPY': 1024, 'NOKSEK': 1025, 'NZDDKK': 1026, 'NZDMXN': 1027, 'NZDNOK': 1028, 'NZDSEK': 1030, 'NZDSGD': 1031, 'NZDTRY': 1032, 'NZDZAR': 1033, 'PLNSEK': 1036, 'SEKDKK': 1037, 'SEKJPY': 1038, 'SGDJPY': 1041, 'USDDKK': 1045, 'NZDCHF': 1048, 'GBPHUF': 1049, 'USDCZK': 1050, 'USDHUF': 1051, 'CADSGD': 1054, 'EURCZK': 1056, 'EURHUF': 1057, 'USDTHB': 1062, 'IOTUSD-L': 1116, 'XLMUSD-L': 1117, 'NEOUSD-L': 1118, 'ADAUSD-L': 1119, 'XEMUSD-L': 1120, 'XRPUSD-L': 1122, 'EEM': 1203, 'FXI': 1204, 'IWM': 1205, 'GDX': 1206, 'XOP': 1209, 'XLK': 1210, 'XLE': 1211, 'XLU': 1212, 'IEMG': 1213, 'XLY': 1214, 'IYR': 1215, 'SQQQ': 1216, 'OIH': 1217, 'SMH': 1218, 'EWJ': 1219, 'XLB': 1221, 'DIA': 1222, 'TLT': 1223, 'SDS': 1224, 'EWW': 1225, 'XME': 1227, 'QID': 1229, 'AUS200': 1230, 'FRANCE40': 1231, 'GERMANY30': 1232, 'HONGKONG50': 1233, 'SPAIN35': 1234, 'US30': 1235, 'USNDAQ100': 1236, 'JAPAN225': 1237, 'USSPX500': 1239, 'UK100': 1241, 'TRXUSD-L': 1242, 'EOSUSD-L': 1244, 'BNBUSD-L': 1279, 'ACB': 1288, 'CGC': 1289, 'CRON': 1290, 'GWPH': 1291, 'MJ': 1292, 'TLRY': 1293, 'BUD': 1294, 'LYFT': 1313, 'PINS': 1315, 'ZM': 1316, 'UBER': 1334, 'MELI': 1335, 'BYND': 1336, 'BSVUSD-L': 1338, 'ONTUSD-L': 1339, 'ATOMUSD-L': 1340, 'WORK': 1343, 'FDJP': 1350, 'CAN': 1351, 'VIAC': 1352, 'TFC': 1353'''
    lista_de_ativos = ativos.split(',')
    lista_ativos = []
    for i in range(len(lista_de_ativos) - 1):
        ati = lista_de_ativos[i].replace('\'', '')
        ati = ati.replace(' ', '')
        ati = ati.replace(':', '')
        ati = re.sub('[0-9]', '', ati)
        lista_ativos.append(ati)

    #MENU
    print('\n')
    print('=-=' * 30)
    print(f'''\tValores Padrões\n
    [Valor de entrada] = {entrada}
    [Par de moeda] = {moeda}
    [Tipo de banca] = {banca}
    [Valor da banca] = {iqoptionapi.get_balance()}
    [TOPs Ranking] = {ranking}
    [Tempo Expiração] = {expiracao} ({tempo_expiracao} minuto(s))
    [Soros] = {soros}
    [Niveis do soros] = {niveis_soros}
    [Stop Loss] = {stop_loss}
    [Stop Win] = {stop_win}\n''')
    time.sleep(5)
    print('=-='*30)
    opcao = -1
    while opcao!=0:
        print('=-=' * 30)
        print('''\t\tMenu\n
        [1] Selecionar/Alterar a banca
        [2] Selecionar/Alterar valor de entrada
        [3] Selecionar/Alterar o par de moedas (Digite sem '/')
        [4] Selecionar/Alterar Top Ranking para copiar
        [5] Mostrar lista de ativos IQOption
        [6] Mostrar banca/valor entrada/moedas/ranking atuais
        [7] Ativar/Desativar Soros
        [8] Alterar tempo de expiração das entradas
        [9] Alterar Stop Win / Stop Loss
        [10] Iniciar entradas
        [0] Fechar programa\n''')

        opcao = int(input('Informe a opção que deseja:'))
        if(opcao==1):
            banca = selecionar_tipo_conta(iqoptionapi)
            time.sleep(2)
        elif(opcao==2):
            entrada = selecionar_valor_entrada()
            time.sleep(2)
        elif(opcao==3):
            moeda = selecionar_par_moedas(lista_ativos)
            time.sleep(2)
        elif(opcao==4):
            ranking = selecionar_top_ranking()
            time.sleep(2)
        elif(opcao==5):
            listar_ativos(lista_ativos)
            time.sleep(5)
        elif(opcao==6):
            mostrar_perfil_atual(entrada, moeda, banca, ranking,soros,niveis_soros,iqoptionapi.get_balance(), expiracao, stop_loss, stop_win)
            time.sleep(5)
        elif(opcao==7):
            soros, niveis_soros= ativar_soros(soros, niveis_soros)
            time.sleep(1)
        elif(opcao==8):
            expiracao, tempo_expiracao = alerar_tempo_expiracao()
            time.sleep(2)
        elif(opcao==9):
            stop_win = alterar_stop_win()
            time.sleep(1)
            stop_loss = alterar_stop_loss()
            time.sleep(1)
        elif(opcao==10):
            iniciar_entradas(iqoptionapi, moeda, entrada, ranking, banca, soros, niveis_soros, expiracao, tempo_expiracao, stop_loss, stop_win)
        elif(opcao==0):
            print('O programa será fechado.')
            sys.exit()
        else:
            print('\033[31m\nVocê selecionou um opção inválida\nTente novamente\033[m')

#Dados do usuário
print('\033[7;30mBem-Vindo ao Copy Trader AKOL\033[m\n')
print('\033[32mDigite suas credenciais\033[m')

email = input('Digite o seu e-mail (IQOption): ')
senha = input('Digite o sua senha (IQOption): ')
# senha = getpass.getpass("Digite o sua senha (IQOption): ")
print('=-='*20)


#Estabelecer Conexão
API = IQ_Option(email, senha)
API.connect()
print('======ESTABELECENDO CONEXÃO ======')


#Verificando conexão
if API.check_connect():
	print(' Conectado com sucesso!')
else:
	print(' Erro ao conectar')
	input(' Aperte enter para sair')
	sys.exit()
time.sleep(2)


#Menu
menu_bot(API)


