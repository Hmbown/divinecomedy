#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "click",
# ]
# ///

from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import click
import json


class SpecialTokensMapEnum(Enum):
    BOS_TOKEN = "bos_token"
    EOS_TOKEN = "eos_token"
    PAD_TOKEN = "pad_token"
    UNK_TOKEN = "unk_token"



@dataclass(frozen=True)
class SpecialToken:
    id: int
    content: str
    lstrip: bool = False
    normalized: bool = False
    rstrip: bool = False
    single_word: bool = False
    special: bool = False
    special_token_map: list[SpecialTokensMapEnum] = field(default_factory=list)

    def to_added_tokens_decoder(self):
        data = asdict(self)
        token_id = str(data.pop("id"))
        data.pop("special_token_map")
        return {token_id: data}

    def to_added_tokens(self):
        data = asdict(self)
        data.pop("special_token_map")
        return data

    def to_special_tokens_map(self) -> dict[str, dict]:
        special_tokens_map = {}
        for special_token_map in self.special_token_map:
            data = asdict(self)
            data.pop("special_token_map")
            data.pop("special")
            data.pop("id")
            special_tokens_map[special_token_map.value] = data

        return special_tokens_map


MODEL_MAX_LENGTH = 65536

DESIRED_MAPPING = [
      SpecialToken(id=100256, content="<|extra_id_0|>"),
      SpecialToken(
        id=100257,
        content="<|endoftext|>",
        special=True,
        special_token_map=[
            SpecialTokensMapEnum.BOS_TOKEN,
            SpecialTokensMapEnum.EOS_TOKEN,
            SpecialTokensMapEnum.UNK_TOKEN,
        ]),
      SpecialToken(id=100258, content="<|fim_prefix|>", special=True),
      SpecialToken(id=100259, content="<|fim_middle|>", special=True),
      SpecialToken(id=100260, content="<|fim_suffix|>",special=True),
      SpecialToken(id=100261, content="|||PHONE_NUMBER|||"),
      SpecialToken(id=100262, content="|||EMAIL_ADDRESS|||"),
      SpecialToken(id=100263, content="|||IP_ADDRESS|||"),
      SpecialToken(id=100264, content="<|im_start|>", special=True),
      SpecialToken(id=100265, content="<|im_end|>", special=True),
      SpecialToken(id=100266, content="<|extra_id_1|>"),
      SpecialToken(id=100267, content="<|extra_id_2|>"),
      SpecialToken(id=100268, content="<|extra_id_3|>"),
      SpecialToken(id=100269, content="<|extra_id_4|>"),
      SpecialToken(id=100270, content="<|extra_id_5|>"),
      SpecialToken(id=100271, content="<|extra_id_6|>"),
      SpecialToken(id=100272, content="<|extra_id_7|>"),
      SpecialToken(id=100273, content="<|extra_id_8|>"),
      SpecialToken(id=100274, content="<|extra_id_9|>"),
      SpecialToken(id=100275, content="<|extra_id_10|>"),
      SpecialToken(id=100276, content="<|endofprompt|>", special=True),
      SpecialToken(
        id=100277,
        content="<|pad|>",
        special=True,
        special_token_map=[SpecialTokensMapEnum.PAD_TOKEN],
      ),
]

SCRIPT_DIR = Path(__file__).parent
TOKENIZER_CONFIG_FILE = SCRIPT_DIR / "tokenizer_config.json"
TOKENIZER_FILE = SCRIPT_DIR / "tokenizer.json"
VOCAB_FILE = SCRIPT_DIR / "vocab.json"
SPECIAL_TOKENS_MAP_FILE = SCRIPT_DIR / "special_tokens_map.json"



@click.group()
def cli():
    """Dataset processing tools."""
    pass



def _get_mapped_special_token(
    special_tokens: list[SpecialToken],
    mapped_token: SpecialTokensMapEnum
) -> SpecialToken:
    all_mapped_tokens = [token for token in special_tokens if mapped_token in token.special_token_map]
    if len(all_mapped_tokens) == 0:
        raise ValueError(f"Cannot find mapped token for {mapped_token}")
    if len(all_mapped_tokens) > 1:
        all_mapped_tokens_str = ", ".join([token.content for token in all_mapped_tokens])
        raise ValueError(f"Found multiple mapped tokens for {mapped_token}: {all_mapped_tokens_str}")
    return all_mapped_tokens[0]


def get_unk_token(special_tokens: list[SpecialToken]) -> SpecialToken:
    return _get_mapped_special_token(special_tokens, SpecialTokensMapEnum.UNK_TOKEN)


def get_bos_token(special_tokens: list[SpecialToken]) -> SpecialToken:
    return _get_mapped_special_token(special_tokens, SpecialTokensMapEnum.BOS_TOKEN)


