---
title: "PyCharm on Ubunutu"
tags:
	- guides
	- python
status: draft

---

http://www.webupd8.org/2011/10/things-to-tweak-after-installing-ubuntu.html
http://theaccidentalcoder.com/content/swapping-openjdk-sun-jdk-ubuntu

    sudo add-apt-repository ppa:ferramroberto/java
    sudo apt-get update
    sudo apt-get install sun-java6-jdk sun-java6-jre sun-java6-plugin
    sudo update-alternatives --config java

select the newly available Sun/Oracle version

now type `java -version` and you should see something like:

    java version "1.6.0_26"
    Java(TM) SE Runtime Environment (build 1.6.0_26-b03)
    Java HotSpot(TM) Client VM (build 20.1-b02, mixed mode, sharing)
