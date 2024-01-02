import configparser


class ConfigReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.config = configparser.RawConfigParser()
        try:
            self.config.read(file_path, encoding='utf-8')
        except configparser.Error:
            pass

    # 读取键值
    def get_value(self, section, option, fallback=None):  # fallback默认值
        return self.config.get(section, option, fallback=fallback)

    def get_int_value(self, section, option):
        return self.config.getint(section, option)

    def get_float_value(self, section, option):
        return self.config.getfloat(section, option)

    def get_boolean_value(self, section, option):
        return self.config.getboolean(section, option)

    def get_section(self, section):
        if section in self.config:
            return dict(self.config[section])
        else:
            return {}

    def get_sections(self):
        return self.config.sections()

    # 写入键值
    def set_value(self, set_info=None):
        if set_info is not None:
            section = set_info['tools']
            if not self.config.has_section(section):
                self.config.add_section(section)
            for k, v in set_info.items():
                if k != 'tools':
                    self.config.set(section, k, v)

    def save_config(self):
        with open(self.file_path, 'w', encoding='utf-8') as configfile:
            self.config.write(configfile)
