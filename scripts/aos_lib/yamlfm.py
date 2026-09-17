from __future__ import annotations

import json
import re
from datetime import date
from typing import Any

_DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
_INT_RE = re.compile(r"^-?\d+$")
_FLOAT_RE = re.compile(r"^-?\d+\.\d+$")


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines(keepends=True)
    end = None
    for i, line in enumerate(lines[1:], start=1):
        if line.rstrip("\r\n") == "---":
            end = i
            break
    if end is None:
        return {}, text
    fm_text = "".join(lines[1:end])
    body = "".join(lines[end + 1 :])
    return parse_yaml(fm_text), body


def join_frontmatter(data: dict[str, Any], body: str) -> str:
    dumped = dump_yaml(data)
    text = f"---\n{dumped}---\n"
    if body and not body.startswith("\n"):
        text += "\n"
    text += body
    if not text.endswith("\n"):
        text += "\n"
    return text


def parse_yaml(text: str) -> dict[str, Any]:
    lines = text.replace("\t", "  ").splitlines()
    data, _ = _parse_mapping(lines, 0, 0)
    return data


def dump_yaml(data: dict[str, Any], indent: int = 0) -> str:
    return "".join(line + "\n" for line in _dump_mapping(data, indent))


def _parse_mapping(lines: list[str], i: int, indent: int) -> tuple[dict[str, Any], int]:
    result: dict[str, Any] = {}
    n = len(lines)
    while i < n:
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        cur = _indent_of(raw)
        if cur < indent:
            break
        if cur > indent:
            raise ValueError(f"unexpected indent at line {i + 1}: {raw!r}")
        stripped = raw.strip()
        if stripped.startswith("- "):
            raise ValueError(f"list item in mapping at line {i + 1}")
        if ":" not in stripped:
            raise ValueError(f"expected key: at line {i + 1}: {raw!r}")
        key, _, rest = stripped.partition(":")
        key = key.strip()
        rest = rest.strip()
        if rest.startswith("#"):
            rest = ""
        elif " #" in rest:
            rest = _strip_comment(rest)
        if rest == "":
            value, i = _parse_nested(lines, i + 1, indent)
            result[key] = value
        else:
            result[key] = parse_scalar(rest)
            i += 1
    return result, i


def _parse_nested(lines: list[str], i: int, parent_indent: int) -> tuple[Any, int]:
    n = len(lines)
    while i < n and (not lines[i].strip() or lines[i].lstrip().startswith("#")):
        i += 1
    if i >= n:
        return None, i
    cur = _indent_of(lines[i])
    if cur < parent_indent:
        return None, i
    if lines[i].lstrip().startswith("- "):
        if cur == parent_indent or cur > parent_indent:
            return _parse_list(lines, i, cur)
    if cur <= parent_indent:
        return None, i
    return _parse_mapping(lines, i, cur)


def _parse_list(lines: list[str], i: int, indent: int) -> tuple[list[Any], int]:
    items: list[Any] = []
    n = len(lines)
    while i < n:
        raw = lines[i]
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        cur = _indent_of(raw)
        if cur < indent:
            break
        stripped = raw.strip()
        if not stripped.startswith("- "):
            break
        rest = stripped[2:].strip()
        if rest.startswith("#"):
            items.append(None)
            i += 1
            continue
        if rest == "" or rest == ":":
            value, i = _parse_nested(lines, i + 1, indent)
            items.append(value)
            continue
        if rest.startswith("{") or (":" in rest and not rest.startswith("[")):
            # inline mapping not required; treat as scalar if no nested
            if rest.endswith(":") or rest == ":":
                value, i = _parse_nested(lines, i + 1, indent)
                items.append(value)
                continue
        items.append(parse_scalar(_strip_comment(rest)))
        i += 1
    return items, i


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _strip_comment(value: str) -> str:
    in_single = False
    in_double = False
    for i, ch in enumerate(value):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            if i == 0 or value[i - 1].isspace():
                return value[:i].rstrip()
    return value.rstrip()


