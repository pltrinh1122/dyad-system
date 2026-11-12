# channels craft manifest (Rule-11 property 2: `requires:`)

`key: value` lines (`dyadlib.parse_kv`), read by the craft guard (`dyad/guards/craft/crafts.py`) and by
`dyad craft install`. `requires:` names the minimum version of another craft this one depends on; `dyad craft
install` refuses an unmet requirement.

`dyad-operator>=1.2.0`: the core whose runner runs a craft's run-book as `<craft>:<name>`, whose provenance guard
holds the credential shapes the fence refuses (`FAIL_SHAPES`), whose inbox guard holds the disposition shape
(`DISPOSITION`), and whose `dyad/scripts/privatecite.py` reads the instance's private list by hash; `posts.py` imports
each (`dyadlib.load_guard`, `dyadlib.load_module`) rather than restating it. The craft requires the core only.

No `seeds:`. The templates describe records of the channels repository, which is no instance path of this system.

name: channels
requires: dyad-operator>=1.2.0
