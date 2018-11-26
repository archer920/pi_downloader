from rom_downloader.emulator_platform.platform_db import PlatformDB
from rom_downloader.rom_driver import RomDriver


def main() -> None:
    rom_driver = RomDriver()
    pfb = PlatformDB()
    pfb.open('../rp_roms.db')
    pfb.create_table()

    try:
        rom_driver.navigate_to('https://romsmania.cc/roms')

        links = rom_driver.find_rom_links('.table > tbody:nth-child(2)')
        for l in links:
            rom_driver.navigate_to(l['href'])
            selectors = ['li.pagination__el:nth-child(6) > a:nth-child(1)',
                         'li.pagination__el:nth-child(2) > a:nth-child(1)']

            num_pages = rom_driver.get_text_from_selectors(selectors)

            if num_pages == 'Next':
                num_pages = rom_driver.get_element_text('li.pagination__el:nth-child(5) > a:nth-child(1)')

            if num_pages is None:
                num_pages = 1

            print(l, num_pages)
            pfb.add_platform(l['title'], l['href'], int(num_pages))
    finally:
        rom_driver.close()


if __name__ == '__main__':
    main()
