"""Evidence catalogs for the USB/FPGA device static-learning package.

Each catalog module exposes an ``ENTRIES`` list. Every entry is a plain dict
with the required keys: identifier, layer, module, description, status,
boundary, evidence.
"""


def make_entry(identifier, layer, module, description, status, boundary, evidence):
    """Build a single ledger entry with the required schema.

    status is one of: E1 (frozen static evidence), candidate (anchor exists but
    behaviour not proven), unknown (boundary declared, not reversed).
    """
    return {
        "identifier": identifier,
        "layer": layer,
        "module": module,
        "description": description,
        "status": status,
        "boundary": boundary,
        "evidence": evidence,
    }
