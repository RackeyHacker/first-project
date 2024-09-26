import os
import tarfile
import json
import argparse
import sys

class ShellEmulator:
    def __init__(self, tar_path, log_path):
        """Инициализация эмулятора оболочки."""
        self.log_path = log_path
        self.current_dir = '/'
        self.vfs = {}
        self.load_vfs(tar_path)
        self.actions = []

    def load_vfs(self, tar_path):
        """Загрузка виртуальной файловой системы из tar-архива."""
        with tarfile.open(tar_path, 'r') as tar:
            for member in tar.getmembers():
                if member.isfile():
                    self.vfs[member.name] = tar.extractfile(member).read().decode('utf-8')
                elif member.isdir():
                    self.vfs[member.name] = []

    def log_action(self, action):
        """Запись действия в лог."""
        self.actions.append(action)

    def save_log(self):
        """Сохранение лога в файл."""
        with open(self.log_path, 'w') as log_file:
            json.dump(self.actions, log_file)

    def ls(self):
        """Вывод списка файлов и директорий в текущей директории."""
        if not self.current_dir.endswith('/'):
            self.current_dir += '/'
        items = []
        for item in self.vfs.keys():
            if self.current_dir == '/' and '/' not in item.lstrip('/'):
                items.append(item)
            elif item.startswith(self.current_dir):
                relative_path = item[len(self.current_dir):]
                if '/' not in relative_path.strip('/'):
                    items.append(relative_path)
        if items:
            print('\n'.join(items))
        else:
            print("No files found.")
        self.log_action({'command': 'ls', 'output': items})

    def cd(self, path):
        """Изменение текущей директории."""
        if path == '' or path == '/':
            self.current_dir = '/'
            self.log_action({'command': 'cd', 'path': self.current_dir})
        elif path == '..':
            if self.current_dir == '/':
                print("Находитесь в корневой директории, нельзя подняться выше.")
            else:
                self.current_dir = '/'.join(self.current_dir.split('/')[:-1]) or '/'
                self.log_action({'command': 'cd', 'path': self.current_dir})
        elif path in self.vfs:
            self.current_dir = path
            self.log_action({'command': 'cd', 'path': path})
        else:
            print(f"cd: no such file or directory: {path}")

    def whoami(self):
        """Вывод имени текущего пользователя."""
        user = os.getlogin()
        print(user)
        self.log_action({'command': 'whoami', 'output': user})

    def tac(self, filenames):
        """Вывод содержимого файлов в обратном порядке."""
        for filename in filenames:
            if filename in self.vfs:
                if isinstance(self.vfs[filename], list):
                    print("Нельзя так делать: нельзя использовать tac для директории.")
                else:
                    content = self.vfs[filename].splitlines()[::-1]
                    print(f"\n--- {filename} ---\n")
                    print('\n'.join(content))
                    self.log_action({'command': 'tac', 'filename': filename, 'output': content})
            else:
                print(f"tac: {filename}: No such file")

    def exit(self):
        """Выход из эмулятора и сохранение лога."""
        self.save_log()
        print("Exiting...")
        sys.exit(0)


    def run(self):
        """Основной цикл для обработки команд пользователя."""
        while True:
            command = input(f"{self.current_dir} $ ").strip().split()
            if not command:
                continue
            
            cmd = command[0]
            if cmd == 'ls':
                self.ls()
            elif cmd == 'cd' and len(command) > 1:
                self.cd(command[1])
            elif cmd == 'whoami':
                self.whoami()
            elif cmd == 'tac' and len(command) > 1:
                self.tac(command[1:])  # Передаем список всех файлов
            elif cmd == 'exit':
                self.exit()
            else:
                print(f"{cmd}: command not found")


def main():
    """Главная функция для запуска эмулятора."""
    parser = argparse.ArgumentParser(description="Shell Emulator")
    parser.add_argument('tar_path', help='Path to the virtual filesystem tar file')
    parser.add_argument('log_path', help='Path to the log file')
    args = parser.parse_args()

    emulator = ShellEmulator(args.tar_path, args.log_path)
    emulator.run()

if __name__ == "__main__":
    main()
