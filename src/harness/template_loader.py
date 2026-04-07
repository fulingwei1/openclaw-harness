from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from jinja2 import ChoiceLoader, DictLoader, Environment, FileSystemLoader


DEFAULT_TEMPLATES = {
    "golden_rules.md": """# {{ title }}

{{ description }}

{% if rules %}
{% for rule in rules -%}
- {{ rule }}
{% endfor %}
{% else %}
- Add rules with `harness add-rule "<rule>"`.
{% endif %}
""",
    "skill_template.md": """# {{ name }}

## Description
{{ description }}

## Triggers
{% if triggers %}
{% for trigger in triggers -%}
- {{ trigger }}
{% endfor %}
{% else %}
- Trigger patterns will be refined from future runs.
{% endif %}

## Steps
{% if steps %}
{% for step in steps -%}
{{ loop.index }}. {{ step }}
{% endfor %}
{% else %}
1. Review the task context.
2. Execute the core workflow.
3. Evaluate the result before finishing.
{% endif %}

## Checkpoints
{% if checkpoints %}
{% for checkpoint in checkpoints -%}
- {{ checkpoint }}
{% endfor %}
{% else %}
- Confirm the output satisfies the task.
{% endif %}

## Examples
{% if examples %}
{% for example in examples -%}
- {{ example }}
{% endfor %}
{% else %}
- No examples captured yet.
{% endif %}
""",
}


def _template_dirs() -> list[Path]:
    configured = os.getenv("HARNESS_TEMPLATE_DIR")
    candidates = [
        Path(configured) if configured else None,
        Path.cwd() / "templates",
        Path(__file__).resolve().parents[2] / "templates",
    ]
    return [path for path in candidates if path and path.exists()]


@lru_cache(maxsize=1)
def build_template_environment() -> Environment:
    loaders = [FileSystemLoader([str(path) for path in _template_dirs()])]
    loaders.append(DictLoader(DEFAULT_TEMPLATES))
    return Environment(
        loader=ChoiceLoader(loaders),
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
