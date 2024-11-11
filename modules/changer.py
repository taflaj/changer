# modules/changer.py

import argparse, glob, json, logging, os, re, secrets, sys, time

from modules.system import execute, Script, System


class Exceptions:
    def __init__(self, exceptions: dict) -> None:
        self.exceptions = exceptions

    def clear_exception(self, filename: str) -> None:
        if filename in self.exceptions:
            del self.exceptions[filename]

    def get_exception(self, filename: str) -> str | None:
        return self.exceptions[filename] if filename in self.exceptions else None
    
    def set_exception(self, filename: str, exception: str) -> None:
        self.exceptions[filename] = exception
    

class Changer:
    def __init__(self, cwd: str) -> None:
        os.chdir(cwd[:cwd.rfind('/')])
        logging.debug(f'Running from {os.getcwd()}')
        parser = argparse.ArgumentParser()
        parser.add_argument('command', help=f"Command to execute (run `{sys.argv[0]} commands' to see the list of available commands)")
        default_config = './changer.json'
        parser.add_argument('-c', '--config', help=f'Configuration file (default={default_config})', default=default_config)
        self.args, self.extra = parser.parse_known_args()

    def __help__(self) -> None:
        print('Commands:')
        print('=========')
        print('commands  Presents this list and exits.')
        print('delete    Deletes the current wallpaper from the repository.')
        print('next      Changes the wallpaper, setting it to the predefined style.')
        print('reload    Reloads all pictures according to the configuration.')
        print('skip      Removes the current wallpaper from the sequence (without deleting it).')
        print('version   Displays the current program version and exits.')
        print('<style>   Defines the style for the current wallpaper:')
        print('  center')
        print('  combo | mosaic')
        print('  default')
        print('  fill  | zoom')
        print('  fit   | scale')
        print('  stretch')
        print('  tile')

    def __apply_module__(self, module: dict, style: str, fore: Script, back: Script) -> None:
        filename = self.config['wallpaper']['file']
        command = f"  -font {module['font']} -pointsize {module['size']} -gravity {module['gravity']}"
        if module['type'] == 'file':
            name = filename.replace('\\', '/').replace('/', '\\n')
            fore.append(f"{command} -stroke none -fill {module['color']} \\")
            back.append(f"{command} -strokewidth 2 -stroke {module['shadow']} \\")
            command = f"    -annotate {module['geometry']} '{name}' \\"
            fore.append(command)
            back.append(command)
        elif module['type'] == 'image':
            script = Script(self.system)
            script.append(f"identify -format '%w|%h|%k|%b|%[exif:DateTime]' '{filename}'")
            _, result, _ = script.run()
            params = result.split('|')
            info = f'{style}\\n{params[0]} x {params[1]}\\nRatio: {int(params[0])/int(params[1])}\\n{params[2]} colors\\n{params[3]}'
            info = f'{info}\\n{params[4]}' if len(params[4]) > 0 else info
            fore.append(f"{command} -stroke none -fill {module['color']} \\")
            back.append(f"{command} -strokewidth 2 -stroke {module['shadow']} \\")
            command = f"    -annotate {module['geometry']} '{info}' \\"
            fore.append(command)
            back.append(command)
        elif module['type'] == 'system':
            sysinfo = self.system.create_temp_file(suffix='.txt', mode='w')
            execute(['./scripts/sysinfo.sh', sysinfo, module['file'], module['token']])
            fore.append(f"{command} -stroke none -fill {module['color']} \\")
            back.append(f"{command} -strokewidth 2 -stroke {module['shadow']} \\")
            command = f"    -annotate {module['geometry']} '@{sysinfo}' \\"
            fore.append(command)
            back.append(command)
        elif module['type'] == 'weather':
            file = module['file']
            if not os.path.isfile(file):
                self.__display__weather__(module)
            fore.append(f"  -gravity {module['gravity']} {file} -geometry {module['geometry']} -composite \\")

    def __display__weather__(self, module: dict) -> None:
        location = module['location']
        logging.info(f'Loading weather information for {location}')
        script = Script(self.system)
        script.append(f"curl --silent 'https://api.openweathermap.org/data/2.5/weather?{location}&appid={module['appid']}'")
        _, result, _ = script.run()
        data = json.loads(result)
        info = self.system.create_temp_file(suffix='.txt', mode='w')
        with open(info, 'w') as f:
            f.write(f"{data['name']} - {data['sys']['country']}\n")
            f.write(time.ctime(data['dt']) + '\n')
            w = data['weather'][0]
            f.write(f"{w['main']} ({w['description']})\n")
            c = data['main']['temp'] - 273.15
            f.write('{:.1f}°F = {:.1f}°C\n'.format(c * 9 / 5 + 32, c))
            f.write(f"Cloudiness: {data['clouds']['all']}%\n")
            f.write(f"Humidity: {data['main']['humidity']}%\n")
            if 'visibility' in data:
                v = data['visibility']
                f.write('Visibility: {:.2f} mi = {:.2f} km\n'.format(v / 1609, v / 1000))
            wind = data['wind']['speed']
            deg = data['wind']['deg']
            direction = 'N' if deg > 348.75 else \
                'NNW' if deg > 326.75 else \
                'NW' if deg > 303.75 else \
                'WNW' if deg > 281.25 else \
                'W' if deg > 258.75 else \
                'WSW' if deg > 216.25 else \
                'SW' if deg > 213.75 else \
                'SSW' if deg > 191.25 else \
                'S' if deg > 168.75 else \
                'SSE' if deg > 146.25 else \
                'SE' if deg > 123.75 else \
                'ESE' if deg > 101.25 else \
                'E' if deg > 78.75 else \
                'ENE' if deg > 56.25 else \
                'NE' if deg > 33.75 else \
                'NNE' if deg > 11.25 else \
                'N'
            f.write('Wind: {:.1f} mph = {:.1f} km/h {}\n'.format(wind * 2.23694, wind * 3.6, direction))
        script.reset()
        icon = self.system.create_temp_file(suffix='.png')
        script.append(f"curl --output '{icon}' --silent 'http://openweathermap.org/img/wn/{w['icon']}@2x.png'")
        blur = self.system.create_temp_file(suffix='.png')
        script.append(f"magick '{icon}' -resize 125% -fill Black -colorize 50% -channel RGBA -blur 2x2 '{blur}'")
        full = self.system.create_temp_file(suffix='.png')
        script.append(f"magick -size 100x100 canvas:#ffffff40 -gravity Center '{blur}' -composite '{icon}' -composite '{full}'")
        script.append(f"magick -size 1024x640 canvas:none -font {module['font']} -pointsize {module['size']} -gravity {module['gravity']} \\")
        script.append(f"  -stroke {module['shadow']} -strokewidth 2 -annotate {module['offset']} '@{info}' \\")
        script.append('  -channel RGBA -blur 2x2 \\')
        script.append(f"  -stroke none -fill {module['color']} -annotate {module['offset']} '@{info}' \\")
        script.append(f"  '{full}' -composite \\")
        script.append(module['file'])
        script.run()

    def __do_next__(self) -> None:
        files = []
        with open(self.catalog, 'r') as f:
            while True:
                filename = f.readline()
                if len(filename) == 0:
                    break
                files.append(filename[:-1])
        exception = True
        while True:
            n = secrets.randbelow(len(files))
            filename = files[n]
            mode = self.exceptions.get_exception(filename)
            if mode == None:
                style = self.config['wallpaper']['render']
                exception = False
                break
            elif mode == 'skip':
                logging.info(f'Skipping #{n}: {filename}')
                continue
            else:
                style = mode
                logging.info(f'Custom style: {style}')
                break
        logging.info(f'{n}: {filename}')
        self.config['wallpaper']['file'] = filename
        self.__set_wallpaper__(style, exception)

    def __do_reload__(self) -> None:
        pattern = re.compile(self.config['files']['type'], re.IGNORECASE)
        files = set()
        folders = self.config['files']['folders']
        for folder in folders:
            path = folder['path'] + '**'
            all_files = glob.glob(path, recursive=folder['recursive'])
            for filename in all_files:
                if os.path.isfile(filename):
                    if re.match(pattern, filename) != None:
                        files.add(filename)
        logging.info(f'{len(files)} files in repository')
        with open(self.catalog, 'w') as f:
            for filename in files:
                f.write(filename + '\n')

    def __do_skip__(self) -> None:
        filename = self.config['wallpaper']['file']
        logging.info(f'Skipping {filename}')
        self.exceptions.set_exception(filename, 'skip')
        self.__do_next__()

    def __do_style__(self, style: str) -> None:
        filename = self.config['wallpaper']['file']
        exception = True
        if style in ['combo', 'mosaic']:
            style = 'combo/mosaic'
        elif style in ['fill', 'zoom']:
            style = 'fill/zoom'
        elif style in ['fit', 'scale']:
            style = 'fit/scale'
        logging.info(f'New custom style for {filename}: {style}')
        if style == 'default':
            self.exceptions.clear_exception(filename)
            style = self.config['wallpaper']['render']
            exception = False
        else:
            self.exceptions.set_exception(filename, style)
        self.__set_wallpaper__(style, exception)

    def __set_wallpaper__(self, style: str, exception: bool) -> None:
        filename = self.config['wallpaper']['file']
        oriented = self.system.create_temp_file(suffix='.png')
        script = Script(self.system)
        script.append(f"magick '{filename}' -auto-orient '{oriented}'")
        script.run()
        script.reset()
        width = self.config['width']
        height = self.config['height']
        backdrop = self.system.create_temp_file(suffix='.png')
        if style == 'center':
            script.append(f"magick -size {width}x{height} canvas:{self.config['wallpaper']['filler']['blank']['color']} -gravity Center '{oriented}' -composite '{backdrop}'")
        elif style == 'combo/mosaic':
            tile = self.system.create_temp_file(suffix='.png')
            script.append(f"magick '{oriented}' -resize {width}x{height} '{tile}'")
            script.append(f"magick -size {width}x{height} tile:'{tile}' '{backdrop}'")
        elif style == 'fill/zoom':
            screen_ratio = width / height
            temp_script = Script(self.system)
            temp_script.append(f"identify -format '%w|%h' '{oriented}'")
            _, result, _ = temp_script.run()
            params = result.split('|')
            image_ratio = int(params[0]) / int(params[1])
            size = str(width) if image_ratio < screen_ratio else f'x{height}'
            script.append(f"magick -size {width}x{height} canvas:none -gravity Center '{oriented}' -resize {size} -composite '{backdrop}'")
        elif style == 'fit/scale':
            scaled = self.system.create_temp_file(suffix='.png')
            script.append(f"magick '{oriented}' -resize {width}x{height} '{scaled}'")
            script.append(f"magick -size {width}x{height} canvas:{self.config['wallpaper']['filler']['blank']['color']} -gravity Center '{scaled}' -composite '{backdrop}'")
        elif style == 'stretch':
            script.append(f"magick '{oriented}' -resize {width}x{height}! '{backdrop}'")
        else: # tile
            script.append(f"magick -size {width}x{height} tile:'{oriented}' '{backdrop}'")
        script.run()
        foreground = self.system.create_temp_file(suffix='.png')
        fore = Script(self.system)
        command = f'magick -size {width}x{height} canvas:none \\'
        fore.append(command)
        background = self.system.create_temp_file(suffix='.png')
        back = Script(self.system)
        back.append(command)
        for module in self.config['modules']:
            if module['enabled']:
                self.__apply_module__(module, style, fore, back)
        fore.append(f"  '{foreground}'")
        fore.run()
        back.append(f"  -channel RGBA -blur 2x2 '{background}'")
        back.run()
        script.reset()
        wallpaper = self.config['wallpaper']['wallpaper']
        script.append(f"magick '{backdrop}' '{background}' -composite '{foreground}' -composite '{wallpaper}'")
        script.run()
        execute(['./scripts/wallpaper.sh', wallpaper])

    def exit(self, code: int) -> None:
        self.system.close()
        if code == 0:
            file = self.args.config
            try:
                os.replace(file, file + '.bak')
            except FileNotFoundError:
                pass
            with open(file, 'w') as f:
                json.dump(self.config, f, indent=4)
        sys.exit(code)

    def start(self, version: str) -> None:
        logging.debug(self.args)
        logging.debug(self.extra)
        config_file = self.args.config
        logging.info(f'Reading configuration file {config_file}')
        try:
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            logging.critical(f'Configuration file {config_file} not found.')
            self.exit(2)
        self.system = System(self.config)
        self.catalog = self.config['catalog']
        self.exceptions = Exceptions(self.config['wallpaper']['exceptions'])
        try:
            command = self.args.command
            if command == 'commands' or command == 'help':
                self.__help__()
            elif command == 'next':
                try:
                    self.__do_next__()
                except FileNotFoundError:
                    logging.info(f'Repository {self.catalog} does not exist. Recreating…')
                    self.__do_reload__()
                    self.__do_next__()
            elif command == 'reload':
                self.__do_reload__()
            elif command == 'skip':
                self.__do_skip__()
            elif command == 'version':
                print(f'{sys.argv[0]} {version}')
                print('Copyright © 2024 Jose Tafla. All rights reserved.')
            elif command in ['center', 'default', 'combo', 'fill', 'fit', 'mosaic', 'scale', 'stretch', 'tile', 'zoom']:
                self.__do_style__(command)
            else:
                print(f'Unknown command: {command}')
                self.exit(3)
            self.exit(0)
        except Exception as e:
            logging.exception(e, exc_info=True, stack_info=True)
            self.exit(1)