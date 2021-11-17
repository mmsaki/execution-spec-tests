"""
Common values used in Ethereum tests.
"""

from ethereum.frontier.eth_types import Address, Root
from ethereum.utils.hexadecimal import hex_to_bytes

TestPrivateKey = (
    "0x45a915e4d060149eb4365960e6a7a45f334393093061116b197e3240065ff2d8"
)
TestAddress = "0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b"

AddrAA = "0x00000000000000000000000000000000000000aa"
AddrBB = "0x00000000000000000000000000000000000000bb"

EmptyTrieRoot = Root(
    hex_to_bytes(
        "0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421"  # noqa: E501
    )
)
