# This file is part of the Trezor project.
#
# Copyright (C) 2012-2019 SatoshiLabs and contributors
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the License along with this library.
# If not, see <https://www.gnu.org/licenses/lgpl-3.0.html>.

import pytest

from trezorlib import cardano, messages
from trezorlib.cardano import NETWORK_IDS, PROTOCOL_MAGICS
from trezorlib.exceptions import TrezorFailure


class InputAction:
    """
    Test cases don't use the same input flows. These constants are used to define
    the expected input flows for each test case. Corresponding input actions
    are then executed on the device to simulate user inputs.
    """

    SWIPE = 0
    YES = 1


SAMPLE_INPUTS = {
    "byron_input": {
        "path": "m/44'/1815'/0'/0/1",
        "prev_hash": "1af8fa0b754ff99253d983894e63a2b09cbb56c833ba18c3384210163f63dcfc",
        "prev_index": 0,
    },
    "byron_input_different_path": {
        "path": "m/44'/1815'/0'/0/5",
        "prev_hash": "a34dc95d806a3b206aab5e0c2aaa5ff0704f84868fe65793053f6ae9a7970979",
        "prev_index": 0,
    },
    "shelley_input": {
        "path": "m/1852'/1815'/0'/0/0",
        "prev_hash": "3b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b7",
        "prev_index": 0,
    },
    "shelley_input_different_path": {
        "path": "m/1852'/1815'/0'/0/5",
        "prev_hash": "33ad5e2a8f298053da804c30c9f72836bfac0a58a30aef2ff87656418b01f70b",
        "prev_index": 0,
    },
}

SAMPLE_OUTPUTS = {
    "simple_byron_output": {
        "address": "Ae2tdPwUPEZCanmBz5g2GEwFqKTKpNJcGYPKfDxoNeKZ8bRHr8366kseiK2",
        "amount": "3003112",
    },
    "byron_change_output": {
        "addressType": 8,
        "path": "m/44'/1815'/0'/0/1",
        "amount": "1000000",
    },
    "simple_shelley_output": {
        "address": "addr1q84sh2j72ux0l03fxndjnhctdg7hcppsaejafsa84vh7lwgmcs5wgus8qt4atk45lvt4xfxpjtwfhdmvchdf2m3u3hlsd5tq5r",
        "amount": "1",
    },
    "base_address_with_script_output": {
        "address": "addr1z90z7zqwhya6mpk5q929ur897g3pp9kkgalpreny8y304r2dcrtx0sf3dluyu4erzr3xtmdnzvcyfzekkuteu2xagx0qeva0pr",
        "amount": "7120787",
    },
    "base_address_change_output": {
        "addressType": 0,
        "path": "m/1852'/1815'/0'/0/0",
        "stakingPath": "m/1852'/1815'/0'/2/0",
        "amount": "7120787",
    },
    "staking_key_hash_output": {
        "addressType": 0,
        "path": "m/1852'/1815'/0'/0/0",
        "stakingKeyHash": "32c728d3861e164cab28cb8f006448139c8f1740ffb8e7aa9e5232dc",
        "amount": "7120787",
    },
    "pointer_address_output": {
        "addressType": 4,
        "path": "m/1852'/1815'/0'/0/0",
        "blockIndex": 1,
        "txIndex": 2,
        "certificateIndex": 3,
        "amount": "7120787",
    },
    "enterprise_address_output": {
        "addressType": 6,
        "path": "m/1852'/1815'/0'/0/0",
        "amount": "7120787",
    },
    "invalid_address": {
        "address": "jsK75PTH2esX8k4Wvxenyz83LJJWToBbVmGrWUer2CHFHanLseh7r3sW5X5q",
        "amount": "3003112",
    },
    "invalid_cbor": {
        "address": "5dnY6xgRcNUSLGa4gfqef2jGAMHb7koQs9EXErXLNC1LiMPUnhn8joXhvEJpWQtN3F4ysATcBvCn5tABgL3e4hPWapPHmcK5GJMSEaET5JafgAGwSrznzL1Mqa",
        "amount": "3003112",
    },
    "invalid_crc": {
        "address": "Ae2tdPwUPEZ5YUb8sM3eS8JqKgrRLzhiu71crfuH2MFtqaYr5ACNRZR3Mbm",
        "amount": "3003112",
    },
    "invalid_address_too_short": {
        "address": "addr1q89s8py7y68e3x66sscs0wkhlg5ssfrfs65084jry45scvehcr",
        "amount": "3003112",
    },
    "invalid_address_too_long": {
        "address": "addr1q89s8py7y68e3x66sscs0wkhlg5ssfrfs65084jrlrqcfqqj922xhxkn6twlq2wn4q50q352annk3903tj00h45mgfm5z3vcwsfrvkr5zglq4rxu",
        "amount": "3003112",
    },
    "large_simple_byron_output": {
        "address": "Ae2tdPwUPEZCanmBz5g2GEwFqKTKpNJcGYPKfDxoNeKZ8bRHr8366kseiK2",
        "amount": "449999999199999999",
    },
    # address type 10
    "unsupported_address_type": {
        "address": "addr1590z7zqwhya6mpk5q929ur897g3pp9kkgalpreny8y304r2dcrtx0sf3dluyu4erzr3xtmdnzvcyfzekkuteu2xagx0qt7gvvj",
        "amount": "3003112",
    },
    "testnet_output": {
        "address": "2657WMsDfac7BteXkJq5Jzdog4h47fPbkwUM49isuWbYAr2cFRHa3rURP236h9PBe",
        "amount": "3003112",
    },
    "shelley_testnet_output": {
        "address": "addr_test1vr9s8py7y68e3x66sscs0wkhlg5ssfrfs65084jrlrqcfqqtmut0e",
        "amount": "1",
    },
}

