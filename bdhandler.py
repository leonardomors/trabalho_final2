import sqlite3
from threading import Lock


class BDHandler():
    """
    Classe para manipulacao do banco de dados sqlite3
    """
    def __init__(self, dbpath, tags, tablename = 'dataTable'):
        """
        construtor
        """
        self._dbpath = dbpath
        self._tablename = tablename
        self._con = sqlite3.connect(self._dbpath, check_same_thread=False) # A 3 flag serve para possibilitar que o banco rode em threads distintas, uma vez que em um thread ele é criado/inserido, e em outra thread é realizada a consulta
        self._cursor = self._con.cursor() 
        self._col_names = tags.keys() # Define o nome das colunas na futura tabela
        self._lock = Lock() # O Lock é um objeto que serve para permitir a inserção / busca de forma simultânea (em diferentes threads). Enquanto a consulta é feita, não há inserção (conflito)
        self.createTable() # Cria a tabela para consulta.

    def __del__(self):
        self._con.close()
    
    def createTable(self):
        """
        Metodo que cria a tabela para armazenamento dos dados, 
        caso ela nao exista
        """
        try:
            sql_str = f"""
            CREATE TABLE IF NOT EXISTS {self._tablename}(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
            
            """ # Uma string contendo os "comandos" SQL (linguagem). Nesse caso basicamente o que é feito: Cria uma tabela se ela não existe, passando como parâmetro o nome da tabela, 
            # e os parâmetros das linhas. O ID possui auto-incremento, ou seja, não precisa ser informado, o timestamp não é um tipo de dado especifico, então é usado um tipo de TEXT,
            # posteriormente é feito uma varredura nas tags para inseri-las na tabela também.

            for n in self._col_names:
                sql_str += f'{n} REAL,'

            sql_str = sql_str[:-1] # Remove a virgula no ultimo caractere adicionado. Uso do recurso slicing 
            sql_str += ');' # concatena a string com um );
            self._lock.acquire()
            self._cursor.execute(sql_str)
            self._con.commit() # Implementa as alterações no banco.
            self._lock.release()
          
                         
            
        except Exception as e:
            print("Erro na parte SQL: ", e.args)
            

    def insertData(self, data):
        """
        método para inserir dados na tabela
        """
        try:
            self._lock.acquire()
            timestamp = str(data['timestamp'])
            str_cols = 'timestamp,' + ','.join(data['values'].keys())
            str_values = f"'{timestamp}'," + ','.join([str(data['values'][k]) for k in data['values'].keys()])
            sql_str = f'INSERT INTO  {self._tablename} ({str_cols}) VALUES ({str_values});'
            self._cursor.execute(sql_str)
            self._con.commit()
            
        except Exception as e:
            print("Erro no SQL 2: ", e.args)

        finally:
            self._lock.release()

    def selectData(self, cols, init_t, final_t):
        """
        Método que realiza a busca no BD entre dois horarios especificados
        init_t: periodo inicial
        final_t: periodo final
        """
        try:
            self._lock.acquire()
            sql_str = f"SELECT {','.join(cols)} FROM {self._tablename} WHERE timestamp BETWEEN '{init_t}' AND '{final_t}'"
            self._cursor.execute(sql_str)
            dados = dict((sensor, []) for sensor in cols)
            for linha in self._cursor.fetchall():
                for d in range(0, len(linha)):
                    dados[cols[d]].append(linha[d])
                    
            
            return dados

        except Exception as e:
            print("Erro na consulta: ", e.args) 

        finally:
            self._lock.release()

        


