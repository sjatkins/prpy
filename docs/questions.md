# Rooms
## exits oddity
Some times they are of form to {direction, room_label}.
Other times tehy are of form 
to (num, num)
  keywords {str*}  
What does the second form mean?  For instance Room #9 in 
Midgard.room file. 
## bad room files FIXED
### PlainsPharsica.room
Had two "#offset " lines.
### ThaumloreFortress.room
Extra closing brace at ~#1554
# Mobs

It looks like it should be trivial to pull block structure from these files
using same Block code as for Rooms.  This also seems to be the case for Objects.
