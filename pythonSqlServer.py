#Valido con Python 3.6.2
import pyodbc
import smtplib
from email.mime.text import MIMEText
import time
import configparser 
import logging

#Generador de log de python
logging.basicConfig(filename='C:\ServicioMonitor\pythonSqlServer.log',level=logging.DEBUG,format='%(asctime)s [%(levelname)s] %(message)s')
##Seccion de configuraciones
#El .ini debe indicarse con la ruta completa, ya que cuando se ejecuta como tarea, la instancia se ejecuta en otra carpeta, no encontrando la confuguracion.
fileINI="C:\ServicioMonitor\pythonSqlServer.ini"

#Metodo encargado de obtener la configuracion del .ini
def config(secction,key):
    config = configparser.ConfigParser()
    if not config.read(fileINI):
        print ("No existe el archivo")
    secciones = config.sections()
    if len(secciones)>0:
        return config.get(secction, key)
#Conf correo
mail_fromaddr = config('mail','fromaddr')
#Debe ser una lista para el envio de multiples destinatarios
mail_toaddr = config('mail','toaddr').split(',')
mail_subject = config('mail','subject')
mail_password = config('mail','password')
mail_adr = config('mail','adr')
mail_port = config('mail','port')
mail_sendnoerror = config('mail','sendnoerror')
#Conf DB
db_server = config('database','server')
db_database = config('database','database')
db_username = config('database','username')
db_password = config('database','password')
db_tsql = config('database','tsql')
##Fin seccion de configuraciones

#Funcion encargada de conectarse a la db
def conexionDB():
    cnxn = pyodbc.connect('DRIVER={ODBC Driver 13 for SQL Server};SERVER=' + db_server + ';PORT=1443;DATABASE=' + db_database + ';UID=' + db_username + ';PWD=' + db_password)
    cursor = cnxn.cursor()
    cursor.execute(db_tsql)#Ejecuto la transaccion
    rows = cursor.fetchall()#obtengo todas las filas
    elemtError = len(rows)#Obtengo la cantidad de elementos
    #si el es mayor a 0, se envia un mensaje dando aviso
    if elemtError > 0:
        mensaje = 'Hay informacion con inconsistencia! \n\n'
        #recorro los elementos y los agrego al mensaje
        for campo in rows:
            mensaje += '* UUID: ' + campo[0] + ' | NOMBRE DOCUMENTO' + campo[1] + '\n'

        horaFechaActual = time.strftime('%Y/%m/%d %H:%M:%S')
        mensaje += '\n\n-----------------------------------------\n'
        mensaje += 'Fecha Hora de Envio: ' + horaFechaActual + '\n'

        # Envio por correo el aviso con los elmentos
        enviar_correo(mensaje)
        logging.info("OK-se envia error")
    else:
        logging.info("Sistema Ok, no se encuentran errores de informacion")
        if mail_sendnoerror == '1':
            enviar_correo('Sistema Ok, no se encuentran errores de informacion')

#Funcion encargada de enviar un correo
def enviar_correo(text_body):
    # Compose message
    msg = MIMEText(text_body)
    msg['From'] = mail_fromaddr
    msg['To'] = ", ".join(mail_toaddr)
    msg['Subject'] = mail_subject

    # Send mail
    smtp = smtplib.SMTP(mail_adr, mail_port)
    #smtp.set_debuglevel(1)#Muestra en pantalla
    smtp.starttls()#Exigencia para mandar correo con gmail
    smtp.login(mail_fromaddr, mail_password)
    smtp.sendmail(mail_fromaddr, mail_toaddr, msg.as_string())
    smtp.quit()

##Ejecuta lo realizado
print("Ejecutado: ",conexionDB())