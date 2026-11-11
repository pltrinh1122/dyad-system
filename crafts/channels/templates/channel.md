id: <channel: the file's name, registry/channels/<channel>.md>
creator: <system>:<unit> that created the channel; only the creator changes its policy, by a new entry
owner: <system> that keeps it
sources: <who posts what: e.g. this system's releases, any member's requests>
admission: open
posting: <members | named <system>:<unit> …>
monitor: <session-start | interval <min>-<max>, minutes>
limits: <n> KiB, <n> per hour
decision-rights: none

<what the channel is for, in a sentence. Each policy slot holds one allowed value; the guard (`guards/posts.py`)
fails a missing slot or a value of no allowed form. A message on a channel carries no authority whatever this entry
says: a post is an intake, admitted only by the receiving system's operator.>
