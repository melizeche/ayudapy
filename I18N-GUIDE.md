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
