Open the file, it uses the selenium library. It spams login with random stuff and reloads the browser to reload the page.
This is purely for educational purposes and should not be used on the real website, even though the code suggests it it is meant for purely local application.
If you need the website locally you can use a programm like WinHTTrack. (or use the zip file provided)
Proxies: If you're on version 0.7 and up you have the option to use proxies, these must be in a file called proxies.txt in the same directory as the file. The script doesn't support authing via a username and password so please enable ip authentification at your provider. The proxies should be in the format http://ip:port 1 per line.

TO-DO:
-    Change to packet based logins. 
    someone go make this and open a pull request idk if its really worth it, or if it'll be consistent
- [x]   Add proxy support (maybe even rotating once one gets blocked)(just looked through the process of adding paid proxies, and that might take a while as its a pain in the ass to auth)


Since I genuinly don't rlly know what else to add since the website is down for another while, if you want something that isnt added currently just open an issue feature request and tell me. If I have some free time I'll probably add it


### Setup

1. Install [Python3](https://www.python.org/) via one of their [Download](https://www.python.org/downloads/).

2. Clone the repository into a directory of your choice.

```bash
git clone https://github.com/helmhotzgang/fillhakunamatata.git
```

3. Enter the new directory and install packages.

```bash
cd fillhakunamatata
pip install -r requirements.txt
```

4. If you want to use proxies for the project create a proxies.txt file in the directory and put one proxy per line in the format 

```bash
http://ip:port
```

5. Then just start the script

```bash
hakuna.py
```

6. If you have proxies it will automatically pick them up, it will ask you for the amount of threads you want to run (same number as browser instances), it is not recommended to have this set above 25.

 ### More info on Proxies

  If you have added 1 or multiple proxies is will never use your own IP-Adress, if you have multiple proxies it will dynamically switch when they start failing and with 1 it will just use that.
