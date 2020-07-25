import configparser
import datetime
from iqoptionapi.stable_api import IQ_Option
import time, json
from dateutil import tz

# logging.disable(level=(logging.DEBUG))

# Estabelecendo uma conexão entre a API e a plataforma
API = IQ_Option('sheldonsobral12@gmail.com', 'shureck12')
API.connect()


# Funções
def timestamp_converter(x, retorno=1):
    hora = datetime.strptime(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    hora = hora.replace(tzinfo=tz.gettz('GMT'))

    return str(hora.astimezone(tz.gettz('America/Sao Paulo')))[:-6] if retorno == 1 else hora.astimezone(
        tz.gettz('America/Sao Paulo'))


def perfil():
    perfil = json.loads(json.dumps(API.get_profile_ansyc()))

    return perfil

    '''
        name
        first_name
        last_name
        email
        city
        nickname
        currency
        currency_char 
        address
        created
        postal_index
        gender
        birthdate
        balance		
    '''


def banca():
    return API.get_balance()


# Verificando a conexão com o servidor
if (API.check_connect() != True):
    print('A conexão não foi estabelecida\nVerifique suas credenciais.')
    print(API.check_connect())
else:
    print('A conexão com a plataforma foi estabelecida com sucesso.')
    print(API.check_connect())

# Desenvolvendo
modo_da_conta = 'PRACTICE'
preco_fixo = [100, 70, 50]
paridades = ['EURNZD', 'EURAUD', 'EURJPY']
acoes = ['put', 'call', 'call']
duracao = [0.0, 0.0, 0.0]
duracao_m1 = 1
print(perfil())
# while(API.check_connect()==True):
#     API.change_balance(modo_da_conta)
# API.buy(30,'EURJPY', 'call', -1)
# API.buy_multi(preco_fixo,paridades,acoes, duracao)
# break
# print(API.get_all_open_time())
# ranking = API.get_leader_board('Worldwide',1,5,0)
# # print(json.dumps(ranking, indent=1))
# lideres = ranking['result']['positional']
# lista_id_lideres = []
# for lider in lideres:
#     print(lideres[lider]['user_id'])
#     lista_id_lideres.append(lideres[lider]['user_id'])
#
# print(lista_id_lideres)
#
# operador = API.get_user_profile_client(lista_id_lideres[2])
# print(operador)

# arquivo = configparser.RawConfigParser()
# arquivo.read('config.txt')
# tipo = 'live-deal-binary-option-placed'  # live-deal-binary-option-placed
# timeframe = 'PT1M'  # PT5M / PT15M
# old = 0
# minutos = datetime.datetime.now().strftime('%M')
# minutos_lista = [0,5,10,15,20,25,30,35,40,45,50,55]
# # ok = True
# for minut in minutos_lista:
#     if(int(minutos)==0):
#         expiracao = 5
#         print(expiracao)
#
#     elif(int(minutos)>=55 and int(minutos)<=60 ):
#         expiracao = 60 - int(minutos)
#         print(expiracao)
#     else:
#         for tempo in minutos_lista:
#             if(tempo - int(minutos)<=5 and tempo - int(minutos)>=0):
#                 expiracao = tempo - int(minutos)
#                 print(expiracao)
#         break
# API.buy(30, 'EURJPY', 'call', expiracao)
# print(minutos)
# # API.buy(30,'EURJPY', 'call', 1)
# teste = API.buy_digital_spot('AUDCAD', 7, 'put', 1595439420000)
# IQ_Option.buy_digital(API,1,1)
# API.buy_digital(7, 7)
# API.subscribe_live_deal(tipo, 'GBPCAD', timeframe, 10)
# while True:
#     trades = API.get_live_deal(tipo, 'EURUSD', timeframe)
#     print(trades)

# API.buy_digital_spot('EURUSD', trades[0]['amount_enrolled'], trades[0]['instrument_dir'], 1)
