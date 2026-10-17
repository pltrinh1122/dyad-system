"""ledgerd: a daemon that keeps a queryable projection of a ledger current (the core craft's server
component, `dyad/server/ledgerd/`; d-work #336). "Ledger" here is the general sense: any store of
records a schema module can load; the vocabulary's own ledger (the d-work row store) is the first
schema, `schemas/dwork.py`. Three seams: a store adapter (`store.py`), a ledger schema (`schema.py`)
and a supervisor adapter (`supervisor.py`); the daemon (`core.py`) knows none of what a d-work is."""
__version__ = "0.1.0"