def get_eos_token(special_tokens: list[SpecialToken]) -> SpecialToken:
    return _get_mapped_special_token(special_tokens, SpecialTokensMapEnum.EOS_TOKEN)


def get_pad_token(special_tokens: list[SpecialToken]) -> SpecialToken:
    return _get_mapped_special_token(special_tokens, SpecialTokensMapEnum.PAD_TOKEN)


@cli.command()
def check():
    """Check if the current config matches the desired mapping."""

    # STEP 1: Check the Tokenizer Config File #
    print("STEP 1: Checking tokenizer config file...")

    if not TOKENIZER_CONFIG_FILE.exists():
        raise FileNotFoundError(f"Tokenizer config file not found: {TOKENIZER_CONFIG_FILE}")

    with open(TOKENIZER_CONFIG_FILE, "r") as f:
        tokenizer_config = json.load(f)

    added_tokens_decoder = tokenizer_config.get("added_tokens_decoder", {})
    for token in DESIRED_MAPPING:
        str_token_id = str(token.id)
        if str_token_id not in added_tokens_decoder:
            raise ValueError(f"Token {token.id} not found in added tokens decoder")

        computed_added_tokens_decoder = token.to_added_tokens_decoder()
        if computed_added_tokens_decoder[str_token_id] != added_tokens_decoder[str_token_id]:
            raise ValueError(f"Token {token.id} has different content in added tokens decoder")

        print(f"Token {token.id} found in added tokens decoder; content matches")

    bos_token = get_bos_token(DESIRED_MAPPING)
    if bos_token.content != tokenizer_config["bos_token"]:
        raise ValueError(f"Bos token content mismatch: {bos_token.content} != {tokenizer_config['bos_token']}")
    else:
        print("Bos token content matches")

    eos_token = get_eos_token(DESIRED_MAPPING)
    if eos_token.content != tokenizer_config["eos_token"]:
        raise ValueError(f"Eos token content mismatch: {eos_token.content} != {tokenizer_config['eos_token']}")
    else:
        print("Eos token content matches")

    pad_token = get_pad_token(DESIRED_MAPPING)
    if pad_token.content != tokenizer_config["pad_token"]:
        raise ValueError(f"Pad token content mismatch: {pad_token.content} != {tokenizer_config['pad_token']}")
    else:
        print("Pad token content matches")

    unk_token = get_unk_token(DESIRED_MAPPING)
    if unk_token.content != tokenizer_config["unk_token"]:
        raise ValueError(f"Unk token content mismatch: {unk_token.content} != {tokenizer_config['unk_token']}")
    else:
        print("Unk token content matches")

    if tokenizer_config["model_max_length"] != MODEL_MAX_LENGTH:
        raise ValueError(f"Model max length mismatch: {tokenizer_config['model_max_length']} != {MODEL_MAX_LENGTH}")
    else:
        print("Model max length matches")


    # STEP 2: Check the Tokenizer File #
    print("STEP 2: Checking tokenizer file...")

    if not TOKENIZER_FILE.exists():
        raise FileNotFoundError(f"Tokenizer file not found: {TOKENIZER_FILE}")

    with open(TOKENIZER_FILE, "r") as f:
        tokenizer = json.load(f)

    # check if added_tokens matches
    added_tokens_dict = {token["id"]: token for token in tokenizer.get("added_tokens", [])}
    for token in DESIRED_MAPPING:
        if token.id not in added_tokens_dict:
            raise ValueError(f"Token {token.id} not found in added tokens")

        computed_added_token = token.to_added_tokens()
        if computed_added_token != added_tokens_dict[token.id]:
            raise ValueError(f"Token {token.id} has different content in added tokens")
        print(f"Token {token.id} found in added tokens; content matches.")

    # check vocab
    vocab = tokenizer.get("model", {}).get("vocab", {})
    for token in DESIRED_MAPPING:
        if token.content not in vocab:
            raise ValueError(f"Token `{token.content}` not found in vocab")
        if token.id != vocab[token.content]:
            raise ValueError(f"Token `{token.content}`: vocab=`{vocab[token.content]}` provided=`{token.id}`")
        print(f"Token `{token.content}` found in vocab; id `{token.id}` matches.")

    seen_values: dict[int, list[str]] = {}
    for key, value in vocab.items():
        seen_values.setdefault(value, []).append(key)

    broken_vocab = False
    for value, keys in seen_values.items():
        if len(keys) > 1:
            broken_vocab = True
            print(f"Vocab value {value} is not unique; keys: {keys}")

    if broken_vocab:
        raise ValueError("Vocab values are not unique")

    else:
        print("Vocab values are unique")

    # STEP 3: Check the Vocab File #
    print("STEP 3: Checking vocab file...")

    if not VOCAB_FILE.exists():
        raise FileNotFoundError(f"Vocab file not found: {VOCAB_FILE}")

    with open(VOCAB_FILE, "r") as f:
        vocab = json.load(f)

    for token in DESIRED_MAPPING:
        if token.content not in vocab:
            raise ValueError(f"Token `{token.content}` not found in vocab")
        if token.id != vocab[token.content]:
            raise ValueError(f"Token `{token.content}`: vocab=`{vocab[token.content]}` provided=`{token.id}`")
        print(f"Token `{token.content}` found in vocab; id `{token.id}` matches.")

    if len(set(vocab.values())) != len(vocab):
        raise ValueError("Vocab values are not unique")

    # STEP 4: Check the Special Tokens Map File #
    print("STEP 4: Checking special tokens map file...")

    if not SPECIAL_TOKENS_MAP_FILE.exists():
        raise FileNotFoundError(f"Special tokens map file not found: {SPECIAL_TOKENS_MAP_FILE}")

    with open(SPECIAL_TOKENS_MAP_FILE, "r") as f:
        special_tokens_map = json.load(f)

    # This checks the special tokens map file.
    seen_special_tokens = set()
    for token in DESIRED_MAPPING:
        for key, value in token.to_special_tokens_map().items():
            if key not in special_tokens_map:
                raise ValueError(f"Special token map {key} not found in special tokens map")
            if value != special_tokens_map[key]:
                raise ValueError(f"Special token map {key} content mismatch: {value} != {special_tokens_map[key]}")

            print(f"Special token map {key} content matches")
            seen_special_tokens.add(key)

    if len(seen_special_tokens) != len(special_tokens_map):
        raise ValueError("Special tokens map values are not unique")
    print("All special tokens map values match")


