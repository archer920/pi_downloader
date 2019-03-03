from datetime import datetime
from queue import Queue
from threading import Thread, Lock

from rom_downloader.rom_db import RomDB
from rom_downloader.rom_driver import RomDriver

NUM_WORKERS = 2
WORK_QUEUE = Queue()
LOCK = Lock()
FAILS = []


def worker() -> None:
    try:
        while True:
            url = WORK_QUEUE.get()

            if url is None:
                break

            try:
                scrape_direct_download(url)
            except Exception as e:
                LOCK.acquire(timeout=500)
                print(datetime.now().time(), e)
                FAILS.append(url)
                LOCK.release()
            finally:

                WORK_QUEUE.task_done()
    except Exception as e:
        print(datetime.now().time(), e)
        pass


def scrape_direct_download(url: str):
    rom_driver = RomDriver()
    rom_db = RomDB()

    try:
        rom_driver.navigate_to(url)
        rom_driver.click_element('#download_link')
        dd_link = rom_driver.href_by_link_text('click here')

        try:
            LOCK.acquire(timeout=2000)
            rom_db.open('rp_roms.db')
            rom_db.add_direct_download(url, dd_link)
            print(datetime.now().time(), 'Recorded {} for {}'.format(dd_link, url))
        except Exception as e:
            print(datetime.now().time(), e)
        finally:
            rom_db.close()
            LOCK.release()
    except Exception as e:
        print(datetime.now().time(), e)
    finally:
        rom_driver.close()


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
        print(datetime.now().time(), 'Failed to find direct download for {}'.format(f))

    rom_db.close()


def reboot():
    print('Restarting...')
    import subprocess, os
    subprocess.call(['python3', os.path.join(os.path.sep, os.getcwd(), 'scrape_direct_downloads.py')])


if __name__ == '__main__':
    main()