SAMPLE_CERTIFICATES = {
    "stake_registration": {"type": 0, "path": "m/1852'/1815'/0'/2/0"},
    "stake_deregistration": {"type": 1, "path": "m/1852'/1815'/0'/2/0"},
    "stake_delegation": {
        "type": 2,
        "path": "m/1852'/1815'/0'/2/0",
        "pool": "f61c42cbf7c8c53af3f520508212ad3e72f674f957fe23ff0acb4973",
    },
    "invalid_non_staking_path": {"type": 0, "path": "m/1852'/1815'/0'/0/0"},
    "invalid_pool_size": {
        "type": 2,
        "path": "m/1852'/1815'/0'/2/0",
        "pool": "f61c42cbf7c8c53af3f520508212ad3e72",
    },
}

SAMPLE_WITHDRAWALS = {
    "valid": {"path": "m/1852'/1815'/0'/2/0", "amount": "1000"},
    "invalid_non_staking_path": {"path": "m/1852'/1815'/0'/0/0", "amount": "1000"},
    "invalid_amount_too_large": {
        "path": "m/1852'/1815'/0'/2/0",
        "amount": "449999999199999999",
    },
}

VALID_VECTORS = [
    # Mainnet transaction without change
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["byron_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_byron_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # input flow
        [[InputAction.SWIPE, InputAction.YES], [InputAction.SWIPE, InputAction.YES]],
        # tx hash
        "73e09bdebf98a9e0f17f86a2d11e0f14f4f8dae77cdf26ff1678e821f20c8db6",
        # serialized tx
        "83a400818258201af8fa0b754ff99253d983894e63a2b09cbb56c833ba18c3384210163f63dcfc00018182582b82d818582183581c9e1c71de652ec8b85fec296f0685ca3988781c94a2e1a5d89d92f45fa0001a0d0c25611a002dd2e802182a030aa1028184582089053545a6c254b0d9b1464e48d2b5fcf91d4e25c128afb1fcfc61d0843338ea5840da07ac5246e3f20ebd1276476a4ae34a019dd4b264ffc22eea3c28cb0f1a6bb1c7764adeecf56bcb0bc6196fd1dbe080f3a7ef5b49f56980fe5b2881a4fdfa00582026308151516f3b0e02bb1638142747863c520273ce9bd3e5cd91e1d46fe2a63541a0f6",
    ),
    # Mainnet transaction with change
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["byron_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_byron_output"], SAMPLE_OUTPUTS["byron_change_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # input flow
        [
            [InputAction.SWIPE, InputAction.YES],
            [InputAction.YES],
            [InputAction.SWIPE, InputAction.YES],
        ],
        # tx hash
        "81b14b7e62972127eb33c0b1198de6430540ad3a98eec621a3194f2baac43a43",
        # serialized tx
        "83a400818258201af8fa0b754ff99253d983894e63a2b09cbb56c833ba18c3384210163f63dcfc00018282582b82d818582183581c9e1c71de652ec8b85fec296f0685ca3988781c94a2e1a5d89d92f45fa0001a0d0c25611a002dd2e882582b82d818582183581cda4da43db3fca93695e71dab839e72271204d28b9d964d306b8800a8a0001a7a6916a51a000f424002182a030aa1028184582089053545a6c254b0d9b1464e48d2b5fcf91d4e25c128afb1fcfc61d0843338ea5840d909b16038c4fd772a177038242e6793be39c735430b03ee924ed18026bd28d06920b5846247945f1204276e4b759aa5ac05a4a73b49ce705ab0e5e54a3a170e582026308151516f3b0e02bb1638142747863c520273ce9bd3e5cd91e1d46fe2a63541a0f6",
    ),
    # simple transaction with base address change output
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [
            SAMPLE_OUTPUTS["simple_shelley_output"],
            SAMPLE_OUTPUTS["base_address_change_output"],
        ],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # input flow
        [[InputAction.SWIPE, InputAction.YES], [InputAction.SWIPE, InputAction.YES]],
        # tx hash
        "16fe72bb198be423677577e6326f1f648ec5fc11263b072006382d8125a6edda",
        # tx body
        "83a400818258203b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b700018282583901eb0baa5e570cffbe2934db29df0b6a3d7c0430ee65d4c3a7ab2fefb91bc428e4720702ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff018258390180f9e2c88e6c817008f3a812ed889b4a4da8e0bd103f86e7335422aa122a946b9ad3d2ddf029d3a828f0468aece76895f15c9efbd69b42771a006ca79302182a030aa100818258205d010cf16fdeff40955633d6c565f3844a288a24967cf6b76acbeb271b4f13c158406a78f07836dcf4a303448d2b16b217265a9226be3984a69a04dba5d04f4dbb2a47b5e1cbb345f474c0b9634a2f37b921ab26e6a65d5dfd015dacb4455fb8430af6",
    ),
    # Mainnet transaction with multiple inputs
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [
            SAMPLE_INPUTS["byron_input"],
            SAMPLE_INPUTS["byron_input_different_path"],
            SAMPLE_INPUTS["shelley_input"],
            SAMPLE_INPUTS["shelley_input_different_path"],
        ],
        # outputs
        [SAMPLE_OUTPUTS["simple_byron_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # input flow
        [[InputAction.SWIPE, InputAction.YES], [InputAction.SWIPE, InputAction.YES]],
        # tx hash
        "7e16a0b47bdfc37abf4ddd3143f7481af07ffe7abd68f752676f5b0b2890d05b",
        # serialized tx
        "83a400848258201af8fa0b754ff99253d983894e63a2b09cbb56c833ba18c3384210163f63dcfc00825820a34dc95d806a3b206aab5e0c2aaa5ff0704f84868fe65793053f6ae9a7970979008258203b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b70082582033ad5e2a8f298053da804c30c9f72836bfac0a58a30aef2ff87656418b01f70b00018182582b82d818582183581c9e1c71de652ec8b85fec296f0685ca3988781c94a2e1a5d89d92f45fa0001a0d0c25611a002dd2e802182a030aa20082825820e246aa6392958f01fc8fafd5ac1cf5f28ef34af05820b49c98919753a76109c05840517ca4c901a9cded7b4ab3b1d576f41b28a05aed9ed96ef86a78556099aaa5e996a38c74783262d807d86d48c131b1cb91cbab4ef4b6b52dc8d49708b0f40d068258205d010cf16fdeff40955633d6c565f3844a288a24967cf6b76acbeb271b4f13c15840e661d9d1002bc2f8b310e0b0541f9bb9c3357e8e6e7f772ca72fdfd4dfc27f9ae040197d4ef69c98dc16a105f00c7ff2cebf2d85920307606bff087e550b470d028284582089053545a6c254b0d9b1464e48d2b5fcf91d4e25c128afb1fcfc61d0843338ea5840ca7325ac3280708a12a70f794699243fa1c2a3e3981dccd7e5a1200f521e19fad52489c9be81e8a8ccaccd3c42d917ffd1719e6808e11fbcd1ef495f7324b10b582026308151516f3b0e02bb1638142747863c520273ce9bd3e5cd91e1d46fe2a63541a084582040ed7b4134e85866f55ec896a8a81e9d41c20969af8f88c532e5ad1f9c9425ab5840e11444cf81b94754a15e244259d983cc3099ff04a8212dde814d6e0a9cb7e4423caa440cdee9e2d663b59e5005dbfeee8057765245b96711f1ff20caf8cfb3025820ec19de133d3c5a598212a3b8ad9249453c4ca10e0b9228714700eeaed944590941a0f6",
    ),
    # simple transaction with base script address change output
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [
            SAMPLE_OUTPUTS["base_address_with_script_output"],
            SAMPLE_OUTPUTS["base_address_change_output"],
        ],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # input flow
        [[InputAction.SWIPE, InputAction.YES], [InputAction.SWIPE, InputAction.YES]],
        # tx hash
        "5ddbb530b8a89e2b08fc91db03950c876c4a9c1c3fb6e628c4cab638b1c97648",
        # tx body
        "83a400818258203b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b7000182825839115e2f080eb93bad86d401545e0ce5f2221096d6477e11e6643922fa8d4dc0d667c1316ff84e572310e265edb31330448b36b7179e28dd419e1a006ca7938258390180f9e2c88e6c817008f3a812ed889b4a4da8e0bd103f86e7335422aa122a946b9ad3d2ddf029d3a828f0468aece76895f15c9efbd69b42771a006ca79302182a030aa100818258205d010cf16fdeff40955633d6c565f3844a288a24967cf6b76acbeb271b4f13c15840e0bdaa59016f2a521d31179b60364eacdcb53c34ae01c56b339afa62d312f5f89783579691cac777e3d5f2e7810aa8fe554ba545a8d1578c55405af5ae51b30ff6",
    ),
    # simple transaction with base address change output with staking key hash
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [
            SAMPLE_OUTPUTS["simple_shelley_output"],
            SAMPLE_OUTPUTS["staking_key_hash_output"],
        ],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # input flow
        [
            [InputAction.SWIPE, InputAction.YES],
            [InputAction.SWIPE, InputAction.YES],
            [InputAction.SWIPE, InputAction.YES],
        ],
        # tx hash
        "d1610bb89bece22ed3158738bc1fbb31c6af0685053e2993361e3380f49afad9",
        # tx body
        "83a400818258203b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b700018282583901eb0baa5e570cffbe2934db29df0b6a3d7c0430ee65d4c3a7ab2fefb91bc428e4720702ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff018258390180f9e2c88e6c817008f3a812ed889b4a4da8e0bd103f86e7335422aa32c728d3861e164cab28cb8f006448139c8f1740ffb8e7aa9e5232dc1a006ca79302182a030aa100818258205d010cf16fdeff40955633d6c565f3844a288a24967cf6b76acbeb271b4f13c15840622f22d03bc9651ddc5eb2f5dc709ac4240a64d2b78c70355dd62106543c407d56e8134c4df7884ba67c8a1b5c706fc021df5c4d0ff37385c30572e73c727d00f6",
    ),
    # simple transaction with pointer address change output
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [
            SAMPLE_OUTPUTS["simple_shelley_output"],
            SAMPLE_OUTPUTS["pointer_address_output"],
        ],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # input flow
        [
            [InputAction.SWIPE, InputAction.YES],
            [InputAction.SWIPE, InputAction.YES],
            [InputAction.SWIPE, InputAction.YES],
        ],
        # tx hash
        "40535fa8f88515f1da008d3cdf544cf9dbf1675c3cb0adb13b74b9293f1b7096",
        # tx body
        "83a400818258203b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b700018282583901eb0baa5e570cffbe2934db29df0b6a3d7c0430ee65d4c3a7ab2fefb91bc428e4720702ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff018258204180f9e2c88e6c817008f3a812ed889b4a4da8e0bd103f86e7335422aa0102031a006ca79302182a030aa100818258205d010cf16fdeff40955633d6c565f3844a288a24967cf6b76acbeb271b4f13c15840dbbf050cc13d0696b1884113613318a275e6f0f8c7cb3e7828c4f2f3c158b2622a5d65ea247f1eed758a0f6242a52060c319d6f37c8460f5d14be24456cd0b08f6",
    ),
    # simple transaction with enterprise address change output
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [
            SAMPLE_OUTPUTS["simple_shelley_output"],
            SAMPLE_OUTPUTS["enterprise_address_output"],
        ],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # input flow
        [
            [InputAction.SWIPE, InputAction.YES],
            [InputAction.YES],
            [InputAction.SWIPE, InputAction.YES],
        ],
        # tx hash
        "d3570557b197604109481a80aeb66cd2cfabc57f802ad593bacc12eb658e5d72",
        # tx body
        "83a400818258203b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b700018282583901eb0baa5e570cffbe2934db29df0b6a3d7c0430ee65d4c3a7ab2fefb91bc428e4720702ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff0182581d6180f9e2c88e6c817008f3a812ed889b4a4da8e0bd103f86e7335422aa1a006ca79302182a030aa100818258205d010cf16fdeff40955633d6c565f3844a288a24967cf6b76acbeb271b4f13c15840c5996650c438c4493b2c8a94229621bb9b151b8d61d75fb868c305e917031e9a1654f35023f7dbf5d1839ab9d57b153c7f79c2666af51ecf363780397956e00af6",
    ),
    # transaction with stake registration certificate
    (
        # network id
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_shelley_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [SAMPLE_CERTIFICATES["stake_registration"]],
        # withdrawals
        [],
        # metadata
        "",
        # input flow
        [
            [InputAction.SWIPE, InputAction.YES],
            [InputAction.YES],
            [InputAction.SWIPE, InputAction.YES],
        ],
        # tx hash
        "1a3a295908afd8b2afc368071272d6964be6ee0af062bb765aea65ca454dc0c9",
        # tx body
        "83a500818258203b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b700018182583901eb0baa5e570cffbe2934db29df0b6a3d7c0430ee65d4c3a7ab2fefb91bc428e4720702ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff0102182a030a048182008200581c122a946b9ad3d2ddf029d3a828f0468aece76895f15c9efbd69b4277a100818258205d010cf16fdeff40955633d6c565f3844a288a24967cf6b76acbeb271b4f13c15840a938b16bd81aea8d3aaf11e4d460dad1f36d34bf34ad066d0f5ce5d4137654145d998c3482aa823ff1acf021c6e2cd2774fff00361cbb9e72b98632307ee4000f6",
    ),
    # transaction with stake registration and stake delegation certificates
    (
        # network id
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_shelley_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [
            SAMPLE_CERTIFICATES["stake_registration"],
            SAMPLE_CERTIFICATES["stake_delegation"],
        ],
        # withdrawals
        [],
        # metadata
        "",
        # input flow
        [
            [InputAction.SWIPE, InputAction.YES],
            [InputAction.YES],
            [InputAction.SWIPE, InputAction.YES],
            [InputAction.SWIPE, InputAction.YES],
        ],
        # tx hash
        "439764b5f7e08839881536a3191faeaf111e75d9f00f83b102c5c1c6fa9fcaf9",
        # tx body
        "83a500818258203b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b700018182583901eb0baa5e570cffbe2934db29df0b6a3d7c0430ee65d4c3a7ab2fefb91bc428e4720702ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff0102182a030a048282008200581c122a946b9ad3d2ddf029d3a828f0468aece76895f15c9efbd69b427783028200581c122a946b9ad3d2ddf029d3a828f0468aece76895f15c9efbd69b4277581cf61c42cbf7c8c53af3f520508212ad3e72f674f957fe23ff0acb4973a10082825820bc65be1b0b9d7531778a1317c2aa6de936963c3f9ac7d5ee9e9eda25e0c97c5e58400dbdf36f92bc5199526ffb8b83b33a9eeda0ed3e46fb4025a104346801afb9cf45fa1a5482e54c769f4102e67af46205457d7ae05a889fc342acb0cdc23ecd038258205d010cf16fdeff40955633d6c565f3844a288a24967cf6b76acbeb271b4f13c158405ebe8eff752f07e8448f55304fdf3665ac68162099dcacd81886b73affe67fb6df401f8a5fa60ddb6d5fb65b93235e6a234182a40c001e3cf7634f82afd5fe0af6",
    ),
    # transaction with stake deregistration
    (
        # network id
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_shelley_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [SAMPLE_CERTIFICATES["stake_deregistration"]],
        # withdrawals
        [],
        # metadata
        "",
        # input flow
        [
            [InputAction.SWIPE, InputAction.YES],
            [InputAction.YES],
            [InputAction.SWIPE, InputAction.YES],
        ],
        # tx hash
        "3aca1784d151dc75bdbb80fae71bda3f4b26af3f5fd71bd5e9e9bbcdd2b64ad1",
        # tx body
        "83a500818258203b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b700018182583901eb0baa5e570cffbe2934db29df0b6a3d7c0430ee65d4c3a7ab2fefb91bc428e4720702ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff0102182a030a048182018200581c122a946b9ad3d2ddf029d3a828f0468aece76895f15c9efbd69b4277a10082825820bc65be1b0b9d7531778a1317c2aa6de936963c3f9ac7d5ee9e9eda25e0c97c5e584084f321d313da67f80f7fab2e4f3996d3dbe3186659e6f98315e372dbe88c55d56f637ccc7534890c3601ddd31ba885dc86ba0074c230869f20099b7dd5eeaf008258205d010cf16fdeff40955633d6c565f3844a288a24967cf6b76acbeb271b4f13c15840e563a8012e16affd801564e8410ca7b2c96f76f8ecb878e35c098a823c40be7f59dc12cb44a9b678210d4e8f18ab215133eef7ca9ece94b4683d3db0fd37e105f6",
    ),
    # transaction with stake deregistration and withdrawal
    (
        # network id
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_shelley_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [SAMPLE_CERTIFICATES["stake_deregistration"]],
        # withdrawals
        [SAMPLE_WITHDRAWALS["valid"]],
        # metadata
        "",
        # input flow
        [
            [InputAction.SWIPE, InputAction.YES],
            [InputAction.YES],
            [InputAction.YES],
            [InputAction.SWIPE, InputAction.YES],
        ],
        # tx hash
        "22c67f12e6f6aa0f2f09fd27d472b19c7208ccd7c3af4b09604fd5d462c1de2b",
        # tx body
        "83a600818258203b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b700018182583901eb0baa5e570cffbe2934db29df0b6a3d7c0430ee65d4c3a7ab2fefb91bc428e4720702ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff0102182a030a048182018200581c122a946b9ad3d2ddf029d3a828f0468aece76895f15c9efbd69b427705a1581de1122a946b9ad3d2ddf029d3a828f0468aece76895f15c9efbd69b42771903e8a10082825820bc65be1b0b9d7531778a1317c2aa6de936963c3f9ac7d5ee9e9eda25e0c97c5e58400202826a8b9688cf978000e7d1591582c65b149bb9f55dc883ae1acf85432618ca32be8a06fef37e69df503a294e7093006f63ababf9fcea639390226934020a8258205d010cf16fdeff40955633d6c565f3844a288a24967cf6b76acbeb271b4f13c158407efa634e42fa844cad5f60bf005d645817cc674f30eaab0da398b99034850780b40ab5a1028da033330a0f82b01648ec92cff8ca85a072594efb298016f38d0df6",
    ),
    # transaction with metadata
    (
        # network id
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_shelley_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "a200a11864a118c843aa00ff01a119012c590100aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        # input flow
        [[InputAction.SWIPE, InputAction.YES], [InputAction.SWIPE, InputAction.YES]],
        # tx hash
        "1875f1d59a53f1cb4c43949867d72bcfd857fa3b64feb88f41b78ddaa1a21cbf",
        # tx body
        "83a500818258203b40265111d8bb3c3c608d95b3a0bf83461ace32d79336579a1939b3aad1c0b700018182583901eb0baa5e570cffbe2934db29df0b6a3d7c0430ee65d4c3a7ab2fefb91bc428e4720702ebd5dab4fb175324c192dc9bb76cc5da956e3c8dff0102182a030a075820ea4c91860dd5ec5449f8f985d227946ff39086b17f10b5afb93d12ee87050b6aa100818258205d010cf16fdeff40955633d6c565f3844a288a24967cf6b76acbeb271b4f13c15840b2015772a91043aeb04b98111744a098afdade0db5e30206538d7f2814965a5800d45240137f4d0dc81845a71e67cda38beaf816a520d73c4decbf7cbf0f6d08a200a11864a118c843aa00ff01a119012c590100aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    ),
    # Testnet transaction
    (
        # protocol magic
        PROTOCOL_MAGICS["testnet"],
        # network id
        NETWORK_IDS["testnet"],
        # inputs
        [SAMPLE_INPUTS["byron_input"]],
        # outputs
        [
            SAMPLE_OUTPUTS["testnet_output"],
            SAMPLE_OUTPUTS["shelley_testnet_output"],
            SAMPLE_OUTPUTS["byron_change_output"],
        ],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # input flow
        [
            [InputAction.SWIPE, InputAction.YES],
            [InputAction.SWIPE, InputAction.YES],
            [InputAction.YES],
            [InputAction.SWIPE, InputAction.YES],
        ],
        # tx hash
        "47cf79f20c6c62edb4162b3b232a57afc1bd0b57c7fd8389555276408a004776",
        # serialized tx
        "83a400818258201af8fa0b754ff99253d983894e63a2b09cbb56c833ba18c3384210163f63dcfc00018382582f82d818582583581cc817d85b524e3d073795819a25cdbb84cff6aa2bbb3a081980d248cba10242182a001a0fb6fc611a002dd2e882581d60cb03849e268f989b5a843107bad7fa2908246986a8f3d643f8c184800182582f82d818582583581c98c3a558f39d1d993cc8770e8825c70a6d0f5a9eb243501c4526c29da10242182a001aa8566c011a000f424002182a030aa1028184582089053545a6c254b0d9b1464e48d2b5fcf91d4e25c128afb1fcfc61d0843338ea5840cc11adf81cb3c3b75a438325f8577666f5cbb4d5d6b73fa6dbbcf5ab36897df34eecacdb54c3bc3ce7fc594ebb2c7aa4db4700f4290facad9b611a035af8710a582026308151516f3b0e02bb1638142747863c520273ce9bd3e5cd91e1d46fe2a63545a10242182af6",
    ),
]

