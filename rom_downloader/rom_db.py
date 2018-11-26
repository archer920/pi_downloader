from rom_downloader.db.BaseDB import BaseDB


class RomDB(BaseDB):

    def __init__(self):
        super().__init__()

    def create_table(self):
        c = self.get_cursor()

        c.execute('CREATE TABLE IF NOT EXISTS "ROMS" ( `title` text, `href` text, `direct_download` text, `downloaded` boolean, '
                  '`emulator_platform` TEXT, UNIQUE(`title`,`href`,`direct_download`) )')
        self.commit()

    def add_rom(self, title: str, href: str, platform: str) -> None:
        rom_t = (title, href, None, False, platform)
        c = self.get_cursor()

        c.execute('INSERT INTO ROMS VALUES (?, ?, ?, ?, ?)', rom_t)
        self.commit()

    def add_direct_download(self, href, dd):
        tt = (dd, href)

        c = self.get_cursor()
        c.execute('UPDATE ROMS SET direct_download=? WHERE href=?', tt)
        self.commit()

    def mark_downloaded(self, direct_download_url):
        tt = (True, direct_download_url)

        c = self.get_cursor()
        c.execute('UPDATE ROMS SET downloaded=? where direct_download=?', tt)
        self.commit()

    def delete_by_platform(self, platform_name: str) -> None:
        sql = 'Delete from ROMS where platform = ?'

        self.get_cursor().execute(sql, (platform_name, ))
        self.commit()


if __name__ == '__main__':
    import os

    rd = RomDB()

    rd.open('test.db')
    rd.create_table()
    rd.add_rom('example', 'example.nes', 'nes')

    for row in rd.get_cursor().execute('SELECT * FROM ROMS'):
        print (row)

    rd.add_direct_download('example.nes', 'example.dd')

    for row in rd.get_cursor().execute('SELECT * FROM ROMS'):
        print (row)

    os.remove('test.db')
