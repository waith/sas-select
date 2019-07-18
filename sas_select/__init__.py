import os

from flask import Flask, render_template, abort, request, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from . import datasheet
from . import db
from . import version


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    Bootstrap(app)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'db_products.sqlite'),    # change db name
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/', methods=('GET', 'POST'))
    def view_products():
        def sql_search_str(form_search_str):
            if form_search_str is None or len(form_search_str.strip()) == 0:
                return ''
            else:
                return form_search_str.strip()

        sas_db = db.get_db()
        if request.method == 'POST':
            company_code = sql_search_str(request.form['CompanyCode'])
            brand_name = sql_search_str(request.form['BrandName'])

            if len(company_code) == 0 and len(brand_name) == 0:
                products = None
                flash('No search query entered', 'error')
            else:
                # Try fetching exact company_code first
                sql = """select *
                        from tbl_products
                        where CompanyCode=:cc and BrandName like :bn
                        limit 20
                        """

                products = sas_db.execute(sql, {"cc": company_code, "bn": '%' + brand_name + '%'}).fetchall()

                if not products:  # Can't find exact company_code
                    sql = """select *
                            from tbl_products
                            where CompanyCode like :cc and BrandName like :bn
                            limit 20
                            """
                    products = sas_db.execute(sql, {"cc": '%' + company_code + '%', "bn": '%' + brand_name + '%'}).fetchall()

        else:
            products = None
        return render_template('listproducts.html', products=products, page_title="Products in database", frm=request.form, version=version.VERSION)

    def pack_entitlement(packsize, entitlement):
        if "m" in entitlement:
            frequency = "month"
        elif "a" in entitlement:
            frequency = "year"
        else:
            return

        packs = int(entitlement[:-1])//packsize
        exception1 = packsize//int(entitlement[:-1])
        if packs > 0:
            return "Your medicare entitlement is " + str(packs) + " packs per " + frequency
        else:
            remainder = packsize % int(entitlement[:-1])
            if remainder > 0:
                exception1 += 1
        return "Your medicare entitlement is " + str(exception1) + " packs per " + frequency

    @app.route('/product/<id_product>')
    def view_product(id_product):
        if not id_product:
            abort(404)
        pm_db = db.get_db()
        product = pm_db.execute('select * from tbl_products where id=?', (id_product,)).fetchone()
        if not product:
            abort(404)
        qty = pack_entitlement(product["PackSize"], product["MaximumQty"])
        print(qty)
        return render_template('viewproduct.html', product=product, page_title="View product", pack_entitlement=qty, version=version.VERSION)
    db.init_app(app)

    @app.route('/init-db')
    def init_db():
        datasheet.init_db()
        return redirect(url_for('view_products'))

    @app.template_filter()
    def format_price(price):
        if price is None:
            return '-'
        elif price >= 0:
            return '${:,.2f}'.format(price)
        else:
            return '-${:,.2f}'.format(abs(price))

    return app