INVALID_VECTORS = [
    # Output address is a valid CBOR but invalid Cardano address
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["byron_input"]],
        # outputs
        [SAMPLE_OUTPUTS["invalid_address"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # error message
        "Invalid address",
    ),
    # Output address is invalid CBOR
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["byron_input"]],
        # outputs
        [SAMPLE_OUTPUTS["invalid_cbor"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # error message
        "Invalid address",
    ),
    # Output address has invalid CRC
    (
        # protocol magic (mainnet)
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["byron_input"]],
        # outputs
        [SAMPLE_OUTPUTS["invalid_crc"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # error message
        "Invalid address",
    ),
    # Output address is too short
    (
        # protocol magic (mainnet)
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["invalid_address_too_short"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # error message
        "Invalid address",
    ),
    # Output address is too long
    (
        # protocol magic (mainnet)
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["invalid_address_too_long"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # error message
        "Invalid address",
    ),
    # Fee is too high
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["byron_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_byron_output"]],
        # fee
        45000000000000001,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # error message
        "Fee is out of range!",
    ),
    # Output total is too high
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["byron_input"]],
        # outputs
        [
            SAMPLE_OUTPUTS["large_simple_byron_output"],
            SAMPLE_OUTPUTS["byron_change_output"],
        ],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # error message
        "Total transaction amount is out of range!",
    ),
    # Mainnet transaction with testnet output
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["byron_input"]],
        # outputs
        [SAMPLE_OUTPUTS["testnet_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # error message
        "Output address network mismatch!",
    ),
    # Testnet transaction with mainnet output
    (
        # protocol magic
        PROTOCOL_MAGICS["testnet"],
        # network id
        NETWORK_IDS["testnet"],
        # inputs
        [SAMPLE_INPUTS["byron_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_byron_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # error message
        "Output address network mismatch!",
    ),
    # Shelley mainnet transaction with testnet output
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["shelley_testnet_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # error message
        "Invalid address",
    ),
    # Shelley testnet transaction with mainnet output
    (
        # protocol magic
        PROTOCOL_MAGICS["testnet"],
        # network id
        NETWORK_IDS["testnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_shelley_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # error message
        "Invalid address",
    ),
    # Testnet protocol magic with mainnet network id
    (
        # protocol magic
        PROTOCOL_MAGICS["testnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_shelley_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # error message
        "Invalid network id/protocol magic combination!",
    ),
    # Mainnet protocol magic with testnet network id
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["testnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_byron_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "",
        # error message
        "Invalid network id/protocol magic combination!",
    ),
    # Unsupported address type
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["unsupported_address_type"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata hash
        "",
        # error message
        "Invalid address",
    ),
    # Certificate has non staking path
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_byron_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [SAMPLE_CERTIFICATES["invalid_non_staking_path"]],
        # withdrawals
        [],
        # metadata
        "",
        # error message
        "Invalid certificate",
    ),
    # Certificate has invalid pool size
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_byron_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [SAMPLE_CERTIFICATES["invalid_pool_size"]],
        # withdrawals
        [],
        # metadata
        "",
        # error message
        "Invalid certificate",
    ),
    # Withdrawal has non staking path
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_byron_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [SAMPLE_WITHDRAWALS["invalid_non_staking_path"]],
        # metadata
        "",
        # error message
        "Invalid withdrawal",
    ),
    # Withdrawal amount is too large
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_byron_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [SAMPLE_WITHDRAWALS["invalid_amount_too_large"]],
        # metadata
        "",
        # error message
        "Invalid withdrawal",
    ),
    # Metadata too large
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_byron_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "a200a11864a118c843aa00ff01a119012c590202aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        # error message
        "Invalid metadata",
    ),
    # Metadata is a list
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_byron_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "82a200a11864a118c843aa00ff01a119012c590100aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa0A",
        # error message
        "Invalid metadata",
    ),
    # Metadata is incomplete
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_byron_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "a200a11864a118c843aa00ff01",
        # error message
        "Invalid metadata",
    ),
    # Metadata has leftover data
    (
        # protocol magic
        PROTOCOL_MAGICS["mainnet"],
        # network id
        NETWORK_IDS["mainnet"],
        # inputs
        [SAMPLE_INPUTS["shelley_input"]],
        # outputs
        [SAMPLE_OUTPUTS["simple_byron_output"]],
        # fee
        42,
        # ttl
        10,
        # certificates
        [],
        # withdrawals
        [],
        # metadata
        "a200a11864a118c843aa00ff01a119012c590100aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa000000",
        # error message
        "Invalid metadata",
    ),
]


