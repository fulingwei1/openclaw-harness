# {name}

{description}

## 标准流程

{% for step in steps %}
{{ loop.index }}. {{ step }}
{% endfor %}

{% if checkpoints %}

## 检查点

{% for checkpoint in checkpoints %}
- [ ] {{ checkpoint }}
{% endfor %}

{% endif %}

{% if examples %}

## 成功案例

{% for example in examples %}
- {{ example }}
{% endfor %}

{% endif %}

{% if tags %}

## 标签

{{ tags | join(', ') }}

{% endif %}

---

- 源任务: {{ source_task_id }}
- 创建时间: {{ created_at }}
