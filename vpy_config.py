from os import path as ospath
from os import makedirs, listdir
import json

class LanguageConfig:
    def __init__(self):
        self.config_path = "config"
        self.languages = {}
        self.load_configs()
    
    def load_configs(self):
        if not ospath.exists(self.config_path):
            makedirs(self.config_path)
            self.create_default_config()
        
        for file in listdir(self.config_path):
            if file.endswith('.json'):
                with open(ospath.join(self.config_path, file)) as f:
                    config = json.load(f)
                    if 'lang' in config:
                        self.languages[config['lang']['name']] = config
    
    def create_default_config(self):
        python_config = {
            "lang": {
                "name": "Python",
                "extensions": ["py", "pyc", "pyw"]
            },
            "keywords": [
                "and", "assert", "break", "class", "continue", "def",
                "del", "elif", "else", "except", "False", "finally",
                "for", "from", "global", "if", "import", "in", "is",
                "lambda", "None", "nonlocal", "not", "or", "pass",
                "raise", "return", "True", "try", "while", "with", "yield"
            ],
            "colors": {
                "keyword": "#FF6B6B",
                "string": "#98C379",
                "comment": "#5C6370",
                "function": "#61AFEF",
                "class": "#E5C07B",
                "number": "#D19A66",
                "decorator": "#C678DD"
            }
        }
        
        with open(ospath.join(self.config_path, 'python.json'), 'w') as f:
            json.dump(python_config, f, indent=4)
    
    def get_language_config(self, file_extension):
        for lang_config in self.languages.values():
            if file_extension.lstrip('.') in lang_config['lang']['extensions']:
                return lang_config
        return None

    def get_language_by_name(self, name):
        return self.languages.get(name)

class ConfigManager:
    def __init__(self):
        self.config_dir = ospath.join(ospath.expanduser('~'), '.vysual_ide')
        self.config_path = ospath.join(self.config_dir, 'config.json')
        self.ensure_config_exists()
        
    def ensure_config_exists(self):
        makedirs(self.config_dir, exist_ok=True)
        if not ospath.exists(self.config_path):
            self.save_config(self.get_default_config())

    def get_default_config(self):
        return {
            'editor': {
                'colors': {
                    'keyword': "#FF6B6B",
                    'string': "#98C379",
                    'comment': "#5C6370",
                    'function': "#61AFEF",
                    'class': "#E5C07B",
                    'number': "#D19A66",
                    'decorator': "#C678DD"
                }
            },
            'blueprint': {
                'grid_size': 50
            },
            'execution': {
                'grid_size': 50
            },
            'environment': {
                'python': {
                    'interpreter': "",
                    'lib_paths': []
                },
                'build': {
                    'compiler': "",
                    'linker': "",
                    'lib_paths': []
                }
            }
        }
    
    def load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.get_default_config()
    
    def save_config(self, config):
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def update_config(self, values):
        config = self.load_config()
        
        if 'grid_size' in values:
            config['blueprint']['grid_size'] = values['grid_size']['blueprint']
            config['execution']['grid_size'] = values['grid_size']['execution']
     
        # Update editor colors
        if 'colors' in values:
            config['editor']['colors'] = {
                name: color.name() for name, color in values['colors'].items()
            }
        
        # Update environment settings
        if 'env' in values:
            env = values['env']
            config['environment']['python']['interpreter'] = env['interpreter']
            config['environment']['python']['lib_paths'] = env['python_lib_paths']
            config['environment']['build']['compiler'] = env['compiler']
            config['environment']['build']['linker'] = env['linker']
            config['environment']['build']['lib_paths'] = env['other_lib_paths']
        
        self.save_config(config)
