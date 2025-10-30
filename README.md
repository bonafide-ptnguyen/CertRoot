# Moccasin Project

🐍 Welcome to your Moccasin project!

## command list

<!-- install uv -->

https://docs.astral.sh/uv/#installation

<!-- install dependency -->

uv venv
uv add vyper==0.4.3
uv add titanoboa
uv add pytest
uv tool install moccasin
uv sync

<!-- create moccasin project -->

mox init --vscode --pyproject

<!-- compile all contracts -->

mox compile

<!-- encrypt a private key -->

mox wallet import [account_name]
mox wallet list
mox wallet view [account_name]

<!-- using a key (specifying the key) -->

mox run deploy --network anvil --account anvil1

<!-- using a key (default account set in moccasin.toml) -->

mox run deploy --network anvil

<!-- run all test -->

mox test

<!-- run specific test -->

mox test -k [test_name e.g. test_can_add_people]

## Quickstart

1. Deploy to a fake local network that titanoboa automatically spins up!

```bash
mox run deploy
```

2. Run tests

```
mox test
```

_For documentation, please run `mox --help` or visit [the Moccasin documentation](https://cyfrin.github.io/moccasin)_
