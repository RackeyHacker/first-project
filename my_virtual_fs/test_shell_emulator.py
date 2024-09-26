import unittest
from unittest.mock import patch, MagicMock
import os
import tarfile
import json
import io
from emulator import ShellEmulator

class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        """Создает временный tar-архив с тестовыми файлами и инициализирует эмулятор."""
        self.tar_path = 'test.tar'
        self.log_path = 'test_log.json'
        with tarfile.open(self.tar_path, 'w') as tar:
            tarinfo = tarfile.TarInfo(name="file1.txt")
            tarinfo.size = len("Hello, World!\n")
            tar.addfile(tarinfo, io.BytesIO(b"Hello, World!\n"))
            tarinfo = tarfile.TarInfo(name="dir1/")
            tarinfo.type = tarfile.DIRTYPE
            tar.addfile(tarinfo)
            tarinfo = tarfile.TarInfo(name="dir1/file2.txt")
            tarinfo.size = len("Content of file2.txt\n")
            tar.addfile(tarinfo, io.BytesIO(b"Content of file2.txt\n"))

        self.emulator = ShellEmulator(self.tar_path, self.log_path)

    def tearDown(self):
        """Удаляет временные файлы после завершения тестов."""
        os.remove(self.tar_path)
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    @patch('builtins.print')
    def test_ls_root(self, mock_print):
        """Тестирует команду 'ls' в корневом каталоге."""
        self.emulator.ls()
        mock_print.assert_called_once_with("file1.txt\ndir1")

    @patch('builtins.print')
    def test_ls_dir1(self, mock_print):
        """Тестирует команду 'ls' в подкаталоге 'dir1'."""
        self.emulator.cd('dir1')
        self.emulator.ls()
        mock_print.assert_called_once_with("file2.txt")

    @patch('builtins.print')
    def test_cd_root(self, mock_print):
        """Тестирует переход в корневой каталог из подкаталога."""
        self.emulator.cd('dir1')
        self.emulator.cd('/')
        self.assertEqual(self.emulator.current_dir, '/')

    @patch('builtins.print')
    def test_cd_dir1(self, mock_print):
        """Тестирует переход в подкаталог 'dir1' и проверяет текущий каталог."""
        self.emulator.cd('dir1')
        self.emulator.ls()
        self.assertEqual(self.emulator.current_dir, 'dir1/')

    @patch('builtins.print')
    def test_cd_parent(self, mock_print):
        """Тестирует переход на уровень вверх из подкаталога."""
        self.emulator.cd('dir1')
        self.emulator.cd('..')
        self.assertEqual(self.emulator.current_dir, '/')

    @patch('builtins.print')
    def test_cd_nonexistent(self, mock_print):
        """Тестирует обработку попытки перехода в несуществующий каталог."""
        self.emulator.cd('nonexistent')
        mock_print.assert_called_once_with("cd: no such file or directory: nonexistent")

    @patch('builtins.print')
    @patch('os.getlogin', return_value='testuser')
    def test_whoami(self, mock_getlogin, mock_print):
        """Тестирует команду 'whoami', которая возвращает имя пользователя."""
        self.emulator.whoami()
        mock_print.assert_called_once_with('testuser')

    @patch('builtins.print')
    def test_tac_file(self, mock_print):
        """Тестирует команду 'tac' для существующего файла."""
        self.emulator.tac(['file1.txt'])
        mock_print.assert_has_calls([
            unittest.mock.call("\n--- file1.txt ---\n"),
            unittest.mock.call("Hello, World!")
        ])

    @patch('builtins.print')
    def test_tac_directory(self, mock_print):
        """Тестирует обработку попытки использовать 'tac' для директории."""
        self.emulator.tac(['dir1'])
        mock_print.assert_called_once_with("Нельзя так делать: нельзя использовать tac для директории.")

    @patch('builtins.print')
    def test_tac_nonexistent(self, mock_print):
        """Тестирует обработку попытки использовать 'tac' для несуществующего файла."""
        self.emulator.tac(['nonexistent.txt'])
        mock_print.assert_called_once_with("tac: nonexistent.txt: No such file")

    @patch('builtins.print')
    @patch('sys.exit')

    def test_exit(self, mock_exit, mock_print):
        """Тестирует корректное завершение работы эмулятора."""
        self.emulator.exit()
        mock_print.assert_called_once_with("Exiting...")
        mock_exit.assert_called_once_with(0)

if __name__ == '__main__':
    unittest.main()
