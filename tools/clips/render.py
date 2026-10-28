import subprocess, sys
sys.path.insert(0, __import__('os').path.dirname(__file__))
from data import CLIPS
F = '/mnt/user-data/uploads/360.mp4'; O = '/home/claude/inc/out'; E = 1.4; AT = sys.argv[2] if len(sys.argv) > 2 else '1'
only = sys.argv[1].split(',') if len(sys.argv) > 1 and sys.argv[1] != 'all' else list(CLIPS)
for k in only:
    c = CLIPS[k]; ps = c['p']; D = sum(z - a for a, z in ps)
    inp = []
    for a, z in ps: inp += ['-ss', f'{a}', '-t', f'{z-a:.2f}', '-i', F]
    n = len(ps); ov, end = n, n + 1
    inp += ['-loop', '1', '-i', f'{O}/ov{k}.png', '-loop', '1', '-i', f'{O}/end.png']
    if n > 1:
        cc = ''.join(f'[{i}:v][{i}:a:{AT}]' for i in range(n)) + f'concat=n={n}:v=1:a=1[cv][ca];'
        V, A = '[cv]', '[ca]'
    else:
        cc = ''; V, A = '[0:v]', f'[0:a:{AT}]'
    # flash time relative to clip
    fl = ''
    if c['flash']:
        base = 0
        for a, z in ps:
            if a <= c['flash'] <= z: R = c['flash'] - a + base
            base += z - a
        fl = f",drawbox=x=0:y=0:w=iw:h=ih:color=0xC1121F@0.45:t=fill:enable='between(t,{R:.2f},{R+0.1:.2f})'"
    boost = ''
    if c.get('boost'):
        b0, b1 = c['boost']; r0 = b0 - ps[0][0]; r1 = b1 - ps[0][0]
        boost = f"volume=14dB:enable='between(t,{r0:.2f},{r1:.2f})',alimiter=limit=0.9,"
    fc = (cc + f"{V}fps=30,setsar=1,split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:3,eq=brightness={c.get('bgb',-0.32)}:saturation=0.6[bg];"
          f"[b]scale=1080:600,eq=saturation=0.8:contrast=1.06[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2-20[o1];"
          f"[o1][{ov}:v]overlay=0:0:shortest=1,subtitles={O}/sub{k}.ass:fontsdir=/home/claude/fontdl/ttf,noise=alls=6:allf=t{fl},"
          f"tpad=stop_mode=clone:stop_duration={E}[v2];"
          f"[{end}:v]format=rgba,fade=in:st=0:d=0.25:alpha=1,setpts=PTS+{D:.2f}/TB[endc];[v2][endc]overlay=0:0:enable='gte(t,{D:.2f})',format=yuv420p[v];"
          f"{A}{boost}afade=t=in:d=0.3,afade=t=out:st={D-0.5:.2f}:d=0.5,apad=pad_dur={E}[aout]")
    cmd = ['ffmpeg', '-v', 'error', '-y'] + inp + ['-filter_complex', fc, '-map', '[v]', '-map', '[aout]', '-t', f'{D+E:.2f}',
           '-c:v', 'libx264', '-crf', '22', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '160k',
           '-movflags', '+faststart', f'{O}/2026-11-02-incantation-{k}.mp4']
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(k, f'{D+E:.1f}s', 'OK' if r.returncode == 0 else r.stderr[-800:], flush=True)
