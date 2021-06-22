import click
from main import YaDisk
import requests
import os

client_id = "16d12faa3bde4e31830bf05fecc00e7a"
client_secret = "b7a8d9b4a22648c682c0e60e2289355d"


@click.group()
def cli():
    if not os.path.isfile('token.txt'):
        init()


def init():
    click.echo(f"https://oauth.yandex.ru/authorize?response_type=code"
               f"&client_id={client_id}")
    code = input()
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret
    }
    url = f"https://oauth.yandex.ru/token"
    resp = requests.post(url, data=data)
    token = open("token.txt", 'w+')
    token.write(resp.json()['access_token'])
    click.echo('success')


@cli.command()
@click.argument("path", default='/')
def ls(path):
    with open('token.txt', 'r') as token:
        disk = YaDisk(token.read())
        print(*disk.ls(path), sep="\n")


@cli.command()
@click.argument("path")
@click.argument("file")
def download(path, file):
    with open('token.txt', 'r') as token:
        disk = YaDisk(token.read())
        disk.download(path, file)
        click.echo('success')


@cli.command()
@click.argument("path")
@click.argument("file")
@click.option("--zip", "--z", "is_zip", is_flag=True, default=False)
def upload(path, file, is_zip=False):
    with open('token.txt', 'r') as token:
        disk = YaDisk(token.read())
        if is_zip:
            disk.upload_zip(path, file)
        else:
            disk.upload(file, path)
        click.echo('success')


@cli.command()
@click.argument("path")
def rm(path):
    with open('token.txt', 'r') as token:
        disk = YaDisk(token.read())
        disk.remove(path)
        click.echo('success')


@cli.command()
def clr():
    os.remove('token.txt')


if __name__ == "__main__":
    cli()
