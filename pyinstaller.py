import PyInstaller.__main__

# PyInstaller.__main__.run([
#     'app_post_factum.py',
#     '--hidden-import=nidaqmx',
#     '--noconfirm'
# ])

PyInstaller.__main__.run([
    'app_real_time.py',
    '--hidden-import=nidaqmx',
    '--noconfirm',
])
