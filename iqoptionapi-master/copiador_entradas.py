from iqoptionapi.stable_api import IQ_Option
import time, json, logging, configparser
from datetime import datetime, date, timedelta
from dateutil import tz
import sys

# logging.disable(level=(logging.DEBUG))

API = IQ_Option('sheldonsobral12@gmail.com', 'shureck12')
API.connect()

API.change_balance('PRACTICE')  # PRACTICE / REAL

while True:
    if API.check_connect() == False:
        print('Erro ao se conectar')

        API.connect()
    else:
        print('\n\nConectado com sucesso')
        break

    time.sleep(1)


def get_perfil():
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


def timestamp_converter(x, retorno=1):
    hora = datetime.strptime(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    hora = hora.replace(tzinfo=tz.gettz('GMT'))

    return str(hora.astimezone(tz.gettz('America/Sao Paulo')))[:-6] if retorno == 1 else hora.astimezone(
        tz.gettz('America/Sao Paulo'))


def get_banca():
    return API.get_balance()

def configuracao():
    arquivo = configparser.RawConfigParser()
    arquivo.read('config.txt')

    return {'seguir_ids': arquivo.get('GERAL', 'seguir_ids'), 'stop_win': arquivo.get('GERAL', 'stop_win'),
            'stop_loss': arquivo.get('GERAL', 'stop_loss'), 'payout': 0, 'banca_inicial': get_banca(),
            'filtro_diferenca_sinal': arquivo.get('GERAL', 'filtro_diferenca_sinal'),
            'martingale': arquivo.get('GERAL', 'martingale'), 'sorosgale': arquivo.get('GERAL', 'sorosgale'),
            'niveis': arquivo.get('GERAL', 'niveis'), 'filtro_pais': arquivo.get('GERAL', 'filtro_pais'),
            'filtro_top_traders': arquivo.get('GERAL', 'filtro_top_traders'),
            'valor_minimo': arquivo.get('GERAL', 'valor_minimo'), 'paridade': arquivo.get('GERAL', 'paridade'),
            'valor_entrada': arquivo.get('GERAL', 'valor_entrada'), 'timeframe': arquivo.get('GERAL', 'timeframe')}

def filtro_ranking(config):
    user_id = []

    try:
        ranking = API.get_leader_board(
            'Worldwide' if config['filtro_pais'] == 'todos' else config['filtro_pais'].upper(), 1,
            int(config['filtro_top_traders']), 0)

        if int(config['filtro_top_traders']) != 0:
            for n in ranking['result']['positional']:
                id = ranking['result']['positional'][n]['user_id']
                # print(id)
                user_id.append(id)
    except:
        pass

    return user_id


def entradas(config, entrada, direcao, timeframe):
    status, id = API.buy_digital_spot(config['paridade'], entrada, direcao, timeframe)

    if status:
        # #STOP WIN/STOP LOSS
        # banca_att = get_banca()
        # stop_loss = False
        # stop_win = False
        #
        # if round((banca_att - float(config['banca_inicial'])), 2) <= (abs(float(config['stop_loss'])) * -1.0):
        #     stop_loss = True
        #
        # if round((banca_att - float(config['banca_inicial'])) + (float(entrada) * float(config['payout'])) + float(
        #         entrada), 2) >= abs(float(config['stop_win'])):
        #     stop_win = True

        while True:
            status, lucro = API.check_win_digital_v2(id)

            if status:
                if lucro > 0:
                    return 'win', round(lucro, 2)
                else:
                    return 'loss', 0
                break


    else:
        return 'error', 0, False

#ZONA DE COMUNICAÇÃO

print('\nOlá',get_perfil()['email'])
print('Sua banca é de:',get_banca())

# #ZONA DE COPIAMENTO
config = configuracao()
config['banca_inicial'] = get_banca()
# print('Os IDs dos traders que você está seguindo é: ',filtro_ranking(config))
filtro_top_traders = filtro_ranking(config)

if config['seguir_ids'] != '':
    if ',' in config['seguir_ids']:
        x = config['seguir_ids'].split(',')
        for old in x:
            filtro_top_traders.append(int(old))
    else:
        filtro_top_traders.append(int(config['seguir_ids']))

tipo = 'live-deal-digital-option'  # live-deal-binary-option-placed live-deal-digital-option
timeframe = 'PT' + config['timeframe'] + 'M'  # PT5M / PT15M
old = 0
# API.buy(1, 'AUDCAD', 'put', 1)
API.subscribe_live_deal(tipo, config['paridade'], timeframe, 10)
ok = True
print(filtro_top_traders)

while True:

    trades = API.get_live_deal(tipo, config['paridade'], timeframe)
    # print(trades)
    if len(trades) > 0 and old != trades[0]['user_id'] and trades[0]['amount_enrolled'] >= float(
            config['valor_minimo']):
        print(' [', trades[0]['flag'], ']', config['paridade'], '/', trades[0]['amount_enrolled'], '/',
              trades[0]['instrument_dir'], '/', trades[0]['name'], '/',trades[0]['user_id'],'/',trades[0]['expiration_type'])

        ok = True
        # print('2',ok)

        # Correcao de bug em relacao ao retorno de datas errado
        res = round(time.time() - datetime.timestamp(timestamp_converter(trades[0]['created_at'] / 1000, 2)), 2)
        ok = True if res <= int(config['filtro_diferenca_sinal']) else False

        # if len(filtro_top_traders) > 0:
        #     if trades[0]['user_id'] not in filtro_top_traders:
        #         print(' esse está na lista[', trades[0]['flag'], ']', config['paridade'], '/', trades[0]['amount_enrolled'], '/',
        #               trades[0]['instrument_dir'], '/', trades[0]['name'], trades[0]['user_id'])
        #         ok = False

        if len(filtro_top_traders) > 0:
            if trades[0]['user_id'] in filtro_top_traders:
                # entradas(config, config['valor_entrada'], trades[0]['instrument_dir'],
                #                                            int(config['timeframe']))
                # API.buy_digital_spot(config['paridade'],config['valor_entrada'], trades[0]['instrument_dir'], 1)
                # minutos = datetime.datetime.now().strftime('%M')
                # minutos_lista = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
                # # ok = True
                # for minut in minutos_lista:
                #     if (int(minutos) == 0):
                #         expiracao = 5
                #         print(expiracao)
                #
                #     elif (int(minutos) >= 55 and int(minutos) <= 60):
                #         expiracao = 60 - int(minutos)
                #         print(expiracao)
                #     else:
                #         for tempo in minutos_lista:
                #             if (tempo - int(minutos) <= 5 and tempo - int(minutos) >= 0):
                #                 expiracao = tempo - int(minutos)
                #                 print(expiracao)
                #         break
                # API.buy(1, config['paridade'], trades[0]['instrument_dir'], expiracao)
                print(' esse está na lista[', trades[0]['flag'], ']', config['paridade'], '/',
                      trades[0]['amount_enrolled'], '/',
                      trades[0]['instrument_dir'], '/', trades[0]['name'], trades[0]['user_id'])
                resultado, lucro= entradas(config, config['valor_entrada'], trades[0]['instrument_dir'],
                                                  int(config['timeframe']))
                print('   -> ', resultado, '/', lucro, '\n\n')

                # if resultado == 'win':
                #
                #     # valor_antigo = config['valor_entrada']
                #     valor_soros = float(config['valor_entrada']) + float(lucro)
                #     config['valor_entrada']= valor_soros
                ok = True
                # print('3', ok)
        # if ok==True:
        #     # print('4', ok)
        #     # Dados sinal
        #     print(res, end='')
        #     print(' [', trades[0]['flag'], ']', config['paridade'], '/', trades[0]['amount_enrolled'], '/',
        #           trades[0]['instrument_dir'], '/', trades[0]['name'], trades[0]['user_id'])
        #
        #     # 1 entrada
        #     resultado, lucro, stop = entradas(config, config['valor_entrada'], trades[0]['instrument_dir'],
        #                                       int(config['timeframe']))
        #     print('   -> ', resultado, '/', lucro, '\n\n')
            #
            # if stop:
            #     print('\n\nStop', resultado.upper(), 'batido!')
            #     sys.exit()

            # # Martingale
            # if resultado == 'loss' and config['martingale'] == 'S':
            #     valor_entrada = martingale('auto', float(config['valor_entrada']), float(config['payout']))
            #     for i in range(int(config['niveis']) if int(config['niveis']) > 0 else 1):
            #
            #         print('   MARTINGALE NIVEL ' + str(i + 1) + '..', end='')
            #         resultado, lucro, stop = entradas(config, valor_entrada, trades[0]['instrument_dir'],
            #                                           int(config['timeframe']))
            #         print(' ', resultado, '/', lucro, '\n')
            #         if stop:
            #             print('\n\nStop', resultado.upper(), 'batido!')
            #             sys.exit()
            #
            #         if resultado == 'win':
            #             print('\n')
            #             break
            #         else:
            #             valor_entrada = martingale('auto', float(valor_entrada), float(config['payout']))

            # elif resultado == 'loss' and config['sorosgale'] == 'S':  # SorosGale
            #
            #     if float(config['valor_entrada']) > 5:
            #
            #         lucro_total = 0
            #         lucro = 0
            #         perca = float(config['valor_entrada'])
            #         # Nivel
            #         for i in range(int(config['niveis']) if int(config['niveis']) > 0 else 1):
            #
            #             # Mao
            #             for i2 in range(2):
            #
            #                 if lucro_total >= perca:
            #                     break
            #
            #                 print('   SOROSGALE NIVEL ' + str(i + 1) + ' | MAO ' + str(i2 + 1) + ' | ', end='')
            #
            #                 # Entrada
            #                 resultado, lucro, stop = entradas(config, (perca / 2) + lucro, trades[0]['instrument_dir'],
            #                                                   int(config['timeframe']))
            #                 print(resultado, '/', lucro, '\n')
            #                 if stop:
            #                     print('\n\nStop', resultado.upper(), 'batido!')
            #                     sys.exit()
            #
            #                 if resultado == 'win':
            #                     lucro_total += lucro
            #                 else:
            #                     lucro_total = 0
            #                     perca += perca / 2
            #                     break

        old = trades[0]['user_id']
    # time.sleep(0.2)

API.unscribe_live_deal(tipo, config['paridade'], timeframe)