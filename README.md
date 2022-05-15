Solutions to ZZAZZ April fools challenges (https://zzazzdzz.github.io/fools2022/)

Also contains code for my JOYBUS "bridge" that allowed a real GBA to connect to
the event server, as seen in this video: https://www.youtube.com/watch?v=tJX78p5oMk0

(See the folder at "2022/teensy-joybus", specifically "teensy\_server.py" and
"teensy.ino")

The joybus bridge was designed to work only on a Teensy LC (could be adjusted
for other hardware but the timings would need to be adjusted).

In theory the joybus bridge could connect a real GBA to the Dolphin emulator but
latency issues make this fairly impractical. Maybe if someone tried it with
a real serial port (with lower latency than the teensy's emulated one) they
would have more luck with it?
