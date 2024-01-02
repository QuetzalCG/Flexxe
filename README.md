## Flexxe <3

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

```python
import Flexxe

flexxe = Flexxe.analize(url = 'https://www.example.com')

print(flexxe)
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