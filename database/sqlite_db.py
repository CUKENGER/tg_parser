import sqlite3

class Database:
    
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()


    async def set_status_user(self, tgid, status):
        with self.connection:
            self.cursor.execute('INSERT OR IGNORE INTO `status_active`(`tgid`, `status`) VALUES(?, ?)', (tgid, status, ))


    async def update_status_user(self, tgid, status):
        with self.connection:
            self.cursor.execute('UPDATE `status_active` SET status=? WHERE tgid=?', (status, tgid))


    def get_status_user(self, tgid):
        with self.connection:
            return self.cursor.execute('SELECT `status` FROM `status_active` WHERE tgid=?', (tgid, )).fetchone()


    async def get_kwork_names(self):
        with self.connection:
            return self.cursor.execute('SELECT `name` FROM `list_kworks`').fetchall()


    async def add_kwork(self, name):
        with self.connection:
            self.cursor.execute('INSERT OR IGNORE INTO `list_kworks`(`name`) VALUES (?)', (name, ))