@pytest.mark.altcoin
@pytest.mark.cardano
@pytest.mark.skip_t1  # T1 support is not planned
@pytest.mark.parametrize(
    "protocol_magic,network_id,inputs,outputs,fee,ttl,certificates,withdrawals,metadata,input_flow_sequences,tx_hash,serialized_tx",
    VALID_VECTORS,
)
def test_cardano_sign_tx(
    client,
    protocol_magic,
    network_id,
    inputs,
    outputs,
    fee,
    ttl,
    certificates,
    withdrawals,
    metadata,
    input_flow_sequences,
    tx_hash,
    serialized_tx,
):
    inputs = [cardano.create_input(i) for i in inputs]
    outputs = [cardano.create_output(o) for o in outputs]
    certificates = [cardano.create_certificate(c) for c in certificates]
    withdrawals = [cardano.create_withdrawal(w) for w in withdrawals]

    expected_responses = [
        messages.ButtonRequest(code=messages.ButtonRequestType.Other)
        for i in range(len(input_flow_sequences))
    ]
    expected_responses.append(messages.CardanoSignedTx())

    def input_flow():
        for sequence in input_flow_sequences:
            yield
            for action in sequence:
                if action == InputAction.SWIPE:
                    client.debug.swipe_up()
                elif action == InputAction.YES:
                    client.debug.press_yes()
                else:
                    raise ValueError("Invalid input action")

    with client:
        client.set_expected_responses(expected_responses)
        client.set_input_flow(input_flow)
        response = cardano.sign_tx(
            client=client,
            inputs=inputs,
            outputs=outputs,
            fee=fee,
            ttl=ttl,
            certificates=certificates,
            withdrawals=withdrawals,
            metadata=bytes.fromhex(metadata),
            protocol_magic=protocol_magic,
            network_id=network_id,
        )
        assert response.tx_hash.hex() == tx_hash
        assert response.serialized_tx.hex() == serialized_tx


