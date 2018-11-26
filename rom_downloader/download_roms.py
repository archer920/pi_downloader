import os
import shutil
import urllib
from queue import Queue
from threading import Lock, Thread

from rom_downloader.rom_db import RomDB

NUM_WORKERS = 8
WORK_QUEUE = Queue()
LOCK = Lock()
FAILS = []


def worker() -> None:
    while True:
        rom_download = WORK_QUEUE.get()

        if rom_download is None:
            break

        try:
            download(rom_download['name'], rom_download['target_dir'], rom_download['rom_platform'],
                     rom_download['url'])
        except Exception as e:
            LOCK.acquire()

            print(e)
            FAILS.append(rom_download)

            LOCK.release()
        finally:
            WORK_QUEUE.task_done()


def download(name: str, target_dir: str, rom_platform: str, url: str):
    LOCK.acquire()
    print('Starting {}'.format(name, url))
    LOCK.release()

    rom_db = RomDB()
    rom_db.open('rp_roms.db')

    out_dir = os.path.join(os.sep, target_dir, rom_platform)
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    file_extension = url.split('.')[-1]
    out_path = os.path.join(os.sep, out_dir, name + '.' + file_extension)

    with urllib.request.urlopen(url) as response, open(out_path, 'wb') as fout:
        shutil.copyfileobj(response, fout)

        LOCK.acquire()
        rom_db.mark_downloaded(url)
        print('Saved {}'.format(out_path))
        LOCK.release()

    rom_db.close()


def main():
    roms_dir = os.path.join(os.path.sep, os.getcwd(), 'downloads')
    rom_db = RomDB()
    rom_db.open('rp_roms.db')

    if not os.path.exists(roms_dir):
        os.mkdir(roms_dir)

    c = rom_db.get_cursor()
    c.execute('SELECT TITLE, DIRECT_DOWNLOAD, PLATFORM FROM ROMS WHERE DOWNLOADED=? and DIRECT_DOWNLOAD is not null', (False,))

    for row in c.fetchall():
        WORK_QUEUE.put({'name': row[0], 'target_dir': roms_dir, 'rom_platform': row[2], 'url': row[1]})
    rom_db.close()

    workers = []
    for i in range(NUM_WORKERS):
        t = Thread(target=worker)
        t.start()
        workers.append(t)

    WORK_QUEUE.join()
    for i in range(NUM_WORKERS):
        WORK_QUEUE.put(None)
    for t in workers:
        t.join()

    for f in FAILS:
        print('Failed to download: {}'.format(f))


if __name__ == '__main__':
    main()
