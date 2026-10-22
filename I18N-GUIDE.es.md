# Guía de I18N

[English version](I18N-GUIDE.md)

## Para agregar un nuevo idioma

```
$ django-admin makemessages --ignore=env -l es
```

NOTA: `es` es el código del idioma (locale). Esto genera un nuevo archivo `.po` en el directorio `locale`.

## Para actualizar todos los idiomas existentes

```
$ django-admin makemessages --ignore=env -a
```

## Para compilar los idiomas

```
$ django-admin compilemessages
```

NOTA: esto genera archivos binarios `.mo` para cada archivo `.po`, y estos no deben incluirse en el código fuente.

## Ejemplos

### Templates

Textos cortos:
```
{% trans "Texto corto" %}
```

Párrafos largos:
```
{% blocktrans trimmed %}
Este es un párrafo largo
que ocupa más de
una sola línea.
{% endblocktrans %}
```

Párrafos largos con reemplazos:
```
{% blocktrans trimmed with icon="<i class=\"fas fa-map-marker-alt\"></i>" %}
Este es un párrafo largo con una etiqueta {{icon}}
que NO querés que se mezcle con
los textos a traducir.
{% endblocktrans %}
```

### Python

```
from django.utils.translation import gettext as _

_("Usalo como cualquier otro texto")
```
