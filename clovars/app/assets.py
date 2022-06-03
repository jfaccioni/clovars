from flask_assets import Bundle
from webassets.exceptions import BuildError


def compile_static_assets(
        assets,
        env: str,
) -> None:
    # Home asset bundles
    home_style_bundle = Bundle(
        'css/*.css',
        # 'less/*.less',
        # 'home_bp/css/*.css',
        # 'home_bp/less/*.less',
        filters='less,cssmin',
        depends=('css/*.css', 'home_bp/css/*.css'),
        output='dist/style.min.css',
        extra={'rel': 'stylesheet/css'}
    )
    home_js_bundle = Bundle(
        # 'js/*.js',
        # 'home_bp/js/*.js',
        filters='jsmin',
        depends=('js/*.js', 'home_bp/js/*.js'),
        output='dist/main.min.js'
    )
    # Treatment asset bundles
    treatment_style_bundle = Bundle(
        'css/*.css',
        # 'less/*.less',
        'treatment_bp/css/*.css',
        # 'treatment_bp/less/*.less',
        filters='less,cssmin',
        depends=('css/*.css', 'treatment_bp/css/*.css'),
        output='treatment_bp/dist/style.min.css',
        extra={'rel': 'stylesheet/css'}
    )
    treatment_js_bundle = Bundle(
        # 'js/*.js',
        # 'treatment_bp/js/*.js',
        filters='jsmin',
        depends=('js/*.js', 'treatment_bp/js/*.js'),
        output='dist/main.min.js'
    )
    assets.register('home_styles', home_style_bundle)
    assets.register('home_js', home_js_bundle)
    assets.register('treatment_styles', treatment_style_bundle)
    assets.register('treatment_js', treatment_js_bundle)
    if env == 'development':
        home_style_bundle.build()
        try:
            home_style_bundle.build()
            print('Built CSS for home blueprint')
        except BuildError:
            print('Skipped building CSS for home blueprint - empty contents')
        try:
            home_js_bundle.build()
            print('Built JS for home blueprint')
        except BuildError:
            print('Skipped building JS for home blueprint - empty contents')
        try:
            treatment_style_bundle.build()
            print('Built CSS for treatment blueprint')
        except BuildError:
            print('Skipped building CSS for treatment blueprint - empty contents')
        try:
            treatment_js_bundle.build()
            print('Built JS for treatment blueprint')
        except BuildError:
            print('Skipped building JS for treatment blueprint - empty contents')
