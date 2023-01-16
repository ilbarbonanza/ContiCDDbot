# by ilbarbonanza



# librerie usate
import gspread
import json
import locale
import logging
import os
import random
import sys
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime
from gspread.utils import rowcol_to_a1



# ---------------------------------------------------------------------------   FUNZIONI   ---------------------------------------------------------------------------


# metodo per scrivere in un file le informazioni contenute in un array
def array_to_file(pos: str, array: list):
    file = open(pos, "wt")
    for i in range(len(array)):
        file.write(str(array[i]) + "\n")
    file.close()
    return


# metodo per scrivere in un file le informazioni contenute in un array di array
def arrayofarray_to_file(pos: str, arrayofarray: list):
    file = open(pos, "wt")
    for i in range(len(arrayofarray)):
        for j in range(len(arrayofarray[i])):
            file.write(str(arrayofarray[i][j]) + "§")
        file.write("\n")
    file.close()
    return


# metodo per controllare se un codice generato per un accredito è già stato generato
def check_code(codice: int):
    for i in range(len(accrediti)):
        if (int(accrediti[i][0]) == codice):
            return True
    return False


# metodo per scrivere in un array le informazioni contenute in un file
def file_to_array(pos: str):
    array = []
    file = open(pos, "rt")
    data = file.readlines()
    for line in data:
        if (line.__contains__("\n")):
            line = line[:-1]
        array.append(line)
    file.close()
    return array


# metodo per scrivere in un array di array le informazioni contenute in un file
def file_to_arrayofarray(pos: str):
    arrayofarray = []
    file = open(pos, "rt")
    data = file.readlines()
    for line in data:
        if (line.__contains__("\n")):
            line = line[:-1]
        arrayofarray.append(line.split("§"))
    file.close()
    return arrayofarray


# metodo per scrivere in una variabile le informazioni contenute in un file nel caso ci sia una sola riga
def file_to_variable(pos: str):
    file = open(pos, "rt")
    data = file.readlines()
    if (len(data) <= 0):
        return ""
    variable = data[0][:-1]
    file.close()
    return variable


# metodo per trovare un id nell'array nomi_id a partire dal nome
def find_id(nome: str):
    for i in range(len(nomi_id)):
        if (nomi_id[i][0] == nome):
            return nomi_id[i][1]
    return ""


# metodo per trovare un nome nell'array nomi_id a partire dall'id
def find_name(id: str):
    for i in range(len(nomi_id)):
        if (nomi_id[i][1] == id):
            return nomi_id[i][0]
    return ""


# metodo per generare un codice per un accredito
def generate_code():
    done = False
    codice = 0
    while (not done):
        codice = random.randint(100, 999)
        if (check_code(codice)):
            continue
        else:
            done = True
            break
    return codice


# metodo per controllare se un mittente è in blacklist
def is_blacklisted(id: str):
    for i in range(len(listanera)):
        if (str(listanera[i]) == id):
            return True
    return False


# metodo per controllare se un mittente è nell'array nomi_id
def is_stranger(id: str):
    for i in range(len(nomi_id)):
        if (nomi_id[i][1] == id):
            return False
    return True


# metodo per loggare le informazioni di uno sconosciuto
def log(message: types.Message, command: str):
    info = []
    info.append(datetime.now().strftime("%d/%m/%Y")) # [0]: data
    info.append(datetime.now().strftime("%H:%M:%S")) # [1]: ora
    info.append(str(message.from_user.id)) # [2]: id account Telegram
    info.append(str(message.from_user.is_bot)) # [3]: è bot?
    info.append(str(message.from_user.first_name)) # [4]: nome
    info.append(str(message.from_user.last_name)) # [5]: cognome
    info.append(str(message.from_user.username)) # [6]: username
    info.append(str(message.from_user.language_code)) # [7]: codice lingua
    info.append(str(message.chat.id)) # [8]: id chat
    info.append(str(message.chat.type)) # [9]: tipo chat
    info.append(str(message.chat.title)) # [10]: titolo chat
    info.append(str(message.chat.bio)) # [11]: biografia chat
    info.append(str(message.chat.description)) # [12] descrizione chat
    info.append(command) # [13]: comando usato
    array_to_file(POS_LOGS, info)
    #file = open(POS_LOGS, "at")
    #file.write(info)
    #file.close()
    return


# metodo per stampare gli accrediti
def print_accrediti():
    risposta = "Ecco gli accrediti in attesa:\n   Codice | Debitore |   $   | Motivo   "
    for i in range(len(accrediti)):
        debitore = accrediti[i][7]
        id_debitore = accrediti[i][8]
        if (id_debitore == ID_CASSA):
            id_debitore = ID_LUCA
        mention = "[" + debitore + "](tg://user?id=" + id_debitore + ")"
        risposta = risposta + "\n" + str(i + 1) + ")   *" + str(accrediti[i][0]) + "*   |   " + mention + "   | " + locale.currency(abs(float(accrediti[i][9]))) + " | Verso " + accrediti[i][3] + " per " + accrediti[i][10]
    return risposta


# metodo per stampare i crediti
def print_crediti(id: str):
    counter = 0
    risposta = "Ecco i tuoi crediti:\n   Codice |     $      | Motivo   "
    for i in range(len(accrediti)):
        id_creditore = accrediti[i][4]
        if (id_creditore == id or (id_creditore == ID_CASSA and id == ID_LUCA)):
            counter += 1
            if (id == ID_CASSA):
                id = ID_LUCA
            risposta = risposta + "\n" + str(counter) + ")   *" + str(accrediti[i][0]) + "*   | " + locale.currency(abs(float(accrediti[i][9]))) + " | Da *" + accrediti[i][7] + "* per " + accrediti[i][10]
        else:
            continue
    return risposta


# metodo per stampare i debiti
def print_debiti(id: str):
    counter = 0
    risposta = "Ecco i tuoi debiti:\n   Codice |     $      | Motivo   "
    for i in range(len(accrediti)):
        id_debitore = accrediti[i][8]
        if (id_debitore == id or (id_debitore == ID_CASSA and id == ID_LUCA)):
            counter += 1
            if (id == ID_CASSA):
                id = ID_LUCA
            risposta = risposta + "\n" + str(counter) + ")   *" + str(accrediti[i][0]) + "*   | " + locale.currency(abs(float(accrediti[i][9]))) + " | Verso *" + accrediti[i][3] + "* per " + accrediti[i][10]
        else:
            continue
    return risposta


# metodo di supporto per ordinare l'array accrediti
def sort_debtor(val):
    return val[7]


# metodo per stampare la data nel formato gg/mm/aaaa
def time():
    now = datetime.now()
    return now.strftime("%d/%m/%Y")


# metodo per scrivere in un file le informazioni contenute in una variabile stringa
def variable_to_file(pos: str, variable: str):
    file = open(pos, "wt")
    file.write(variable + "\n")
    file.close()
    return



# ---------------------------------------------------------------------   INIZIALIZZAZIONE  BOT   ---------------------------------------------------------------------


cwd = os.getcwd().replace("\\", "/")

# informazioni per il bot
critical_pos = cwd + "/critical/info.json"

# informazioni per il testing
#critical_pos = cwd + "/critical/test_info.json"

# informazioni critiche
critical_file = open(critical_pos)
critical_data = json.load(critical_file)
critical_file.close()

# inizializzazione del bot
bot = Bot(critical_data["api_token"])
dp = Dispatcher(bot)

# inizializzazione sheet
gc = gspread.service_account() # controllare che il file service_account.json esista e sia messo nella cartella giusta
SHEET_ID = critical_data["sheet_id"]
sheet = gc.open_by_key(SHEET_ID).get_worksheet(0) # sheet 2023
feuille = gc.open_by_key(SHEET_ID).get_worksheet(1) # sheet ATM
foglio = gc.open_by_key(SHEET_ID).get_worksheet(2) # sheet Spese

# posizioni dei file
POS_A = cwd + critical_data["pos_a"]
POS_B = cwd + critical_data["pos_b"]
POS_L = cwd + critical_data["pos_l"]
POS_LOGS = cwd + critical_data["pos_logs"]
POS_T = cwd + critical_data["pos_t"]

# associazioni tra nomi ed id degli account Telegram
nomi_id = critical_data["nomi_id"]

# eliminazione informazioni critiche
critical_data.clear()

# inizializzazione log
logging.basicConfig(format = "%(asctime)s %(levelname)-8s %(message)s", level = logging.INFO, datefmt = "%d/%m/%Y %H:%M:%S")

# inizializzazione locale
locale.setlocale(locale.LC_ALL, "")

# id dell'account Telegram di Luca
ID_LUCA = nomi_id[0][1]

# id dell'account Telegram di Pippo
ID_PIPPO = nomi_id[11][1]

# id dell'account Telegram di Riky
ID_RIKY = nomi_id[12][1]

# id della Cassa del Clan
ID_CASSA = nomi_id[14][1]

# array in cui vengono salvati gli accrediti in attesa
accrediti = file_to_arrayofarray(POS_A)

# inizializzazione dell'array listanera a partire dal file blacklist.txt
listanera = file_to_array(POS_B)

# array in cui vengono salvate le transazioni in attesa
transazioni = file_to_arrayofarray(POS_T)

# struttura di un array transazione:
"""

[0]: riga della cella contenente il nome del mittente
[1]: colonna della cella contenente il nome del mittente
[2]: nome del mittente
[3]: id dell'account Telegram del mittente
[4]: tipo di transazione {"P", "R"}
[5]: somma di denaro della transazione
[6]: causale/motivo della transazione

"""

# struttura di un array accredito:
"""

[0]: codice identificativo dell'accredito
[1]: riga della cella contenente il nome del creditore
[2]: colonna della cella contenente il nome del creditore
[3]: nome del creditore
[4]: id dell'account Telegram del creditore
[5]: riga della cella contenente il nome del debitore
[6]: colonna della cella contenente il nome del debitore
[7]: nome del debitore
[8]: id dell'account Telegram del debitore
[9]: somma di denaro della transazione
[10]: causale/motivo della transazione
[11]: flag per controllare se l'accredito è stato creato da /prestito {"atm", "normale", "prestito"}

"""

# struttura di un array log
"""

[0]: data
[1]: ora
[2]: id account Telegram
[3]: è bot?
[4]: nome
[5]: cognome
[6]: username
[7]: codice lingua
[8]: id chat
[9]: tipo chat
[10]: titolo chat
[11]: biografia chat
[12]: descrizione chat
[13]: comando usato

"""

commands_list = """
Lista di Comandi:
/accredito [danaro], [debitore], [causale] - accredita l'ammontare indicato nel proprio conto
/aiuto - lista di comandi
/capitale - mostra quanti soldi custodiscono Luca e Riky
/conti - lista dei nomi dei conti disponibili
/crediti - mostra i crediti in attesa
/debiti - mostra i debiti in attesa
/donazione [danaro], [causale] - dona l'ammontare indicato alla Cassa
/movimenti - mostra tutti i movimenti del proprio conto
/movimenti [lunghezza] - mostra i più recenti movimenti del proprio conto, specificando quanti
/nope - rifiuta tutti gli accrediti possibili
/nope [codice1], [codice2], ... - rifiuta gli accrediti selezionati
/okay - approva tutti gli accrediti possibili
/okay [codice1], [codice2], ... - approva gli accrediti selezionati
/ping - manda un promemoria a tutti i debitori
/prelievo [danaro] - preleva dal proprio conto l'ammontare indicato
/prestito [danaro], [beneficiario], [causale] - presta l'ammontare indicato al beneficiario
/ricarica [danaro] - ricarica il proprio conto dell'ammontare indicato
/rimuovitastiera - rimuove la tastiera
/ruok - T'appost?
/saldo - mostra il proprio saldo
/tastiera - mostra una tastiera con alcuni comandi
/versamento [danaro], [beneficiario], [causale] - trasferisce l'ammontare indicato al beneficiario

N.B.: il [danaro] usa il punto per i decimali
esempio: 4,20 darà errore, 6.90 verrà accettato
"""

conti_disponibili = """
Ecco i nomi dei conti disponibili:
- Cassa
- Albo
- Alex
- Andy
- Cele
- Dado
- Dani
- Jaco
- Kekko
- Lenzi
- Licia
- Luca
- Maso
- Pippo
- Riky
"""



# ----------------------------------------------------------------------------   COMANDI   ----------------------------------------------------------------------------


