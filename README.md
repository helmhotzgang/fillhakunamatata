## Short Explanation
The file uses the Selenium Library to open the page and login, when you start it it will ask for how many threads aka. browser instances to open. Please keep in mind there's a 0.3s delay between opening them in the code, which can be changed by just looking for a bit. Opening too many instances WILL crash your PC. Have fun!
Nowadays use packe_hakuna.py its much better

# Does it actually work
Through some testing we have found out that all of the code works (hakuna.py will only work when the site is up). As of writing this it also works when the site is down.
We can guarantee that as of right now course_registration.py definitely works as it also sends verification emails, packet_hakuna.py also works as we can check if the courses are filling up [hm.helmholtzschule.de/script/register-user.php](hm.helmholtzschule.de/script/register-user.php)
#### Funny Business
I got some inside info that nobody that the person that would be responsible for changing the website and fix this vulnerability is not going to do that in the near future (even though they got hints from us) so we can have fun. The Project is most likely going to start at the same time that it usually would again so be ready, we as a community decided to give people between 5 and 15 Minutes after it started before we start bombarding it. Please be civil. (since packet_hakuna.py also works before the projects start I can only recommend not filling all courses before 6 PM on whatever day it starts.)
Now that we also know that the code works right now, I personally can't stop you from just infinitely creating courses till their storage is full.


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
 -After like 1 minute of trying and using my brain, its also way less strenuous on your hardware 1000 threads can easily run but at that point you might limit the website while 100 is perfectly fine.
 Please keep in mind this script is not done and doesnt do a pull for open courses yet which isnt possible since the webpage is down. I was able to code this part of the local download I had of the page.

 # Course Registration script

 The file called course_registration.py is a new addition I made, it uses a different php backend to, instead of logging into courses, actually register courses with names, description, teacher wishes, room wishes etc. For this you will need a teachers.txt and students.txt file with names in it, I originally uploaded those too but they are no longer on the github, since im not sure if i can share them, for some reason mainly the bigger payloads this script is much slower than the original but still works perfectly. (As of writing this there is no check if you should be able to register courses at the moment on the backend so you can just fill up their servers) Please keep in mind that if you use a real students list (wherever you got that) the script is good enough to send actual verify emails to people in the list since it uses the correct email format and all other data.