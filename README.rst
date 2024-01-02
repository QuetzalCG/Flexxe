Flexxe | Install
-----------------
``git clone https://github.com/QuetzalCG/Flexxe.git``
``pip install -r Flexxe/requirements.txt``

Flexxe | USAGE
-----------------

The API exposes two objects: ``Flexxe.Flexxe`` and ``Flexxe.WebPage``. 

>>> from Flexxe import Flexxe, WebPage

First create a WebPage. The following code creates a webpage with the ``request`` module. 

>>> webpage = WebPage.newFURL('http://example.com')

Then analyze it with Flexxe.

>>> flexxe = Flexxe.latest()
>>> flexxe.analyze(webpage)
{
    "status": true,
    "url": "ur.site.here",
    "server": "cloudflare",
    "securities": [
        "Cloudflare"
    ],
    "ecommerce": [
        "WooCommerce"
    ],
    "langsP": [
        "PHP"
    ],
    "processors": [
        "Braintree"
    ]
}

Note:
    Last version to support Python2 was `0.2.2`.  