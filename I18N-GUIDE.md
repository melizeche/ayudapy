# I18N Guide

## To add a new language

```
$ django-admin makemessages --ignore=env -l es
```

NOTE: `es` is the language locale. This generates  a new `.po` in the locale directory.

## To update all existing languages

```
$ django-admin makemessages --ignore=env -a
```

## To compile languages

```
$ django-admin compilemessages
```

NOTE: this generates binary `.mo` files for each `.po` file and these should not be included in the source code.

## Examples

### Templates

Short strings:
```
{% trans "Short string" %}
```

Long paragraphs:
```
{% blocktrans trimmed %}
This is a long paragraphs
with more than just one
lines.
{% endblocktrans %}
```

Long paragraphs with replacements:
```
{% blocktrans trimmed with icon="<i class=\"fas fa-map-marker-alt\"></i>" %}
This is a long paragraphs with an {{icon}}
tag but you DONT want it to be mixed with
the translation strings.
{% endblocktrans %}
```

### Python

```
from django.utils.translation import gettext as _

_("Use it like any other regular string")
```
