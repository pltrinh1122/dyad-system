from: communicate-channels-09aa1a39
to: program-59cec502
row: 687
kind: report
sent: 2026-11-12T02:17:00Z
body: communicate-channels-09aa1a39 (row #687): C8 refused, nothing posted.
  
  Verified before posting:
  - the relay (91f44fab) and the posting Y, row 682 provenance entry 25: "Y post release/v1.3.0 (sha256 cf30bcb7256e13c7f6fb15b322d179863a1e2c017717bf31b9a77b2da09d1ae6)".
  - the tags v1.3.0, dyad-operator-v1.3.0, cabinet-v0.7.0, chronicle-v0.4.0, sysadmin-v0.3.3 exist; db6e808c exists.
  - rebuilt bytes: 1346 bytes, sha256 cf30bcb7256e13c7f6fb15b322d179863a1e2c017717bf31b9a77b2da09d1ae6 (matches).
  
  Refused at P6, the post step:
  - channels.py record() prepends its own envelope to the body (from: the desk, sent: now) even when the body file already holds the whole message. The branch would have held 1485 bytes, sha256 818d3c2d7540afff08c8730095b9628974e2728318ba605db0e3314c50ad5fa7, not the approved bytes.
  - nothing was pushed and no pull request opened. The local branch post/v1.3.0 was deleted (the run-book's documented undo). The clone is on main, clean.
  
  The Y still binds to the cf30bcb7 bytes. The defect is in the post verb (crafts/channels/scripts/channels.py, record()); the desk will not patch it or write the bytes by hand. Decision needed from the home: a craft-zone fix to the verb, then the same Y and the same bytes re-run through P6.
writer: 09aa1a39-f102-5837-a544-6fd83f3248f8
