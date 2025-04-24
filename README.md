## Short Explanation
The file uses the Selenium Library to open the page and login, when you start it it will ask for how many threads aka. browser instances to open. Please keep in mind there's a 0.3s delay between opening them in the code, which can be changed by just looking for a bit. Opening too many instances WILL crash your PC. Have fun!
#### Funny Business
I got some inside info that nobody that the person that would be responsible for changing the website and fix this vulnerability is not going to do that in the near future (even though they got hints from us) so we can have fun. The Project is most likely going to start at the same time that it usually would again so be ready, we as a community decided to give people between 5 and 15 Minutes after it started before we start bombarding it. Please be civil.

TO-DO:
-    Change to packet based logins. 
    someone go make this and open a pull request idk if its really worth it, or if it'll be consistent
- [x]   Add proxy support (maybe even rotating once one gets blocked)(just looked through the process of adding paid proxies, and that might take a while as its a pain in the ass to auth)


Since I genuinly don't rlly know what else to add since the website is down for another while, if you want something that isnt added currently just open an issue feature request and tell me. If I have some free time I'll probably add it


## Setup

1. Install [Python3](https://www.python.org/) via their [Download](https://www.python.org/downloads/).

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

 ## More info on Proxies

  If you have added 1 or multiple proxies is will never use your own IP-Adress, if you have multiple proxies it will dynamically switch when they start failing and with 1 it will just use that.

 ### Info on Paid Proxies

 If you try using better paid private proxies that require authentication using a password and and username that won't work with the script since chrome webdriver doesn't support also giving username and password as an option but just literally port and ip. If you still need to (which I really recommend since free proxies are terrible) then try out [Webshare](https://www.webshare.io/). They don't have the cheapest proxies but you can definitely get some good datacenter ones, then just change the authentication method from Username/Password to Ip Authentication and add your own IP.

 # Info on Packet Based Code

 The file called packet_hakuna.py does basically the same stuff the first file does just much faster much more efficient and much more stupid. If you know what youre doing you can also find 1 course figure out its course id and just keep filling that one otherwise the code should do it all for you. Also different to the hakuna.py it doesnt get its names from the name list (which worked fine for me) since on some PC's I tried it on that just refused to work, instead it uses the Faker library to generate german names.