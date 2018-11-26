from queue import Queue
from threading import Thread, Lock
from rom_downloader.emulator_platform.platform_db import PlatformDB
from rom_downloader.rom_db import RomDB
from rom_downloader.rom_driver import RomDriver

NUM_WORKS = 8
platform_queue = Queue()
lock = Lock()
FAILS = []


def worker():
    rom_driver = RomDriver()
    try:
        while True:
            pf = platform_queue.get()

            if pf is None:
                break

            try:
                scrape_rom_urls(pf['Link'], pf['Pages'], pf['Name'], rom_driver)

                lock.acquire()
                print('Finished with platform = {}'.format(pf['Name']))
                lock.release()
            except Exception:

                lock.acquire()
                FAILS.append(pf['Name'])
                print('Failed to process platform = {}'.format(pf['Name']))
                lock.release()
            finally:
                platform_queue.task_done()
    except Exception:
        pass
    finally:
        rom_driver.close()


def scrape_rom_urls(url: str, num_pages: int, platform: str, rom_driver : RomDriver) -> None:
    rom_db = RomDB()
    rom_db.open('rp_roms.db')

    try:
        rom_db.create_table()
        rom_driver.navigate_to(url)
        rom_driver.select_combo_box_option('div.select:nth-child(3) > select:nth-child(1)', 'USA')

        for pg in range(1, num_pages):
            links = rom_driver.find_rom_links('.table > tbody:nth-child(2)')

            for lk in links:
                lock.acquire()
                rom_db.add_rom(lk['title'], lk['href'], platform)
                lock.release()

            rom_driver.click_next_by_title('.pagination__list', 'Next page')
    finally:
        rom_db.close()


def main():
    pfb = PlatformDB()
    pfb.open('rp_roms.db')

    rom_platforms = []
    for rpf in pfb.get_cursor().execute(
            'select * from Platform where name not in (select distinct Platform from ROMS)'):
        rom_platforms.append({'Name': rpf[0], 'Link': rpf[1], 'Pages': rpf[2]})

    pfb.close()

    workers = []
    for i in range(NUM_WORKS):
        t = Thread(target=worker)
        t.start()
        workers.append(t)

    for pf in rom_platforms:
        platform_queue.put(pf)

    platform_queue.join()

    for i in range(NUM_WORKS):
        platform_queue.put(None)
    for t in workers:
        t.join()

    rom_db = RomDB()
    rom_db.open('rp_roms.db')
    for pf in FAILS:
        rom_db.delete_by_platform(pf)

    rom_db.close()


if __name__ == '__main__':
    main()
