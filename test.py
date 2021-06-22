import unittest
import os
import random
import string
import shutil
from main import YaDisk, YaDiskException

os.environ['YANDEX_TOKEN'] = 'AQAAAAAiInFGAAcnrrMWM26pAU06kf9ELT3P3-I'
TOKEN = os.environ['YANDEX_TOKEN']


class TestYaDisk(unittest.TestCase):
    disk = None
    remote_folder = None
    remote_path = None
    remote_file = None

    @classmethod
    def setUpClass(cls):
        cls.disk = YaDisk(TOKEN)
        for item in os.listdir('.'):
            if os.path.isfile(item):
                cls.remote_file = item
                break
        cls.remote_folder = f"/TestYaDisk_{''.join(random.choice(string.ascii_uppercase) for _ in range(6))}"
        cls.remote_path = f"{cls.remote_folder}/{cls.remote_file}"

    def test_00main(self):
        def mkdir(remote_folder):
            self.disk.make_direction(remote_folder)

            try:
                self.disk.make_direction(
                    '{folder}/dir/bad'.format(folder=remote_folder))
            except YaDiskException as e:
                self.assertEqual(e.code, 409)

            try:
                self.disk.make_direction(remote_folder)
            except YaDiskException as e:
                self.assertEqual(e.code, 409)

        mkdir(self.remote_folder)
        tmp_local_file = f"{self.remote_file}~"

        self.disk.upload(self.remote_file, self.remote_path)

        self.assertRaises(YaDiskException, self.disk.ls, 'fake_folder')
        ls = self.disk.ls(self.remote_folder)
        self.assertEqual(len(ls), 1)
        self.assertEqual(ls, ['disk:' + self.remote_path])

        self.disk.download(self.remote_path, tmp_local_file)

        pref = self.disk.ls()
        self.disk.remove(self.remote_folder)
        post = self.disk.ls()
        self.assertEqual(len(pref), len(post) + 1)
        pref.remove('disk:' + self.remote_folder)
        self.assertEqual(pref, post)
        self.assertRaises(YaDiskException, self.disk.remove, self.remote_folder)
        self.assertRaises(YaDiskException, self.disk.download, self.remote_path, tmp_local_file)

        os.remove(tmp_local_file)

    def test_upload_direction(self):
        names = ['\\'+''.join(random.choice(string.ascii_uppercase) for _ in range(6)) for _ in range(3)]
        path = f"{''.join(names)}"
        path = '.' + path
        os.makedirs(path)
        self.disk.upload_dir(os.path.abspath(path.split('\\')[1]))
        shutil.rmtree(os.path.abspath(path.split('\\')[1]))
        self.assertEqual(self.disk.ls('/'+names[0][1:]), [f'disk:/{names[0][1:]}/{names[1][1:]}'])
        self.assertEqual(self.disk.ls(f'/{names[0][1:]}/{names[1][1:]}'), [f'disk:/{names[0][1:]}/{names[1][1:]}/{names[2][1:]}'])
        self.disk.remove('/'+names[0][1:])

    def test_bad_auth(self):
        try:
            YaDisk(None)
        except YaDiskException as exception:
            self.assertTrue(str(exception).startswith(str(exception.code)))


if __name__ == '__main__':
    unittest.main()