@cli.command()
def fix():
    """Fix the tokens in the tokenizer config, tokenizer file, vocab file, and special tokens map file."""

    print("STEP 1: Fixing tokenizer config file...")
    with open(TOKENIZER_CONFIG_FILE, "r") as f:
        tokenizer_config = json.load(f)

    tokenizer_config["bos_token"] = get_bos_token(DESIRED_MAPPING).content
    tokenizer_config["eos_token"] = get_eos_token(DESIRED_MAPPING).content
    tokenizer_config["pad_token"] = get_pad_token(DESIRED_MAPPING).content
    tokenizer_config["unk_token"] = get_unk_token(DESIRED_MAPPING).content
    tokenizer_config["model_max_length"] = MODEL_MAX_LENGTH

    added_tokens_decoder = {}
    for token in DESIRED_MAPPING:
        added_tokens_decoder.update(token.to_added_tokens_decoder())
    tokenizer_config["added_tokens_decoder"] = added_tokens_decoder

    with open(TOKENIZER_CONFIG_FILE, "w") as f:
        json.dump(tokenizer_config, f, indent=2)
    print(f"Updated tokenizer config file in {TOKENIZER_CONFIG_FILE}.")


    print("STEP 2: Fixing tokenizer file...")
    with open(TOKENIZER_FILE, "r") as f:
        tokenizer = json.load(f)
    added_tokens = []
    for token in DESIRED_MAPPING:
        added_tokens.append(token.to_added_tokens())
    tokenizer["added_tokens"] = added_tokens

    for token in DESIRED_MAPPING:
        # check if vocab id is used already
        for key in list(tokenizer["model"]["vocab"].keys()):
            if tokenizer["model"]["vocab"][key] == token.id:
                tokenizer["model"]["vocab"].pop(key)

        # now that we know this is safe, add the token
        tokenizer["model"]["vocab"][token.content] = token.id

    with open(TOKENIZER_FILE, "w") as f:
        json.dump(tokenizer, f, indent=2)

    print(f"Updated tokenizer file in {TOKENIZER_FILE}.")

    print("STEP 3: Fixing vocab file...")
    with open(VOCAB_FILE, "r") as f:
        vocab = json.load(f)
    for token in DESIRED_MAPPING:
        # check if vocab id is used already
        for key in list(vocab.keys()):
            if vocab[key] == token.id:
                vocab.pop(key)

        # now that we know this is safe, add the token
        vocab[token.content] = token.id
    with open(VOCAB_FILE, "w") as f:
        json.dump(vocab, f, indent=2)
    print(f"Updated vocab file in {VOCAB_FILE}.")

    print("STEP 4: Fixing special tokens map file...")
    with open(SPECIAL_TOKENS_MAP_FILE, "r") as f:
        special_tokens_map = json.load(f)

    for token in DESIRED_MAPPING:
        for key, value in token.to_special_tokens_map().items():
            special_tokens_map[key] = value
            print(f"Updated special token map {key} content")

    with open(SPECIAL_TOKENS_MAP_FILE, "w") as f:
        json.dump(special_tokens_map, f, indent=2)

    print(f"Updated special tokens map file in {SPECIAL_TOKENS_MAP_FILE}.")


if __name__ == "__main__":
    cli()