@pytest.mark.altcoin
@pytest.mark.cardano
@pytest.mark.skip_t1  # T1 support is not planned
@pytest.mark.parametrize(
    "protocol_magic,network_id,inputs,outputs,fee,ttl,certificates,withdrawals,metadata,expected_error_message",
    INVALID_VECTORS,
)
def test_cardano_sign_tx_validation(
    client,
    protocol_magic,
    network_id,
    inputs,
    outputs,
    fee,
    ttl,
    certificates,
    withdrawals,
    metadata,
    expected_error_message,
):
    inputs = [cardano.create_input(i) for i in inputs]
    outputs = [cardano.create_output(o) for o in outputs]
    certificates = [cardano.create_certificate(c) for c in certificates]
    withdrawals = [cardano.create_withdrawal(w) for w in withdrawals]

    expected_responses = [messages.Failure()]

    with client:
        client.set_expected_responses(expected_responses)

        with pytest.raises(TrezorFailure, match=expected_error_message):
            cardano.sign_tx(
                client=client,
                inputs=inputs,
                outputs=outputs,
                fee=fee,
                ttl=ttl,
                certificates=certificates,
                withdrawals=withdrawals,
                metadata=bytes.fromhex(metadata),
                protocol_magic=protocol_magic,
                network_id=network_id,
            )
