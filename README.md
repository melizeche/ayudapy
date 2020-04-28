# ayudaPy

Platform to help people help people

#### URL

https://ayudapy.org

## Requirements

- Python 3.6+
- Django 2.2+
- PostGIS 3.0+
- PostgreSQL 11+

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

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Add your name and git account to the Contributors section in this `Readme.MD` :D
6. Submit a pull request to `dev` branch

## Author

- Marcelo Elizeche Landó https://github.com/melizeche

## Contributors / Thanks

- Agustin Gomez Mansilla https://github.com/gomezag
- Agustín Gómez https://github.com/gomezag
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
- Roque Vera https://github.com/roquegv

## TODO

- Documentation
- Support geolocation
- Captcha
- ~~Create models~~
- Users(?)
- Test

More in [TODO.md](TODO.md)

## License

This project is licensed under the terms of the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details
