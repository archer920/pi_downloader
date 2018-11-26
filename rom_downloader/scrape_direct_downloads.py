from queue import Queue
from threading import Thread, Lock

from rom_downloader.rom_db import RomDB
from rom_downloader.rom_driver import RomDriver

NUM_WORKERS = 8
WORK_QUEUE = Queue()
LOCK = Lock()
FAILS = []


def worker() -> None:
    rom_driver = RomDriver()

    try:
        while True:
            url = WORK_QUEUE.get()

            if url is None:
                break

            try:
                scrape_direct_download(url, rom_driver)
            except Exception:
                LOCK.acquire()
                FAILS.append(url)
                LOCK.release()
            finally:
                WORK_QUEUE.task_done()
    except Exception:
        pass
    finally:
        rom_driver.close()


def scrape_direct_download(url: str, rom_driver: RomDriver):
    rom_db = RomDB()

    try:
        rom_db.open('rp_roms.db')

        rom_driver.navigate_to(url)
        rom_driver.click_element('#download_link')

        dd_link = rom_driver.href_by_link_text('click here')
        rom_driver.go_back()

        LOCK.acquire()

        rom_db.add_direct_download(url, dd_link)
        print('Recorded {} for {}'.format(dd_link, url))

        LOCK.release()
    finally:
        rom_db.close()


def main():
    rom_db = RomDB()
    rom_db.open('rp_roms.db')

    sql = 'SELECT * FROM ROMS WHERE DOWNLOADED=? and direct_download is null'

    c = rom_db.get_cursor()
    c.execute(sql, (False,))

    workers = []
    for i in range(NUM_WORKERS):
        t = Thread(target=worker)
        t.start()
        workers.append(t)

    for url in c.fetchall():
        WORK_QUEUE.put(url[1])

    WORK_QUEUE.join()

    for i in range(NUM_WORKERS):
        WORK_QUEUE.put(None)
    for t in workers:
        t.join()

    for f in FAILS:
        print('Failed to find direct download for {}'.format(f))

    rom_db.close()


if __name__ == '__main__':
    main()
