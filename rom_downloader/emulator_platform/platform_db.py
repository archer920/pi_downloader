from rom_downloader.db.BaseDB import BaseDB


class PlatformDB(BaseDB):
    def __init__(self) -> None:
        super().__init__()

    def create_table(self) -> None:
        sql = 'CREATE TABLE IF NOT EXISTS `Platform` (`Name` TEXT UNIQUE, `Link` TEXT UNIQUE, `Num_Pages` INTEGER)'

        c = self.get_cursor()
        c.execute(sql)
        self.commit()

    def add_platform(self, platform_name: str, platform_link: str, num_pages: int) -> None:
        platform_args = (platform_name, platform_link, num_pages)

        c = self.get_cursor()

        c.execute('INSERT INTO PLATFORM VALUES (?, ?, ?)', platform_args)
        self.commit()


if __name__ == '__main__':
    import os

    pdb = PlatformDB()

    pdb.open('test.db')
    pdb.create_table()

    pdb.add_platform('nes', 'mynes.com', 25)

    for row in pdb.get_cursor().execute('SELECT * from PLATFORM'):
        print (row)

    os.remove('test.db')