def parse_scalar(token: str) -> Any:
    token = token.strip()
    if token in ("null", "~", "Null", "NULL"):
        return None
    if token in ("true", "True", "TRUE", "yes", "Yes"):
        return True
    if token in ("false", "False", "FALSE", "no", "No"):
        return False
    if token == "[]":
        return []
    if token == "{}":
        return {}
    if token.startswith("[") and token.endswith("]"):
        return _parse_inline_list(token[1:-1])
    if (token.startswith('"') and token.endswith('"')) or (
        token.startswith("'") and token.endswith("'")
    ):
        return _unquote(token)
    m = _DATE_RE.match(token)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    if _INT_RE.match(token):
        return int(token)
    if _FLOAT_RE.match(token):
        return float(token)
    return token


def _parse_inline_list(inner: str) -> list[Any]:
    inner = inner.strip()
    if not inner:
        return []
    items: list[Any] = []
    buf: list[str] = []
    in_single = False
    in_double = False
    for ch in inner:
        if ch == "'" and not in_double:
            in_single = not in_single
            buf.append(ch)
        elif ch == '"' and not in_single:
            in_double = not in_double
            buf.append(ch)
        elif ch == "," and not in_single and not in_double:
            items.append(parse_scalar("".join(buf).strip()))
            buf = []
        else:
            buf.append(ch)
    if buf or items:
        leftover = "".join(buf).strip()
        if leftover:
            items.append(parse_scalar(leftover))
    return items


def _unquote(token: str) -> str:
    if token.startswith('"'):
        return json.loads(token)
    return token[1:-1].replace("''", "'")


def _dump_mapping(data: dict[str, Any], indent: int) -> list[str]:
    pad = " " * indent
    lines: list[str] = []
    for key, value in data.items():
        lines.extend(_dump_key(pad, key, value, indent))
    return lines


def _dump_key(pad: str, key: str, value: Any, indent: int) -> list[str]:
    if isinstance(value, dict):
        if not value:
            return [f"{pad}{key}: {{}}"]
        out = [f"{pad}{key}:"]
        out.extend(_dump_mapping(value, indent + 2))
        return out
    if isinstance(value, list):
        if not value:
            return [f"{pad}{key}: []"]
        if all(not isinstance(x, (dict, list)) for x in value) and _use_inline_list(
            value
        ):
            inner = ", ".join(format_scalar(x) for x in value)
            return [f"{pad}{key}: [{inner}]"]
        out = [f"{pad}{key}:"]
        item_pad = pad + "  "
        for item in value:
            if isinstance(item, dict):
                first = True
                for k, v in item.items():
                    dumped = _dump_key(item_pad, k, v, indent + 2)
                    if first:
                        dumped[0] = item_pad[:-2] + "  - " + dumped[0][len(item_pad) :]
                        first = False
                        out.extend(dumped)
                    else:
                        out.extend(dumped)
            elif isinstance(item, list):
                out.append(f"{item_pad}- {format_scalar(item)}")
            else:
                out.append(f"{item_pad}- {format_scalar(item)}")
        return out
    return [f"{pad}{key}: {format_scalar(value)}"]


def _use_inline_list(value: list[Any]) -> bool:
    if len(value) > 12:
        return False
    return all(not isinstance(x, (dict, list)) for x in value)


def format_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    s = str(value)
    if s == "" or s.lower() in {"null", "true", "false", "~", "yes", "no"}:
        return json.dumps(s, ensure_ascii=False)
    if _DATE_RE.match(s) or _INT_RE.match(s) or _FLOAT_RE.match(s):
        return json.dumps(s, ensure_ascii=False)
    if s != s.strip() or any(c in s for c in ":#[]{}&*!|>%@`'\"\n"):
        return json.dumps(s, ensure_ascii=False)
    return s


def as_date(value: Any) -> date | None:
    if value is None or value == "":
        return None
    if isinstance(value, date):
        return date(value.year, value.month, value.day)
    if isinstance(value, str):
        value = value.strip()
        if not value or value.lower() == "null":
            return None
        return date.fromisoformat(value)
    raise TypeError(f"not a date: {value!r}")


def as_date_list(value: Any) -> list[date]:
    if not value:
        return []
    if not isinstance(value, list):
        raise TypeError(f"expected list, got {type(value)}")
    out: list[date] = []
    for item in value:
        d = as_date(item)
        if d is not None:
            out.append(d)
    return out
