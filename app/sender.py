import psycopg2
import redis
import json
import os
from bottle import Bottle, request

#aqui estou passando algumas configuraçoes
#informando o nome do banco o usuario e o host=db que é um serviço la no docker-compose


class Sender(Bottle):
    def __init__(self):
        super().__init__()
        self.route('/', method='POST', callback=self.send)

        redis_host = os.getenv('REDIS_HOST','queue')
        self.fila = redis.StrictRedis(host=redis_host, port=6379, db=0)

        db_host = os.getenv('DB_HOST','db')
        db_user = os.getenv('DB_USER','postgres')
        db_name = os.getenv('DB_NAME','sender')
        dsn = f'dbname={db_name} user={db_user} host={db_host}'
        # DSN = 'dbname=email_sender user=postgres host=db'
        self.conn = psycopg2.connect(dsn)

    def register_message(self, assunto, mensagem):
        SQL = 'INSERT INTO emails(assunto, mensagem) VALUES (%s, %s)'
        cur = self.conn.cursor()
        cur.execute(SQL,(assunto, mensagem))
        self.conn.commit()
        cur.close()

        msg = {'assunto': assunto, 'mensagem': mensagem}
        self.fila.rpush('sender', json.dumps(msg))
        
        print('mensagem registrada!')

    def send(self):
        assunto = request.forms.get('assunto')
        mensagem = request.forms.get('mensagem')
        
        self.register_message(assunto,mensagem)

        return 'Mensagem enfileirada! Assunto: {} Menssagem: {}'.format(
            assunto, mensagem
        )

if __name__ == '__main__':
    # run(host='0.0.0.0', port=8080, debug=True)    
    sender = Sender()
    sender.run(host='0.0.0.0', port=8080, debug=True)