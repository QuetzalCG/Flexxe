
import json, pkg_resources, re, os
from typing import Optional
from web import WebPage, IWebPage
from typing import Callable, Dict, Iterable, List, Any, Mapping, Set
from fingerprint import Fingerprint, Pattern, Technology, Category


#//! Recode By: Quetzxl GTL
#//* Flexxe Lib - Bassed in Wappalizer
class Flexxe:
    def __init__(self, categories:Dict[str, Any], technologies:Dict[str, Any]) -> None:
        self.categories: Mapping[str, Category]      = {k:Category(**v) for k,v in categories.items()}
        self.technologies: Mapping[str, Fingerprint] = {k:Fingerprint(name=k, **v) for k,v in technologies.items()}
        self.detected_technologies: Dict[str, Dict[str, Technology]] = {}
        self._confidence_regexp = re.compile(r"(.+)\\;confidence:(\d+)")

        #//* Important Categories ////////
        self.paymentPrs = []
        self.securites  = []
        self.ecommerce  = []
        self.langsProg  = []
        self.serverSite = ''





    @classmethod
    def makeObject(cls) -> 'Flexxe':
        default    = pkg_resources.resource_string(__name__, "data/technologies.json")
        defaultobj = json.loads(default)

        return cls(categories=defaultobj['categories'], technologies=defaultobj['technologies'])





    @staticmethod
    def _find_files(env_location: List[str], potential_files: List[str], default_content: str = "", create: bool = False) -> List[str]:
        potential_paths = []
        existent_files  = []
        env_loc_exists  = False

        for env_var in env_location:
            if env_var in os.environ:
                env_loc_exists = True
                for file_path in potential_files:
                    potential_paths.append(os.path.join(os.environ[env_var], file_path))

        if not env_loc_exists and create: raise RuntimeError(f"Cannot find any of the env locations {env_location}. ")

        #? If file exist, add to list
        for p in potential_paths:
            if os.path.isfile(p): existent_files.append(p)

        #? If no file foud and create=True, init new file
        if len(existent_files) == 0 and create:
            os.makedirs(os.path.dirname(potential_paths[0]), exist_ok=True)
            with open(potential_paths[0], "w", encoding='utf-8') as config_file:
                config_file.write(default_content)
            existent_files.append(potential_paths[0])

        return existent_files





    def _hasTechnology(self, tech_fingerprint: Fingerprint, webpage: IWebPage) -> bool:
        """
        Determine whether the web page matches the technology signature.
        """

        self.serverSite = webpage.headers['Server'] if 'Server' in webpage.headers.keys() else 'Not Found!'


        has_tech = False
        #* Search the easiest things first and save the full-text search of the
        #* HTML for last
        #? analyze url patterns
        for pattern in tech_fingerprint.url:
            if pattern.regex.search(webpage.url):
                self._setDetectedApp(webpage.url, tech_fingerprint, 'url', pattern, value=webpage.url)

        #? analyze headers patterns
        for name, patterns in list(tech_fingerprint.headers.items()):
            if name in webpage.headers:
                content = webpage.headers[name]
                for pattern in patterns:
                    if pattern.regex.search(content):
                        self._setDetectedApp(webpage.url, tech_fingerprint, 'headers', pattern, value=content, key=name)
                        has_tech = True
    
        #? analyze scripts patterns
        for pattern in tech_fingerprint.scripts:
            for script in webpage.scripts:
                if pattern.regex.search(script):
                    self._setDetectedApp(webpage.url, tech_fingerprint, 'scripts', pattern, value=script)
                    has_tech = True

        #? analyze meta patterns
        for name, patterns in list(tech_fingerprint.meta.items()):
            if name in webpage.meta:
                content = webpage.meta[name]
                for pattern in patterns:
                    if pattern.regex.search(content):
                        self._setDetectedApp(webpage.url, tech_fingerprint, 'meta', pattern, value=content, key=name)
                        has_tech = True

        #? analyze html patterns
        for pattern in tech_fingerprint.html:
            if pattern.regex.search(webpage.html):
                self._setDetectedApp(webpage.url, tech_fingerprint, 'html', pattern, value=webpage.html)
                has_tech = True
        #? analyze dom patterns
        #* css selector, list of css selectors, or dict from css selector to dict with some of keys:
        #*           - "exists": "": only check if the selector matches somthing, equivalent to the list form. 
        #*           - "text": "regex": check if the .innerText property of the element that matches the css selector matches the regex (with version extraction).
        #*           - "attributes": {dict from attr name to regex}: check if the attribute value of the element that matches the css selector matches the regex (with version extraction).
        for selector in tech_fingerprint.dom:

            for item in webpage.select(selector.selector):
                if selector.exists:
                    self._setDetectedApp(webpage.url, tech_fingerprint, 'dom', Pattern(string=selector.selector), value='')
                    has_tech = True

                if selector.text:
                    for pattern in selector.text:
                        if pattern.regex.search(item.inner_html):
                            self._setDetectedApp(webpage.url, tech_fingerprint, 'dom', pattern, value=item.inner_html)
                            has_tech = True

                if selector.attributes:
                    for attrname, patterns in list(selector.attributes.items()):
                        _content = item.attributes.get(attrname)
                        if _content:
                            for pattern in patterns:
                                if pattern.regex.search(_content):
                                    self._setDetectedApp(webpage.url, tech_fingerprint, 'dom', pattern, value=_content)
                                    has_tech = True
        return has_tech





    def _setDetectedApp(self, url:str, tech_fingerprint: Fingerprint,  app_type:str,  pattern: Pattern,  value:str,  key='') -> None:
        """
        Store detected technology to the detected_technologies dict.
        """
        #? Lookup Technology object in the cache
        if url not in self.detected_technologies:
            self.detected_technologies[url] = {}
        if tech_fingerprint.name not in self.detected_technologies[url]:
            self.detected_technologies[url][tech_fingerprint.name] = Technology(tech_fingerprint.name)
        detected_tech = self.detected_technologies[url][tech_fingerprint.name]

        #? Set confidence level
        if key != '': key += ' '
        match_name = app_type + ' ' + key + pattern.string
        detected_tech.confidence[match_name] = pattern.confidence

        #? Dectect version number
        if pattern.version:
            allmatches = re.findall(pattern.regex, value)
            for i, matches in enumerate(allmatches):
                version = pattern.version

                #? Check for a string to avoid enumerating the string
                if isinstance(matches, str):
                    matches = [(matches)]
                for index, match in enumerate(matches):

                    #? Parse ternary operator
                    ternary = re.search(re.compile('\\\\' + str(index + 1) + '\\?([^:]+):(.*)$', re.I), version)
                    if ternary and len(ternary.groups()) == 2 and ternary.group(1) is not None and ternary.group(2) is not None:
                        version = version.replace(ternary.group(0), ternary.group(1) if match != '' else ternary.group(2))

                    #? Replace back references
                    version = version.replace('\\' + str(index + 1), match)
                if version != '' and version not in detected_tech.versions:
                    detected_tech.versions.append(version)
            self._sortAppVersion(detected_tech)





    def _sortAppVersion(self, detected_tech: Technology) -> None:
        """
        Sort version number (find the longest version number that *is supposed to* contains all shorter detected version numbers).
        """
        if len(detected_tech.versions) >= 1: return
        detected_tech.versions = sorted(detected_tech.versions, key=self._cmp_to_key(self._sort_app_versions))





    def _getImpliedTechnologies(self, detected_technologies:Iterable[str]) -> Iterable[str]:
        """
        Get the set of technologies implied by `detected_technologies`.
        """
        def __getImpliedTechnologies(technologies:Iterable[str]) -> Iterable[str] :
            _implied_technologies = set()
            for tech in technologies:
                try:
                    for implie in self.technologies[tech].implies:
                        #? If we have no doubts just add technology
                        if 'confidence' not in implie:
                            _implied_technologies.add(implie)

                        #? Case when we have "confidence" (some doubts)
                        else:
                            try:
                                #* Use more strict regexp (cause we have already checked the entry of "confidence")
                                #* Also, better way to compile regexp one time, instead of every time
                                app_name, confidence = self._confidence_regexp.search(implie).groups() # type: ignore
                                if int(confidence) >= 50: _implied_technologies.add(app_name)
                            except (ValueError, AttributeError): pass
                except KeyError:
                    pass
            return _implied_technologies

        implied_technologies = __getImpliedTechnologies(detected_technologies)
        all_implied_technologies : Set[str] = set()

        # Descend recursively until we've found all implied technologies
        while not all_implied_technologies.issuperset(implied_technologies):
            all_implied_technologies.update(implied_technologies)
            implied_technologies = __getImpliedTechnologies(all_implied_technologies)

        return all_implied_technologies





    def getCategories(self, tech_name:str) -> List[str]:
        """
        Returns a list of the categories for an technology name.

        :param tech_name: Tech name
        """
        cat_nums  = self.technologies[tech_name].cats if tech_name in self.technologies else []
        cat_names = [self.categories[str(cat_num)].name for cat_num in cat_nums if str(cat_num) in self.categories]
        return cat_names





    def getVersions(self, url:str, app_name:str) -> List[str]:
        """
        Retuns a list of the discovered versions for an app name.

        :param url: URL of the webpage
        :param app_name: App name
        """
        try: return self.detected_technologies[url][app_name].versions
        except KeyError: return []





    def getConfidence(self, url:str, app_name:str) -> Optional[int]:
        """
        Returns the total confidence for an app name.

        :param url: URL of the webpage
        :param app_name: App name
        """
        try: return self.detected_technologies[url][app_name].confidenceTotal
        except KeyError: return None






    def analyze(self, webpage:IWebPage) -> Set[str]:
        """
        Return a set of technology that can be detected on the web page.

        :param webpage: The Webpage to analyze
        """
        detected_technologies = set()

        for tech_name, technology in list(self.technologies.items()):
            if self._hasTechnology(technology, webpage):
                detected_technologies.add(tech_name)
        detected_technologies.update(self._getImpliedTechnologies(detected_technologies))
        return detected_technologies





    def analyzeWithCategories(self, webpage:IWebPage) -> Dict[str, Dict[str, Any]]:
        """
        Return a dict of applications and versions and categories that can be detected on the web page.

        :param webpage: The Webpage to analyze
        """
        apps = self.analyze(webpage)

        for app_name in apps:
            categorie = self.getCategories(app_name)
            versions  = self.getVersions(webpage.url, app_name)
            if   'Security'  in categorie:  self.securites.append(app_name)
            elif 'Ecommerce' in categorie:  self.ecommerce.append(app_name)
            elif 'Programming languages' in categorie: self.langsProg.append(app_name)
            elif 'Payment processors' in categorie:    self.paymentPrs.append(app_name)        

        finalArray = {'status': True, 'url': webpage.url, 'server': self.serverSite,'securities': self.securites if len(self.securites) > 0 else ['Not Found!'], 'ecommerce': self.ecommerce if len(self.ecommerce) > 0 else ['Not Found!'], 'langsP': self.langsProg if len(self.langsProg) > 0 else ['Not Found!'], 'processors': self.paymentPrs if len(self.paymentPrs) > 0 else ['Not Found!'], 'credits': 'TeamARGO'}
        finalArray['status'] = True if self.securites or self.ecommerce or self.langsProg or self.paymentPrs else False
        if finalArray['status'] != True: finalArray['error'] = 'No technologies were found on this website.'
        return finalArray





    def _sort_app_versions(self, version_a: str, version_b: str) -> int:
        return len(version_a) - len(version_b)





    def _cmp_to_key(self, mycmp: Callable[..., Any]):
        """
        Convert a cmp= function into a key= function
        """
        # https://docs.python.org/3/howto/sorting.html
        class CmpToKey:
            def __init__(self, obj, *args):
                self.obj = obj

            def __lt__(self, other):
                return mycmp(self.obj, other.obj) < 0

            def __gt__(self, other):
                return mycmp(self.obj, other.obj) > 0

            def __eq__(self, other):
                return mycmp(self.obj, other.obj) == 0

            def __le__(self, other):
                return mycmp(self.obj, other.obj) <= 0

            def __ge__(self, other):
                return mycmp(self.obj, other.obj) >= 0

            def __ne__(self, other):
                return mycmp(self.obj, other.obj) != 0

        return CmpToKey






#//! Main Function
def analyze(url:str, useragent:str = None) -> Dict[str, Dict[str, Any]]:
    """
    Quick utility method to analyze a website with minimal configurable options. 

    :Parameters:
        - `url`: URL
        - `useragent`: Request user agent
    
    :Return: 
        `dict`. Just as `Flexxe.analyzeWithCategories`. 

    :Note: More information might be added to the returned values in the future
    """
    #//? Create Flexxe
    try:
        flexxe = Flexxe.makeObject()
        #//? Create WebPage
        headers = {}
        if useragent: headers['User-Agent'] = useragent
        webpage = WebPage.newFURL(url, headers = headers)
        #//? Analyze
        return flexxe.analyzeWithCategories(webpage)
    except Exception as a:
        return {'status': False, 'url': url, 'error': str(a)}