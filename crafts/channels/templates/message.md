format: dyad-channels/1
id: <id: 1-80 of A-Z a-z 0-9 . _ -, the file's name>
channel: <channel: the directory the file sits in>
kind: <fact | proposal | reported-disposition | question | reply>
from: <system>:<unit>
sent: <YYYY-MM-DDTHH:MM:SSZ, UTC>
holder: <optional: the session that wrote it, recorded and never an identity>
in-reply-to: <optional: the id of the message this answers>
refs: <optional: commits or sha256s, space-separated>

<the body: plain text, after one blank line. Canonical message format `dyad-channels/1`, defined upstream by the
channels craft (d-work #682): the six fields above the optional ones are required, the three optional ones are named,
and any other `key: value` line is kept and never refused. A record lives at `channels/<channel>/<system>/<id>.md` of
the channels repository, so each system writes only under its own path; once landed it is never edited or deleted.
A message reports a disposition as a fact and never asks for or gives one.>
