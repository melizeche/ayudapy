# ayudaPy

Humanitarian platform to help people help people

#### URL

https://ayudapy.org

### DjangoCon US 2022 Talk

https://www.youtube.com/watch?v=vtIxkRnQxvk

### Screenshots

![image](https://github.com/melizeche/ayudapy/assets/484773/6e97d802-016c-4512-b90e-15cf1d7c688d)
![image](https://github.com/melizeche/ayudapy/assets/484773/f2d25a99-8914-454a-897b-7d3e83a4ad5d)


## Requirements

- Python 3.8+
- Django 4.2+
- PostGIS 3.0+
- PostgreSQL 11+
- Gettext 0.19+

## Install

GeoDjango https://kitcharoenp.github.io/gis/2018/06/12/geodjango_installation.html

```
git clone git@github.com:melizeche/ayudapy.git
cd ayudapy
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp conf/.env.example conf/.env # you should edit this file with your configuration
./manage.py migrate
./manage.py compilemessages
./manage.py runserver
```

We use `django-pipeline` to handle CSS/JS assests, and this library requires `yuglify`. To install `yuglify`, issue the following:

```
npm -g install yuglify
```

The above command assumes that [NPM](https://www.npmjs.com/get-npm) is available.

## Install using docker-compose

```
git clone git@github.com:melizeche/ayudapy.git && cd ayudapy
cp conf/.env.example conf/.env # you should edit this file with your configuration
docker-compose up -d --build
docker-compose exec app ./manage.py migrate
```

## Want to help?

* Check/Ask GitHub issues https://github.com/melizeche/ayudapy/issues
* If want you add/modify some string in the core app check the [Internationalization/i18n Guide](I18N-GUIDE.md)
* Any doubts?: Ask in the dev channel @ayudapy_dev in Telegram

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Add your name and git account to the Contributors section in this `README.md` :D
6. Submit a pull request to `dev` branch

## Author

- Marcelo Elizeche Landó https://github.com/melizeche

## Contributors / Thanks

- Agustin Gomez Mansilla https://github.com/gomezag
- Alejandro Duque 🇨🇴 https://github.com/aleducode
- Axel Ferreira https://github.com/axelampro
- Blas Isaias Fernández https://github.com/BlasFerna
- Cabu Vallejos https://github.com/cabupy
- Diego Allen https://github.com/dalleng
- Diego Schulz https://github.com/dschulz
- Diosnel Velázquez https://github.com/diosnelv
- Felipe Hermosilla https://github.com/felipehermosilla
- Félix Pedrozo https://github.com/X1lef
- Grosip https://github.com/grosip
- Guillermo Caballero https://github.com/Guillecaba
- Jean Claude Adams https://github.com/jcroot
- Jesus Alderete https://github.com/jesus-bucksapp
- Joaquín Olivera https://github.com/joaquinolivera
- Jorge Ramírez https://github.com/jorgeramirez
- Juan Hüttemann https://github.com/juanhuttemann
- Leonardo Carreras https://github.com/leocarreras
- Manuel Nuñez https://github.com/manununhez
- Mauricio Medina https://github.com/mauri-medina
- Miguel Báez https://github.com/migueljoba 
- Osbarge https://github.com/osbarge
- Pablo Santa Cruz https://github.com/pablo

## TODO

- Documentation
- Tests
- See Github Issues https://github.com/melizeche/ayudapy/issues

## Apps / Related projects

* iOS app
  * App: https://apps.apple.com/py/app/ayudapy/id1508566089
  * Code: https://github.com/pescode/AyudaPY-iOS
* Android app 
  * App: https://play.google.com/store/apps/details?id=org.ayudapy
  * Code: https://gitlab.com/rubenlop88/ayudapy
* Argentina Por Vos fork 
  * Site : https://argentinaporvos.org/
  * Code: https://github.com/coderio-co/argentinaporvos

## License

This project is licensed under the terms of the GNU Affero General Public License v3.0 - see the [LICENSE](LICENSE) file for details
