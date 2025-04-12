# modules/changer.py

import argparse, glob, json, logging, os, re, secrets, sys, time
from modules.system import execute, Script, System


class Exceptions:
    def __init__(self, exceptions: dict) -> None:
        self.exceptions = exceptions

    def clear_exception(self, filename: str) -> None:
        if filename in self.exceptions:
            del self.exceptions[filename]

    get_exception = lambda self, filename: self.exceptions[filename] if filename in self.exceptions else None
    
    def set_exception(self, filename: str, exception: str) -> None:
        self.exceptions[filename] = exception
    

class Changer:
    def __init__(self, cwd: str) -> None:
        os.chdir(cwd[:cwd.rfind('/')])
        logging.debug(f'Running from {os.getcwd()}')
        parser = argparse.ArgumentParser()
        parser.add_argument('command', help=f'Command to execute (run `{sys.argv[0]} commands\' to see the list of available commands)')
        default_config = './changer.json'
        parser.add_argument('-c', '--config', help=f'Configuration file (default={default_config})', default=default_config)
        self.args, self.extra = parser.parse_known_args()

    def __help__(self, version: str) -> None:
        self.__do_version__(version)
        print()
        print('Commands:')
        print('=========')
        print('commands         Presents this list and exits.')
        print('convert <image>  Converts <image> to different formats so it can be presented on a blog.')
        print('delete           Deletes the current wallpaper from the repository.')
        print('next             Changes the wallpaper, setting it to the predefined style.')
        print('reload           Reloads all pictures according to the configuration.')
        print('skip             Removes the current wallpaper from the sequence (without deleting it).')
        print('version          Displays the current program version and exits.')
        print('<style>          Defines the style for the current wallpaper:')
        print('  center')
        print('  combo | mosaic')
        print('  default')
        print('  fill  | zoom')
        print('  fit   | scale')
        print('  stretch')
        print('  tile')

    def __apply_module__(self, module: dict, style: str, fore: Script, back: Script) -> None:
        filename = self.config['wallpaper']['file']
        command = f'  -font {module['font']} -pointsize {module['size']} -gravity {module['gravity']}'
        if module['type'] == 'file':
            name = filename.replace('\\', '/').replace('/', '\\n')
            fore.append(f'{command} -stroke none -fill {module['color']} \\')
            back.append(f'{command} -strokewidth 2 -stroke {module['shadow']} \\')
            command = f'    -annotate {module['geometry']} "{name}" \\'
            fore.append(command)
            back.append(command)
        elif module['type'] == 'image':
            script = Script(self.system)
            script.append(f'identify -format \'%w|%h|%k|%b|%[exif:DateTime]\' "{filename}"')
            _, result, _ = script.run()
            params = result.split('|')
            info = f'{style}\\n{params[0]} x {params[1]}\\nRatio: {int(params[0])/int(params[1])}\\n{params[2]} colors\\n{params[3]}'
            info = f'{info}\\n{params[4]}' if len(params[4]) > 0 else info
            fore.append(f'{command} -stroke none -fill {module['color']} \\')
            back.append(f'{command} -strokewidth 2 -stroke {module['shadow']} \\')
            command = f'    -annotate {module['geometry']} \'{info}\' \\'
            fore.append(command)
            back.append(command)
        elif module['type'] == 'system':
            sysinfo = self.system.create_temp_file(suffix='.txt', mode='w')
            execute(['./scripts/sysinfo.sh', sysinfo, module['file'], module['token']])
            fore.append(f'{command} -stroke none -fill {module['color']} \\')
            back.append(f'{command} -strokewidth 2 -stroke {module['shadow']} \\')
            command = f'    -annotate {module['geometry']} @{sysinfo} \\'
            fore.append(command)
            back.append(command)
        elif module['type'] == 'weather':
            file = module['file']
            if not os.path.isfile(file):
                self.__display_weather__(module)
            fore.append(f'  -gravity {module['gravity']} {file} -geometry {module['geometry']} -composite \\')

    def __display_weather__(self, module: dict) -> None:
        location = module['location']
        logging.info(f'Loading weather information for {location}')
        script = Script(self.system)
        script.append(f'curl --silent \'https://api.openweathermap.org/data/2.5/weather?{location}&appid={module['appid']}\'')
        _, result, _ = script.run()
        data = json.loads(result)
        info = self.system.create_temp_file(suffix='.txt', mode='w')
        with open(info, 'w') as f:
            f.write(f'{data['name']} - {data['sys']['country']}\n')
            f.write(time.ctime(data['dt']) + '\n')
            w = data['weather'][0]
            f.write(f'{w['main']} ({w['description']})\n')
            c = data['main']['temp'] - 273.15
            f.write('{:.1f}°F = {:.1f}°C\n'.format(c * 9 / 5 + 32, c))
            f.write(f'Cloudiness: {data['clouds']['all']}%\n')
            f.write(f'Humidity: {data['main']['humidity']}%\n')
            if 'visibility' in data:
                v = data['visibility']
                f.write('Visibility: {:.2f} mi = {:.2f} km\n'.format(v / 1609, v / 1000))
            wind = data['wind']['speed']
            deg = data['wind']['deg']
            direction = 'N' if deg > 348.75 \
                else 'NNW' if deg > 326.75 \
                else 'NW' if deg > 303.75 \
                else 'WNW' if deg > 281.25 \
                else 'W' if deg > 258.75 \
                else 'WSW' if deg > 216.25 \
                else 'SW' if deg > 213.75 \
                else 'SSW' if deg > 191.25 \
                else 'S' if deg > 168.75 \
                else 'SSE' if deg > 146.25 \
                else 'SE' if deg > 123.75 \
                else 'ESE' if deg > 101.25 \
                else 'E' if deg > 78.75 \
                else 'ENE' if deg > 56.25 \
                else 'NE' if deg > 33.75 \
                else 'NNE' if deg > 11.25 \
                else 'N'
            f.write('Wind: {:.1f} mph = {:.1f} km/h {}\n'.format(wind * 2.23694, wind * 3.6, direction))
        script.reset()
        icon = self.system.create_temp_file(suffix='.png')
        script.append(f'curl --output {icon} --silent \'http://openweathermap.org/img/wn/{w['icon']}@2x.png\'')
        blur = self.system.create_temp_file(suffix='.png')
        script.append(f'magick {icon} -resize 110% -fill Black -colorize 50% -channel RGBA -blur 2x2 {blur}')
        full = self.system.create_temp_file(suffix='.png')
        script.append(f'magick -size 100x100 canvas:#ffffff40 -gravity Center {blur} -composite {icon} -composite {full}')
        script.append(f'magick -size 1024x640 canvas:none -font {module['font']} -pointsize {module['size']} -gravity {module['gravity']} \\')
        script.append(f'  -stroke {module['shadow']} -strokewidth 2 -annotate {module['offset']} @{info} \\')
        script.append('  -channel RGBA -blur 2x2 \\')
        script.append(f'  -stroke none -fill {module['color']} -annotate {module['offset']} @{info} \\')
        script.append(f'  {full} -composite \\')
        script.append(f'  {module['file']}')
        script.run()

    def __do_convert__(self) -> None:
        if len(self.extra) == 0:
            logging.fatal('Please include name of image file to be converted.')
        else:
            input_file = self.extra[0]
            logging.debug(f'Converting {input_file}')
            script = Script(self.system)
            oriented = self.system.create_temp_file(suffix='.png')
            script.append(f'magick "{input_file}" -auto-orient {oriented}')
            script.append(f'identify -format \'%h\' "{oriented}"')
            _, result, _ = script.run()
            height = int(result)
            width = round(height * 16 / 9)
            logging.info(f'Resizing to {width}×{height}')
            script.reset()
            script.append(f'magick -size {width}x{height} canvas:none -gravity Center \\')
            script.append(f'  {oriented} -resize {width} -composite \\')
            script.append(f'  -channel RGBA -blur {self.config['wallpaper']['filler']['blur']} \\')
            script.append(f'  {oriented} -composite \\')
            script.append(f'  "{input_file}.blurred.jpeg"')
            script.append(f'magick -size {width}x{height} canvas:{self.__get_base_color__('mean', oriented)} -gravity Center \\')
            script.append(f'  {oriented} -composite \\')
            script.append(f'  "{input_file}.mean.jpeg"')
            script.append(f'magick -size {width}x{height} canvas:{self.__get_base_color__('median', oriented)} -gravity Center \\')
            script.append(f'  {oriented} -composite \\')
            script.append(f'  "{input_file}.median.jpeg"')
            script.run()
          
    def __do_delete__(self) -> None:
        filename = self.config['wallpaper']['file']
        logging.info(f'Deleting {filename}')
        try:
            os.remove(filename)
        except FileNotFoundError | IsADirectoryError:
            pass
        self.exceptions.clear_exception(filename)
        self.__do_reload__()
        self.__do_next__()

    def __do_next__(self) -> None:
        with open(self.catalog, 'r') as f:
            files = f.read().splitlines()
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
                if os.path.isfile(filename) and re.match(pattern, filename) != None:
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
        style = 'combo/mosaic' if style in ['combo', 'mosaic'] \
            else 'fill/zoom' if style in ['fill', 'zoom'] \
            else 'fit/scale' if style in ['fit', 'scale'] \
            else style
        logging.info(f'New custom style for {filename}: {style}')
        if style == 'default':
            self.exceptions.clear_exception(filename)
            style = self.config['wallpaper']['render']
            exception = False
        else:
            self.exceptions.set_exception(filename, style)
        self.__set_wallpaper__(style, exception)

    def __do_version__(self, version: str) -> None:
        print(f'{sys.argv[0]} {version}')
        print('Copyright © 2024, 2025 Jose Tafla. All rights reserved.')

    def __get_base_color__(self, keyword: str, input_file: str = None) -> str:
        script = Script(self.system)
        input_file = self.config['wallpaper']['file'] if input_file == None else input_file
        script.append(f'identify -verbose \'{input_file}\' | \\')
        script.append(f' command grep {keyword} | \\')
        script.append('  awk \'{print $2}\'')
        _, result, _ = script.run()
        components = result.split('\n')
        __hex__ = lambda i: ('0' + hex(round(float(components[i])))[2:])[-2:]
        return f'#{__hex__(0)}{__hex__(1)}{__hex__(2)}'

    def __set_backdrop__(self, style: str, exception: bool) -> str:
        filename = self.config['wallpaper']['file']
        oriented = self.system.create_temp_file(suffix='.png')
        script = Script(self.system)
        script.append(f'magick "{filename}" -auto-orient {oriented}')
        script.append(f'identify -format \'%w|%h\' {oriented}')
        _, result, _ = script.run()
        params = result.split('|')
        image_width = int(params[0])
        image_height = int(params[1])
        image_ratio = image_width / image_height
        script.reset()
        width = self.config['width']
        height = self.config['height']
        backdrop = self.system.create_temp_file(suffix='.png')
        if not exception:
            if self.config['wallpaper']['auto_adjust']['enabled']:
                logging.debug('Automaticly adjusting image.')
                tolerance = self.config['wallpaper']['auto_adjust']['tolerance']
                if image_width <= width and image_height <= height:
                    if image_width >= tolerance['horizontal'] and image_height >= tolerance['vertical']:
                        pass
                    else:
                        style = 'fit/scale'
                elif image_ratio < 1:
                    style = 'fit/scale'
        base = self.system.create_temp_file(suffix='.png')

        def fill_base() -> None:
            filler = self.config['wallpaper']['filler']
            mode = filler['mode']
            if mode == 'blur':
                screen_ratio = width / height
                size = str(width) if image_ratio < screen_ratio else f'x{height}'
                script.append(f'magick -size {width}x{height} canvas:none -gravity Center \\')
                script.append(f'  {oriented} -resize {size} -composite \\')
                script.append(f'  -channel RGBA -blur {filler[mode]} \\')
                script.append(f'  {base}')
            elif mode == 'overlap':
                pass
            elif mode == 'blank':
                color = filler[mode]['color']
                color = self.__get_base_color__(color) if color in ['mean', 'median'] \
                    else color
                script.append(f'magick -size {width}x{height} canvas:{color} {base}')

        if style == 'center':
            fill_base()
            script.append(f'magick {base} -gravity Center {oriented} -composite {backdrop}')
        elif style == 'combo/mosaic':
            tile = self.system.create_temp_file(suffix='.png')
            script.append(f'magick {oriented} -resize {width}x{height} {tile}')
            script.append(f'magick -size {width}x{height} tile:{tile} {backdrop}')
        elif style == 'fill/zoom':
            screen_ratio = width / height
            size = str(width) if image_ratio < screen_ratio else f'x{height}'
            script.append(f'magick -size {width}x{height} canvas:none -gravity Center {oriented} -resize {size} -composite {backdrop}')
        elif style == 'fit/scale':
            fill_base()
            scaled = self.system.create_temp_file(suffix='.png')
            script.append(f'magick {oriented} -resize {width}x{height} {scaled}')
            script.append(f'magick {base} -gravity Center {scaled} -composite {backdrop}')
        elif style == 'stretch':
            script.append(f'magick {oriented} -resize {width}x{height}! {backdrop}')
        else: # tile
            script.append(f'magick -size {width}x{height} tile:{oriented} {backdrop}')
        script.run()
        return backdrop

    def __set_wallpaper__(self, style: str, exception: bool) -> None:
        backdrop = self.__set_backdrop__(style, exception)
        foreground = self.system.create_temp_file(suffix='.png')
        fore = Script(self.system)
        command = f'magick -size {self.config['width']}x{self.config['height']} canvas:none \\'
        fore.append(command)
        background = self.system.create_temp_file(suffix='.png')
        back = Script(self.system)
        back.append(command)
        for module in self.config['modules']:
            if module['enabled']:
                self.__apply_module__(module, style, fore, back)
        fore.append(f'  {foreground}')
        fore.run()
        back.append(f'  -channel RGBA -blur 2x2 {background}')
        back.run()
        script = Script(self.system)
        wallpaper = self.config['wallpaper']['wallpaper']
        script.append(f'magick {backdrop} {background} -composite {foreground} -composite {wallpaper}')
        script.run()
        _, result, _ = execute(['./scripts/wallpaper.sh', wallpaper, self.config['wallpaper']['filler']['blur']])
        if len(result) > 0:
            self.config['wallpaper']['history'].append(result)

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
                self.__help__(version)
            elif command == 'convert':
                self.__do_convert__()
            elif command == 'delete':
                self.__do_delete__()
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
                self.__do_version__(version)
            elif command in ['center', 'default', 'combo', 'fill', 'fit', 'mosaic', 'scale', 'stretch', 'tile', 'zoom']:
                self.__do_style__(command)
            else:
                print(f'Unknown command: {command}')
                self.exit(3)
            self.exit(0)
        except Exception as e:
            logging.exception(e, exc_info=True, stack_info=True)
            self.exit(1)