# RealTime_PAAO

## Install Instructions

1. Download [Python 3.10](https://www.python.org/downloads/)

2. Install Python and check this checkbox
![link!](/install_instructions/0_add_to_path.png)

3. Download and unzip repository or use git clone
![link!](/install_instructions/1_github_download.png)

4. In files `RealTime_PAAO\app_post_factum.py` and `RealTime_PAAO\app_real_time.py` change 2nd line's path to `"path\\to\\project\\RealTime_PAAO"`

5. Open cmd and run commands

```bash
py -m pip install --upgrade pip
py -m pip install -r path/to/project/requirements.txt
```

6. For real time approximation [NI-DAQmx software](https://www.ni.com/en-us/support/downloads/drivers/download.ni-daqmx.html#445931) must be installed

7. Run project by running one of these commands in cmd

For post factum approximation : `py path/to/project/RealTime_PAOO/app_post_factum.py`
For real time approximation : `py path/to/project/RealTime_PAOO/app_real_time.py`
