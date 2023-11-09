import os
import subprocess

import requests
import typer
from tqdm import tqdm


def download(url, save_path, pool):
    r = requests.get(url)

    if r.status_code != 200:
        typer.echo("m3u8视频下载链接无效")
        return False

    m3u8_list = r.text.split('\n')
    m3u8_list = [i for i in m3u8_list if i and i[0] != '#']

    ts_list = []
    for ts_url in m3u8_list:
        ts_url = url.rsplit('/', 1)[0] + '/' + ts_url
        ts_list.append(ts_url)

    with tqdm(total=len(ts_list)) as prog:
        with open(save_path, 'wb') as f:
            for ts_url in ts_list:
                r = requests.get(ts_url)
                if r.status_code == 200:
                    f.write(r.content)
                    prog.update(1)
                else:
                    typer.echo("下载片段失败")
                    return False
    return True


def convert_to_mp4(ts_file_path, mp4_file_path):
    ex = subprocess.run(
        ['ffmpeg', '-i', ts_file_path, '-c', 'copy', mp4_file_path],
        capture_output=True,
        shell=True
    )
    os.remove(ts_file_path)


def main(file_name: str,
         download_url: str,
         output_dir: str = '',
         pool: bool = False
         ):
    cwd = os.getcwd()
    if output_dir == '':
        output_dir = f'{cwd}/download'
    else:
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

    ts_file_path = f'{output_dir}/{file_name}.ts'
    mp4_file_path = f'{output_dir}/{file_name}.mp4'

    typer.echo("开始下载")
    if not download(download_url, ts_file_path, pool):
        typer.echo("下载失败")
        return
    typer.echo("下载完成")
    typer.echo("开始转码")
    convert_to_mp4(ts_file_path, mp4_file_path)
    typer.echo("转码成功")
    typer.echo(f'文件地址:{mp4_file_path}')


if __name__ == '__main__':
    typer.run(main)
