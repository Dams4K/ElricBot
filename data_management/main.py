import os
import json

BASE_GUILD_FOLDER = "datas/guilds/"

def get_guild_path(*end):
    return os.path.join(BASE_GUILD_FOLDER, *end)

class BaseData:
    def __init__(self, file_path, base_data):
        self.file_path = file_path

        self.data = base_data if not hasattr(self, "data") else self.data
        self.load()


    def create_dirs(self):
        dirname = os.path.dirname(self.file_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)


    def load_base_data(self): pass


    def load(self):
        self.create_dirs()
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                self.data = json.load(f)
        else:
            self.save()


    def save(self):
        data = self.get_data()
        self.create_dirs()
        if data != None:
            with open(self.file_path, "w") as f:
                json.dump(data, f, indent=4)
    

    def get_data(self):
        return self.data.copy()

    def manage_data(func):
        def decorator(self, *args, **kwargs):
            self.load()
            self.load_base_data()

            result = func(self, *args, **kwargs)
            
            self.save()
            
            return result
        return decorator