# il comando /accredito permette di accreditare denaro dal conto di qualcuno nel proprio
@dp.message_handler(commands = ["accredito"])
async def accredito(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "accredito")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha meno di 11 caratteri (ovvero contiene solo /accredito senza l'importo, il debitore e la causale) manda un messaggio e fine
    if (len(message.text) < 11):
        await bot.send_message(id_chat, "È necessario inserire una somma di denaro, un debitore ed una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova ad analizzare l'argomento del comando /versamento, se non ci sono il debitore e la causale manda un messaggio e fine
    try:
        info = message.text[11:].split(",")
    except:
        await bot.send_message(id_chat, "È necessario inserire un debitore ed una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha più di tre argomenti (ovvero non ha solamente [danaro], [debitore] e [causale]) manda un messaggio e fine
    if (len(info) > 3):
        await bot.send_message(id_chat, "Hai inserito troppi argomenti. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha più di due argomenti (ovvero non ha solamente [danaro] e [causale]) manda un messaggio e fine
    if (len(info) < 3):
        await bot.send_message(id_chat, "La sintassi del comando è errata. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se non ci sono [debitore] e [causale] manda un messaggio e fine
    if (len(info[1]) <= 0 or len(info[2]) <= 0):
        await bot.send_message(id_chat, "È necessario inserire un debitore ed una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova a convertire l'argomento [danaro] in numero decimale, se non ci riesce manda un messaggio e fine
    try:
        danaro = float(info[0])
    except:
        await bot.send_message(id_chat, "Il valore inserito non è una somma di denaro. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il denaro è un numero negativo o nullo, manda un messaggio e fine
    if (danaro <= 0):
        await bot.send_message(id_chat, "La somma di denaro non può essere negativa o nulla. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova a cercare la cella che contiene l'id del mittente del comando, se non la trova allora manda un messaggio e fine 
    try: 
        cella = sheet.find(id_mittente)
    except:
        await bot.send_message(id_chat, "Non so chi tu sia")
        return

    debitore = str(info[1])[1:].lower()
    debitore = debitore[0].upper() + debitore[1:]
    id_debitore = find_id(debitore)
    nome_mittente = find_name(id_mittente)

    # se l'id dell'account Telegram del debitore non è stato trovato nell'array nomi_id, manda un messaggio e fine
    if (id_debitore == ""):
        await bot.send_message(id_chat, "Il nome del debitore non è corretto o non esiste. Riprova per favore", reply_to_message_id = message.message_id)
        return

    cella_debitore = sheet.find(id_debitore)

    # se il debitore coincide con il mittente del messaggio manda un messaggio e fine
    if (id_debitore == id_mittente):
        await bot.send_message(id_chat, "Il debitore non può essere te stesso. Riprova per favore", reply_to_message_id = message.message_id)
        return

    causale = info[2][1:]

    # genera il codice per identificare l'accredito evitando doppioni
    codice = generate_code()

    accredito = []

    # inserimento delle informazioni per l'accredito nell'array accredito
    accredito.append(codice) # [0]: codice identificativo dell'accredito
    accredito.append(cella.row) # [1]: riga della cella contenente il nome del creditore
    accredito.append(cella.col - 1) # [2]: colonna della cella contenente il nome del creditore
    accredito.append(nome_mittente) # [3]: nome del creditore
    accredito.append(id_mittente) # [4]: id dell'account Telegram del creditore
    accredito.append(cella_debitore.row) # [5]: riga della cella contenente il nome del debitore
    accredito.append(cella_debitore.col - 1) # [6]: colonna della cella contenente il nome del debitore
    accredito.append(debitore) # [7]: nome del debitore
    accredito.append(id_debitore) # [8]: id dell'account Telegram del debitore
    accredito.append(abs(danaro)) # [9]: somma di denaro della transazione
    accredito.append(causale) # [10]: causale/motivo della transazione
    accredito.append("normale") # [11]: flag per controllare se l'accredito è stato creato da /prestito
    
    # inserimento dell'accredito in coda all'array accrediti
    accrediti.append(accredito)

    # ordina l'array accrediti per il nome del debitore
    accrediti.sort(key = sort_debtor)

    # aggiornamento del file accrediti.txt
    arrayofarray_to_file(POS_A, accrediti)

    # se il debitore è la Cassa l'id diventa quello di Luca
    if (id_debitore == ID_CASSA):
        id_debitore = ID_LUCA

    # stringa di risposta per il creditore
    risposta = "Attendi l'approvazione di " + debitore

    # stringa di risposta per il debitore
    mention = "[" + debitore + "](tg://user?id=" + id_debitore + ")"
    response = mention + ", *" + nome_mittente + "* ha richiesto un accredito di " + locale.currency(abs(danaro)) + " con codice *" + str(codice) + "* per " + causale

    # notifiche
    await bot.send_message(id_chat, risposta, parse_mode = "Markdown", reply_to_message_id = message.message_id)

    await bot.send_message(id_debitore, response, parse_mode = "Markdown")


# il comando /accreditoatm permette solo a Luca e Riky di trasferire soldi per la gestione degli atm
@dp.message_handler(commands = ["accreditoatm"])
async def accreditoatm(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "accreditoatm")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il mitttente del messaggio non è Luca o Riky manda un messaggio e fine
    if (id_mittente != ID_LUCA and id_mittente != ID_RIKY):
        await bot.send_message(id_chat, "Non hai il permesso di eseguire questo comando", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha meno di 14 caratteri (ovvero contiene solo /accreditoatm senza il danaro) manda un messaggio e fine
    if (len(message.text) < 14):
        await bot.send_message(id_chat, "È necessario inserire una somma di denaro. Riprova per favore", reply_to_message_id = message.message_id)
        return
    
    # prova a convertire il danaro del messaggio in numero decimale, se non ci riesce manda un messaggio e fine
    try:
        danaro = float(message.text[14:])
    except:
        await bot.send_message(id_chat, "Il valore inserito non è una somma di denaro. Riprova per favore", reply_to_message_id = message.message_id)
        return
    
    # se il danaro è negativo manda un messaggio e fine
    if (danaro <= 0):
        await bot.send_message(id_chat, "La somma di denaro non può essere negativa o nulla. Riprova per favore", reply_to_message_id = message.message_id)
        return

    riga = 5

    # se il creditore è Luca, allora il debitore è Riky e viceversa
    if (id_mittente == ID_LUCA):
        colonna_creditore = 1
        colonna_debitore = 6
        debitore = "Riky"
        id_debitore = ID_RIKY
    elif (id_mittente == ID_RIKY):
        colonna_creditore = 6
        colonna_debitore = 1
        debitore = "Luca"
        id_debitore = ID_LUCA
    
    nome_mittente = find_name(id_mittente)

    # genera il codice per identificare l'accredito evitando doppioni
    codice = generate_code()

    accredito = []

    # inserimento delle informazioni per l'accredito nell'array accredito
    accredito.append(codice) # [0]: codice identificativo dell'accredito
    accredito.append(riga) # [1]: riga della cella contenente il nome del creditore
    accredito.append(colonna_creditore) # [2]: colonna della cella contenente il nome del creditore
    accredito.append(nome_mittente) # [3]: nome del creditore
    accredito.append(id_mittente) # [4]: id dell'account Telegram del creditore
    accredito.append(riga) # [5]: riga della cella contenente il nome del debitore
    accredito.append(colonna_debitore) # [6]: colonna della cella contenente il nome del debitore
    accredito.append(debitore) # [7]: nome del debitore
    accredito.append(id_debitore) # [8]: id dell'account Telegram del debitore
    accredito.append(abs(danaro)) # [9]: somma di denaro della transazione
    accredito.append("Versamento ATM") # [10]: causale/motivo della transazione
    accredito.append("atm") # [11]: flag per controllare se l'accredito è stato creato da /prestito
    
    # inserimento dell'accredito in coda all'array accrediti
    accrediti.append(accredito)

    # ordina l'array accrediti per il nome del debitore
    accrediti.sort(key = sort_debtor)

    # aggiornamento del file accrediti.txt
    arrayofarray_to_file(POS_A, accrediti)

    # stringa di risposta per il creditore
    risposta = "Attendi l'approvazione di " + debitore

    # stringa di risposta per il debitore
    mention = "[" + debitore + "](tg://user?id=" + id_debitore + ")"
    response = mention + ", *" + nome_mittente + "* ha richiesto un accredito di " + locale.currency(abs(danaro)) + " con codice *" + str(codice) + "* per Versamento ATM"

    # notifiche
    await bot.send_message(id_chat, risposta, parse_mode = "Markdown", reply_to_message_id = message.message_id)

    await bot.send_message(id_debitore, response, parse_mode = "Markdown")


# il comando /accreditocassa permette solo a Luca di accreditare denaro dal conto di qualcuno in quello della Cassa del Clan
@dp.message_handler(commands = ["accreditocassa"])
async def accreditocassa(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "accreditocassa")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il mitttente del messaggio non è Luca manda un messaggio e fine
    if (id_mittente != ID_LUCA):
        await bot.send_message(id_chat, "Non hai il permesso di eseguire questo comando", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha meno di 16 caratteri (ovvero contiene solo /accreditocassa senza l'importo, il debitore e la causale) manda un messaggio e fine
    if (len(message.text) < 16):
        await bot.send_message(id_chat, "È necessario inserire una somma di denaro, un debitore ed una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova ad analizzare l'argomento del comando /versamento, se non ci sono il debitore e la causale manda un messaggio e fine
    try:
        info = message.text[16:].split(",")
    except:
        await bot.send_message(id_chat, "È necessario inserire un debitore ed una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha più di tre argomenti (ovvero non ha solamente [danaro], [debitore] e [causale]) manda un messaggio e fine
    if (len(info) > 3):
        await bot.send_message(id_chat, "Hai inserito troppi argomenti. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha più di due argomenti (ovvero non ha solamente [danaro] e [causale]) manda un messaggio e fine
    if (len(info) < 3):
        await bot.send_message(id_chat, "La sintassi del comando è errata. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se non ci sono [debitore] e [causale] manda un messaggio e fine
    if (len(info[1]) <= 0 or len(info[2]) <= 0):
        await bot.send_message(id_chat, "È necessario inserire un debitore ed una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova a convertire l'argomento [danaro] in numero decimale, se non ci riesce manda un messaggio e fine
    try:
        danaro = float(info[0])
    except:
        await bot.send_message(id_chat, "Il valore inserito non è una somma di denaro. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il denaro è un numero negativo o nullo, manda un messaggio e fine
    if (danaro <= 0):
        await bot.send_message(id_chat, "La somma di denaro non può essere negativa o nulla. Riprova per favore", reply_to_message_id = message.message_id)
        return

    debitore = str(info[1])[1:].lower()
    debitore = debitore[0].upper() + debitore[1:]
    id_debitore = find_id(debitore)

    # se l'id dell'account Telegram del debitore non è stato trovato nell'array nomi_id, manda un messaggio e fine
    if (id_debitore == ""):
        await bot.send_message(id_chat, "Il nome del debitore non è corretto o non esiste. Riprova per favore", reply_to_message_id = message.message_id)
        return

    cella_debitore = sheet.find(id_debitore)

    causale = info[2][1:]

    # genera il codice per identificare l'accredito evitando doppioni
    codice = generate_code()
    
    accredito = []

    # inserimento delle informazioni per l'accredito nell'array accredito
    accredito.append(codice) # [0]: codice identificativo dell'accredito
    accredito.append(5) # [1]: riga della cella contenente il nome del creditore
    accredito.append(1) # [2]: colonna della cella contenente il nome del creditore
    accredito.append("Cassa") # [3]: nome del creditore
    accredito.append(id_mittente) # [4]: id dell'account Telegram del creditore
    accredito.append(cella_debitore.row) # [5]: riga della cella contenente il nome del debitore
    accredito.append(cella_debitore.col - 1) # [6]: colonna della cella contenente il nome del debitore
    accredito.append(debitore) # [7]: nome del debitore
    accredito.append(id_debitore) # [8]: id dell'account Telegram del debitore
    accredito.append(abs(danaro)) # [9]: somma di denaro della transazione
    accredito.append(causale) # [10]: causale/motivo della transazione
    accredito.append("normale") # [11]: flag per controllare se l'accredito è stato creato da /prestito

    # inserimento dell'accredito in coda all'array accrediti
    accrediti.append(accredito)

    # ordina l'array accrediti per il nome del debitore
    accrediti.sort(key = sort_debtor)

    # aggiornamento del file accrediti.txt
    arrayofarray_to_file(POS_A, accrediti)

    # stringa di risposta per il creditore
    risposta = "Attendi l'approvazione di " + debitore

    # stringa di risposta per il debitore
    mention = "[" + debitore + "](tg://user?id=" + id_debitore + ")"
    response = mention + ", la *Cassa* ha richiesto un accredito di " + locale.currency(abs(danaro)) + " con codice *" + str(codice) + "* per " + causale

    # notifiche
    await bot.send_message(id_chat, risposta, parse_mode = "Markdown", reply_to_message_id = message.message_id)

    await bot.send_message(id_debitore, response, parse_mode = "Markdown")


# il comando /aiuto mostra un elenco di comandi
@dp.message_handler(commands = ["aiuto"])
async def aiuto(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "aiuto")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    await bot.send_message(id_chat, commands_list)


# il comando /avviso permette solo a Luca e Pippo di mandare un messaggio a tutti
@dp.message_handler(commands = ["avviso"])
async def avviso(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "avviso")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il mitttente del messaggio non è Luca o Pippo manda un messaggio e fine
    if (id_mittente != ID_LUCA and id_mittente != ID_PIPPO):
        await bot.send_message(id_chat, "Non hai il permesso di eseguire questo comando", reply_to_message_id = message.message_id)
        return

    messaggio = message.text[8:]

    # manda il messaggio a tutti
    for i in range(len(nomi_id) - 1):
        await bot.send_message(nomi_id[i][1], messaggio, parse_mode = "Markdown")

    # notifica per il mittente
    await bot.send_message(id_mittente, "Messaggi inviati")


# il comando /blacklist permette solo a Luca e Pippo di mostrare una lista degli account a cui è proibito usare ogni comando
@dp.message_handler(commands = ["blacklist"])
async def blacklist(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "blacklist")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il mitttente del messaggio non è Luca o Pippo manda un messaggio e fine
    if (id_mittente != ID_LUCA and id_mittente != ID_PIPPO):
            await bot.send_message(id_chat, "Non hai il permesso di eseguire questo comando", reply_to_message_id = message.message_id)
            return

    # se non ci sono persone nella lista nera, manda un messaggio e fine
    if (len(listanera) <= 0):
        await bot.send_message(id_chat, "La blacklist è vuota")
        return

    risposta = ""

    # assegna gli id dell'account Telegram al nome
    for i in range(len(listanera)):
        mention = "[" + str(find_name(str(listanera[i]))) + "](tg://user?id=" + str(listanera[i]) + ")"
        risposta = risposta + "\n- " + mention
    
    await bot.send_message(id_chat, "Ecco chi è in blacklist:" + risposta, parse_mode = "Markdown")


# il comando /capitale mostra la quantità di denaro di tutti i conti custodita da Luca e Riky
@dp.message_handler(commands = ["capitale"])
async def capitale(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "capitale")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    risposta = "*Attualmente nei conti: " + locale.currency(locale.atof((sheet.cell(3, 11).value)[2:])) + "*"
    risposta = risposta + "\nLuca: " + locale.currency(locale.atof((feuille.cell(5, 4).value)[2:])) + " (" + feuille.cell(2, 12).value + ")"
    risposta = risposta + "\nRiky: " + locale.currency(locale.atof((feuille.cell(5, 9).value)[2:])) + " (" + feuille.cell(3, 12).value + ")"

    await bot.send_message(id_chat, risposta, parse_mode = "Markdown")


# il comando /coda permette solo a Luca, Pippo e Riky di mostrare la coda di transazioni
@dp.message_handler(commands = ["coda"])
async def coda(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "coda")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il mitttente del messaggio non è Luca o Pippo o Riky manda un messaggio e fine
    if (id_mittente != ID_LUCA and id_mittente != ID_PIPPO and id_mittente != ID_RIKY):
        await bot.send_message(id_chat, "Non hai il permesso di eseguire questo comando", reply_to_message_id = message.message_id)
        return

    # se non ci sono transazioni in attesa manda un messaggio e fine
    if (len(transazioni) <= 0):
        await bot.send_message(id_chat, "Non ci sono transazioni in attesa")
        return

    # scrivo le transazioni nella stringa risposta
    risposta = "Ecco le transazioni in attesa:\n    Nome | § | Valore | Motivo"
    for i in range(len(transazioni)):
        risposta = risposta + "\n" + str(i + 1) + ") " + transazioni[i][2] + " | " + transazioni[i][4] + " |  " + locale.currency(float(transazioni[i][5])) + "  | " + transazioni[i][6]
    
    await bot.send_message(id_chat, risposta)


# il comando /conti mostra una lista dei nomi dei conti disponibili
@dp.message_handler(commands = ["conti"])
async def conti(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "conti")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    await bot.send_message(id_chat, conti_disponibili)


# il comando /crediti mostra una lista dei crediti del mittente
@dp.message_handler(commands = ["crediti"])
async def crediti(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "crediti")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    empty = True
    totale = 0

    for i in range(len(accrediti)):
        id_creditore = accrediti[i][4]
        if (id_creditore == id_mittente or (id_creditore == ID_CASSA and id_mittente == ID_LUCA)):
            empty = False
            totale += float(accrediti[i][9])

    # se non ci sono crediti in attesa manda un messaggio e fine
    if (len(accrediti) <= 0 or empty):
        await bot.send_message(id_chat, "Non ci sono crediti in attesa")
        return

    risposta = print_crediti(id_mittente) + "\n\nTotale: " + locale.currency(abs(totale))

    await bot.send_message(id_chat, risposta, parse_mode = "Markdown")


# il comando /debiti mostra una lista dei debiti del mittente
@dp.message_handler(commands = ["debiti"])
async def debiti(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "debiti")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    empty = True
    totale = 0

    for i in range(len(accrediti)):
        id_debitore = accrediti[i][8]
        if (id_debitore == id_mittente or (id_debitore == ID_CASSA and id_mittente == ID_LUCA)):
            empty = False
            totale += float(accrediti[i][9])

    # se non ci sono debiti in attesa manda un messaggio e fine
    if (len(accrediti) <= 0 or empty):
        await bot.send_message(id_chat, "Non ci sono debiti in attesa")
        return

    risposta = print_debiti(id_mittente) + "\n\nTotale: " + locale.currency(abs(totale))

    await bot.send_message(id_chat, risposta, parse_mode = "Markdown")


# il comando /debug permette solo a Luca e Pippo di mostrare informazioni contenute nelle strutture dati del bot utili per il debug
@dp.message_handler(commands = ["debug"])
async def debug(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "debug")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il mitttente del messaggio non è Luca o Pippo manda un messaggio e fine
    if (id_mittente != ID_LUCA and id_mittente != ID_PIPPO):
        await bot.send_message(id_chat, "Non hai il permesso di eseguire questo comando", reply_to_message_id = message.message_id)
        return

    # contenuto degli array
    risposta = "*Array*\n\n\n'accrediti':\n" + str(accrediti) + "\n\n'listanera':\n" + str(listanera) + "\n\n'transazioni':\n" + str(transazioni)

    # contenuto dei file    
    risposta += "\n\n\n\n*File*\n\n\n'accrediti':\n" + str(file_to_arrayofarray(POS_A)) + "\n\n'last':\n" + str(file_to_variable(POS_L)) + "\n\n'listanera':\n" + str(file_to_array(POS_B)) + "\n\n'logs':\n" + str(file_to_array(POS_LOGS)) + "\n\n'transazioni':\n" + str(file_to_arrayofarray(POS_T))

    response = ""

    for i in range(len(risposta)):
        
        tmp = response

        response = response + risposta[i]

        if (sys.getsizeof(response) >= 4096):
            await bot.send_message(id_chat, tmp, parse_mode = "Markdown")
            response = risposta[i]

    await bot.send_message(id_chat, response, parse_mode = "Markdown")


# il comando /donazione dona del denaro alla Cassa
@dp.message_handler(commands = ["donazione"])
async def donazione(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "donazione")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha meno di 11 caratteri (ovvero contiene solo /donazione senza l'importo e la causale) manda un messaggio e fine
    if (len(message.text) < 11):
        await bot.send_message(id_chat, "È necessario inserire una somma di denaro, un beneficiario ed una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova ad analizzare l'argomento del comando /versamento, se non c'è la causale manda un messaggio e fine
    try:
        info = message.text[11:].split(",")
    except:
        await bot.send_message(id_chat, "È necessario inserire una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha più di due argomenti (ovvero non ha solamente [danaro] e [causale]) manda un messaggio e fine
    if (len(info) > 2):
        await bot.send_message(id_chat, "Hai inserito troppi argomenti. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha meno di due argomenti (ovvero non ha solamente [danaro] e [causale]) manda un messaggio e fine
    if (len(info) < 2):
        await bot.send_message(id_chat, "La sintassi del comando è errata. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova a convertire l'argomento [danaro] in numero decimale, se non ci riesce manda un messaggio e fine
    try:
        danaro = float(info[0])
    except:
        await bot.send_message(id_chat, "Il valore inserito non è una somma di denaro. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il denaro è un numero negativo, manda un messaggio e fine
    if (danaro <= 0):
        await bot.send_message(id_chat, "La somma di denaro non può essere negativa. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova a cercare la cella che contiene l'id del mittente del comando, se non la trova allora manda un messaggio e fine 
    try: 
        cella = sheet.find(id_mittente)
    except:
        await bot.send_message(id_chat, "Non so chi tu sia")
        return

    # se il saldo del proprio conto non è sufficiente per prelevare il denaro, manda un messaggio e fine
    if (int(locale.atof((sheet.cell(cella.row, cella.col + 2).value)[3:]) * 100) - int(abs(danaro) * 100) < 0):
        await bot.send_message(id_chat, "Il saldo del tuo conto non è sufficiente. Ricarica prima il tuo conto", reply_to_message_id = message.message_id)
        return

    causale = str(info[1][1:])

    # informazioni da inserire nello sheet
    riga = sheet.cell(cella.row, cella.col + 1).value
    colonna = cella.col - 1
    versatore = str(sheet.cell(cella.row, cella.col - 1).value)
    riga_beneficiario = sheet.cell(5, 3).value
    colonna_beneficiario = 1
    data = time()

    # scrittura delle info del versatore nello sheet
    sheet.update(rowcol_to_a1(riga, colonna), [[data, "V", - danaro, "Verso Cassa per Donazione: " + causale]], value_input_option = "USER_ENTERED")

    # scrittura delle info del beneficiario nello sheet
    sheet.update(rowcol_to_a1(riga_beneficiario, colonna_beneficiario), [[data, "A", danaro, "Da " + versatore + " per Donazione: " + causale]], value_input_option = "USER_ENTERED")

    nome_mittente = find_name(id_mittente)
    denaro = locale.currency(abs(danaro))

    # notifiche
    await bot.send_message(id_chat, "Hai donato *" + denaro + "* alla Cassa per " + causale, parse_mode = "Markdown")

    await bot.send_message(ID_LUCA, nome_mittente + " ha donato *" + denaro + "* alla Cassa per " + causale, parse_mode = "Markdown")


# il comando /lista permette solo a Luca e Pippo di mostrare una lista di tutti gli accrediti
@dp.message_handler(commands = ["lista"])
async def lista(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "lista")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il mitttente del messaggio non è Luca o Pippo manda un messaggio e fine
    if (id_mittente != ID_LUCA and id_mittente != ID_PIPPO):
        await bot.send_message(id_chat, "Non hai il permesso di eseguire questo comando", reply_to_message_id = message.message_id)
        return

    # se non ci sono accrediti in attesa manda un messaggio e fine
    if (len(accrediti) <= 0):
        await bot.send_message(id_chat, "Non ci sono accrediti in attesa")
        return

    risposta = print_accrediti()

    await bot.send_message(id_chat, risposta, parse_mode = "Markdown")


# il comando /logs mostra solo a Pippo una lista di logs del bot
@dp.message_handler(commands=["logs"])
async def logs(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "logs")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il mitttente del messaggio non è Pippo manda un messaggio e fine
    if (id_mittente != ID_PIPPO):
        await bot.send_message(id_chat, "Non hai il permesso di eseguire questo comando", reply_to_message_id = message.message_id)
        return

    risposta = ""

    logs = file_to_arrayofarray(POS_LOGS)

    for i in range(len(logs)):

        risposta += str(i + 1) + ") " + logs[i][0] + " " + logs[i][1] + "\nid: " + logs[i][2] + "\nis_bot: " + logs[i][3] + "\nfirst_name: " + logs[i][4] + "\nlast_name: " + logs[i][5] + "\nusername: " + logs[i][6] + "\nlanguage_code: " + logs[i][7] + "\nchat_id: " + logs[i][8] + "\nchat_type: " + logs[i][9] + "\nchat_title: " + logs[i][10] + "\nchat_bio: " + logs[i][11] + "\nchat_description: " + logs[i][12] + "\ncommand: " + logs[i][13] + "\n\n"

    await bot.send_message(id_chat, risposta)


# il comando /movimenti mostra una lista di movimenti del proprio conto
@dp.message_handler(commands = ["movimenti"])
async def movimenti(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "movimenti")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # prova a cercare la cella che contiene l'id del mittente del comando, se non la trova allora manda un messaggio e fine 
    try: 
        cella = sheet.find(id_mittente)
    except:
        await bot.send_message(id_chat, "Non so chi tu sia")
        return

    # prima riga da non leggere
    riga_end = int(sheet.cell(cella.row, cella.col + 1).value)

    # numero di movimenti da mostrare
    lunghezza = str(message.text[11:])

    # se non è specificato alcun parametro nel comando allora mostra tutti i movimenti, altrimenti ne mostra tanti quanti specificati
    if (lunghezza == ""):
        riga = cella.row + 2
    else:
        # prova a convertire l'argomento [lunghezza] in numero intero, se non ci riesce manda un messaggio e fine
        try:
            lunghezza = int(lunghezza)
        except:
            await bot.send_message(id_chat, "Il valore inserito non è un numero intero. Riprova per favore", reply_to_message_id = message.message_id)
            return
        
        if (lunghezza <= 0):
            await bot.send_message(id_chat, "La lunghezza non può essere nulla o negativa. Riprova per favore", reply_to_message_id = message.message_id)
            return
        
        riga = riga_end - lunghezza

        if (riga < 7):
            await bot.send_message(id_chat, "La lunghezza va oltre il numero di movimenti. Riprova per favore", reply_to_message_id = message.message_id)
            return
    
    # saldo del conto del mittente del comando
    saldo = str(sheet.cell(cella.row, cella.col + 2).value)[2:]

    # se non ci sono movimenti manda un messaggio e fine
    if (saldo.strip(" ") == "-"):
        await bot.send_message(id_chat, "Non hai ancora effettuato alcun movimento", reply_to_message_id = message.message_id)
        return

    # conversione del saldo
    saldo = locale.currency(locale.atof(saldo))

    # intervallo di celle che contengono i movimenti del proprio conto
    intervallo = rowcol_to_a1(riga, cella.col - 1) + ":" + rowcol_to_a1(riga_end, cella.col + 2)

    # lista di movimenti del proprio conto a partire dall'intervallo specificato
    movements = sheet.get(intervallo)

    # conteggio statistiche dei movimenti specificati
    entrate = 0
    uscite = 0

    for i in range(len(movements)):
        
        tipo = movements[i][1]
        danaro = locale.atof(movements[i][2][2:])

        if (tipo == "R" or tipo == "A"):
            entrate += danaro

        elif (tipo == "P" or tipo == "V"):
            uscite += danaro

    # menzione del mittente del comando
    mention = "[" + find_name(id_mittente) + "](tg://user?id=" + id_mittente + ")"

    # inizializzazione della stringa risposta
    risposta = mention + ", ecco i movimenti del tuo conto:\n            Data       | § |  Valore  | Motivo\n"

    # scrivo i movimenti nella stringa risposta
    for i in range(len(movements)):

        # stringa dove vengono salvati i movimenti dell'iterazione precedente
        response = risposta

        # stringa dove viene salvato il movimento dell'iterazione corrente
        movimento = str(i + 1) + ") "

        # concatenazione informazioni di un movimento
        for j in range(0, len(movements[i])):
            movimento = movimento + str(movements[i][j]) + " | "
        
        # formattazione stringa movimento
        if (movimento.__contains__("None")):
            movimento = str(movimento[: -8])
        else:
            movimento = str(movimento[: -3])
        
        # stringa dove vengono salvati i movimenti delle iterazioni precedenti (< 4096 byte) e dell'iterazione corrente
        risposta = risposta + movimento + "\n"
        
        # se il messaggio è troppo lungo (MESSAGE_TOO_LONG Telegram API Error), manda i movimenti dell'iterazione precedente
        if (sys.getsizeof(risposta) >= 4096):
            await bot.send_message(id_chat, response, parse_mode = "Markdown", reply_to_message_id = message.message_id)
            risposta = movimento + "\n"

    await bot.send_message(id_chat, risposta, parse_mode = "Markdown", reply_to_message_id = message.message_id)

    await bot.send_message(id_chat, "\n*Saldo:  " + saldo + "*\nSaldo parziale: " + locale.currency(round(entrate + uscite, 2)) + "\nNumero movimenti: " + str(riga_end - 7), parse_mode = "Markdown", reply_to_message_id = message.message_id)


# il comando /no permette solo a Luca e Riky di rifiutare una transazione
@dp.message_handler(commands = ["no"])
async def no(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)
    nome_mittente = find_name(id_mittente)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "no")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il mitttente del messaggio non è Luca o Riky manda un messaggio e fine
    if (id_mittente != ID_LUCA and id_mittente != ID_RIKY):
        await bot.send_message(id_chat, "Non hai il permesso di eseguire questo comando", reply_to_message_id = message.message_id)
        return
    
    # se non ci sono transazioni in attesa manda un messaggio e fine
    if (len(transazioni) <= 0):
        await bot.send_message(id_chat, "Non ci sono transazioni in attesa")
        return

    # rimozione della transazione in testa alla coda di transazioni
    transazione = transazioni.pop(0)

    # aggiornamento del file transazioni.txt
    arrayofarray_to_file(POS_T, transazioni)

    # stringa di risposta per il mittente della transazione
    id = transazione[3]
    mention = "[" + transazione[2] + "](tg://user?id=" + id + ")"
    danaro = float(transazione[5])
    tipo = transazione[4]
    if (tipo == "R"):
        risposta = mention + ", la ricarica di " + locale.currency(abs(danaro)) + " è stata cancellata da " + nome_mittente
    elif (tipo == "P"):
        risposta = mention + ", il prelievo di " + locale.currency(abs(danaro)) + " è stato cancellato da " + nome_mittente

    # notifiche
    await bot.send_message(ID_LUCA, "La transazione in testa alla coda è stata cancellata da " + nome_mittente)

    await bot.send_message(ID_RIKY, "La transazione in testa alla coda è stata cancellata da " + nome_mittente)

    await bot.send_message(id, risposta, parse_mode = "Markdown")


# il comando /nope permette di rifiutare uno o più accrediti
@dp.message_handler(commands = ["nope"])
async def nope(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)
    nome_mittente = find_name(id_mittente)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "nope")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    codici = message.text[6:].split(",")

    # se il comando non contiene nessun parametro rifiuta tutti gli accrediti, tranne quelli creati con /prestito
    if (codici[0] == ""):
        
        indexes = []

        # raggruppa gli indici degli accrediti che il mittente del comando può rifiutare
        for i in range(len(accrediti) - 1, - 1, - 1):

            id_debitore = accrediti[i][8]
            flag = accrediti[i][11]

            if ((id_debitore == id_mittente or (id_debitore == ID_CASSA and id_mittente == ID_LUCA)) and (flag == "atm" or flag == "normale")):
                indexes.append(i)

        # se non ci sono accrediti da rifiutare, manda un messaggio e fine
        if (len(indexes) <= 0):
            await bot.send_message(id_mittente, "Non ci sono accrediti in attesa")
            return

        # rifiuto degli accrediti
        for i in range(len(indexes)):

            # rimozione dell'accredito selezionato
            accredito = accrediti.pop(indexes[i])

            codice = "*" + str(accredito[0]) + "*"
            nome_creditore = accredito[3]
            id_creditore = accredito[4]
            nome_debitore = accredito[7]
            danaro = float(accredito[9])
            causale = accredito[10]
            
            # stringa di risposta per il creditore
            mention = "[" + nome_creditore + "](tg://user?id=" + id_creditore + ")"
            response = mention + ", " + nome_debitore + " ha rifiutato l'accredito di " + locale.currency(abs(danaro)) + " per " + causale
            
            # notifica per il creditore
            await bot.send_message(id_creditore, response, parse_mode = "Markdown")

        # stringa di risposta per il mittente
        mention = "[" + find_name(id_mittente) + "](tg://user?id=" + id_mittente + ")"
        risposta = mention + ", tutti gli accrediti sono stati cancellati"

        # notifica per il mittente
        await bot.send_message(id_chat, risposta, parse_mode = "Markdown", reply_to_message_id = message.message_id)

    # se il comando contiene dei parametri controlla che siano corretti e rifiuta gli accrediti richiesti
    else:

        # rifiuto degli accrediti
        for i in range(len(codici)):

            codice = codici[i].strip()

            # se un codice ha meno di tre cifre manda un messaggio e fine
            if (len(codice) < 3):
                await bot.send_message(id_chat, "Il " + str(i + 1) + "° codice è troppo corto. Riprova per favore", reply_to_message_id = message.message_id)
                continue
        
            # se un codice ha più di tre cifre manda un messaggio e fine
            elif (len(codice) > 3):
                await bot.send_message(id_chat, "Il " + str(i + 1) + "° codice è troppo lungo. Riprova per favore", reply_to_message_id = message.message_id)
                continue

            # prova a convertire il codice del messaggio in numero intero, se non ci riesce manda un messaggio e fine
            try:
                codice = int(codice)
            except:
                await bot.send_message(id_chat, "Il " + str(i + 1) + "° valore inserito non è un codice valido. Riprova per favore", reply_to_message_id = message.message_id)
                continue

            # cerca se il codice è presente nell'array acccrediti
            codeFound = False
            for j in range(len(accrediti)):
                if (str(accrediti[j][0]) == str(codice)):
                    codeFound = True
                    id_creditore = str(accrediti[j][4])
                    id_debitore = str(accrediti[j][8])
                    index = j
                    flag = accrediti[j][11]
            
            # se il codice nel messaggio non è nell'array accrediti, manda un messaggio e fine
            if (codeFound == False):
                await bot.send_message(id_chat, "Il" + str(i + 1) + "° codice inserito non esiste. Riprova per favore", reply_to_message_id = message.message_id)
                continue

            # se l'accredito è stato creato da un prestito non si può rifiutare, quindi manda un messaggio e continua
            if (flag == "prestito"):
                await bot.send_message(id_chat, "Non puoi rifiutare l'accredito con codice *" + str(codice) + "* perché proviene da un prestito", parse_mode = "Markdown", reply_to_message_id = message.message_id)
                continue
    
            # nel caso in cui il debitore sia la Cassa del Clan, solo Luca può rifiutare l'accredito
            if (id_debitore == ID_CASSA):
                id_debitore = ID_LUCA

            # se il mittente del messaggio non è colui che deve rifiutare l'accredito, manda un messaggio e fine
            if (id_mittente != id_debitore and id_mittente != id_creditore):
                await bot.send_message(id_chat, "Non puoi rifiutare il " + str(i + 1) + "° accredito", reply_to_message_id = message.message_id)
                continue

            # rimozione dell'accredito selezionato
            accredito = accrediti.pop(index)

            codice = "*" + str(accredito[0]) + "*"
            nome_creditore = accredito[3]
            nome_debitore = accredito[7]
            danaro = float(accredito[9])
            causale = accredito[10]

            if (id_mittente == id_debitore):

                # stringa di risposta per il creditore
                mention = "[" + nome_creditore + "](tg://user?id=" + id_creditore + ")"
                response = mention + ", " + nome_debitore + " ha rifiutato l'accredito di " + locale.currency(abs(danaro)) + " per " + causale
            
                # notifica per il creditore
                await bot.send_message(id_creditore, response, parse_mode = "Markdown")
            
            elif (id_mittente == id_creditore):

                # stringa di risposta per il debitore
                mention = "[" + nome_debitore + "](tg://user?id=" + id_debitore + ")"
                response = mention + ", " + nome_creditore + " ha cancellato l'accredito di " + locale.currency(abs(danaro)) + " per " + causale

                # notifica per il debitore
                await bot.send_message(id_debitore, response, parse_mode = "Markdown")

            # stringa di risposta per il mittente
            mention = "[" + nome_mittente + "](tg://user?id=" + id_mittente + ")"
            risposta = mention + ", l'accredito con codice " + codice + " è stato cancellato"

            # notifica per il mittente
            await bot.send_message(id_chat, risposta, parse_mode = "Markdown", reply_to_message_id = message.message_id)

    # aggiornamento del file accrediti.txt
    arrayofarray_to_file(POS_A, accrediti)


# il comando /nuke permette solo a Luca e a Pippo di eliminare la coda di transazioni
@dp.message_handler(commands = ["nuke"])
async def nuke(message: types.Message):
    
    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)
    nome_mittente = find_name(id_mittente)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "nuke")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il mitttente del messaggio non è Luca manda un messaggio e fine
    if (id_mittente != ID_LUCA and id_mittente != ID_PIPPO):
        await bot.send_message(id_chat, "Non hai il permesso di eseguire questo comando", reply_to_message_id = message.message_id)
        return

    # se gli array transazioni e accrediti sono vuoti manda un messaggio e fine
    if (len(transazioni) == 0 and len(accrediti) == 0):
        await bot.send_message(id_chat, "Non ci sono transazioni o accrediti in attesa", reply_to_message_id = message.message_id)
        return

    if (len(transazioni) == 0 or len(accrediti) == 0):
        if (len(transazioni) == 0):
            for i in range(len(accrediti) - 1, - 1, - 1):
                if (str(accrediti[i][11]) != "prestito"):

                    accredito = accrediti.pop(i)

                    codice = str(accredito[0])
                    nome_creditore = accredito[3]
                    id_creditore = accredito[4]
                    nome_debitore = accredito[7]
                    id_debitore = accredito[8]
                    danaro = float(accredito[9])
                    causale = accredito[10]

                    # notifiche
                    await bot.send_message(id_creditore, "L'accredito di " + locale.currency(danaro) + " a *" + nome_debitore + "* per " + causale + " è stato eliminato da " + nome_mittente + " con il comando /nuke", parse_mode = "Markdown")

                    await bot.send_message(id_debitore, "L'accredito di " + locale.currency(danaro) + " con codice *" + codice + "* da *" + nome_creditore + "* per " + causale + " è stato eliminato da " + nome_mittente + " con il comando /nuke", parse_mode = "Markdown")

        else:
            for i in range(len(transazioni)):

                transazione = transazioni.pop(i)

                id = transazione[3]
                tipo = transazione[4]
                danaro = float(transazione[5])
                causale = transazione[6]

                if (tipo == "P"):
                    risposta = "Il *prelievo* di " + locale.currency(danaro) + " è stato eliminato da " + nome_mittente + " con il comando /nuke"
                elif (tipo == "R"):
                    risposta = "La *ricarica* di " + locale.currency(danaro) + " è stata eliminata da " + nome_mittente + " con il comando /nuke"

                # notifica
                await bot.send_message(id, risposta, parse_mode = "Markdown")

    else:
        # pulizia dell'array transazioni
        for i in range(len(transazioni)):

            transazione = transazioni.pop(i)

            id = transazione[3]
            tipo = transazione[4]
            danaro = float(transazione[5])
            causale = transazione[6]

            if (tipo == "P"):
                risposta = "Il *prelievo* di " + locale.currency(danaro) + " è stato eliminato da " + nome_mittente + " con il comando /nuke"
            elif (tipo == "R"):
                risposta = "La *ricarica* di " + locale.currency(danaro) + " è stata eliminata da " + nome_mittente + " con il comando /nuke"

            # notifica
            await bot.send_message(id, risposta, parse_mode = "Markdown")

        # pulizia dell'array accrediti
        for i in range(len(accrediti) - 1, - 1, - 1):
            if (str(accrediti[i][11]) != "prestito"):

                accredito = accrediti.pop(i)

                codice = str(accredito[0])
                nome_creditore = accredito[3]
                id_creditore = accredito[4]
                nome_debitore = accredito[7]
                id_debitore = accredito[8]
                danaro = float(accredito[9])
                causale = accredito[10]

                # notifiche
                await bot.send_message(id_creditore, "L'accredito di " + locale.currency(danaro) + " a *" + nome_debitore + "* per " + causale + " è stato eliminato da " + nome_mittente + " con il comando /nuke", parse_mode = "Markdown")

                await bot.send_message(id_debitore, "L'accredito di " + locale.currency(danaro) + " con codice *" + codice + "* da *" + nome_creditore + "* per " + causale + " è stato eliminato da " + nome_mittente + " con il comando /nuke", parse_mode = "Markdown")

    # aggiornamento del file transazioni.txt
    arrayofarray_to_file(POS_T, transazioni)

    # aggiornamento del file accrediti.txt
    arrayofarray_to_file(POS_A, accrediti)

    # aggiornamento del file last.txt
    variable_to_file(POS_L, "")

    await bot.send_message(id_chat, "Tutte le transazioni e gli accrediti in attesa, oltre alla causale per /strozzino, sono stati cancellati")


# il comando /ok permette solo a Luca e Riky di approvare la transazione in testa alla coda di transazioni
@dp.message_handler(commands = ["ok"])
async def ok(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)
    nome_mittente = find_name(id_mittente)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "ok")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il mitttente del messaggio non è Luca o Riky manda un messaggio e fine
    if (id_mittente != ID_LUCA and id_mittente != ID_RIKY):
        await bot.send_message(id_chat, "Non hai il permesso di eseguire questo comando", reply_to_message_id = message.message_id)
        return
    
    # se non ci sono transazioni in attesa manda un messaggio e fine
    if (len(transazioni) <= 0):
        await bot.send_message(id_chat, "Non ci sono transazioni in attesa")
        return

    # lettura e rimozione della transazione in testa alla coda di transazioni
    transazione = transazioni.pop(0)

    # lettura dei valori dell'array transazione
    riga = int(transazione[0])
    colonna = int(transazione[1])
    nome = transazione[2]
    id = transazione[3]
    data = time()
    tipo_transazione = transazione[4]
    danaro = float(transazione[5])
    causale = transazione[6]

    # stringa per menzionare il mittente
    mention = "[" + nome + "](tg://user?id=" + id + ")"

    # se il tipo di transazione è un prelievo, allora esegue un controllo sul saldo del conto del mittente
    if (tipo_transazione == "P"):
        # se il saldo del conto del mittente è minore della somma di denaro della transazione, manda un messaggio e fine
        if (int(locale.atof((sheet.cell(riga, colonna + 3).value)[3:]) * 100) - int(abs(danaro) * 100) < 0):
            await bot.send_message(id_chat, "Ora il saldo del conto di " + mention + " non è sufficiente", parse_mode = "Markdown")
            return

    # prima riga vuota
    riga = sheet.cell(riga, colonna + 2).value

    # scrittura delle info nello sheet
    sheet.update(rowcol_to_a1(riga, colonna), [[data, tipo_transazione, danaro, causale]], value_input_option = "USER_ENTERED")

    # controlla chi ha mandato il comando
    if (id_mittente == ID_LUCA):
        column = 1
        id_reply = ID_RIKY
        riga_percentuale = 2
    elif (id_mittente == ID_RIKY):
        column = 6
        id_reply = ID_LUCA
        riga_percentuale = 3
    
    # prima riga vuota nel foglio ATM
    row = feuille.cell(5, column + 2).value

    # scrittura delle info nel foglio ATM
    if (tipo_transazione == "P"):
        feuille.update(rowcol_to_a1(row, column), [[data, tipo_transazione, danaro, "Verso " + nome]], value_input_option = "USER_ENTERED")
    elif (tipo_transazione == "R"):
        feuille.update(rowcol_to_a1(row, column), [[data, tipo_transazione, danaro, "Da " + nome]], value_input_option = "USER_ENTERED")

    # soldi nell'ATM del mittente
    soldi = locale.currency(locale.atof((feuille.cell(5, column + 3).value)[2:]))

    # percentuale di soldi custoditi in ATM rispetto al totale
    percentuale = feuille.cell(riga_percentuale, 12).value

    # formattazione per il messaggio di risposta
    denaro = locale.currency(abs(danaro))
    if (tipo_transazione == "P"):
        risposta = mention + ", il prelievo con *" + nome_mittente + "* di " + denaro + " è riuscito"
        response = "Il prelievo di " + denaro + " è riuscito\nSoldi ATM: " + soldi + "\nPercentuale ATM: " + percentuale
        reply = "Il prelievo è stato effettuato da " + nome_mittente
    elif (tipo_transazione == "R"):
        risposta = mention + ", la ricarica con *" + nome_mittente + "* di " + denaro + " è riuscita"
        response = "La ricarica di " + denaro + " è riuscita\nSoldi ATM: " + soldi + "\nPercentuale ATM: " + percentuale
        reply = "La ricarica è stata effettuata da *" + nome_mittente + "*"

    # pulizia dell'array transazione, eliminando tutti i valori inseriti e impostando la dimensione a zero
    transazione.clear()

    # aggiornamento del file transazioni.txt
    arrayofarray_to_file(POS_T, transazioni)

    # notifiche
    await bot.send_message(id_chat, response, parse_mode = "Markdown")

    await bot.send_message(id, risposta, parse_mode = "Markdown")

    await bot.send_message(id_reply, reply, parse_mode = "Markdown")


# il comando /okay permette di approvare uno o più accrediti
@dp.message_handler(commands = ["okay"])
async def okay(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "okay")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    codici = message.text[6:].split(",")

    # se il comando non contiene nessun parametro approva tutti gli accrediti
    if (codici[0] == ""):
        
        indexes = []

        # raggruppa gli indici degli accrediti che il mittente del comando può approvare
        for i in range(len(accrediti) - 1, - 1, - 1):
            if (accrediti[i][8] == id_mittente or (accrediti[i][8] == ID_CASSA and id_mittente == ID_LUCA)):
                indexes.append(i)

        # se non ci sono accrediti da approvare, manda un messaggio e fine
        if (len(indexes) <= 0):
            await bot.send_message(id_mittente, "Non ci sono accrediti in attesa")
            return

        # approvazione degli accrediti
        for i in range(len(indexes)):
            
            indice = indexes[i]

            # lettura dell'accredito scelto
            accredito = accrediti[indice]

            # lettura dei valori dell'array accredito
            codice = int(accredito[0])
            riga_creditore = int(accredito[1])
            colonna_creditore = int(accredito[2])
            creditore = accredito[3]
            id_creditore = accredito[4]
            riga_debitore = int(accredito[5])
            colonna_debitore = int(accredito[6])
            debitore = accredito[7]
            id_debitore = accredito[8]
            data = time()
            danaro = float(accredito[9])
            causale = accredito[10]
            flag = accredito[11]

            if (flag == "normale"):

                # se il saldo del conto del debitore è minore della somma di denaro della transazione, manda un messaggio e fine
                if (int(locale.atof((sheet.cell(riga_debitore, colonna_debitore + 3).value)[3:]) * 100) - int(abs(danaro) * 100) < 0):
                    mention = "[" + debitore + "](tg://user?id=" + str(id_debitore) + ")"
                    await bot.send_message(id_chat, "Il tuo saldo non è sufficiente per approvare l'accredito con codice *" + str(codice) + "*", parse_mode = "Markdown", reply_to_message_id = message.message_id)
                    continue
            
                # scrittura dei valori dell'accredito al creditore
                riga_creditore = int(sheet.cell(riga_creditore, colonna_creditore + 2).value)
                sheet.update(rowcol_to_a1(riga_creditore, colonna_creditore), [[data, "A", danaro, "Da " + debitore + " per " + causale]], value_input_option = "USER_ENTERED")

                # scrittura dei valori dell'accredito al debitore
                riga_debitore = int(sheet.cell(riga_debitore, colonna_debitore + 2).value)
                sheet.update(rowcol_to_a1(riga_debitore, colonna_debitore), [[data, "V", - danaro, "Verso " + creditore + " per " + causale]], value_input_option = "USER_ENTERED")

                # se l'accredito proviene da /strozzino, aggiorna il colore della cella del debito per significare che il debitore ha pagato
                causali = foglio.row_values(1)
                indice_colonna = 0
                for j in range(len(causali)):
                    if (causali[j] == causale):
                        indice_colonna = j + 1
                if (indice_colonna > 0):
                    for j in range(len(nomi_id)):
                        if (nomi_id[j][0] == debitore):
                            indice_riga = j + 2
                    foglio.format(rowcol_to_a1(indice_riga, indice_colonna), {"backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}})

            elif (flag == "prestito"):

                # se il saldo del conto del debitore è minore della somma di denaro della transazione, manda un messaggio e fine
                if (int(locale.atof((sheet.cell(riga_debitore, colonna_debitore + 3).value)[3:]) * 100) - int(abs(danaro) * 100) < 0):
                    mention = "[" + debitore + "](tg://user?id=" + str(id_debitore) + ")"
                    await bot.send_message(id_chat, "Il tuo saldo non è sufficiente per approvare l'accredito con codice *" + str(codice) + "*", parse_mode = "Markdown", reply_to_message_id = message.message_id)
                    continue
            
                # scrittura dei valori dell'accredito al creditore
                riga_creditore = int(sheet.cell(riga_creditore, colonna_creditore + 2).value)
                sheet.update(rowcol_to_a1(riga_creditore, colonna_creditore), [[data, "A", danaro, "Da " + debitore + " per " + causale]], value_input_option = "USER_ENTERED")

                # scrittura dei valori dell'accredito al debitore
                riga_debitore = int(sheet.cell(riga_debitore, colonna_debitore + 2).value)
                sheet.update(rowcol_to_a1(riga_debitore, colonna_debitore), [[data, "V", - danaro, "Verso " + creditore + " per " + causale]], value_input_option = "USER_ENTERED")


            elif (flag == "atm"):

                # se il saldo del conto del debitore è minore della somma di denaro della transazione, manda un messaggio e fine
                if (int(locale.atof((feuille.cell(riga_debitore, colonna_debitore + 3).value)[3:]) * 100) - int(abs(danaro) * 100) < 0):
                    mention = "[" + debitore + "](tg://user?id=" + str(id_debitore) + ")"
                    await bot.send_message(id_chat, "Il tuo saldo non è sufficiente per approvare l'accredito con codice *" + str(codice) + "*", parse_mode = "Markdown", reply_to_message_id = message.message_id)
                    continue
            
                # scrittura dei valori dell'accredito al creditore
                riga_creditore = int(feuille.cell(riga_creditore, colonna_creditore + 2).value)
                feuille.update(rowcol_to_a1(riga_creditore, colonna_creditore), [[data, "A", danaro, "Da " + debitore + " per " + causale]], value_input_option = "USER_ENTERED")

                # scrittura dei valori dell'accredito al debitore
                riga_debitore = int(feuille.cell(riga_debitore, colonna_debitore + 2).value)
                feuille.update(rowcol_to_a1(riga_debitore, colonna_debitore), [[data, "V", - danaro, "Verso " + creditore + " per " + causale]], value_input_option = "USER_ENTERED")

            # rimozione dell'accredito
            accrediti.pop(indice)

            # pulizia dell'array transazione, eliminando tutti i valori inseriti e impostando la dimensione a zero
            accredito.clear()

            # stringa di risposta per il mittente
            mention = "[" + debitore + "](tg://user?id=" + id_debitore + ")"
            risposta = mention + ", l'accredito con codice *" + str(codice) + "* è riuscito"

            # stringa di risposta per il creditore
            if (creditore == "Cassa"):
                mention = "[Cassa](tg://user?id=" + str(ID_LUCA) + ")"
            else:
                mention = "[" + creditore + "](tg://user?id=" + id_creditore + ")"

            response = mention + " hai ricevuto " + locale.currency(danaro) + " da " + debitore + " per " + causale    

            # notifiche
            await bot.send_message(id_chat, risposta, parse_mode = "Markdown")

            await bot.send_message(id_creditore, response, parse_mode = "Markdown")

    # se il comando contiene dei parametri controlla che siano corretti e approva gli accrediti richiesti
    else:

        # approvazione degli accrediti
        for i in range(len(codici)):

            codice = codici[i].strip()

            # se un codice ha meno di tre cifre manda un messaggio e fine
            if (len(codice) < 3):
                await bot.send_message(id_chat, "Il " + str(i + 1) + "° codice è troppo corto. Riprova per favore", reply_to_message_id = message.message_id)
                continue
        
            # se un codice ha più di tre cifre manda un messaggio e fine
            elif (len(codice) > 3):
                await bot.send_message(id_chat, "Il " + str(i + 1) + "° codice è troppo lungo. Riprova per favore", reply_to_message_id = message.message_id)
                continue

            # prova a convertire il codice del messaggio in numero intero, se non ci riesce manda un messaggio e fine
            try:
                codice = int(codice)
            except:
                await bot.send_message(id_chat, "Il " + str(i + 1) + "° valore inserito non è un codice valido. Riprova per favore", reply_to_message_id = message.message_id)
                continue

            # cerca se il codice è presente nell'array acccrediti
            codeFound = False
            for j in range(len(accrediti)):
                if (str(accrediti[j][0]) == str(codice)):
                    codeFound = True
                    allowed = str(accrediti[j][8])
                    index = j
    
            # se il codice nel messaggio non è nell'array accrediti, manda un messaggio e fine
            if (codeFound == False):
                await bot.send_message(id_chat, "Il " + str(i + 1) + "° codice inserito non esiste. Riprova per favore", reply_to_message_id = message.message_id)
                continue 
    
            # nel caso in cui il debitore sia la Cassa del Clan, solo Luca può approvare l'accredito
            if (allowed == ID_CASSA):
                allowed = ID_LUCA

            # se il mittente del messaggio non è colui che deve approvare l'accredito, manda un messaggio e fine
            if (id_mittente != str(allowed)):
                await bot.send_message(id_chat, "Non puoi approvare il " + str(i + 1) + "° accredito", reply_to_message_id = message.message_id)
                continue

            # lettura dell'accredito scelto
            accredito = accrediti[index]

            # lettura dei valori dell'array accredito
            riga_creditore = int(accredito[1])
            colonna_creditore = int(accredito[2])
            creditore = accredito[3]
            id_creditore = accredito[4]
            riga_debitore = int(accredito[5])
            colonna_debitore = int(accredito[6])
            debitore = accredito[7]
            id_debitore = accredito[8]
            data = time()
            danaro = float(accredito[9])
            causale = accredito[10]
            flag = accredito[11]

            if (flag == "normale"):

                # se il saldo del conto del debitore è minore della somma di denaro della transazione, manda un messaggio e fine
                if (int(locale.atof((sheet.cell(riga_debitore, colonna_debitore + 3).value)[3:]) * 100) - int(abs(danaro) * 100) < 0):
                    mention = "[" + debitore + "](tg://user?id=" + str(id_debitore) + ")"
                    await bot.send_message(id_chat, "Il tuo saldo non è sufficiente per approvare l'accredito con codice *" + str(codice) + "*", parse_mode = "Markdown", reply_to_message_id = message.message_id)
                    continue
            
                # scrittura dei valori dell'accredito al creditore
                riga_creditore = int(sheet.cell(riga_creditore, colonna_creditore + 2).value)
                sheet.update(rowcol_to_a1(riga_creditore, colonna_creditore), [[data, "A", danaro, "Da " + debitore + " per " + causale]], value_input_option = "USER_ENTERED")

                # scrittura dei valori dell'accredito al debitore
                riga_debitore = int(sheet.cell(riga_debitore, colonna_debitore + 2).value)
                sheet.update(rowcol_to_a1(riga_debitore, colonna_debitore), [[data, "V", - danaro, "Verso " + creditore + " per " + causale]], value_input_option = "USER_ENTERED")

                # se l'accredito proviene da /strozzino, aggiorna il colore della cella del debito per significare che il debitore ha pagato
                causali = foglio.row_values(1)
                indice_colonna = 0
                for j in range(len(causali)):
                    if (causali[j] == causale):
                        indice_colonna = j + 1
                if (indice_colonna > 0):
                    for j in range(len(nomi_id)):
                        if (nomi_id[j][0] == debitore):
                            indice_riga = j + 2
                    foglio.format(rowcol_to_a1(indice_riga, indice_colonna), {"backgroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}})

            elif (flag == "prestito"):

                # se il saldo del conto del debitore è minore della somma di denaro della transazione, manda un messaggio e fine
                if (int(locale.atof((sheet.cell(riga_debitore, colonna_debitore + 3).value)[3:]) * 100) - int(abs(danaro) * 100) < 0):
                    mention = "[" + debitore + "](tg://user?id=" + str(id_debitore) + ")"
                    await bot.send_message(id_chat, "Il tuo saldo non è sufficiente per approvare l'accredito con codice *" + str(codice) + "*", parse_mode = "Markdown", reply_to_message_id = message.message_id)
                    continue
            
                # scrittura dei valori dell'accredito al creditore
                riga_creditore = int(sheet.cell(riga_creditore, colonna_creditore + 2).value)
                sheet.update(rowcol_to_a1(riga_creditore, colonna_creditore), [[data, "A", danaro, "Da " + debitore + " per " + causale]], value_input_option = "USER_ENTERED")

                # scrittura dei valori dell'accredito al debitore
                riga_debitore = int(sheet.cell(riga_debitore, colonna_debitore + 2).value)
                sheet.update(rowcol_to_a1(riga_debitore, colonna_debitore), [[data, "V", - danaro, "Verso " + creditore + " per " + causale]], value_input_option = "USER_ENTERED")


            elif (flag == "atm"):

                # se il saldo del conto del debitore è minore della somma di denaro della transazione, manda un messaggio e fine
                if (int(locale.atof((feuille.cell(riga_debitore, colonna_debitore + 3).value)[3:]) * 100) - int(abs(danaro) * 100) < 0):
                    mention = "[" + debitore + "](tg://user?id=" + str(id_debitore) + ")"
                    await bot.send_message(id_chat, "Il tuo saldo non è sufficiente per approvare l'accredito con codice *" + str(codice) + "*", parse_mode = "Markdown", reply_to_message_id = message.message_id)
                    continue
            
                # scrittura dei valori dell'accredito al creditore
                riga_creditore = int(feuille.cell(riga_creditore, colonna_creditore + 2).value)
                feuille.update(rowcol_to_a1(riga_creditore, colonna_creditore), [[data, "A", danaro, "Da " + debitore + " per " + causale]], value_input_option = "USER_ENTERED")

                # scrittura dei valori dell'accredito al debitore
                riga_debitore = int(feuille.cell(riga_debitore, colonna_debitore + 2).value)
                feuille.update(rowcol_to_a1(riga_debitore, colonna_debitore), [[data, "V", - danaro, "Verso " + creditore + " per " + causale]], value_input_option = "USER_ENTERED")

            # rimozione dell'accredito scelto
            accrediti.pop(index)

            # pulizia dell'array transazione, eliminando tutti i valori inseriti e impostando la dimensione a zero
            accredito.clear()

            # stringa di risposta per il mittente
            mention = "[" + debitore + "](tg://user?id=" + id_debitore + ")"
            risposta = mention + ", l'accredito con codice *" + str(codice) + "* è riuscito"

            # stringa di risposta per il creditore
            if (creditore == "Cassa"):
                mention = "[Cassa](tg://user?id=" + str(ID_LUCA) + ")"
            else:
                mention = "[" + creditore + "](tg://user?id=" + id_creditore + ")"

            response = mention + " hai ricevuto " + locale.currency(danaro) + " da " + debitore + " per " + causale

            # notifiche
            await bot.send_message(id_chat, risposta, parse_mode = "Markdown")

            await bot.send_message(id_creditore, response, parse_mode = "Markdown")

    # aggiornamento del file accrediti.txt
    arrayofarray_to_file(POS_A, accrediti)


# il comando /ping permette di mandare un promemoria ai debitori
@dp.message_handler(commands = ["ping"])
async def ping(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "ping")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    counter = 0

    # invia i promemoria
    for i in range(len(accrediti)):
        id_creditore = accrediti[i][4]
        if ((id_creditore == id_mittente or (id_creditore == ID_CASSA and id_mittente == ID_LUCA)) and (int(locale.atof((sheet.cell(int(accrediti[i][5]), int(accrediti[i][6]) + 3).value)[3:]) * 100) - int(abs(float(accrediti[i][9])) * 100) < 0)):
            counter += 1
            risposta = "*" + accrediti[i][3] + "* ti ricorda di pagare l'accredito con codice *" + str(accrediti[i][0]) + "*"
            await bot.send_message(accrediti[i][8], risposta, parse_mode = "Markdown")

    # se non ci sono accrediti il cui creditore è il mittente del comando, manda un messaggio e fine
    if (counter <= 0):
        await bot.send_message(id_mittente, "Non hai promemoria da poter inviare")
        return

    # notifica per il mittente
    await bot.send_message(id_mittente, "Promemoria inviato/i")


# il comando /pop permette solo a Luca e Pippo di rimuovere qualcuno dalla blacklist
@dp.message_handler(commands = ["pop"])
async def pop(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "pop")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il mitttente del messaggio non è Luca manda un messaggio e fine
    if (id_mittente != ID_LUCA and id_mittente != ID_PIPPO):
        await bot.send_message(id_chat, "Non hai il permesso di eseguire questo comando", reply_to_message_id = message.message_id)
        return
    
    # se il comando non contiene un nome da togliere dalla blacklist manda un messaggio e fine
    if (len(message.text) < 5):
        await bot.send_message(id_chat, "È necessario inserire un nome. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # cerca l'id nell'array nomi_id
    target = str(message.text[5:])
    id = find_id(target)

    # se non lo trova manda un messaggio e fine        
    if (id == ""):
        await bot.send_message(id_chat, "Il nome inserito è errato o non esiste. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova a rimuovere l'id dalla blacklist, se non ci riesce manda un messaggio e fine
    try:
        listanera.remove(id)
    except:
        await bot.send_message(id_chat, "Il nome inserito non è presente nella blacklist. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # aggiorna il file blacklist.txt
    array_to_file(POS_B, listanera)

    mention = "[" + str(target) + "](tg://user?id=" + str(id) + ")"
    risposta = mention + " è stato rimosso dalla blacklist"

    await bot.send_message(id_chat, risposta, parse_mode = "Markdown")

    await bot.send_message(id, "*Sei stato rimosso dalla blacklist*", parse_mode = "Markdown")


# il comando /prelievo preleva l'ammontare indicato dal proprio conto
@dp.message_handler(commands = ["prelievo"])
async def prelievo(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "prelievo")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha meno di 10 caratteri (ovvero contiene solo /prelievo senza l'importo) manda un messaggio e fine
    if (len(message.text) < 10):
        await bot.send_message(id_chat, "È necessario inserire una somma di denaro. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il messaggio contiene più di un argomento, manda un messaggio e fine
    if (len(message.text[10:].split(",")) > 1):
        await bot.send_message(id_chat, "Il comando accetta un solo argomento, ovvero [danaro]. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova a convertire l'argomento [danaro] in numero decimale, se non ci riesce manda un messaggio e fine
    try:
        danaro = float(message.text[10:])
    except:
        await bot.send_message(id_chat, "Il valore inserito non è una somma di denaro. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova a cercare la cella che contiene l'id del mittente del comando, se non la trova allora manda un messaggio e fine 
    try: 
        cella = sheet.find(id_mittente)
    except:
        await bot.send_message(id_chat, "Non so chi tu sia", reply_to_message_id = message.message_id)
        return

    # se il saldo del proprio conto non è sufficiente per prelevare il denaro, manda un messaggio e fine
    if (int(locale.atof((sheet.cell(cella.row, cella.col + 2).value)[3:]) * 100) - int(abs(danaro) * 100) < 0):
        await bot.send_message(id_chat, "Il saldo del tuo conto non è sufficiente. Ricarica prima il tuo conto", reply_to_message_id = message.message_id)
        return

    # creazione array transazione in cui salvare le informazioni
    transazione = []

    nome_mittente = find_name(id_mittente)

    # inserimento dei valori precedenti nell'array transazione
    transazione.append(cella.row) # [0]: riga della della cella contenente il nome del mittente
    transazione.append(cella.col - 1) # [1]: colonna della cella contenente il nome del mittente
    transazione.append(find_name(id_mittente)) # [2]: nome del mittente
    transazione.append(id_mittente) # [3]: id dell'account Telegram del mittente
    transazione.append("P") # [4]: tipo di transazione {"P", "R"}
    transazione.append(- abs(danaro)) # [5]: somma di denaro della transazione
    transazione.append("") # [6]: causale/motivo della transazione

    # inserimento dell'array transazione in cosa all'array transazioni
    transazioni.append(transazione)

    # aggiornamento del file transazioni.txt
    arrayofarray_to_file(POS_T, transazioni)

    # stringa di risposta per il mittente
    mention = "[Luca](tg://user?id=" + str(ID_LUCA) + ")"
    risposta = "Attendi l'approvazione di " + mention
    menzione = "[Riky](tg://user?id=" + str(ID_RIKY) + ")"
    risposta = risposta + " o di " + menzione + "..."

    # stringa di risposta per Luca
    response = mention + ", " + nome_mittente + " ha richiesto un prelievo di " + locale.currency(abs(danaro))

    # stringa di risposta per Riky
    reply = menzione + ", " + nome_mittente + " ha richiesto un prelievo di " + locale.currency(abs(danaro))

    # notifiche
    await bot.send_message(id_chat, risposta, parse_mode = "Markdown", reply_to_message_id = message.message_id)

    await bot.send_message(ID_LUCA, response, parse_mode = "Markdown")

    await bot.send_message(ID_RIKY, reply, parse_mode = "Markdown")


# il comando /prestito permette di concedere un prestito a qualcuno, effettuando un versamento ed un accredito
@dp.message_handler(commands = ["prestito"])
async def prestito(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)
    
    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "prestito")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha meno di 10 caratteri (ovvero contiene solo /prestito senza l'importo, il beneficiario e la causale) manda un messaggio e fine
    if (len(message.text) < 10):
        await bot.send_message(id_chat, "È necessario inserire una somma di denaro, un beneficiario ed una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova ad analizzare l'argomento del comando /prestito, se non ci sono il beneficiario e la causale manda un messaggio e fine
    try:
        info = message.text[10:].split(",")
    except:
        await bot.send_message(id_chat, "È necessario inserire un beneficiario ed una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha più di tre argomenti (ovvero non ha solamente [danaro], [beneficiario] e [causale]) manda un messaggio e fine
    if (len(info) > 3):
        await bot.send_message(id_chat, "Hai inserito troppi argomenti. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha più di due argomenti (ovvero non ha solamente [danaro] e [causale]) manda un messaggio e fine
    if (len(info) < 3):
        await bot.send_message(id_chat, "La sintassi del comando è errata. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se non ci sono [beneficiario] e [causale] manda un messaggio e fine
    if (len(info[1]) <= 0 or len(info[2]) <= 0):
        await bot.send_message(id_chat, "È necessario inserire un beneficiario ed una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova a convertire l'argomento [danaro] in numero decimale, se non ci riesce manda un messaggio e fine
    try:
        danaro = float(info[0])
    except:
        await bot.send_message(id_chat, "Il valore inserito non è una somma di denaro. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il denaro è un numero negativo o nullo, manda un messaggio e fine
    if (danaro <= 0):
        await bot.send_message(id_chat, "La somma di denaro non può essere negativa o nulla. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova a cercare la cella che contiene l'id del mittente del comando, se non la trova allora manda un messaggio e fine 
    try: 
        cella = sheet.find(id_mittente)
    except:
        await bot.send_message(id_chat, "Non so chi tu sia")
        return

    # se il saldo del proprio conto non è sufficiente per prelevare il denaro, manda un messaggio e fine
    if (int(locale.atof((sheet.cell(cella.row, cella.col + 2).value)[3:]) * 100) - int(abs(danaro) * 100) < 0):
        await bot.send_message(id_chat, "Il saldo del tuo conto non è sufficiente. Ricarica prima il tuo conto", reply_to_message_id = message.message_id)
        return

    beneficiario = str(info[1])[1:].lower()
    beneficiario = beneficiario[0].upper() + beneficiario[1:]
    id_beneficiario = find_id(beneficiario)

    # se il nome del beneficiario non è presente nell'array nomi_id, manda un messaggio e fine
    if (id_beneficiario == ""):
        await bot.send_message(id_chat, "Il nome del beneficiario non è corretto o non esiste. Riprova per favore", reply_to_message_id = message.message_id)
        return

    cella_beneficiario = sheet.find(id_beneficiario)

    # se il beneficiario coincide con il mittente del messaggio manda un messaggio e fine
    if (id_beneficiario == id_mittente):
        await bot.send_message(id_chat, "Il beneficiario non può essere te stesso. Riprova per favore", reply_to_message_id = message.message_id)
        return

    causale = str(info[2][1:])

    # informazioni da inserire nello sheet
    riga = sheet.cell(cella.row, cella.col + 1).value
    colonna = cella.col - 1
    versatore = str(sheet.cell(cella.row, cella.col - 1).value)
    riga_beneficiario = sheet.cell(cella_beneficiario.row, cella_beneficiario.col + 1).value
    colonna_beneficiario = cella_beneficiario.col - 1
    data = time()

    # scrittura delle info del versatore nello sheet per il versamento
    sheet.update(rowcol_to_a1(riga, colonna), [[data, "V", - danaro, "Verso " + beneficiario + " per " + causale]], value_input_option = "USER_ENTERED")

    # scrittura delle info del beneficiario nello sheet per il versamento
    sheet.update(rowcol_to_a1(riga_beneficiario, colonna_beneficiario), [[data, "A", danaro, "Da " + versatore + " per " + causale]], value_input_option = "USER_ENTERED")

    # genera il codice per identificare l'accredito evitando doppioni
    codice = generate_code()

    accredito = []

    nome_mittente = find_name(id_mittente)

    # inserimento delle informazioni per l'accredito nell'array accredito
    accredito.append(codice) # [0]: codice identificativo dell'accredito
    accredito.append(cella.row) # [1]: riga della cella contenente il nome del creditore
    accredito.append(cella.col - 1) # [2]: colonna della cella contenente il nome del creditore
    accredito.append(nome_mittente) # [3]: nome del creditore
    accredito.append(id_mittente) # [4]: id dell'account Telegram del creditore
    accredito.append(cella_beneficiario.row) # [5]: riga della cella contenente il nome del debitore
    accredito.append(colonna_beneficiario) # [6]: colonna della cella contenente il nome del debitore
    accredito.append(beneficiario) # [7]: nome del debitore
    accredito.append(id_beneficiario) # [8]: id dell'account Telegram del debitore
    accredito.append(abs(danaro)) # [9]: somma di denaro della transazione
    accredito.append(causale) # [10]: causale/motivo della transazione
    accredito.append("prestito") # [11]: flag per controllare se l'accredito è stato creato da /prestito
    
    # inserimento dell'accredito in coda all'array accrediti
    accrediti.append(accredito)

    # ordina l'array accrediti per il nome del debitore
    accrediti.sort(key = sort_debtor)

    # aggiornamento del file accrediti.txt
    arrayofarray_to_file(POS_A, accrediti)

    # stringa di risposta per il mittente
    mention = "[" + versatore + "](tg://user?id=" + id_mittente + ")"
    risposta = mention + ", il prestito è riuscito\n\n"

    # stringa di risposta per il debitore
    if (beneficiario == "Cassa"):
        mention = "[Cassa](tg://user?id=" + str(ID_LUCA) + ")"
    else:
        mention = "[" + beneficiario + "](tg://user?id=" + str(id_beneficiario) + ")"
    codice = "*" + str(codice) + "*"
    response = mention + ", *" + nome_mittente + "* ti ha concesso un prestito di " + locale.currency(abs(danaro)) + " da ripagare con codice " + codice

    # notifiche
    await bot.send_message(id_chat, risposta, parse_mode = "Markdown", reply_to_message_id = message.message_id)

    await bot.send_message(id_beneficiario, response, parse_mode = "Markdown")


# il comando /prestitocassa permette alla Cassa di concedere un prestito a qualcuno, effettuando un versamento ed un accredito
@dp.message_handler(commands = ["prestitocassa"])
async def prestitocassa(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)
    
    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "prestitocassa")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il mitttente del messaggio non è Luca manda un messaggio e fine
    if (id_mittente != ID_LUCA):
        await bot.send_message(id_chat, "Non hai il permesso di eseguire questo comando", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha meno di 15 caratteri (ovvero contiene solo /prestitocassa senza l'importo, il beneficiario e la causale) manda un messaggio e fine
    if (len(message.text) < 15):
        await bot.send_message(id_chat, "È necessario inserire una somma di denaro, un beneficiario ed una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova ad analizzare l'argomento del comando /prestito, se non ci sono il beneficiario e la causale manda un messaggio e fine
    try:
        info = message.text[15:].split(",")
    except:
        await bot.send_message(id_chat, "È necessario inserire un beneficiario ed una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha più di tre argomenti (ovvero non ha solamente [danaro], [beneficiario] e [causale]) manda un messaggio e fine
    if (len(info) > 3):
        await bot.send_message(id_chat, "Hai inserito troppi argomenti. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha più di due argomenti (ovvero non ha solamente [danaro] e [causale]) manda un messaggio e fine
    if (len(info) < 3):
        await bot.send_message(id_chat, "La sintassi del comando è errata. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se non ci sono [beneficiario] e [causale] manda un messaggio e fine
    if (len(info[1]) <= 0 or len(info[2]) <= 0):
        await bot.send_message(id_chat, "È necessario inserire un beneficiario ed una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova a convertire l'argomento [danaro] in numero decimale, se non ci riesce manda un messaggio e fine
    try:
        danaro = float(info[0])
    except:
        await bot.send_message(id_chat, "Il valore inserito non è una somma di denaro. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il denaro è un numero negativo o nullo, manda un messaggio e fine
    if (danaro <= 0):
        await bot.send_message(id_chat, "La somma di denaro non può essere negativa o nulla. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il saldo del proprio conto non è sufficiente per prelevare il denaro, manda un messaggio e fine
    if (int(locale.atof((sheet.cell(5, 1 + 3).value)[3:]) * 100) - int(abs(danaro) * 100) < 0):
        await bot.send_message(id_chat, "Il saldo del tuo conto non è sufficiente. Ricarica prima il tuo conto", reply_to_message_id = message.message_id)
        return

    beneficiario = str(info[1])[1:].lower()
    beneficiario = beneficiario[0].upper() + beneficiario[1:]
    id_beneficiario = find_id(beneficiario)

    # se il nome del beneficiario non è presente nell'array nomi_id, manda un messaggio e fine
    if (id_beneficiario == ""):
        await bot.send_message(id_chat, "Il nome del beneficiario non è corretto o non esiste. Riprova per favore", reply_to_message_id = message.message_id)
        return

    cella_beneficiario = sheet.find(id_beneficiario)

    # se il beneficiario coincide con il mittente del messaggio manda un messaggio e fine
    if (id_beneficiario == id_mittente):
        await bot.send_message(id_chat, "Il beneficiario non può essere te stesso. Riprova per favore", reply_to_message_id = message.message_id)
        return

    causale = str(info[2][1:])

    # informazioni da inserire nello sheet
    riga = sheet.cell(5, 1 + 2).value
    colonna = 1
    riga_beneficiario = sheet.cell(cella_beneficiario.row, cella_beneficiario.col + 1).value
    colonna_beneficiario = cella_beneficiario.col - 1
    data = time()

    # scrittura delle info del versatore nello sheet per il versamento
    sheet.update(rowcol_to_a1(riga, colonna), [[data, "V", - danaro, "Verso " + beneficiario + " per " + causale]], value_input_option = "USER_ENTERED")

    # scrittura delle info del beneficiario nello sheet per il versamento
    sheet.update(rowcol_to_a1(riga_beneficiario, colonna_beneficiario), [[data, "A", danaro, "Da Cassa per " + causale]], value_input_option = "USER_ENTERED")

    # genera il codice per identificare l'accredito evitando doppioni
    codice = generate_code()

    accredito = []

    # inserimento delle informazioni per l'accredito nell'array accredito
    accredito.append(codice) # [0]: codice identificativo dell'accredito
    accredito.append(5) # [1]: riga della cella contenente il nome del creditore
    accredito.append(1) # [2]: colonna della cella contenente il nome del creditore
    accredito.append("Cassa") # [3]: nome del creditore
    accredito.append(id_mittente) # [4]: id dell'account Telegram del creditore
    accredito.append(cella_beneficiario.row) # [5]: riga della cella contenente il nome del debitore
    accredito.append(colonna_beneficiario) # [6]: colonna della cella contenente il nome del debitore
    accredito.append(beneficiario) # [7]: nome del debitore
    accredito.append(id_beneficiario) # [8]: id dell'account Telegram del debitore
    accredito.append(abs(danaro)) # [9]: somma di denaro della transazione
    accredito.append(causale) # [10]: causale/motivo della transazione
    accredito.append("prestito") # [11]: flag per controllare se l'accredito è stato creato da /prestito
    
    # inserimento dell'accredito in coda all'array accrediti
    accrediti.append(accredito)

    # ordina l'array accrediti per il nome del debitore
    accrediti.sort(key = sort_debtor)

    # aggiornamento del file accrediti.txt
    arrayofarray_to_file(POS_A, accrediti)

    # stringa di risposta per il mittente
    mention = "[Cassa](tg://user?id=" + id_mittente + ")"
    risposta = mention + ", il prestito è riuscito\n\n"

    # stringa di risposta per il debitore
    if (beneficiario == "Cassa"):
        mention = "[Cassa](tg://user?id=" + str(ID_LUCA) + ")"
    else:
        mention = "[" + beneficiario + "](tg://user?id=" + str(id_beneficiario) + ")"
    codice = "*" + str(codice) + "*"
    response = mention + ", la *Cassa* ti ha concesso un prestito di " + locale.currency(abs(danaro)) + " da ripagare con codice " + codice

    # notifiche
    await bot.send_message(id_chat, risposta, parse_mode = "Markdown", reply_to_message_id = message.message_id)

    await bot.send_message(id_beneficiario, response, parse_mode = "Markdown")


# il comando /push permette solo a Luca e Pippo di aggiungere qualcuno alla blacklist
@dp.message_handler(commands = ["push"])
async def push(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "push")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il mitttente del messaggio non è Luca manda un messaggio e fine
    if (id_mittente != ID_LUCA and id_mittente != ID_PIPPO):
        await bot.send_message(id_chat, "Non hai il permesso di eseguire questo comando", reply_to_message_id = message.message_id)
        return

    # se il comando non contiene un nome da togliere dalla blacklist manda un messaggio e fine
    if (len(message.text) < 6):
        await bot.send_message(id_chat, "È necessario inserire un nome. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # cerca l'id nell'array nomi_id
    target = str(message.text[6:])
    id = find_id(target)

    # se non lo trova manda un messaggio e fine        
    if (id == ""):
        await bot.send_message(id_chat, "Il nome inserito è errato o non esiste. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se l'id è già presente nella blacklist manda un messaggio e fine
    if(is_blacklisted(id)):
        await bot.send_message(id_chat, "Il nome inserito è già presente nella blacklist", reply_to_message_id = message.message_id)
        return
    
    # aggiunge l'id alla blacklist
    listanera.append(id)

    # aggiorna il file blacklist.txt
    array_to_file(POS_B, listanera)

    mention = "[" + str(target) + "](tg://user?id=" + str(id) + ")"
    risposta = mention + " è stato aggiunto alla blacklist"

    await bot.send_message(id_chat, risposta, parse_mode = "Markdown")
    
    await bot.send_message(id, "*Sei stato aggiunto alla blacklist*", parse_mode = "Markdown")


# il comando /ricarica ricarica il proprio conto dell'ammontare indicato
@dp.message_handler(commands = ["ricarica"])
async def ricarica(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "ricarica")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha meno di 10 caratteri (ovvero contiene solo /ricarica senza l'importo) manda un messaggio e fine
    if (len(message.text) < 10):
        await bot.send_message(id_chat, "È necessario inserire una somma di denaro. Riprova per favore", reply_to_message_id = message.message_id)
        return
    
    # se il messaggio contiene più di un argomento, manda un messaggio e fine
    if (len(message.text[10:].split(",")) > 1):
        await bot.send_message(id_chat, "Il comando accetta un solo argomento, ovvero [danaro]. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova a convertire l'importo del messaggio in numero decimale, se non ci riesce manda un messaggio e fine
    try:
        importo = float(message.text[10:])
    except:
        await bot.send_message(id_chat, "Il valore inserito non è una somma di denaro. Riprova per favore", reply_to_message_id = message.message_id)
        return
    
    # se l'importo è negativo manda un messaggio e fine
    if (importo <= 0):
        await bot.send_message(id_chat, "Non puoi ricaricare una somma di denaro negativa. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova a cercare la cella che contiene l'id del mittente del comando, se non la trova allora manda un messaggio e fine 
    try: 
        cella = sheet.find(id_mittente)
    except:
        await bot.send_message(id_chat, "Non so chi tu sia", reply_to_message_id = message.message_id)
        return

    # creazione array transazione in cui salvare le informazioni
    transazione = []

    nome_mittente = find_name(id_mittente)

    # inserimento dei valori precedenti nell'array transazione
    transazione.append(cella.row) # [0]: riga della cella contenente il nome del mittente
    transazione.append(cella.col - 1) # [1]: colonna della cella contenente il nome del mittente
    transazione.append(nome_mittente) # [2]: nome del mittente
    transazione.append(id_mittente) # [3]: id dell'account Telegram del mittente
    transazione.append("R") # [4]: tipo di transazione {"P", "R"}
    transazione.append(abs(importo)) # [5]: somma di denaro della transazione
    transazione.append("") # [6]: causale/motivo della transazione
    
    # inserimento dell'array transazione in coda all'array transazioni
    transazioni.append(transazione)

    # aggiornamento del file transazioni.txt
    arrayofarray_to_file(POS_T, transazioni)

    # stringa di risposta per il mittente
    mention = "[Luca](tg://user?id=" + str(ID_LUCA) + ")"
    risposta = "Attendi l'approvazione di " + mention
    menzione = "[Riky](tg://user?id=" + str(ID_RIKY) + ")"
    risposta = risposta + " o di " + menzione + "..."

    # stringa di risposta per Luca
    response = mention + ", " + nome_mittente + " ha richiesto una ricarica di " + locale.currency(abs(importo))

    # stringa di risposta per Riky
    reply = menzione + ", " + nome_mittente + " ha richiesto una ricarica di " + locale.currency(abs(importo))

    # notifiche
    await bot.send_message(id_chat, risposta, parse_mode = "Markdown", reply_to_message_id = message.message_id)

    await bot.send_message(ID_LUCA, response, parse_mode = "Markdown")

    await bot.send_message(ID_RIKY, reply, parse_mode = "Markdown")


# il comando /rimuovitastiera rimuove la tastiera
@dp.message_handler(commands = ["rimuovitastiera"])
async def rimuovitastiera(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "rimuovitastiera")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # rimuove la tastiera
    markup = types.ReplyKeyboardRemove(selective = True)

    # cerca il nome nell'array nomi_id
    nome = find_name(id_mittente)
    
    # menzione del mittente del comando
    mention = "[" + nome + "](tg://user?id=" + id_mittente + ")"

    risposta = mention + ", la tastiera è stata rimossa"

    await bot.send_message(id_chat, risposta, parse_mode = "Markdown", reply_markup = markup)


# il comando /ruok manda un messaggio per verificare che il bot sia online e funzioni normalmente
@dp.message_handler(commands = ["ruok"])
async def ruok(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "ruok")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    await bot.send_message(id_chat, "Tutto apposto freh!")


# il comando /saldo mostra il saldo del proprio conto, a Luca e Riky anche i soldi che ha in ATM e a Luca anche i saldi di tutti i conti
@dp.message_handler(commands = ["saldo"])
async def saldo(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "saldo")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return
    
    # prova a cercare la cella che contiene l'id del mittente del comando, se non la trova allora manda un messaggio e fine
    try:
        cella = sheet.find(id_mittente)
    except:
        await bot.send_message(id_chat, "Non so chi tu sia", reply_to_message_id = message.message_id)
        return

    # saldo del conto del mittente del comando
    saldo = str(sheet.cell(cella.row, cella.col + 2).value)[2:]

    # se non ci sono movimenti manda un messaggio e fine
    if (saldo.strip(" ") == "-"):
        await bot.send_message(id_chat, "Non hai ancora effettuato alcun movimento", reply_to_message_id = message.message_id)
        return

    # conversione del saldo
    saldo = locale.currency(locale.atof(saldo))

    # menzione del mittente del comando
    mention = "[" + find_name(id_mittente) + "](tg://user?id=" + id_mittente + ")"

    risposta = mention + ", ecco il tuo saldo:  *" + saldo + "*"

    # se il mittente è Luca allora manda il saldo atm e i saldi di tutti i conti
    if (id_mittente == ID_LUCA):
        
        # soldi nell'ATM del mittente
        soldi = locale.currency(locale.atof((feuille.cell(5, 4).value)[2:]))

        # percentuale di soldi custoditi in ATM rispetto al totale
        percentuale = feuille.cell(2, 12).value

        risposta += "\n\nSoldi in ATM:  " + soldi + " (" + percentuale + ")\n"

        # intervallo di celle che contengono i saldi dei conti
        intervallo = rowcol_to_a1(5, 11) + ":" + rowcol_to_a1(5, 74)
        
        # saldi dei conti a partire dall'intervallo specificato
        saldi = sheet.get(intervallo)

        # stampa dei saldi
        for i in range(1, len(nomi_id) - 1):

            saldo = saldi[0][(i - 1) * 5 + 3]
            risposta += "\n" + nomi_id[i][0] + ": " + saldo

    # se il mittente è Riky allora manda il saldo atm
    if (id_mittente == ID_RIKY):

        # soldi nell'ATM del mittente
        soldi = locale.currency(locale.atof((feuille.cell(5, 9).value)[2:]))

        # percentuale di soldi custoditi in ATM rispetto al totale
        percentuale = feuille.cell(3, 12).value

        risposta += "\nSoldi in ATM:  " + soldi + " (" + percentuale + ")"
    
    await bot.send_message(id_chat, risposta, parse_mode = "Markdown")


# il comando /send permette solo a Luca e Pippo di mandare un messaggio a qualcuno
@dp.message_handler(commands = ["send"])
async def send(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "send")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il mitttente del messaggio non è Luca o Pippo manda un messaggio e fine
    if (id_mittente != ID_LUCA and id_mittente != ID_PIPPO):
        await bot.send_message(id_chat, "Non hai il permesso di eseguire questo comando", reply_to_message_id = message.message_id)
        return
    
    # se il messaggio ha meno di 6 caratteri (ovvero contiene solo /send senza il destinatario ed il messaggio) manda un messaggio e fine
    if (len(message.text) < 6):
        await bot.send_message(id_chat, "È necessario inserire un destinatario ed un messaggio. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova ad analizzare l'argomento del comando /send, se non c'è il messaggio manda un messaggio e fine
    try:
        info = message.text[6:].split(",")
    except:
        await bot.send_message(id_chat, "È necessario inserire un destinatario ed un messaggio. Riprova per favore", reply_to_message_id = message.message_id)
        return
    
    # se il messaggio ha più di due argomenti (ovvero non ha solamente [destinatario] e [messaggio]) manda un messaggio e fine
    if (len(info) < 2):
        await bot.send_message(id_chat, "La sintassi del comando è errata. Riprova per favore", reply_to_message_id = message.message_id)
        return

    destinatario = str(info[0]).lower()
    destinatario = destinatario[0].upper() + destinatario[1:]

    if (destinatario == "Cassa"):
        destinatario = "Luca"

    id_destinatario = find_id(destinatario)

    # se il [destinatario] non è corretto o non esiste manda un messaggio e fine
    if (id_destinatario == ""):
        await bot.send_message(id_chat, "Il destinatario non è corretto o non esiste. Riprova per favore", reply_to_message_id = message.message_id)
        return
    
    messaggio = ""

    for i in range(1, len(info)):
        messaggio += info[i].strip() + ", "

    messaggio = messaggio[:len(messaggio) - 2]

    # notifiche
    await bot.send_message(id_destinatario, messaggio, parse_mode = "Markdown")

    await bot.send_message(id_mittente, "Messaggio inviato")


# il comando /strozzino permette solo a Luca di chiedere un insieme di accrediti verso la Cassa
@dp.message_handler(commands = ["strozzino"])
async def strozzino(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "strozzino")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il mitttente del messaggio non è Luca manda un messaggio e fine
    if (id_mittente != ID_LUCA):
        await bot.send_message(id_chat, "Non hai il permesso di eseguire questo comando", reply_to_message_id = message.message_id)
        return
    
    # intervallo di celle che contengono i debiti
    intervallo = rowcol_to_a1(1, 4) + ":" + rowcol_to_a1(15, 4)

    # lista di debiti a partire dall'intervallo specificato
    debiti = foglio.get(intervallo)

    # causale dell'accredito
    causale = debiti.pop(0)[0]

    # variabile per controllare se il comando /strozzino è già stato usato sulla stessa causale
    last = file_to_variable(POS_L)

    # se il comando è già stato lanciato sulla stessa causale, manda un messaggio e fine
    if (last == causale):
        await bot.send_message(id_chat, "Hai già usato questo comando sulla stessa causale", reply_to_message_id = message.message_id)
        return
    
    # la causale corrente diventa l'ultima causale usata
    last = causale

    # aggiornamento del file last.txt
    variable_to_file(POS_L, last)

    # array per salvare alcune informazioni dell'accredito
    temp = []
    
    # scrittura di alcune informazioni dell'accredito nell'array temp
    for i in range(len(debiti)):

        if (debiti[i][0] == "/" or debiti[i][0] == "None"):
            continue

        debitore = nomi_id[i][0]
        id_debitore = nomi_id[i][1]
        danaro = locale.atof(str(debiti[i][0])[2:])

        # se il danaro è negativo o uguale a zero, manda un messaggio e continua il ciclo
        if (danaro <= 0):
            risposta = "L'accredito di " + debitore + " non può essere un numero negativo o nullo. Controlla Google Sheets"
            await bot.send_message(id_chat, risposta, reply_to_message_id = message.message_id)
            continue

        tmp = []
        tmp.append(debitore)
        tmp.append(id_debitore)
        tmp.append(danaro)
        temp.append(tmp)

    # contatore di quanti accrediti sono stati creati con successo
    counter = 0

    # creazione degli accrediti
    for i in range(len(temp)):

        debitore = temp[i][0]
        id_debitore = temp[i][1]
        danaro = temp[i][2]
        mention = "[" + debitore + "](tg://user?id=" + id_debitore + ")"

        # se l'id dell'account Telegram del debitore non è stato trovato nell'array nomi_id, manda un messaggio e fine
        if (id_debitore == ""):
            risposta = "Il nome " + debitore + " non è corretto o non esiste. Riprova per favore"
            await bot.send_message(id_chat, risposta, reply_to_message_id = message.message_id)
            continue

        cella_debitore = sheet.find(id_debitore)

        # genera il codice per identificare l'accredito evitando doppioni
        codice = generate_code()
    
        accredito = []

        # inserimento delle informazioni per l'accredito nell'array accredito
        accredito.append(codice) # [0]: codice identificativo dell'accredito
        accredito.append(5) # [1]: riga della cella contenente il nome del creditore
        accredito.append(1) # [2]: colonna della cella contenente il nome del creditore
        accredito.append("Cassa") # [3]: nome del creditore
        accredito.append(id_mittente) # [4]: id dell'account Telegram del creditore
        accredito.append(cella_debitore.row) # [5]: riga della cella contenente il nome del debitore
        accredito.append(cella_debitore.col - 1) # [6]: colonna della cella contenente il nome del debitore
        accredito.append(debitore) # [7]: nome del debitore
        accredito.append(id_debitore) # [8]: id dell'account Telegram del debitore
        accredito.append(abs(danaro)) # [9]: somma di denaro della transazione
        accredito.append(causale) # [10]: causale/motivo della transazione
        accredito.append("normale") # [11]: flag per controllare se l'accredito è stato creato da /prestito

        # aggiornamento del contatore di accrediti
        counter += 1

        # inserimento dell'accredito in coda all'array accrediti
        accrediti.append(accredito)

        # aggiornamento del file accrediti.txt
        arrayofarray_to_file(POS_A, accrediti)

        # stringa di risposta per il debitore
        response = mention + ", la *Cassa* ha richiesto un accredito di " + locale.currency(abs(danaro)) + " con codice *" + str(codice) + "* per " + causale

        # notifica per il debitore
        await bot.send_message(id_debitore, response, parse_mode = "Markdown")
    
    temp.clear()

    # ordina l'array accrediti per il nome del debitore
    accrediti.sort(key = sort_debtor)

    # stringa di risposta per il mittente
    risposta = "Creati *" + str(counter) + "* accrediti\n\n" + print_crediti(ID_LUCA)

    # notifica per il mittente
    await bot.send_message(id_chat, risposta, parse_mode = "Markdown", reply_to_message_id = message.message_id)


# il comando /tastiera mostra una tastiera con alcuni comandi
@dp.message_handler(commands = ["tastiera"])
async def tastiera(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "tastiera")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # tastiera dei comandi
    if (id_mittente == str(ID_LUCA)):
        keyboard = [["/aiuto", "/blacklist", "/capitale"], ["/coda", "/conti", "/crediti"], ["/debiti", "/debug", "/lista"], ["/movimenti", "/no", "/nope"], ["/nuke", "/ok", "/okay"], ["/ping", "/ruok", "/saldo"], ["/strozzino"]]
    elif (id_mittente == str(ID_PIPPO)):
        keyboard = [["/aiuto", "/blacklist", "/capitale"], ["/coda", "/conti", "/crediti"], ["/debiti", "/debug", "/lista"], ["/logs", "/movimenti", "/nope"], ["/nuke", "/okay", "/ping"], ["/ruok", "/saldo"]]
    elif (id_mittente == str(ID_RIKY)):
        keyboard = [["/aiuto", "/capitale", "/coda"], ["/conti", "/crediti", "/debiti"], ["/movimenti", "/no", "/nope"], ["/ok", "/okay", "/ping"], ["/ruok", "/saldo"]]
    else:
        keyboard = [["/aiuto", "/capitale", "/conti"], ["/crediti", "/debiti", "/movimenti"], ["/nope", "/okay", "/ping"], ["/ruok", "/saldo"]]

    # inizializzazione tastiera dei comandi
    markup = types.ReplyKeyboardMarkup(keyboard = keyboard, resize_keyboard = True, one_time_keyboard = True, selective = True)

    # cerca il nome nell'array nomi_id
    nome = find_name(id_mittente)
    
    # menzione del mittente del comando
    mention = "[" + nome + "](tg://user?id=" + id_mittente + ")"

    risposta = mention + ", ecco la tua tastiera"

    await bot.send_message(id_chat, risposta, parse_mode = "Markdown", reply_markup = markup)


# il comando /versamento permette di trasferire denaro dal proprio conto ad un altro
@dp.message_handler(commands = ["versamento"])
async def versamento(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "versamento")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha meno di 12 caratteri (ovvero contiene solo /versamento senza l'importo, il beneficiario e la causale) manda un messaggio e fine
    if (len(message.text) < 12):
        await bot.send_message(id_chat, "È necessario inserire una somma di denaro, un beneficiario ed una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova ad analizzare l'argomento del comando /versamento, se non ci sono il beneficiario e la causale manda un messaggio e fine
    try:
        info = message.text[12:].split(",")
    except:
        await bot.send_message(id_chat, "È necessario inserire un beneficiario ed una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha più di tre argomenti (ovvero non ha solamente [danaro], [beneficiario] e [causale]) manda un messaggio e fine
    if (len(info) > 3):
        await bot.send_message(id_chat, "Hai inserito troppi argomenti. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha più di due argomenti (ovvero non ha solamente [danaro] e [causale]) manda un messaggio e fine
    if (len(info) < 3):
        await bot.send_message(id_chat, "La sintassi del comando è errata. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se non ci sono [beneficiario] e [causale] manda un messaggio e fine
    if (len(info[1]) <= 0 or len(info[2]) <= 0):
        await bot.send_message(id_chat, "È necessario inserire un beneficiario ed una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova a convertire l'argomento [danaro] in numero decimale, se non ci riesce manda un messaggio e fine
    try:
        danaro = float(info[0])
    except:
        await bot.send_message(id_chat, "Il valore inserito non è una somma di denaro. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il denaro è un numero negativo, manda un messaggio e fine
    if (danaro <= 0):
        await bot.send_message(id_chat, "La somma di denaro non può essere negativa. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova a cercare la cella che contiene l'id del mittente del comando, se non la trova allora manda un messaggio e fine 
    try: 
        cella = sheet.find(id_mittente)
    except:
        await bot.send_message(id_chat, "Non so chi tu sia")
        return

    # se il saldo del proprio conto non è sufficiente per prelevare il denaro, manda un messaggio e fine
    if (int(locale.atof((sheet.cell(cella.row, cella.col + 2).value)[3:]) * 100) - int(abs(danaro) * 100) < 0):
        await bot.send_message(id_chat, "Il saldo del tuo conto non è sufficiente. Ricarica prima il tuo conto", reply_to_message_id = message.message_id)
        return

    beneficiario = str(info[1])[1:].lower()
    beneficiario = beneficiario[0].upper() + beneficiario[1:]
    id_beneficiario = find_id(beneficiario)

    # se il nome del beneficiario non è presente nell'array nomi_id, manda un messaggio e fine
    if (id_beneficiario == ""):
        await bot.send_message(id_chat, "Il nome del beneficiario non è corretto o non esiste. Riprova per favore", reply_to_message_id = message.message_id)
        return

    cella_beneficiario = sheet.find(id_beneficiario)

    # se il beneficiario coincide con il mittente del messaggio manda un messaggio e fine
    if (id_beneficiario == id_mittente):
        await bot.send_message(id_chat, "Il beneficiario non può essere te stesso. Riprova per favore", reply_to_message_id = message.message_id)
        return

    causale = str(info[2][1:])

    # informazioni da inserire nello sheet
    riga = sheet.cell(cella.row, cella.col + 1).value
    colonna = cella.col - 1
    versatore = str(sheet.cell(cella.row, cella.col - 1).value)
    riga_beneficiario = sheet.cell(cella_beneficiario.row, cella_beneficiario.col + 1).value
    colonna_beneficiario = cella_beneficiario.col - 1
    data = time()

    # scrittura delle info del versatore nello sheet
    sheet.update(rowcol_to_a1(riga, colonna), [[data, "V", - danaro, "Verso " + beneficiario + " per " + causale]], value_input_option = "USER_ENTERED")

    # scrittura delle info del beneficiario nello sheet
    sheet.update(rowcol_to_a1(riga_beneficiario, colonna_beneficiario), [[data, "A", danaro, "Da " + versatore + " per " + causale]], value_input_option = "USER_ENTERED")

    # stringa di risposta per il versatore
    mention = "[" + versatore + "](tg://user?id=" + id_mittente + ")"
    risposta = mention + ", il versamento è riuscito\n\n"

    # stringa di risposta per il beneficiario
    if (beneficiario == "Cassa"):
        mention = "[Cassa](tg://user?id=" + str(ID_LUCA) + ")"
    else:
        mention = "[" + beneficiario + "](tg://user?id=" + str(id_beneficiario) + ")"
    response = mention + " hai ricevuto " + locale.currency(danaro) + " da " + versatore + " per " + causale

    # notifiche
    await bot.send_message(id_chat, risposta, parse_mode = "Markdown")

    await bot.send_message(id_beneficiario, response, parse_mode = "Markdown")


# il comando /versamentocassa permette solo a Luca di trasferire denaro dal conto del Clan ad un altro
@dp.message_handler(commands = ["versamentocassa"])
async def versamentocassa(message: types.Message):

    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "versamentocassa")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il mitttente del messaggio non è Luca manda un messaggio e fine
    if (id_mittente != ID_LUCA):
        await bot.send_message(id_chat, "Non hai il permesso di eseguire questo comando", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha meno di 17 caratteri (ovvero contiene solo /versamentocassa senza l'importo, il beneficiario e la causale) manda un messaggio e fine
    if (len(message.text) < 17):
        await bot.send_message(id_chat, "È necessario inserire una somma di denaro, un beneficiario ed una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova ad analizzare l'argomento del comando /versamento, se non ci sono il beneficiario e la causale manda un messaggio e fine
    try:
        info = message.text[17:].split(",")
    except:
        await bot.send_message(id_chat, "È necessario inserire un beneficiario ed una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha più di tre argomenti (ovvero non ha solamente [danaro], [beneficiario] e [causale]) manda un messaggio e fine
    if (len(info) > 3):
        await bot.send_message(id_chat, "Hai inserito troppi argomenti. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il messaggio ha più di due argomenti (ovvero non ha solamente [danaro] e [causale]) manda un messaggio e fine
    if (len(info) < 3):
        await bot.send_message(id_chat, "È necessario inserire una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se non ci sono [beneficiario] e [causale] manda un messaggio e fine
    if (len(info[1]) <= 0 or len(info[2]) <= 0):
        await bot.send_message(id_chat, "È necessario inserire un beneficiario ed una causale. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # prova a convertire l'argomento [danaro] in numero decimale, se non ci riesce manda un messaggio e fine
    try:
        danaro = float(info[0])
    except:
        await bot.send_message(id_chat, "Il valore inserito non è una somma di denaro. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il denaro è un numero negativo, manda un messaggio e fine
    if (danaro < 0):
        await bot.send_message(id_chat, "La somma di denaro non può essere negativa. Riprova per favore", reply_to_message_id = message.message_id)
        return

    # se il saldo del proprio conto non è sufficiente per prelevare il denaro, manda un messaggio e fine
    if (int((locale.atof((sheet.cell(5, 1 + 3).value)[3:])) * 100) - int(abs(danaro) * 100) < 0):
        await bot.send_message(id_chat, "Il saldo del tuo conto non è sufficiente. Ricarica prima il tuo conto", reply_to_message_id = message.message_id)
        return

    beneficiario = str(info[1])[1:].lower()
    beneficiario = beneficiario[0].upper() + beneficiario[1:]
    id_beneficiario = find_id(beneficiario)

    # se il nome del beneficiario non è presente nell'array nomi_id, manda un messaggio e fine
    if (id_beneficiario == ""):
        await bot.send_message(id_chat, "Il nome del beneficiario non è corretto o non esiste. Riprova per favore", reply_to_message_id = message.message_id)
        return

    cella_beneficiario = sheet.find(id_beneficiario)

    causale = str(info[2])[1:]
    data = time()

    # coordinate della cella del conto del Clan
    riga = sheet.cell(5, 1 + 2).value
    colonna = 1

    # inserimento nello sheet delle informazioni del versamento
    sheet.update(rowcol_to_a1(riga, colonna), [[data, "V", - abs(danaro), "Verso " + beneficiario + " per " + causale]], value_input_option = "USER_ENTERED")

    # coordinate della cella del beneficiario 
    riga_beneficiario = sheet.cell(cella_beneficiario.row, cella_beneficiario.col + 1).value
    colonna_beneficiario = cella_beneficiario.col - 1

    # inserimento nello sheet delle informazioni del beneficiario
    sheet.update(rowcol_to_a1(riga_beneficiario, colonna_beneficiario), [[data, "A", abs(danaro), "Da Cassa per " + causale]], value_input_option = "USER_ENTERED")

    # stringa di risposta per il versatore
    mention = "[Cassa](tg://user?id=" + str(ID_LUCA) + ")"
    risposta = mention + ", il versamento è riuscito\n\n"

    # stringa di risposta per il beneficiario
    mention = "[" + beneficiario + "](tg://user?id=" + id_beneficiario + ")"
    response = mention + " hai ricevuto " + locale.currency(danaro) + " dalla Cassa per " + causale

    # notifiche
    await bot.send_message(id_chat, risposta, parse_mode = "Markdown")

    await bot.send_message(id_beneficiario, response, parse_mode = "Markdown")



# ------------------------------------------------------------------------   COMANDI  STUPIDI  ------------------------------------------------------------------------


# il comando /prova serve a provare una funzionalità
@dp.message_handler(commands = ["prova"])
async def prova(message: types.Message):
    
    id_mittente = str(message.from_user.id)
    id_chat = str(message.chat.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "prova")
        return

    # se l'id del mittente del messaggio è nella blacklist manda un messaggio e fine
    if (is_blacklisted(id_mittente)):
        await bot.send_message(id_chat, "Non puoi usare questo comando perchè sei nella blacklist", reply_to_message_id = message.message_id)
        return

    # se il mitttente del messaggio non è Pippo manda un messaggio e fine
    if (id_mittente != ID_PIPPO):
        await bot.send_message(id_chat, "Non hai il permesso di eseguire questo comando", reply_to_message_id = message.message_id)
        return

    # da testare

    await bot.send_message(id_chat, "Ciao ", parse_mode = "Markdown", reply_to_message_id = message.message_id)



# -------------------------------------------------------------------------   COMANDI COMUNI  -------------------------------------------------------------------------


# il comando /about logga le informazioni del mittente
@dp.message_handler(commands = ["about"])
async def about(message: types.Message):

    id_mittente = str(message.from_user.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "about")
        return

    return


# il comando /botinfo logga le informazioni del mittente
@dp.message_handler(commands = ["botinfo"])
async def botinfo(message: types.Message):

    id_mittente = str(message.from_user.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "botinfo")
        return

    return


# il comando /help logga le informazioni del mittente
@dp.message_handler(commands = ["help"])
async def help(message: types.Message):

    id_mittente = str(message.from_user.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "help")
        return

    return


# il comando /home logga le informazioni del mittente
@dp.message_handler(commands = ["home"])
async def home(message: types.Message):

    id_mittente = str(message.from_user.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "home")
        return

    return


# il comando /info logga le informazioni del mittente
@dp.message_handler(commands = ["info"])
async def info(message: types.Message):

    id_mittente = str(message.from_user.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "info")
        return

    return


# il comando /new logga le informazioni del mittente
@dp.message_handler(commands = ["new"])
async def new(message: types.Message):

    id_mittente = str(message.from_user.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "new")
        return

    return


# il comando /start logga le informazioni del mittente
@dp.message_handler(commands = ["start"])
async def start(message: types.Message):

    id_mittente = str(message.from_user.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "start")
        return

    return


# il comando /stop logga le informazioni del mittente
@dp.message_handler(commands = ["stop"])
async def stop(message: types.Message):

    id_mittente = str(message.from_user.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "stop")
        return

    return


# il comando /welcome logga le informazioni del mittente
@dp.message_handler(commands = ["welcome"])
async def welcome(message: types.Message):

    id_mittente = str(message.from_user.id)

    # se il comando arriva da uno sconosciuto allora logga un avviso e fine
    if (is_stranger(id_mittente)):
        log(message, "welcome")
        return

    return



# ---------------------------------------------------------------------------   AVVIO BOT   ---------------------------------------------------------------------------


# avvia il bot
if __name__ == "__main__":
    executor.start_polling(dp)
