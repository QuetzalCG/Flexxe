## Flexxe: Lib 

***Library to visualize the technologies used by a website, based on wappalizer***


## How Install Flexxe!

**Step One**: `Clone the repository`

```bash
git clone https://github.com/QuetzalCG/Flexxe.git
```


**Step Two**: `Install dependencies`

```bash
pip install -r Flexxe/requirements.txt
```





## How Use Flexxe!
*The API exposes two objects*: ``Flexxe.Flexxe`` *and* ``Flexxe.WebPage``. 

```python
from Flexxe import Flexxe, WebPage
```

*First create a WebPage. The following code creates a webpage with the* ``request`` *module.*

```python
webpage = WebPage.newFURL('http://example.com')
```

*Then analyze it with Flexxe.*

```python
flexxe = Flexxe.latest()
flexxe.analyze(webpage)
```

***Response:***
```json
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
```


*Note:*
    ***Last version to support Python2 was*** `0.2.2`.  